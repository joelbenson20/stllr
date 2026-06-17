from django.conf import settings
from django.db import models


class Beacon(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beacons'
    )
    crew = models.ForeignKey('crews.Crew', on_delete=models.CASCADE, related_name='beacons')
    page = models.ForeignKey('pages.Page', on_delete=models.CASCADE, related_name='beacons')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'crew', 'page'], name='unique_beacon'),
        ]
        indexes = [
            models.Index(fields=['crew', '-created'], name='beacon_crew_created_idx'),
        ]

    def __str__(self):
        return f'{self.user.username} → @{self.crew.handle}: {self.page}'
