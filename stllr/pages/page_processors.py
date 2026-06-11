import requests
from urllib.parse import urlparse, parse_qs

YOUTUBE_OEMBED_URL = 'https://www.youtube.com/oembed'


def youtube_processor(url, data):

    parsed = urlparse(url)

    if parsed.hostname == 'youtu.be':
        video_id = parsed.path.lstrip('/')
    else:
        video_id = parse_qs(parsed.query).get('v', [None])[0]

    data = dict(data)

    if video_id:
        try:
            response = requests.get(
                YOUTUBE_OEMBED_URL,
                params={'url': f'https://www.youtube.com/watch?v={video_id}', 'format': 'json'},
                timeout=5
            )
            if response.ok:
                oembed = response.json()
                data['title'] = oembed.get('title') or data.get('title')
                data['imageUrl'] = oembed.get('thumbnail_url') or f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
                author_name = oembed.get('author_name')
                if author_name:
                    data['description'] = f'A video by {author_name}'
        except requests.RequestException:
            data['imageUrl'] = f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'

    return data