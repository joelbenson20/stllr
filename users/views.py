from django.shortcuts import get_object_or_404, render
from users.models import User

# Create your views here.
def user(request, username):

    user = get_object_or_404(User, username=username)

    context = {
        'user': user,
    }
    return render(request, 'user.html', context)