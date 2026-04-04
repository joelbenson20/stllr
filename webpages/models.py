from django.db import models

# Create your models here.
class Webpage(models.Model):

    canonical = models.URLField(max_length=250, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=400, null=True, blank=True)
    image_url = models.URLField(max_length=250, null=True, blank=True)
    site_name = models.CharField(max_length=100, null=True, blank=True)
    fav_icon_url = models.URLField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.canonical
    
    @property
    def domain(self):
        return self.canonical.split('/')[0]
    
    @property
    def num_votes(self):
        return self.votes.count()