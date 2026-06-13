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

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if not content.strip():
            raise forms.ValidationError('Post content cannot be empty.')
        return content

    class Meta:
        model = Post
        fields = ['content', 'page', 'parent']