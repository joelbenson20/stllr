# Done by Claude, requires review
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_redirect_url(self, request):
        if request.user.is_authenticated:
            return reverse('profile', args=[request.user.username])
        return super().get_email_confirmation_redirect_url(request)
