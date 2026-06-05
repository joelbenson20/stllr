# Features

- Webpage description/tags generator: Generate a description and tags from captured 'inner text' from the page. Update the 'inner text' field if a user w/ a subscription to the page sends over more data (more 'inner text' by virtue of being past the paywall)

- Markdown editor: Add features to the comment editing form that allows users to perhaps view a markdown cheatsheet, upload images, select gifs (GIPHY integration?), and mention other users (=> send notifications to users?).

- Direct Messages: See model plan below. Notifications are implemented (`Notification` and `NotificationActor` in `comms/models.py`); still need `Conversation`, `ConversationMembership`, and `Message` models.

- User Reporting: Allow users to report other users for policy violations (impersonation, harassment, spam). Use the `USER_POLICIES` defined in `oversight/policies.py` and add a `UserReport` model to the `oversight` app.

# Direct Messages — Model Plan

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

## Notes

- `Message` is a candidate to fan out via **Channels** for real-time delivery — same WebSocket infrastructure used in `rooms`.
- `Action` (in `users`) is an activity log (what I did); `Notification` is an inbox (what happened to me). Related but distinct — don't consolidate.
- `Conversation`, `ConversationMembership`, and `Message` live in `comms/models.py`.

# Open questions


# Bugs
