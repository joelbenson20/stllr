from django import forms
from crispy_forms.helper import FormHelper
from users.forms import validate_handle
from .models import Crew


class CrewForm(forms.ModelForm):
    class Meta:
        model = Crew
        fields = ['handle', 'name', 'bio', 'background', 'is_open']

    def __init__(self, *args, requesting_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.requesting_user = requesting_user
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_handle(self):
        handle = self.cleaned_data['handle']
        if not self.instance.pk or handle.lower() != self.instance.handle.lower():
            validate_handle(handle, requesting_user=self.requesting_user)
        return handle
