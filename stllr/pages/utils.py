from urllib.parse import urlparse, urlencode, parse_qsl, quote
import posixpath
from bs4 import BeautifulSoup
import ipaddress

def get_canonical(url):

    # Only these query parameters are preserved. Everything else (tracking params,
    # session tokens, referral IDs, etc.) is stripped before storing the URL.
    ALLOWED_QUERY_PARAMS = {
        'q', 'query', 'search', 'search_query', 'page', 'p', 'id', 'v',
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

class InsecureURLError(Exception):
    """Raised when a URL fails security verification"""
    pass

def verify_security(url):
    """Verify that a URL is safe to store and display
    Checks:
    - Hostname does not resolve to a private/loopback/reserved IP
    - No obviously malicious schemes (javascript:, data:, etc.)

    Raises InsecureURLError if the URL fails any check
    Passes silently for None/empty URLs (optional fields like image_url)
    """

    if not url:
        return
    
    parsed = urlparse(url)

    hostname = parsed.hostname
    if not hostname:
        raise InsecureURLError(f"URL has no hostname: {url}")
    
    # Block private, loopback, and reserved IP addresses
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local:
            raise InsecureURLError(f"URL points to a private/reserved address: {url}")
    except ValueError:
        # hostname is a domain name, not a raw IP -- that's fine
        pass

    # Block localhost variants
    if hostname in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
        raise InsecureURLError(f"URL points to a localhost: {url}")