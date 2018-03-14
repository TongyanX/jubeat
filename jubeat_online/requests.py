# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from .keyOperations import Player, Songs, ID


def upload(request):
    """Dealing an upload scores_files."""
    if request.method == "POST":
        file_obj = request.FILES.get("score")
        wal_file_obj = request.FILES.get("wal")
        pid = request.POST["id"]
        if file_obj:
            player_obj = Player(scores_file=file_obj, wal_file=wal_file_obj, player_id=pid)
            uploading = player_obj.add_to_database()
            if uploading is False:
                return HttpResponse("WRONG")
            id_check, old_pid = player_obj.id_checker()
            if id_check is False:
                return HttpResponse(old_pid)
            return HttpResponse("OK")
    return HttpResponse("EMPTY")


def p_check(request):
    """Check a given pid exists or not."""
    pid = request.GET["pid"]
    print(pid)
    checker = ID(pid=pid)
    return HttpResponse(checker.uid)


def u_check(request):
    """Check a given uid exists or not."""
    uid = request.GET["uid"]
    checker = ID(uid=uid)
    return HttpResponse(checker.pid)


def get_scores(request):
    """Get all scores of a player."""
    uid = request.GET["uid"]
    player_obj = Player(user_id=uid)
    return HttpResponse(player_obj.get_from_database())


def get_scores_summary(request):
    """Summary all scores of a player."""
    uid = request.GET["uid"]
    player_obj = Player(user_id=uid)
    song_obj = Songs()
    return HttpResponse(player_obj.get_score_summary(song_obj.song_classification()))


def get_song_info(request):
    """Get a song's info."""
    sid = int(request.GET["sid"])
    song_obj = Songs()
    return HttpResponse(song_obj.get_song_info(sid))


def get_song_scores(request):
    """Get all player's scores of a single song."""
    sid = int(request.GET["sid"])
    song_obj = Songs()
    return HttpResponse(song_obj.get_song_scores(sid))
