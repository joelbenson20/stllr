# stllr

**stllr.io** — a social layer on top of the internet. Every unique webpage that meets our content and security criteria gets exactly one social space: a threaded forum and a live chat room. The companion browser extension surfaces that social space directly in the browser at wherever the user is currently browsing.

## How it works

1. A user visits a webpage and clicks the Chrome extension (or submits a URL on stllr.io).
2. The extension POSTs the current URL and scraped page metadata to the backend.
3. `pages.utils.get_canonical` normalizes the URL — lowercased host, `www.` stripped, default ports dropped, path normalized, tracking params removed — so every variant of the same page maps to one canonical identity.
4. If no `Page` exists for that canonical, one is created with OpenGraph metadata, domain favicon, and auto-extracted NLTK tags. A security check blocks private IPs and localhost variants.
5. The user enters the page's social space: a threaded forum (persistent posts) and a live chat room (WebSocket, real-time presence).
6. Pages are ranked by a brightness algorithm — a weighted, probabilistic feed where stars act as gravitational pull.

---

## Repository layout

```
stllr/                        ← repo root (docker-compose files live here)
├── Dockerfile
├── docker-compose.yml        ← production stack
├── docker-compose.dev.yml    ← dev stack (DB + Redis + Celery only)
├── wait-for-it.sh
├── config/
│   ├── nginx/default.conf.template
│   └── uwsgi/uwsgi.ini
├── data/                     ← Postgres volume mounts (gitignored)
└── stllr/                    ← Django project root
    ├── manage.py
    ├── requirements.txt
    ├── CLAUDE.md
    ├── stllr/                ← Django project package (settings, urls, asgi, wsgi)
    │   └── settings/
    │       ├── base.py
    │       ├── dev.py
    │       └── prod.py
    ├── pages/                ← Page, Domain, PageStar models; brightness algorithm; signals
    ├── forums/               ← Post, PostStar models; threaded discussions
    ├── rooms/                ← Message model; WebSocket consumer; presence tracking
    ├── users/                ← User, Profile, Contact, Action models; activity feed
    ├── extension/            ← Browser extension API endpoints; WS ticket issuance
    ├── api/                  ← REST endpoints (star, post, markdownify, room count)
    └── governance/           ← Placeholder (no models yet)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Web framework | Django 6 |
| ASGI / WebSockets | Django Channels 4 + Daphne |
| HTTP server | uWSGI (Unix socket) |
| Reverse proxy | Nginx 1.28 (TLS termination, WS upgrade, static files) |
| Task queue | Celery 5 (worker + beat) |
| Database | PostgreSQL 17 |
| Cache / broker | Redis 8 |
| Auth | django-allauth (email verification required) |
| NLP / tagging | NLTK (noun extraction), django-taggit |
| Full-text search | PostgreSQL `SearchVector` + `SearchQuery` |
| Image processing | easy-thumbnails, Pillow |
| Markdown | markdown-deux + bleach sanitization |
| Static files | WhiteNoise (CompressedManifestStaticFilesStorage) |
| TLS | Let's Encrypt (auto-renewed, mounted into nginx container) |
| Monitoring | Sentry (production only) |
| Email | Resend via django-anymail (production) / console (development) |
| Containerization | Docker + Docker Compose |
| Hosting | DigitalOcean droplet |

---

## Running locally

### Option A — Docker (recommended, matches production services)

```bash
# Start Postgres, Redis, Celery worker, and Celery beat
docker compose -f docker-compose.dev.yml up

# In a separate terminal, run Django's dev server (hot-reload)
cd stllr
python manage.py runserver
```

The dev compose file does **not** include a web/daphne container — the dev server handles both HTTP and WebSocket traffic directly.

### Option B — Without Docker

Requires a local PostgreSQL instance and Redis. Set the env vars below, then:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader stopwords wordnet punkt_tab averaged_perceptron_tagger_eng

cd stllr
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Separate terminals for background workers:
celery -A stllr worker --loglevel=info
celery -A stllr beat --loglevel=info
```

### Environment variables (`.env` in the `stllr/` directory)

```bash
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=stllr.settings.dev

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost      # or 'db' when using Docker
POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

MANAGER_EMAIL=
```

---

## Production deployment

The production stack is defined in `docker-compose.yml` and runs on a DigitalOcean droplet at **stllr.io**.

### Services

| Service | Image / Build | Role |
|---|---|---|
| `db` | postgres:17 | Primary database, volume-persisted |
| `cache` | redis:8 | Cache, Channels layer, Celery broker |
| `web` | ./Dockerfile | uWSGI — serves Django over Unix socket |
| `daphne` | ./Dockerfile | Daphne — serves WebSocket connections on port 9001 |
| `nginx` | nginx:1.28 | TLS termination, routes HTTP → uWSGI, `/ws/` → Daphne |
| `celery` | ./Dockerfile | Celery worker (brightness tasks, image downloads) |
| `celery-beat` | ./Dockerfile | Celery beat scheduler |

### Request routing

```
Client
  │
  ▼
Nginx :443 (TLS)
  ├── /ws/*  ──────────────────▶  Daphne :9001  (WebSocket)
  ├── /static/  ───────────────▶  WhiteNoise / filesystem alias
  ├── /media/   ───────────────▶  filesystem alias
  └── /*  ────────────────────▶  uWSGI Unix socket  (HTTP)
```

### Deploying an update

```bash
# On the droplet
git pull
docker compose build
docker compose up -d
```

`wait-for-it.sh` is used by the `web`, `daphne`, and `celery` containers to delay startup until Postgres is accepting connections. `collectstatic` and `migrate` run automatically inside the `web` container on each start.

### Environment variables (`.env.prod` in the `stllr/` directory)

Same variables as development plus:

```bash
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=stllr.settings.prod

DJANGO_ALLOWED_HOSTS=stllr.io,www.stllr.io
DJANGO_CSRF_TRUSTED_ORIGINS=https://stllr.io,https://www.stllr.io

RESEND_API_KEY=
SENTRY_DSN=
```

---

## Key concepts

### Brightness algorithm

Pages are ranked by a **brightness** score inspired by star luminosity:

- `PageStar` records older than 7 days are deleted on a schedule (decay).
- Brightness = `1 / (total_users - star_count)²` — stars add gravitational pull; non-stars add distance.
- Pages are ranked by brightness index, and the home feed uses NumPy weighted random sampling so bright pages appear more frequently without guaranteed ordering ("firmament" mode). Two other sort modes are available: `brightest` (strict rank) and `rising` (rank movement delta).

### Social space per page

Each `Page` has exactly one `forum` (threaded posts, persistent) and one `room` (live chat, ephemeral messages). Both are accessible at the same canonical URL identity. The Chrome extension makes both available as tabs in the extension popup.

### Browser extension

The extension sends page metadata to `/extension/` and renders the returned HTML directly in the popup. For the live chat room, the extension fetches a short-lived WebSocket auth ticket from `/extension/ws-ticket/` (30-second TTL, stored in Redis) since cross-origin sessions can't be shared with the main site via cookies.

Three Chrome extension IDs are registered in CORS, CSRF trusted origins, and the WebSocket `OriginValidator`:
- `polpgpcagljhejdbajfbjgdchdlnfepk`
- `mlilkidmlfonjgccanoodpmbfjflggla`
- `hmpgjgepcimfdojfbffhaedmkndomfml`
