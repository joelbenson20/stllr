# Features

- Handle both http and https pages: Create 'schema' field in pages model. When a user request from https, update page to default to https schema. Otherwise, if user instantiates page with http, use as schema until another user requests from https, proving that the page supports TLS/SSL.

- Webpage description/tags generator: Generate a description and tags from captured 'inner text' from the page. Update the 'inner text' field if a user w/ a subscription to the page sends over more data (more 'inner text' by virtue of being past the paywall)

- Commment thread expand/collapse button: Clean up the look of threads and make the collapse and expand functionality more intuitive. Long term, make comments collapsed or expanded by default based on how many stars its child elements have.

- User profiles and edit pages: Polish the look of a user's profile page and profile edit page. Create a new Django app to track user actions and display a feed of that user's activity.

- SMTP and email verification: Setup the admin@stllr.io email and force new users to verify their emails.

- Markdown editor: Add features to the comment editing form that allows users to perhaps view a markdown cheatsheet, upload images, select gifs (GIPHY integration?), and mention other users (=> send notifications to users?).

- User input sanitization: Ensure that comments and images submitted by users are safe, i.e. not scripts that will run in the database or when served to other users. "Bleach" django library?

# Open questions


# Bugs
