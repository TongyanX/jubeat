# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, "home.html")


def song(request):
    return render(request, "song.html")


def player_detail(request):
    return render(request, "player_detail.html")


def player_summary(request):
    return render(request, "player_summary.html")


def player_detail_skp(request):
    return render(request, "player_detail_skp.html")


def player_summary_skp(request):
    return render(request, "player_summary_skp.html")


def all_summary_skp(request):
    return render(request, "all_summary_skp.html")
