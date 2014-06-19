from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext

from models import UserSettings
from forms import UserSettingsForm


def user_is_superuser(user):
    return user.is_superuser


def sign_in(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            if user.is_active:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                else:
                    return redirect('home')
            else:
                messages.error(request, 'This account is inactive.')
                return redirect('landing')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('landing')


@login_required
def sign_out(request):
    logout(request)
    return redirect('landing')


@login_required
def home(request):
    return render(request, 'home.html')


@user_passes_test(user_is_superuser)
def user_management(request):
    users = User.objects.all().order_by('username')
    current_user_id = request.user.id

    context = RequestContext(request, {
        'users': users,
        'current_user_id': current_user_id
    })

    return render(request, 'user_management.html', context)


@user_passes_test(user_is_superuser)
def user_update(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)

        if request.POST.get('is_active'):
            user.is_active = True
        else:
            user.is_staff = False

        if request.POST.get('is_staff'):
            user.is_staff = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if request.POST.get('is_superuser'):
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False

        user.save()

        return redirect('user_management')
    else:
        return redirect('user_management')


@user_passes_test(user_is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        logout(request)
        user.delete()
        return redirect('landing')
    else:
        user.delete()
        return redirect('user_management')


def user_settings(request):
    UserSettings.objects.get_or_create(user=request.user)
    user_settings = request.user.usersettings
    form = UserSettingsForm(initial={
        'bug': user_settings.bug,
        'new_feature': user_settings.new_feature,
        'task': user_settings.task,
        'improvement': user_settings.improvement
    })

    context = RequestContext(request, {
        'form': form
    })
    return render(request, 'user_settings.html', context)


def user_settings_update(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST)
        user = User.objects.get(pk=request.user.pk)

        if form.is_valid():
            user.usersettings.bug = form.cleaned_data['bug']
            user.usersettings.save()
            messages.success(request, 'Your settings have been saved.')
            return redirect('user_settings')
        else:
            messages.error(request, 'Form data invalid.')
            return redirect('user_settings')