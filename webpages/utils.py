import os
from urllib.parse import quote
import requests
from extension.utils import get_canonical

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