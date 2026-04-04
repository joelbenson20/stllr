# Features

- URL security verification

Verify that a URL is secure, maybe by calling some API that tests whether it's indexed by Google?

- Webpage classifier

Python script that takes in a webpage url, calls the url, and classifies the webpage into categories based on the response. (Article, Video, Social Media Post, etc. (Or maybe other features???))

- Webpage description generator
  
When a webpage does not have a <og:description> tag, I leave the description blank. It might be better for us to call the page, and based on the content generate a short AI description.

# Open questions

Do we want to only support HTTPS supported webpages? I think yes.
What kind of statistical algorithm do we want to use to order the webpage feed?

# Bugs

- Converting Unicode to ASCII for JSON
  
Webpages with curly quotes or apostraphes in their titles cause an error with the extension, because those characters are Unicode, not ASCII. Need to convert.
