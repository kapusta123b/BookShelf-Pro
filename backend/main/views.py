from django.shortcuts import render


def index(request):
    return render(request, 'main/index.html')


def privacy(request):
    return render(request, 'main/privacy.html')


def terms(request):
    return render(request, 'main/terms.html')
