from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response


def login(request):
    if request.user.is_authenticated():
        return redirect('/done')
    return render_to_response('login.html')


@login_required
def done(request):
    return render_to_response('logout.html')


@login_required
def logout(request):
    auth_logout(request)
    return redirect('/login')
