from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import requests
from requests.exceptions import MissingSchema
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from .models import Page
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from django.contrib.postgres.search import SearchVector

User = get_user_model()

@receiver(post_save, sender=Page)
def download_images(sender, instance, created, update_fields, **kwargs):
    if instance.image_url and not instance.image:
        name = str(instance.id)
        extension = instance.image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        try:
            response = requests.get(instance.image_url)
            instance.image.save(
                image_name,
                ContentFile(response.content)
            )
        except MissingSchema:
            try:
                response = requests.get('https://' + instance.domain.name + instance.image_url)
                instance.image.save(
                image_name,
                ContentFile(response.content)
            )
            except:
                pass
            
    domain = instance.domain
    if domain.fav_icon_url and not domain.fav_icon:
        name = str(domain.id)
        extension = domain.fav_icon_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        try:
            response = requests.get(domain.fav_icon_url)
            domain.fav_icon.save(
                image_name,
                ContentFile(response.content)
            )
        except MissingSchema:
            # If schema is missing, try prepending the site url
            try:
                response = requests.get('https://' + domain.name + domain.fav_icon_url)
                domain.fav_icon.save(
                    image_name,
                    ContentFile(response.content)
                )
            except:
                pass
    return

@receiver(post_save, sender=Page)
def update_search_vector(sender, instance, created, update_fields, **kwargs):
    Page.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector('title', weight='A') +
            SearchVector('description', weight='B') +
            SearchVector('content', weight='C')
        )
    )
    return

@receiver(post_save, sender=Page)
def update_tags(sender, instance, created, update_fields, **kwargs):
    stop_words = set(stopwords.words('english'))
    raw = (instance.title or '') + ' ' + (instance.description or '') + ' ' + (instance.content or '')
    tokens = word_tokenize(raw)
    tagged = pos_tag(tokens)
    words = [word for word, pos in tagged if pos in ('NN', 'NNP') and word.isalpha() and word.lower() not in stop_words]
    keywords = [word.upper() for word, count in Counter(words).most_common(10)]
    instance.tags.set(keywords)
    return

@receiver(m2m_changed, sender=Page.users_star.through)
def update_brightness_on_star_change(sender, instance, action, **kwargs):
    if action not in ('post_add', 'post_remove', 'post_clear'):
        return
    User = get_user_model()
    page = instance
    total_stars = page.users_star.count()
    d = User.objects.count() - total_stars
    brightness = 1e15 if d == 0 else 1 / (d ** 2)
    Page.objects.filter(pk=page.pk).update(total_stars=total_stars, brightness=brightness)

