from django.db import models

# Create your models here.
class Webpage(models.Model):

    canonical = models.URLField(max_length=250, unique=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=400, null=True, blank=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.canonical
    
    @property
    def num_votes(self):
        return self.votes.count()