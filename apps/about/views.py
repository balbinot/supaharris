from django.shortcuts import render

def info(request):
    return render(request, "about/info.html", {})


def privacy_policy(request):
    return render(request, "about/privacy_policy.html", {})


def handler404(request):
    return render(request, "404.html")

def handler500(request):
    return render(request, "500.html")
