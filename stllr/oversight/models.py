from django.db import models
from django.conf import settings
from oversight.policies import PAGE_POLICIES, POST_POLICIES


class Report(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("dismissed", "Dismissed"),
        ("actioned", "Actioned"),
    ]

    justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class PageReport(Report):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_reports")
    page = models.ForeignKey("pages.Page", on_delete=models.CASCADE, related_name="reports")
    policy = models.CharField(max_length=20, choices=PAGE_POLICIES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reporter', 'page'], name='unique_page_report_per_reporter'),
        ]


class PostReport(Report):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports")
    post = models.ForeignKey("forums.Post", on_delete=models.CASCADE, related_name="reports")
    policy = models.CharField(max_length=20, choices=POST_POLICIES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reporter', 'post'], name='unique_post_report_per_reporter'),
        ]
