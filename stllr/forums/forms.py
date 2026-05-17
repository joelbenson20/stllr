from django import forms
from .models import Post
from pages.models import Page

class PostForm(forms.ModelForm):
    page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
    )
    parent = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        required=False,
    )

    class Meta:
        model = Post
        fields = ['content', 'page', 'parent']