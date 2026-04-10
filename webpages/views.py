from django.shortcuts import redirect, render
from .models import Webpage
from .utils import getOGMetaData
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from extension.utils import get_canonical, verify_security

@login_required
@require_POST
def post_float(request):

    user = request.user
    url = request.POST.get('url')
    canonical = get_canonical(url)

    try:
        webpage = Webpage.objects.get(canonical=canonical)
        return redirect('webpages:detail', pk=webpage.pk)
    except Webpage.DoesNotExist:
        pass

    try:
        og_metadata = getOGMetaData(url)
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return redirect('index')

    verify_security(og_metadata['image_url'])
    verify_security(og_metadata['fav_icon_url'])

    webpage = Webpage.objects.create(canonical=og_metadata['canonical'],
                                title=og_metadata['title'],
                                description=og_metadata['description'],
                                image_url=og_metadata['image_url'],
                                site_name=og_metadata.get('site_name', ''),
                                fav_icon_url=og_metadata.get('fav_icon_url', '')
                                )
        
    # Add vote for the webpage by the user.
    if (not user.webpage_votes.filter(webpage=webpage).exists()):
        user.webpage_votes.create(webpage=webpage)

    return redirect('webpages:detail', pk=webpage.pk)


def detail(request, pk):

    context = {
        "webpage": Webpage.objects.get(pk=pk)
    }

    return render(request, 'webpages/detail.html', context=context)