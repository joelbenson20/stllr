from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class Crew(models.Model):
    handle = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    bio = models.CharField(max_length=300, blank=True)
    background = models.ImageField(upload_to='crews/%Y/%m/%d/', blank=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='crews_created'
    )
    is_open = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.creator:
            Membership.objects.create(
                crew=self,
                user=self.creator,
                role=Membership.Role.OWNER,
                status=Membership.Status.ACCEPTED,
            )

    @property
    def member_count(self):
        return self.memberships.filter(status=Membership.Status.ACCEPTED).count()

    @property
    def admin_pks(self):
        return self.memberships.filter(
            role__in=[Membership.Role.OWNER, Membership.Role.ADMIN],
            status=Membership.Status.ACCEPTED,
        ).values_list('user', flat=True)

    def get_absolute_url(self):
        return reverse('crews:crew_detail', kwargs={'handle': self.handle})

    def __str__(self):
        return f'@{self.handle}'


class Membership(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        INVITED = 'invited', 'Invited'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        BANNED = 'banned', 'Banned'

    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'

    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crew_memberships'
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    
    created = models.DateTimeField(auto_now_add=True)
    joined = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['crew', 'user'], name='unique_membership'),
        ]

    def save(self, *args, **kwargs):
        if self.status == self.Status.ACCEPTED and self.joined is None:
            self.joined = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} in @{self.crew.handle} ({self.role})'

