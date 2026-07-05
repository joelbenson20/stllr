import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field
from allauth.socialaccount.forms import SignupForm as SocialSignupFormBase

User = get_user_model()

RESERVED_USERNAMES = {
    # Brand/identity
    'stllr', 'stlr', 'stllrr', 'steller', 'stellar', 'stlllr',
    'stlla', 'stla', 'stllaa', 'stella', 'stllla',
    'admin', 'administrator', 'support', 'help', 'info', 'contact',
    'team', 'staff', 'official',
    # Authority roles
    'moderator', 'mod', 'owner', 'founder', 'ceo',
    'bot', 'system', 'root', 'superuser',
    # Trust/legal surface
    'security', 'privacy', 'legal', 'trust', 'safety',
    'announcement', 'announcements', 'news',
    'api', 'dev', 'developer',
    # Routing/display hazards
    'me', 'null', 'undefined', 'anonymous',
    'everyone', 'all', 'here',
}


def validate_handle(value, requesting_user=None):
    if not re.fullmatch(r'[A-Za-z0-9_]+', value):
        raise forms.ValidationError("Handle may only contain letters, numbers, and underscores.")

    if value.lower() in RESERVED_USERNAMES and not (requesting_user and requesting_user.is_staff):
        raise forms.ValidationError("This handle is reserved for staff.")

    if User.objects.filter(username__iexact=value).exists():
        raise forms.ValidationError("This handle is already taken by a user.")

    from crews.models import Crew
    if Crew.objects.filter(handle__iexact=value).exists():
        raise forms.ValidationError("This handle is already taken by a crew.")

class SocialSignupForm(SocialSignupFormBase):
    username = forms.CharField(
        max_length=30,
        help_text="Only letters, numbers, and underscores allowed.",
    )
    background = forms.ImageField(required=False, label="Profile background (optional)")

    def clean_username(self):
        username = self.cleaned_data['username']
        validate_handle(username)
        return username

    def custom_signup(self, request, user):
        user.username = self.cleaned_data['username']
        user.save(update_fields=['username'])
        background = self.cleaned_data.get('background')
        if background:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.background = background
            profile.save()


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(help_text="Only letters, numbers, and underscores allowed.")
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
        validate_handle(username)
        return username

    def clean_email(self):
        User = get_user_model()
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return data

class UserEditForm(forms.ModelForm):
    username = forms.CharField(help_text="Only letters, numbers, and underscores allowed.")

    class Meta:
        model = get_user_model()
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_username(self):
        username = self.cleaned_data['username']
        if username.lower() != self.instance.username.lower():
            validate_handle(username, requesting_user=self.instance)
        return username

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'background']

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