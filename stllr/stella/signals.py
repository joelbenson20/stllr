from django.db.models.signals import post_save
from django.dispatch import receiver
from pages.models import Page
from .models import Prompt
from .prompts import DEFAULT_PROMPTS


@receiver(post_save, sender=Page)
def generate_page_prompts(sender, instance, created, update_fields, **kwargs):
    if not created and (update_fields is None or 'content' not in update_fields):
        return
    if instance.prompts.exists():
        return
    for prompt_config in DEFAULT_PROMPTS:
        Prompt.objects.get_or_create(
            page=instance,
            prompt=prompt_config["prompt"],
            defaults={
                "title": prompt_config["title"],
                "status": Prompt.Status.PENDING,
            },
        )
