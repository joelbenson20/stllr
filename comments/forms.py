from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        required=False,
        empty_label=None
    )

    class Meta:
        model = Comment
        fields = ['content', 'parent']