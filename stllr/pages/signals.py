from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests
from requests.exceptions import MissingSchema
from django.core.files.base import ContentFile
from .models import Page, Domain
from django.contrib.postgres.search import SearchVector

@receiver(post_save, sender=Page)
def download_image(sender, instance, created, update_fields, **kwargs):
    if created or update_fields and 'image_url' in update_fields:
        if instance.image_url:
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

@receiver(post_save, sender=Domain)
def download_favicon(sender, instance, created, update_fields, **kwargs):
    if created or update_fields and 'fav_icon_url' in update_fields:
        if instance.fav_icon_url:
            name = str(instance.id)
            extension = instance.fav_icon_url.rsplit('.', 1)[1].lower()
            image_name = f'{name}.{extension}'
            try:
                response = requests.get(instance.fav_icon_url)
                instance.fav_icon.save(
                    image_name,
                    ContentFile(response.content)
                )
            except MissingSchema:
                try:
                    response = requests.get('https://' + instance.name + instance.fav_icon_url)
                    instance.fav_icon.save(
                        image_name,
                        ContentFile(response.content)
                    )
                except:
                    pass

@receiver(post_save, sender=Page)
def update_search_vector(sender, instance, created, update_fields, **kwargs):
    if created or update_fields and any(f in update_fields for f in ('title', 'description', 'content')):
        Page.objects.filter(pk=instance.pk).update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('description', weight='B') +
                SearchVector('content', weight='C')
            )
        )

