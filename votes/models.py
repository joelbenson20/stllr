from django.db import models
from users.models import User
from comments.models import Comment

# Create your models here.
class Vote(models.Model):

    user = models.ForeignKey(User, related_name='%(class)ss', on_delete=models.CASCADE)
    value = models.IntegerField(
        choices=[(1, 'Upvote'), (-1, 'Downvote')]
    )
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-datetime']

    
class WebpageVote(Vote):

    webpage = models.ForeignKey('webpages.Webpage', related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} Webpage: {self.webpage}, Vote: {self.value}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'webpage'],
                name='unique_user_webpage_vote'
            )
        ]

class CommentVote(Vote):
    
    comment = models.ForeignKey(Comment, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} Comment: {self.comment}, Vote: {self.value}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_user_comment_vote'
            )
        ]