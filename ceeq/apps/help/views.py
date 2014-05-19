from django.shortcuts import render


def help_guide(request):
    return render(request, 'guide.html')


def help_faq(request):
    return render(request, 'faq.html')