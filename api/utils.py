
from urllib.parse import urlparse, urlencode, parse_qsl, ParseResult
import posixpath

# Only these query parameters are preserved. Everything else (tracking params,
# session tokens, referral IDs, etc.) is stripped before storing the URL.
ALLOWED_QUERY_PARAMS = {
    'q', 'query', 'search', 'page', 'p', 'id', 'v',
}

def get_canonical(url):

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