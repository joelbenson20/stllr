from django.db import models
from users.models import User

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='user_comments', on_delete=models.CASCADE)
    webpage = models.ForeignKey('webpages.Webpage', related_name='webpage_comments', on_delete=models.CASCADE)
    content = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.datetime} Comment by {self.user.username}: {self.content[:20]}..."
    
    class Meta:
        ordering = ['-datetime']
