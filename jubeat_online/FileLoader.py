# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from .Scores import Scores, Songs, ID

# Create your views here.


def upload(request):
    """Dealing an upload scores_files."""
    if request.method == "POST":
        file_obj = request.FILES.get("score")
        wal_file_obj = request.FILES.get("wal")
        pid = request.POST["id"]
        if file_obj:
            scores_obj = Scores(scores_file=file_obj, wal_file=wal_file_obj, player_id=pid)
            uploading = scores_obj.add_to_database()
            if uploading is False:
                return HttpResponse("WRONG")
            id_check, old_pid = scores_obj.id_checker()
            if id_check is False:
                return HttpResponse(old_pid)
            return HttpResponse("OK")
    return HttpResponse("EMPTY")


def check(request):
    pid = request.GET["pid"]
    checker = ID(pid)
    return HttpResponse(checker.uid)


def get_scores(request):
    uid = request.GET["uid"]
    scores_obj = Scores(user_id=uid)
    return HttpResponse(scores_obj.get_from_database())

def get_song_info(request):
    sid = int(request.GET["sid"])
    song_obj = Songs()
    return HttpResponse(song_obj.get_song_info(sid))

def get_song_scores(request):
    sid = int(request.GET["sid"])
    song_obj = Songs()
    return HttpResponse(song_obj.get_song_scores(sid))
