from django.db import models

# Create your models here.
class Webpage(models.Model):
    url = models.URLField(max_length=250, unique=True)

    def __str__(self):
        return self.url
    
    @property
    def votes_sum(self):
        return self.webpage_votes.aggregate(total=models.Sum("value"))["total"] or 0