from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class AccountAdapter(DefaultAccountAdapter):
    def get_email_verification_redirect_url(self, email_address):
        request = self.request
        if request.user.is_authenticated:
            return reverse('profile', args=[request.user.username])
        return super().get_email_verification_redirect_url(email_address)
