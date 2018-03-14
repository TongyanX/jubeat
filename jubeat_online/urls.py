# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views, requests

urlpatterns = [
    url(r'^home/$', views.home, name='home'),
    url(r'^upload/$', requests.upload, name='upload'),
    url(r'^p_check/$', requests.p_check, name='p_check'),
    url(r'^u_check/$', requests.u_check, name='u_check'),
    url(r'^scores/$', requests.get_scores, name='get_scores'),
    url(r'^summary/$', requests.get_scores_summary, name='get_scores_summary'),
    url(r'^song/$', views.song, name='song'),
    url(r'^song/info/$', requests.get_song_info, name='get_song_info'),
    url(r'^song/scores/$', requests.get_song_scores, name='get_song_scores'),
    url(r'^player/detail/$', views.player_detail, name='player_detail'),
    url(r'^player/summary/$', views.player_summary, name='player_summary'),
]
