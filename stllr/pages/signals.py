from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests
from requests.exceptions import MissingSchema
from django.core.files.base import ContentFile
from .models import Page
from django.contrib.postgres.search import SearchVector

@receiver(post_save, sender=Page)
def download_images(sender, instance, created, update_fields, **kwargs):
    if update_fields is None or 'image_url' in update_fields:
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
                try:
                    response = requests.get('https://' + domain.name + domain.fav_icon_url)
                    domain.fav_icon.save(
                        image_name,
                        ContentFile(response.content)
                    )
                except:
                    pass

@receiver(post_save, sender=Page)
def update_search_vector(sender, instance, created, update_fields, **kwargs):
    if update_fields is None or any(f in update_fields for f in ('title', 'description', 'content')):
        Page.objects.filter(pk=instance.pk).update(
            search_vector=(
                SearchVector('title', weight='A') +
                SearchVector('description', weight='B') +
                SearchVector('content', weight='C')
            )
        )

