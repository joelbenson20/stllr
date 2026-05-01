<!-- Done by Claude, requires review -->

# stellr — The Universal Forum

stellr is a "universal forum" that turns any public webpage into a shared
discussion thread. Anyone can paste a URL into stellr (or click the
companion Chrome extension while browsing) and the page becomes a
first-class object in the system: it gets a normalized canonical
identity, OpenGraph-derived metadata, an upvote count, and a threaded
comment section. The home feed ranks pages by vote count, so the
community surfaces the parts of the web worth talking about.

The Django project on disk is named `float` — the verb the product is
built around. To *float* a URL is to lift it out of your browser and
into the public conversation.

## Mission

Most internet discussion happens in walled gardens (Reddit, X, Hacker News,
Discord servers) where a piece of content has to be re-posted into each
community to be discussed. stellr inverts that: the URL itself is the
discussion anchor, and every voter and commenter — regardless of where they
found the link — converges on the same thread. The goal is one canonical
conversation per webpage on the open web.

## How it works

1. A signed-in user submits a URL through the navbar form or the Chrome
   extension.
2. `forum.utils.get_canonical` normalizes the URL — lowercased host,
   `www.` stripped, default ports dropped, path normalized, and an
   allowlist of query params (`q`, `query`, `search`, `page`, `p`, `id`, `v`)
   so tracking/session params can't fragment the same page into many
   threads.
3. If a `Page` with that canonical already exists, the user is redirected
   to its forum thread. Otherwise `getOGMetaData` calls the
   [opengraph.io](https://opengraph.io) API to fetch title, description,
   image, site name, and favicon, and a new `Page` row is created.
4. Submitting a page also casts the submitter's first upvote
   (`PageVote`). Other users can toggle their own vote from the feed or
   the page detail view.
5. Comments are powered by `django-comments-xtd`, configured for threaded
   replies (max depth 3), flagging, and feedback on the `forum.page`
   model.

## Repository layout

```
float/
├── float/          Django project package — settings, root urls, wsgi/asgi
├── forum/          Core app: Page model, feed, page detail, "float" submission, OG fetch
├── users/          Custom AbstractUser + PageVote model + per-user profile view
├── extension/      JSON endpoints used by the Chrome extension (CSRF, float, vote toggle)
├── comments/       Template overrides + templatetags for django-comments-xtd
├── webpages/       Legacy app (migrations only — superseded by forum.Page)
├── staticfiles/    collectstatic output (whitenoise serves these in prod)
├── manage.py       Django entry point
├── requirements.txt
└── TODO.md         Open feature ideas and questions
```

### `forum/` — the link aggregator

- `models.Page` — one row per canonical URL, with cached OG metadata and a
  `num_votes` property. Registered with `XtdCommentModerator` so comments
  can be flagged.
- `views.index` — home feed, top 100 pages by vote count.
- `views.page_forum` — single-page forum thread (looked up by `?page=<canonical>`).
- `views.page_float` — POST handler for submitting a URL. Performs a
  cheap canonical lookup first, then falls back to fetching OG metadata
  and creating the `Page`.
- `utils.get_canonical` — URL normalization (the heart of "one
  conversation per page").
- `utils.getOGMetaData` — OpenGraph.io client.
- `utils.verify_security` — placeholder for the URL-safety check listed
  in `TODO.md`.

### `users/` — accounts and votes

- `models.User` — `AbstractUser` subclass with `voted_pages` /
  `voted_pages_ids` helpers used by the feed templates to render the vote
  state.
- `models.PageVote` — `(user, page)` unique-together vote row; counted via
  `Page.votes` reverse relation.
- `views.user` — public profile page showing a user's voted pages and
  every public comment they've left, with parent-comment context bulk-loaded.

### `extension/` — Chrome extension API

These endpoints are JSON, not HTML, and are CSRF-trusted for a specific
Chrome extension origin (see `CORS_ALLOWED_ORIGINS` and
`CSRF_TRUSTED_ORIGINS` in `float/settings.py`). The extension itself is
not committed to this repo.

- `csrf-token/` — issues a CSRF token to a logged-in extension session.
- `extension/` — given page metadata scraped by the extension's content
  script, finds-or-creates a `Page` and returns rendered HTML for the
  extension popup.
- `page_float/` — toggles the current user's vote on a `Page` and returns
  the new vote count.

### `comments/` — django-comments-xtd glue

Template overrides and template tags for the comment widget. The model
itself comes from `django_comments_xtd`; this app only customizes
presentation.

## Tech stack

- Django 6 + djangorestframework
- django-comments-xtd for threaded comments
- whitenoise for static file serving
- psycopg2 + dj-database-url so the same code runs against SQLite locally
  and Postgres in production (toggled by `USE_ONLINE_STORAGE`)
- BeautifulSoup / lxml / metadata_parser / tldextract for URL and HTML
  handling
- requests for outbound HTTP (OG metadata fetch)

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Required environment variables (put them in a .env at the repo root)
#   DJANGO_SECRET_KEY=<random string>
#   DJANGO_DEBUG=True
#   OPEN_GRAPH_API_KEY=<your opengraph.io key>
#   MANAGER_EMAIL=<email for django ManagementCommand error reports>
# Optional:
#   USE_ONLINE_STORAGE=True and DATABASE_URL=postgres://...   # use Postgres instead of sqlite
#   LOCAL_IP_ADDRESS=192.168.x.x                              # add to ALLOWED_HOSTS

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Email is routed to the console backend in development, so password-reset
links and comment notifications print to the terminal.

## Roadmap

See [`TODO.md`](TODO.md). Headline items:

- URL-safety verification before a page is created (currently a no-op stub).
- Webpage classifier — categorize submitted URLs (article / video / social
  post / …).
- AI-generated descriptions for pages that don't expose `og:description`.
- A real ranking algorithm for the feed (vote count is a placeholder).
