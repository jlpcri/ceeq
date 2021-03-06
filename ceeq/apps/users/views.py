from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.conf import settings

from models import UserSettings


def user_is_superuser(user):
    return user.is_superuser


def sign_in(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            if user.is_active:
                login(request, user)
                try:
                    UserSettings.objects.get(user=user)
                except UserSettings.DoesNotExist:
                    UserSettings.objects.create(user=user)
                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                else:
                    return redirect('users:home')
            else:
                messages.error(request, 'This account is inactive.')
                return redirect('landing')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('landing')
    else:
        return redirect('landing')


@login_required
def sign_out(request):
    logout(request)
    return redirect('landing')


@login_required
def home(request):
    context = RequestContext(request, {
        'root_path': settings.LOGIN_URL
    })
    return render(request, 'users/home.html', context)


@user_passes_test(user_is_superuser)
def user_management(request):
    if request.method == 'GET':

        sort_types = [
            'username',
            '-username',
            'last_login',
            '-last_login'
        ]
        users = ''
        sort = request.GET.get('sort', '')
        sort = sort if sort else 'username'

        if sort in sort_types:
            if sort == 'username':
                users = User.objects.all().order_by('username')
            elif sort == '-username':
                users = User.objects.all().order_by('-username')
            elif sort == 'last_login':
                users = User.objects.all().order_by('last_login')
            elif sort == '-last_login':
                users = User.objects.all().order_by('-last_login')

        current_user_id = request.user.id

        context = RequestContext(request, {
            'users': users,
            'sort': sort,
            'current_user_id': current_user_id
        })

        return render(request, 'users/user_management.html', context)

    return HttpResponseNotFound()


@user_passes_test(user_is_superuser)
def user_update(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, pk=user_id)

        user.is_active = request.POST.get('is_active', False) \
            or request.POST.get('is_staff', False) \
            or request.POST.get('is_superuser', False)
        user.is_staff = request.POST.get('is_staff', False)
        user.is_superuser = request.POST.get('is_superuser', False)

        user.save()

        return redirect('users:management')
    else:
        return redirect('users:management')


@user_passes_test(user_is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        logout(request)
        user.delete()
        return redirect('landing')
    else:
        user.delete()
        return redirect('users:management')


@login_required()
def user_settings(request):
    UserSettings.objects.get_or_create(user=request.user)
    user_settings = request.user.usersettings

    context = RequestContext(request, {
        'user_settings': user_settings
    })
    return render(request, 'users/user_settings.html', context)


@login_required()
def user_settings_update(request):
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.pk)

        if request.POST.get('bug'):
            if request.POST.get('improvement'):
                user.usersettings.improvement = True
            else:
                user.usersettings.improvement = False

            if request.POST.get('new_feature'):
                user.usersettings.new_feature = True
            else:
                user.usersettings.new_feature = False

            if request.POST.get('task'):
                user.usersettings.task = True
            else:
                user.usersettings.task = False

            if request.POST.get('environment'):
                user.usersettings.environment = True
            else:
                user.usersettings.environment = False

            if request.POST.get('suggested_improvement'):
                user.usersettings.suggested_improvement = True
            else:
                user.usersettings.suggested_improvement = False

            user.usersettings.save()
            messages.success(request, 'Your settings have been saved. Need update CEEQ score.')
        else:
            messages.error(request, 'Issue type Bug should be selected.')
        return redirect('users:user_settings')
    else:
        messages.error(request, 'Sorry, your settings cannot be saved.')
        return redirect('users:user_settings')
