# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views, FileLoader

urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^upload/$', FileLoader.upload, name='upload'),
    url(r'^check/$', FileLoader.check, name='check'),
    url(r'^scores/$', FileLoader.get_scores, name='get_scores'),
    url(r'^song/$', views.song, name='song'),
    url(r'^song/info/$', FileLoader.get_song_info, name='get_song_info'),
    url(r'^song/scores/$', FileLoader.get_song_scores, name='get_song_scores'),
]
