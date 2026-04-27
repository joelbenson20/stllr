from django import forms
from .models import Comment
from pages.models import Page

class CommentForm(forms.ModelForm):
    page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
    )
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,
    )

    class Meta:
        model = Comment
        fields = ['content', 'page', 'parent']