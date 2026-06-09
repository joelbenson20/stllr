DEFAULT_PROMPTS = [
    {
        "title": "Summary",
        "prompt": (
            "Write a concise one-paragraph summary of this webpage.\n\n"
            "Title: {title}\nURL: {canonical}\nDescription: {description}\nContent: {content}"
        ),
    },
    {
        "title": "Primary Sources",
        "prompt": (
            "List the primary sources referenced or implied by this webpage. "
            "For each, provide a title and URL if available, or a description if not.\n\n"
            "Title: {title}\nURL: {canonical}\nDescription: {description}\nContent: {content}"
        ),
    },
    {
        "title": "User Sentiment",
        "prompt": (
            "Based on the forum posts below, summarize the overall sentiment of users "
            "discussing this page. Note any dominant opinions, points of agreement, "
            "or recurring concerns.\n\n"
            "Page: {canonical}\n\nForum posts:\n{forum_posts}"
        ),
    },
    {
        "title": "User-Added Context",
        "prompt": (
            "Based on the forum posts below, formulate a paragraph of context that users "
            "have collectively added to this page — insights, corrections, background, "
            "or commentary that enriches understanding of the content.\n\n"
            "Page: {canonical}\n\nForum posts:\n{forum_posts}"
        ),
    },
]
