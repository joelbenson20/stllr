from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from webpages.models import Webpage

class User(AbstractUser):
    
    def get_absolute_url(self):
        return reverse('user', kwargs={'username': self.username})
    
    @property
    def voted_webpage_ids(self):
        return set(self.webpage_votes.values_list('webpage_id', flat=True))
    
class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    webpage = models.ForeignKey('webpages.Webpage', related_name='webpage_comments', on_delete=models.CASCADE)
    content = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.datetime} Comment by {self.user.username}: {self.content[:20]}..."
    
    class Meta:
        ordering = ['-datetime']

class Vote(models.Model):

    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
    
class WebpageVote(Vote):

    user = models.ForeignKey(User, related_name='webpage_votes', on_delete=models.CASCADE)
    webpage = models.ForeignKey(Webpage, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} : {self.webpage}"
    
    class Meta:
        unique_together = ('user', 'webpage')

class CommentVote(Vote):
    
    user = models.ForeignKey(User, related_name='comment_votes', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} : {self.comment}"
    
    class Meta:
        unique_together = ('user', 'comment')