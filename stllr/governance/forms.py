from django import forms
from .models import PageReport, PostReport


class PageReportForm(forms.ModelForm):
    class Meta:
        model = PageReport
        fields = ["policy", "justification"]
        widgets = {
            "policy": forms.Select(attrs={"class": "form-select rounded-card border-0"}),
            "justification": forms.Textarea(attrs={
                "class": "form-control rounded-card border-0 shadow-none p-3",
                "placeholder": "Detailed justification of removal by virtue of this policy (optional)",
                "rows": 4,
            }),
        }

class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ["policy", "justification"]
        widgets = {
            "policy": forms.Select(attrs={"class": "form-select rounded-card border-0"}),
            "justification": forms.Textarea(attrs={
                "class": "form-control rounded-card border-0 shadow-none p-3",
                "placeholder": "Detailed justification of removal by virtue of this policy (optional)",
                "rows": 4,
            }),
        }
