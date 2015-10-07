from django.shortcuts import render, redirect


def landing(request):
    if request.user.is_authenticated():
        return redirect('users:home')
    return render(request, 'core/landing.html')
