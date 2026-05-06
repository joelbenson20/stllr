from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import requests
from requests.exceptions import MissingSchema
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from .models import Page
from django.contrib.postgres.search import SearchVector

User = get_user_model()

@receiver(post_save, sender=Page)
def download_images(sender, instance, created, **kwargs):
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
def update_search_vector(sender, instance, **kwargs):
    Page.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector('title', weight='A') +
            SearchVector('description', weight='B') +
            SearchVector('inner_text', weight='C')
        )
    )

@receiver(m2m_changed, sender=Page.users_star.through)
def users_star_changed(sender, instance, **kwargs):
    total_stars = instance.users_star.count()
    # Distance is defined as the number of users that have not yet starred the page
    d = User.objects.count() - total_stars
    # If all users have liked, return the highest big integer to avoid dividing by 0
    if (d == 0):
        brightness = 1.0000000001
    # Otherwise, return the inverse squared value
    else:
        brightness = 1 / (d ** 2)
    # Done by Claude, requires review
    # Use update() instead of save() to avoid re-triggering post_save → download_images
    Page.objects.filter(pk=instance.pk).update(total_stars=total_stars, brightness=brightness)
    return

