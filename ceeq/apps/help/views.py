from django.shortcuts import render


def guide(request):
    context = {
        'base_url': 'http://' + request.get_host(),
        'superuser': request.user.is_superuser
    }
    if request.user.username == 'sliu':
        return render(request, 'help/guide_framework.html', context)
    else:
        return render(request, 'help/guide.html', context)


def faq(request):
    return render(request, 'help/faq.html')