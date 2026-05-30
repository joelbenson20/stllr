from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from forums.templatetags.utility_tags import safe_markdown_filter
from django.template.loader import render_to_string
from pages.models import Page, PageStar, PagePin  # Done by Claude, requires review
from forums.models import Post, PostStar
from forums.forms import PostForm
from rooms.consumers import _get_users
from users.models import Action, Mute, ContactRelation
from comms.notifications import notify
from comms.models import Notification

User = get_user_model()

@login_required
@require_POST
def markdownify(request):
    content = request.POST.get('content', '')
    response = {
        'status': '200',
        'markdown': safe_markdown_filter(content),
    }
    return JsonResponse(response)

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def star_page(request):
    page_id = request.POST.get('id')
    action = request.POST.get('action')
    if page_id and action:
        try:
            page = Page.objects.get(id=page_id)
            if action == 'star':
                PageStar.objects.get_or_create(page=page, user=request.user)
                Action.objects.create(
                    actor=request.user, verb=Action.Verb.STARRED, object=page  # Done by Claude, requires review
                )
            else:
                PageStar.objects.filter(page=page, user=request.user).first().delete()
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
@require_POST
def pin_page(request):  # Done by Claude, requires review
    page_id = request.POST.get('id')
    action = request.POST.get('action')
    if page_id and action:
        try:
            page = Page.objects.get(id=page_id)
            if action == 'pin':
                PagePin.objects.get_or_create(page=page, user=request.user)
            else:
                PagePin.objects.filter(page=page, user=request.user).first().delete()
            return JsonResponse({'status': '200'})
        except Page.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def create_post(request):
    new_post = None
    form = PostForm(data=request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        new_post = form.save(commit=False)
        new_post.author = request.user
        if (new_post.parent):
            new_post.thread_level = new_post.parent.thread_level + 1
        new_post.save()
        if (new_post.parent):
            Action.objects.create(
                actor=request.user, verb=Action.Verb.REPLIED, object=new_post  # Done by Claude, requires review
            )
        else:
            Action.objects.create(
                actor=request.user, verb=Action.Verb.POSTED, object=new_post  # Done by Claude, requires review
            )
        response = {
            'status': '201',
            'postId': new_post.id,
            'post': render_to_string('post/tree.html', {'posts': [new_post]}, request=request)
        }
        return (JsonResponse(response))
    return JsonResponse({'status': '400'})

@login_required
@require_POST
@ratelimit(key='user', rate='3/s', method='POST', block=True)
def star_post(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'star':
                PostStar.objects.get_or_create(post=post, user=request.user)
            else:
                PostStar.objects.filter(post=post, user=request.user).first().delete()
            return JsonResponse({'status': '200'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def mute_user(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            target = User.objects.get(id=user_id)
            if target == request.user:
                return JsonResponse({'status': '400'})
            if action == 'mute':
                Mute.objects.get_or_create(muter=request.user, muted=target)
            else:
                Mute.objects.filter(muter=request.user, muted=target).delete()
            return JsonResponse({'status': '200'})
        except User.DoesNotExist:
            pass
    return JsonResponse({'status': '500'})

# Done by Claude, requires review
@login_required
def search_users(request):
    q = request.GET.get('q', '').strip()
    users = []
    if q:
        users = list(
            User.objects.filter(
                username__icontains=q
            ).exclude(id=request.user.id).select_related('profile')[:10]
        )
    html = render_to_string('user/search_results.html', {'users': users}, request=request)
    return JsonResponse({'html': html})


@login_required
@require_POST
def send_contact_request(request):
    import json
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    if not username:
        return JsonResponse({'error': 'Username required'}, status=400)

    to_user = get_object_or_404(User, username=username)
    if to_user == request.user:
        return JsonResponse({'error': 'Cannot add yourself'}, status=400)

    existing = ContactRelation.objects.filter(
        from_user=request.user, to_user=to_user
    ).first() or ContactRelation.objects.filter(
        from_user=to_user, to_user=request.user
    ).first()

    if existing:
        return JsonResponse({'error': 'ContactRelation relationship already exists'}, status=400)

    ContactRelation.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'status': 'ok'})


def get_room_count(request):
    ids = [i.strip() for i in request.GET.get('ids', '').split(',') if i.strip()]
    counts = {page_id: len(_get_users(f'room_{page_id}')) for page_id in ids}
    return JsonResponse(counts)

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def share_object(request):
    object_type = request.POST.get('object_type')
    object_id = request.POST.get('object_id')
    contact_id = request.POST.get('contact_id')

    if not (object_type and object_id and contact_id):
        return JsonResponse({'status': '404'}, status=404)
    
    try:
        recipient = User.objects.get(id=contact_id)
    except User.DoesNotExist:
        return JsonResponse({'status': '400'}, status=400)
    
    if recipient not in request.user.get_contacts():
        return JsonResponse({'status': '403'}, status=403)
    
    if object_type == 'page':
        try:
            obj = Page.objects.get(id=object_id)
            event = Notification.Event.PAGE_SHARED
        except Page.DoesNotExist:
            return JsonResponse({'status': '404'}, status=404)
    elif object_type == 'post':
        try:
            obj = Post.objects.get(id=object_id)
            event = Notification.Event.POST_SHARED
        except Post.DoesNotExist:
            return JsonResponse({'status': '404'}, status=404)
    else:
        return JsonResponse({'status': '400'}, status=400)
    
    notify(recipient=recipient, event=event, object=obj, actor=request.user)
    return JsonResponse({'status': '200'})