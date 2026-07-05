# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Policy Conformance Rule

All code in this project must conform with our privacy policy, terms of service, and the policies listed in stllr/oversight/policies.py, which includes policies for pages, posts, users, and even code, which means all the code of this project. You will guide programmers to write code that conforms with these policies within reason. Where conformance is not within reason, a policy change ought to be suggested.

## Project Vision

Stllr will be a social layer residing on top of the internet. It will be the *place* where the socializing happens. This will include forums and chat rooms uniquely attached to every webpage across the internet, accessible through our browser extension or on our webpage. Stllr will be the best way to share and talk about internet content. Furthermore, information extracted from our forums will help to "frame" every webpage on the internet with informational context generated from posts in our forums.

Stllr will be transparent and built on top of well-defined policies. Content removal will be a public act, open to scrutiny, though excising content that cannot be shown at all. This transparency will spark discussions about our policies, which will help to refine them into a more *consistent* and *complete* almost mathematical delineation of exactly what *qualities* ought to be enforced in the social layer of the internet. Our policies will make Stllr forums safe, playful, educational spaces. From the browser extension standpoint, this will enable us to add informative context to any webpage, breaking down the social bubbles across the internet.

## Code Style
Use bootstrap classes instead of CSS whenever possible, within reason. Any JS needs to be able run in the browser extension as well, so JS cannot be injected into the document after it is loaded. onclick(), for example is not allowed.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (http://localhost:8000/)
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test                    # all tests
python manage.py test forums             # single app
python manage.py test forums.tests.TestClassName.test_method  # single test

# Start Celery worker
celery -A stllr worker -l info

# Start Celery beat scheduler
celery -A stllr beat -l info

# Collect static files (production)
python manage.py collectstatic

# Create admin user
python manage.py createsuperuser         # admin at /admin/
```

## Architecture

### Django Apps

- **pages** — Core content app. `Page` stores webpage metadata (canonical URL, title, description, OG image, domain, brightness, search vector). `Domain` stores per-domain metadata (favicon, category). `PagePin` is the pin/bookmark junction. Signals auto-download images and rebuild PostgreSQL search vectors on save. `utils.py` contains URL canonicalization, security verification, and `UnsupportedURLError`. `page_processors.py` handles YouTube oEmbed enrichment.
- **forums** — Threaded discussion posts linked to pages. `Post` supports self-referential threading (parent FK, thread_level) and soft-deletion (removed + removed_by fields). Rate-limited at 10 posts/min. Replies are enforced to begin with `@parent_author_username`.
- **rooms** — Real-time chat per page. `Broadcast` model stores chat messages (retained 90 days). `consumers.py` is the Django Channels WebSocket consumer with presence tracking (Redis cache, 20s TTL heartbeat).
- **stars** — Generic star/like system. `Star` model uses a ContentType generic FK and can target `Page` or `Post`. `utils.py` contains the `calculate_brightness()` formula. Celery tasks handle star decay and brightness recalculation. Rate-limited at 3 stars/second.
- **users** — Custom `User` (extends AbstractUser), `Profile` (OneToOne, background image), `ContactRelation` (friendship with PENDING/ACCEPTED states), `Mute` (per-user content filtering). Context processors inject notifications, contacts list, and muted user IDs into all templates.
- **comms** — Notification system. `Notification` (with actor aggregation via `NotificationActor`) handles events: CONTACT_REQUEST, CONTACT_ACCEPTED, POST_STARRED, POST_REPLIED, POST_SHARED, PAGE_SHARED, PAGE_ALSO_STARRED, POST_ALSO_STARRED. Signals in various apps call the central `notify()` helper. `share_object` view lets users share pages/posts with contacts (rate-limited 10/min).
- **oversight** — Content moderation. `PageReport` and `PostReport` models (both extend abstract `Report`) allow users to flag content against enumerated policies defined in `policies.py`. Prevents duplicate reports per user per content item.
- **extension** — Chrome extension API endpoints. Accepts page metadata POST (requires extension version 2.0+), creates `Page` if needed, returns popup HTML for forum/room/nearby/frame tabs. Provides CSRF tokens and short-lived WebSocket auth tickets (30s TTL via Redis). CORS-whitelisted for three registered extension IDs.
- **stella** — AI prompt management. `Prompt` model stores per-page LLM prompts (model, prompt template, output, status, token count). Default prompts (summary, primary sources, user sentiment, user-added context) are auto-created via signal when a Page gets content. Output is surfaced in the extension's frame tab.

### Key Models & Relationships

```
Page → (has many) Post → (posted by) User
Page → (has many) Broadcast → (posted by) User
Page → (belongs to) Domain
Page → (has many) Prompt (AI-generated summaries)
User → (has many) Star → (references) Page or Post  [via ContentType]
User → (has many) PagePin → (references) Page
User → (has many) Notification (as recipient)
User → (has many) ContactRelation (self-referential friendship)
User → (has many) Mute (self-referential content filtering)
User → (has one) Profile
```

### Brightness Algorithm ("Firmament")

Pages and Posts are both ordered by a **brightness** score that decays over time:

- `Star` records older than 7 days are deleted by a Celery task (`stars.delete_old_stars`).
- Brightness is recalculated as `1/(user_count - star_count)^2` (inverse square law: stars = pull, non-stars = distance). Edge cases: all-starred → `1e15`, no-stars → `1e-15`.
- `brightness_index` ranks pages by brightness with a random tiebreaker (`RANDOM()` in PostgreSQL). The `rise` field tracks rank movement.
- The page feed uses NumPy weighted random selection so brighter pages appear more frequently but not exclusively — a probabilistic "night sky" feed.
- All three tasks live in `stars/tasks.py` and are scheduled daily in `CELERY_BEAT_SCHEDULE`.

### Real-Time Chat (Django Channels)

- ASGI server: Daphne. Config in `stllr/asgi.py` — `ProtocolTypeRouter` for HTTP + WebSocket.
- WebSocket route: `ws/room/<page_id>/`
- `RoomConsumer` (async): authenticates via Django session cookie **or** a short-lived WS ticket (for extension cross-origin context). Tracks presence in Redis, broadcasts join/leave events and new messages to the room group.
- OriginValidator whitelist: `stllr.io` + three Chrome extension IDs.

### Celery Background Tasks

Redis broker + backend. Four periodic tasks scheduled in `CELERY_BEAT_SCHEDULE`:

- `stars.delete_old_stars` — removes Stars older than 7 days (daily).
- `stars.update_brightnesses` — recalculates brightness for all Pages and Posts (daily).
- `stars.update_brightness_indexes_and_rises` — re-ranks pages and stores `rise` delta (daily).
- `rooms.delete_old_broadcasts` — removes Broadcasts older than 90 days (daily).

### URL Structure

- `/` — Home (authenticated feed / landing).
- `/explore/` — Page feed. Supports `query=`, `sort=firmament|brightest|rising`, `starred_by=`, `near_to=`.
- `/contacts/` — Contact management (requires login).
- `/comms/` — Notification inbox (marks notifications read on visit).
- `/pins/` — User's pinned pages.
- `/forum/<page_id>/` — Threaded forum for a page.
- `/room/<page_id>/` — Real-time chat room for a page.
- `/users/<username>/posts/` — User's posts.
- `/users/<username>/stars/` — User's starred items.
- `/users/<username>/edit/` — Edit profile.
- `/accounts/` — django-allauth (login, signup, Google OAuth2, email verification).
- `/policies/<policy>/` — Privacy policy / user agreement.
- `/oversight/` — Report page/post endpoints.
- `/extension/` — Extension endpoints: root POST (metadata), `csrf-token/`, `ws-ticket/`, `restricted/`.
- `/stars/` — Toggle star endpoint.
- `/pages/` — Toggle pin endpoint.
- `/admin/` — Django admin.
- `ws/room/<page_id>/` — WebSocket endpoint (Channels).

### Database & Configuration

- PostgreSQL (configured via environment variables using `python-decouple`).
- Redis for cache, Channels layer, and Celery broker/backend.
- Settings split: `stllr/settings/base.py` (shared), `dev.py` (DEBUG, console email), `prod.py` (SSL, Sentry, Resend email, WhiteNoise).

### Static Files & Templates

- Global static assets in `stllr/static/` — Bootstrap 5, Bootstrap Icons, brand assets.
- Per-app CSS/JS in `<app>/static/` — `forums.js`, `rooms.js`, `pages.js`, `stllr.js`, `modals.js`, `stars.js`.
- Base template at `stllr/templates/base.html` — navbar, search, auth status.
- Template directories follow the pattern `<app>/templates/<app>/<model>/<variant>.html` (e.g., `forums/templates/forums/post/card.html`).
- WhiteNoise (`CompressedManifestStaticFilesStorage`) serves static files in production.

### Template Tags & Utilities

- `forums/templatetags/forum_tags.py` — `safe_markdown` filter (Markdown → bleach-sanitized HTML; allowed tags: p, br, strong, em, code, pre, blockquote, ul/ol/li, h1-h6, hr, a, img); `render_post` filter (same + @mention linking); `ancestry_chain` tag for threaded post hierarchy.
- `pages/templatetags/page_tags.py` — `random_seed()` tag.
- `stars/templatetags/star_tags.py` — `starred_by` filter, `object_ct_name` filter.
- Context processors (all three injected into every template):
  - `comms.context_processors.notifications` — `notifications.all` and `notifications.unread`.
  - `comms.context_processors.contacts` — `contacts_list` (sorted accepted contacts).
  - `comms.context_processors.muted_users` — `muted_user_ids` set for content filtering.

### Browser Extension Integration

Three registered Chrome extension IDs are whitelisted in CORS, CSRF trusted origins, and the WebSocket OriginValidator:

- `polpgpcagljhejdbajfbjgdchdlnfepk`
- `mlilkidmlfonjgccanoodpmbfjflggla`
- `hmpgjgepcimfdojfbffhaedmkndomfml`

**Extension flow:** User clicks extension → extension POSTs current URL + page metadata to `/extension/` (must be extension version 2.0+) → backend canonicalizes URL, runs YouTube enrichment if applicable, creates `Page` if new, returns popup HTML (forum/room/nearby/frame tabs) → for chat, extension fetches a WS ticket from `/extension/ws-ticket/` and opens WebSocket with `?ticket=<token>` → the frame tab shows Stella AI prompts generated for the page.

### Content Moderation (Oversight)

`PageReport` and `PostReport` each reference a policy choice from `oversight/policies.py`:

- **PAGE_POLICIES:** `not_a_page`, `explicit`, `spam`, `malicious`, `duplicate`, `misleading_thumbnail`, `other`.
- **POST_POLICIES:** `spam`, `harassment`, `misinformation`, `explicit`, `off_topic`, `other`.
- Reports have a `status` of `pending | dismissed | actioned`. Each user can submit at most one report per content item.
