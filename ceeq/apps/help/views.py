from django.shortcuts import render


def guide(request):
    context = {
        'base_url': 'http://' + request.get_host(),
        'superuser': request.user.is_superuser
    }

    return render(request, 'help/guide.html', context)


def guide_framework(request):
    context = {
        'base_url': 'http://' + request.get_host(),
        'superuser': request.user.is_superuser
    }

    return render(request, 'help/guide_framework.html', context)


def faq(request):
    return render(request, 'help/faq.html')