import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field

def validate_username(username, instance=None):
    if not re.fullmatch(r'[A-Za-z0-9_]+', username):
        raise forms.ValidationError("Username may only contain letters, numbers, and underscores.")
    User = get_user_model()
    qs = User.objects.filter(username__iexact=username)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise forms.ValidationError("This username is already taken.")

class UserRegistrationForm(forms.ModelForm):
    password1=forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError("Passwords do not match.")
        return cd['password2']
    
    def clean_username(self):
        username = self.cleaned_data['username']
        validate_username(username)
        return username

    def clean_email(self):
        User = get_user_model()
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return data

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username']

    # Done by Claude, requires review
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_username(self):
        username = self.cleaned_data['username']
        validate_username(username, self.instance)
        return username

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['background']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        image_html = ""
        if self.instance and self.instance.background:
            image_html = f'<img class="mb-3" style="max-height: 96px;" src="{self.instance.background.url}">'

        self.helper.layout = Layout(
            Field('background'),
            HTML(image_html),
        )