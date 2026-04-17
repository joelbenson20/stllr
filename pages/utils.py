import os
from urllib.parse import urlparse, urlencode, parse_qsl, quote
import posixpath
from firecrawl import Firecrawl
from django.conf import settings
from bs4 import BeautifulSoup

def get_canonical(url):

    # Only these query parameters are preserved. Everything else (tracking params,
    # session tokens, referral IDs, etc.) is stripped before storing the URL.
    ALLOWED_QUERY_PARAMS = {
        'q', 'query', 'search', 'page', 'p', 'id', 'v',
    }

    parsed = urlparse(url)
    scheme = (parsed.scheme or '').lower()

    # Lowercase and strip leading 'www.' from the host
    host = parsed.hostname or ''
    if host.startswith('www.'):
        host = host[4:]

    # Keep non-default ports because they can point to a different app/site.
    # Drop default ports to avoid duplicates like :80 and :443.
    if parsed.port is not None:
        default_ports = {'http': 80, 'https': 443}
        if default_ports.get(scheme) != parsed.port:
            host = f'{host}:{parsed.port}'

    # Normalize the path: resolve any '..' or '.' segments.
    # Preserve a meaningful trailing slash so '/forum/?q=..' stays distinct from '/forum?q=..'.
    raw_path = parsed.path or ''
    path = posixpath.normpath(raw_path) if raw_path else ''
    if raw_path.endswith('/') and path not in ('', '/'):
        path += '/'
    if path == '/':
        path = ''

    # Allowlist query params to remove tracking/session/cookie values
    filtered_params = [
        (k, v) for k, v in parse_qsl(parsed.query)
        if k.lower() in ALLOWED_QUERY_PARAMS
    ]
    query = urlencode(filtered_params) if filtered_params else ''

    # Reconstruct without scheme, userinfo, or fragment
    normalized = host + path
    if query:
        normalized += '?' + query

    return normalized

def get_domain_name(url):
    parsed = urlparse(url)
    scheme = (parsed.scheme or '').lower()
    # Lowercase and strip leading 'www.' from the host
    host = parsed.hostname or ''
    if host.startswith('www.'):
        host = host[4:]
    return host

def verify_security(url):
    pass

def get_meta(url, head):
    try:
        soup = BeautifulSoup(head, 'html.parser')
    except Exception as e:
        print(f"BeautifulSoup parsing error: {e}")
        return None
    
    def get_meta_tag(name, attr='property'):
        """Get content from meta tag by name or property."""
        tag = soup.find('meta', {attr: name})
        return tag.get('content', '').strip() if tag else ''
    
    def get_text(selector, default=''):
        """Get text from first matching selector."""
        elem = soup.select_one(selector)
        return elem.get_text(strip=True) if elem else default
    
    # Extract title - try og:title first, then <title>, then <h1>
    title = (
        get_meta_tag('og:title') or
        get_text('title') or
        get_text('h1') or
        'Untitled'
    )
    
    # Extract description - try og:description, then meta description
    description = (
        get_meta_tag('og:description') or
        get_meta_tag('description', attr='name') or
        ''
    )
    
    # Extract image - try og:image first, then find first img tag
    image_url = get_meta_tag('og:image')
    if not image_url:
        img_tag = soup.find('img')
        image_url = img_tag.get('src', '') if img_tag else ''
    
    # Extract site name
    site_name = (
        get_meta_tag('og:site_name') or
        get_text('meta[property="og:site_name"]') or
        ''
    )
    
    # Extract favicon - look for link rel="icon" or rel="shortcut icon"
    fav_icon_url = ''
    favicon_link = soup.find('link', rel=['icon', 'shortcut icon'])
    if favicon_link:
        fav_icon_url = favicon_link.get('href', '')
    
    # Extract keywords/tags
    tags = (
        get_meta_tag('keywords', attr='name') or
        get_meta_tag('article:tag') or
        ''
    )
    
    # Extract content type
    content_type = (
        get_meta_tag('og:type') or
        get_meta_tag('content-type', attr='http-equiv') or
        ''
    )
    
    # Extract all inner text (document content)
    # Remove script and style elements
    for script in soup(['script', 'style']):
        script.decompose()
    inner_text = soup.get_text(separator=' ', strip=True)
    # Clean up excessive whitespace
    inner_text = ' '.join(inner_text.split())
    
    return {
        'title': title[:200],  # CharField max_length=200
        'type': content_type[:30],  # CharField max_length=30
        'description': description[:400],  # TextField max_length=400
        'image_url': image_url[:250],  # URLField max_length=250
        'site_name': site_name[:100],  # CharField max_length=100
        'fav_icon_url': fav_icon_url[:250],  # URLField max_length=250
        'tags': tags,  # Will be split by comma in views
        'inner_text': inner_text,  # TextField, no limit
    }
