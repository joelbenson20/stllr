from django.db import models
from django.conf import settings


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
    POLICY_CHOICES = [
        ("not_a_page", "Not a real or accessible webpage"),
        ("explicit", "Adult or explicit content"),
        ("spam", "Spam or purely commercial"),
        ("malicious", "Malicious, phishing, or harmful site"),
        ("duplicate", "Duplicate of another page"),
        ("misleading_thumbnail", "Misleading or inaccurate page thumbnail"),
        ("other", "Other"),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="page_reports")
    page = models.ForeignKey("pages.Page", on_delete=models.CASCADE, related_name="reports")
    policy = models.CharField(max_length=20, choices=POLICY_CHOICES)

    class Meta:
        unique_together = ("reporter", "page")


class PostReport(Report):
    POLICY_CHOICES = [
        ("spam", "Spam or self-promotion"),
        ("harassment", "Harassment or hate speech"),
        ("misinformation", "Misinformation or false claims"),
        ("explicit", "Adult or explicit content"),
        ("off_topic", "Off topic or irrelevant"),
        ("other", "Other"),
    ]

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reports")
    post = models.ForeignKey("forums.Post", on_delete=models.CASCADE, related_name="reports")
    policy = models.CharField(max_length=20, choices=POLICY_CHOICES)

    class Meta:
        unique_together = ("reporter", "post")
