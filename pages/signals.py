from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
import requests
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files.base import ContentFile
from .models import Page

User = get_user_model()

@receiver(post_save, sender=Page)
def download_images(sender, instance, created, **kwargs):
    if instance.image_url and not instance.image:
        response = requests.get(instance.image_url)
        name = slugify(instance.title) + str(instance.id)
        extension = instance.image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        try:
            instance.image.save(
                image_name,
                ContentFile(response.content)
            )
        except:
            pass
    domain = instance.domain
    if domain.fav_icon_url and not domain.fav_icon:
        response = requests.get(domain.fav_icon_url)
        name = slugify(domain.name) + str(domain.id)
        extension = domain.fav_icon_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        try:
            domain.fav_icon.save(
                image_name,
                ContentFile(response.content)
            )
        except:
            pass
    return

@receiver(m2m_changed, sender=Page.users_star.through)
def users_star_changed(sender, instance, **kwargs):
    instance.total_stars = instance.users_star.count()
    # Distance is defined as the number of users that have not yet starred the page
    d = User.objects.count() - instance.total_stars
    # If all users have liked, return the highest big integer to avoid dividing by 0
    if (d == 0):
        instance.brightness = 1.0000000001
    # Otherwise, return the inverse squared value
    else:
        instance.brightness = 1 / (d ** 2)
    instance.save()
    return