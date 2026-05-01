# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Edit Attribution Rule

Every code change made by Claude or Claude Code must include a comment marking it for human review. Add a comment near the change in the appropriate language syntax:

- **Python**: `# Done by Claude, requires review`
- **JavaScript**: `// Done by Claude, requires review`
- **HTML/Templates**: `<!-- Done by Claude, requires review -->`
- **CSS**: `/* Done by Claude, requires review */`

Place the comment on the line directly above or inline with the changed code. For multi-line changes, a single comment at the top of the changed block is sufficient.

## Project Overview

Float (branded as "stellr") is a Django web application that serves as a universal forum/discussion platform for any webpage. Users submit ("float") URLs, which are stored with Open Graph metadata, creating discussion threads with threaded comments and voting.

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
python manage.py test forum              # single app
python manage.py test forum.tests.TestClassName.test_method  # single test

# Collect static files (production)
python manage.py collectstatic

# Create admin user
python manage.py createsuperuser         # admin at /admin/
```

## Architecture

### Django Apps

- **forum** — Core app. The `Page` model stores webpage metadata (canonical URL, title, description, OG image). Views: index (top pages feed), page_forum (detail + comments), page_float (create page + vote). `utils.py` contains URL canonicalization, OpenGraph metadata fetching, and security verification.
- **users** — Custom `User` model (extends AbstractUser) and `PageVote` model (user-page vote, unique together). Profile view shows user's comments and voted pages.
- **extension** — Chrome extension API endpoints. Returns CSRF tokens, renders extension popup HTML, handles votes. CORS-whitelisted for `chrome-extension://ejnoheplbbmipnokmhagihclpgnkiano`.

### Comments System

Uses `django-comments-xtd` for threaded comments (max 3 levels deep). Custom template tag `sort_xtdcomment_tree` sorts comments by like count. Custom templates live in `forum/templates/django_comments_xtd/`.

### Key Relationships

```
Page → (has many) XtdComment → (posted by) User
User → (has many) PageVote → (references) Page
```

### URL Structure

- `/` — Page feed (index)
- `/page/?page=<canonical_url>` — Page detail/forum
- `/page_float/` — POST to create page + vote
- `/users/<username>/` — User profile
- `/extension/` — Chrome extension endpoints (csrf-token, extension, page_float)
- `/comments/` — django-comments-xtd threaded comment endpoints
- `/admin/` — Django admin

### Database

Configured via environment: if `DATABASE_URL` is set and `USE_ONLINE_STORAGE=True`, uses PostgreSQL (Railway); otherwise falls back to SQLite3 (`db.sqlite3`).

### Static Files & Templates

- Global static assets in `float/static/` (Bootstrap 5, Bootstrap Icons, FontAwesome, brand assets)
- Forum-specific CSS/JS in `forum/static/` — `floatButtons.js` (voting), `commentsAPI.js` (comment forms/replies)
- Base template at `forum/templates/base.html` — shared navbar and layout
- WhiteNoise serves compressed static files in production