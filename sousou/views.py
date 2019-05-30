from django.shortcuts import render

from user.models import UserInfo


def index(request):
    """首页"""
    return render(request, 'index.html')


def get_help(request):
    """帮助中心"""
    return render(request, 'help.html')
