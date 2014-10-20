from django.shortcuts import render


def help_guide(request):
    context = {
        'base_url': 'http://' + request.get_host(),
        'superuser': request.user.is_superuser
    }
    return render(request, 'guide.html', context)


def help_faq(request):
    return render(request, 'faq.html')