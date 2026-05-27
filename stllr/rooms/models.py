from django.conf import settings
from django.db import models


# Done by Claude, requires review
class Broadcast(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='broadcasts'
    )
    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
        related_name='broadcasts'
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} on {self.page} at {self.created}'

