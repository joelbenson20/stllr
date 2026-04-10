import os
from urllib.parse import urlparse, urlencode, parse_qsl, quote
import posixpath
import requests


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

    # Normalize the path: resolve any '..' or '.' segments and strip trailing slash
    path = posixpath.normpath(parsed.path) if parsed.path else ''
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

def verify_security(url):
    pass

# Using OpenGraph.io
def getOGMetaData(url):

    encoded_url = quote(url, safe='')
    
    endpoint = f"https://opengraph.io/api/3.0/site/{encoded_url}?app_id={os.getenv('OPEN_GRAPH_API_KEY')}"

    response = requests.get(endpoint).json()
    hybrid = response.get('hybridGraph') or {}

    print(hybrid)
    
    og_canonical = get_canonical(hybrid.get('url') or url)
    og_title = hybrid.get('title')
    og_description = hybrid.get('description')
    og_image_url = hybrid.get('image') or hybrid.get('summary_image') \
        or hybrid.get('summary_large_image') \
        or hybrid.get('imageSecureUrl') 
    og_site_name = hybrid.get('site_name')
    og_fav_icon_url = hybrid.get('favicon')
    
    return {
        'canonical': og_canonical,
        'title': og_title,
        'description': og_description,
        'image_url': og_image_url,
        'site_name': og_site_name,
        'fav_icon_url': og_fav_icon_url
    }