from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field

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
    
    def clean_email(self):
        User = get_user_model()
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        image_html = ""
        if self.instance and self.instance.photo:
            image_html = f'<img src="{self.instance.photo.url}" class="mb-3" style="max-height: 96px;">'

        self.helper.layout = Layout(
            Field('photo'),
            HTML(image_html),
            'bio',
        )