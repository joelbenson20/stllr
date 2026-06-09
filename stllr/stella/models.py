from django.db import models
from pages.models import Page

class Prompt(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETE = 'complete', 'Complete'
        FAILED = 'failed', 'Failed'

    page = models.ForeignKey(Page, related_name='prompts', on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    model = models.CharField(max_length=64, default="claude-sonnet-4-6")
    prompt = models.TextField()
    output = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("page", "prompt")]
