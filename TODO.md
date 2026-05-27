# Features

- Handle both http and https pages: Create 'schema' field in pages model. When a user request from https, update page to default to https schema. Otherwise, if user instantiates page with http, use as schema until another user requests from https, proving that the page supports TLS/SSL.

- Webpage description/tags generator: Generate a description and tags from captured 'inner text' from the page. Update the 'inner text' field if a user w/ a subscription to the page sends over more data (more 'inner text' by virtue of being past the paywall)

- Commment thread expand/collapse button: Clean up the look of threads and make the collapse and expand functionality more intuitive. Long term, make comments collapsed or expanded by default based on how many stars its child elements have.

- User profiles and edit pages: Polish the look of a user's profile page and profile edit page. Create a new Django app to track user actions and display a feed of that user's activity.

- SMTP and email verification: Setup the admin@stllr.io email and force new users to verify their emails.

- Markdown editor: Add features to the comment editing form that allows users to perhaps view a markdown cheatsheet, upload images, select gifs (GIPHY integration?), and mention other users (=> send notifications to users?).

- User input sanitization: Ensure that comments and images submitted by users are safe, i.e. not scripts that will run in the database or when served to other users. "Bleach" django library?

- Messages & Notifications: See model plan below.

# Messages & Notifications — Model Plan

## Messages

Use a **Conversation** container (supports 1:1 and group) with a through model for membership. Track unread state with a `last_read_at` timestamp per membership rather than a per-message read receipt M2M.

```
Conversation
  ├── name (CharField, blank — only set for named group chats)
  ├── participants (M2M → User, through ConversationMembership)
  └── last_message_at (DateTimeField, denormalized for inbox sort)

ConversationMembership  [through model]
  ├── user (FK → User)
  ├── conversation (FK → Conversation)
  ├── joined (DateTimeField, auto_now_add)
  └── last_read_at (DateTimeField, null — updated when user opens the thread)
      → unread count = Message.objects.filter(conversation=conv, created__gt=last_read_at).exclude(sender=user)

Message
  ├── conversation (FK → Conversation)
  ├── sender (FK → User)
  ├── content (TextField)
  └── created (DateTimeField, auto_now_add)
  [Meta: ordering = ['created']]
```

`is_group` is a property derived from participant count — no stored boolean needed.

## Notifications

Collapse by **(recipient, verb, target_object)**. One `Notification` row per unique combination; additional actors accumulated in a through M2M. When a new actor triggers the same event, the notification flips back to unread.

```
Notification
  ├── recipient (FK → User)
  ├── verb (TextChoices: MESSAGE_RECEIVED, CONTACT_REQUEST, POST_STARRED, POST_REPLIED)
  ├── target_ct / target_id / target (GenericFK — the object the event is about)
  │     • POST_STARRED / POST_REPLIED → Post
  │     • MESSAGE_RECEIVED → Conversation
  │     • CONTACT_REQUEST → Contact
  ├── actors (M2M → User, through NotificationActor)
  ├── actor_count (PositiveIntegerField, denormalized — for "Alice and 3 others")
  ├── read (BooleanField, default=False — set to False again when actor_count grows)
  ├── created (DateTimeField, auto_now_add — time of first trigger)
  └── updated (DateTimeField, auto_now — bumped on each new actor)
  [Meta: unique_together = (recipient, verb, target_ct, target_id), ordering = ['-updated']]

NotificationActor  [through model]
  ├── notification (FK → Notification)
  ├── actor (FK → User)
  └── created (DateTimeField, auto_now_add)
  [Meta: unique_together = (notification, actor), ordering = ['-created']]
```

**Collapse logic** (signal or service function):
1. `get_or_create` on `(recipient, verb, target_ct, target_id)`
2. `NotificationActor.objects.get_or_create(notification=notif, actor=actor)`
3. Update `actor_count`, set `read=False`, save

Gives display text like *"Alice, Bob, and 4 others starred your post"* from a single row.

## Notes

- Both `Message` and `Notification` are candidates to fan out via **Channels** for real-time delivery — same WebSocket infrastructure used in `rooms`.
- `Notification.actor_count` is denormalized to avoid a COUNT on every render; keep consistent via `post_save`/`post_delete` signals on `NotificationActor`.
- `Action` (in `users`) is an activity log (what I did); `Notification` is an inbox (what happened to me). Related but distinct — don't consolidate.
- `Conversation`, `ConversationMembership`, and `Message` live in `comms/models.py`. `Notification` and `NotificationActor` can live there or in `users`.

# Open questions


# Bugs
