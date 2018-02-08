# -*- coding: utf-8 -*-
from jubeat import settings
from sqlite3 import connect as s_con
from MySQLdb import connect as m_con
from . import DatabaseCommands as DC
import os
import xmltodict
import json


class SongScores(object):
    """Song scores."""
    def __init__(self, data_tuple):
        self.id = data_tuple[0]
        self.bas = data_tuple[1]
        self.adv = data_tuple[2]
        self.ext = data_tuple[3]


class SongInfo(object):
    """Song info."""
    def __init__(self, info_dict):
        if "ArtistE" not in info_dict["key"]:
            if len(info_dict["integer"]) == 5:
                self.id = int(info_dict["integer"][0])
                self.title = info_dict["string"][1]
                self.artist = info_dict["string"][0] if info_dict["string"][0] is not None else None
                self.bas = int(info_dict["integer"][2])
                self.adv = int(info_dict["integer"][1])
                self.ext = int(info_dict["integer"][3])
            elif len(info_dict["integer"]) == 4:
                self.id = int(info_dict["string"][1])
                self.title = info_dict["string"][2]
                self.artist = info_dict["string"][0] if info_dict["string"][0] is not None else None
                self.bas = int(info_dict["integer"][1])
                self.adv = int(info_dict["integer"][0])
                self.ext = int(info_dict["integer"][2])
            else:
                pass
        else:
            self.id = int(info_dict["string"][2])
            self.title = info_dict["string"][3]
            self.artist = info_dict["string"][0] if info_dict["string"][0] != None else None
            self.bas = int(info_dict["integer"][1])
            self.adv = int(info_dict["integer"][0])
            self.ext = int(info_dict["integer"][2])


class Scores(object):
    """Score-related operations."""
    def __init__(self, scores_file=None, wal_file=None, player_id=None, user_id=None):
        self.file = scores_file
        self.wal = wal_file
        self.pid = player_id if player_id is not None else None
        if self.file is not None:
            self.local_save()
        self.uid = "T_" + self.get_user_id() if user_id is None else user_id
        database_info = settings.DATABASES["default"]
        self.conn = m_con(host=database_info["HOST"],
                          user=database_info["USER"],
                          passwd=database_info["PASSWORD"],
                          db=database_info["NAME"])
        self.cursor = self.conn.cursor()

    def local_save(self):
        """Save scores_file to local directories."""
        accessory_dir = settings.BASE_DIR + settings.ACCESSORY_DIR
        if not os.path.isdir(accessory_dir):
            os.mkdir(accessory_dir)

        upload_file = "%s%s.sqlite" % (accessory_dir, self.pid)
        with open(upload_file, "wb") as new_file:
            for chunk in self.file.chunks():
                new_file.write(chunk)

        if self.wal is not None:
            print("WAL DETECTED!")
            wal_file = "%s%s.sqlite-wal" % (accessory_dir, self.pid)
            new_wal_file = open(wal_file, "wb")
            for chunk in self.wal.chunks():
                new_wal_file.write(chunk)

    def get_user_id(self):
        """Extract user_id from local file."""
        conn = s_con(database=settings.BASE_DIR + settings.ACCESSORY_DIR + self.pid + ".sqlite")
        cursor = conn.cursor()

        cursor.execute("select Z_UUID from Z_METADATA")
        user_id = cursor.fetchall()[0][0].replace("-", "_")

        cursor.close()
        conn.close()
        return user_id

    def get_scores(self):
        """Extract scores from local file."""
        conn = s_con(database=settings.BASE_DIR + settings.ACCESSORY_DIR + self.pid + ".sqlite")
        cursor = conn.cursor()

        # if self.wal is not None:
        #     cursor.execute("PRAGMA wal_autocheckpoint=0")

        cursor.execute("select ZTUNEID, ZSCOBAS, ZSCOADV, ZSCOEXT from ZSCORERECORD")
        raw_data = cursor.fetchall()
        score_list = [SongScores(data) for data in raw_data]

        cursor.close()
        conn.close()
        return score_list

    def add_to_database(self):
        """Add scores to online database."""
        try:
            score_list = self.get_scores()
        except Exception:
            os.remove("%s%s.sqlite" % (settings.BASE_DIR + settings.ACCESSORY_DIR, self.pid))
            return False
        self.cursor.execute(DC.create_score % self.uid)

        for song in score_list:
            try:
                self.cursor.execute(DC.insert_score % (self.uid, song.id, song.bas, song.adv, song.ext))
            except Exception:
                self.cursor.execute(DC.update_score % (self.uid, song.bas, song.adv, song.ext, song.id))
        self.conn.commit()

        os.remove("%s%s.sqlite" % (settings.BASE_DIR + settings.ACCESSORY_DIR, self.pid))
        # if self.wal is not None:
        #     os.remove("%s%s.sqlite-wal" % (settings.BASE_DIR + settings.ACCESSORY_DIR, self.pid))
        return True

    def get_from_database(self):
        """Get scores from online database."""
        self.cursor.execute(DC.get_score % self.uid)
        score_list = self.cursor.fetchall()
        output_list = []
        for score in score_list:
            self.cursor.execute(DC.get_song % score[0])
            song = self.cursor.fetchall()
            if len(song) == 0:
                continue
            else:
                song = song[0]
                output_dict = {"sid": score[0],
                               "bas_score": score[1] if score[1] != -1 else "--",
                               "adv_score": score[2] if score[2] != -1 else "--",
                               "ext_score": score[3] if score[3] != -1 else "--",
                               "title": song[1],
                               "artist": song[2],
                               "bas_level": "Lv " + str(song[3]),
                               "adv_level": "Lv " + str(song[4]),
                               "ext_level": "Lv " + str(song[5])}
                output_list.append(output_dict)
        return json.dumps(output_list)

    def id_checker(self):
        """Check player_id and user_id."""
        try:
            self.cursor.execute(DC.insert_id % (self.uid, self.pid))
            pid = self.pid
        except Exception:
            self.cursor.execute(DC.get_pid % self.uid)
            pid = self.cursor.fetchall()[0][0]
            self.cursor.execute(DC.update_id % (self.pid, self.uid))
        self.conn.commit()
        return pid == self.pid, pid


class Songs(object):
    """Song-related operations."""
    def __init__(self):
        database_info = settings.DATABASES["default"]
        self.conn = m_con(host=database_info["HOST"],
                          user=database_info["USER"],
                          passwd=database_info["PASSWORD"],
                          db=database_info["NAME"])
        self.cursor = self.conn.cursor()

    def update_song(self):
        """Update song list."""
        f = open(settings.BASE_DIR + "/musiccache.json")
        text = f.read()
        f.close()
        dict_list = json.loads(text)["plist"]["dict"]["dict"]
        song_list = [SongInfo(song_dict) for song_dict in dict_list]
        for song in song_list:
            if (song.id > 100000100) and (song.id < 900000000):
                try:
                    print(DC.insert_song %
                                        (song.id, song.title, song.artist, song.bas, song.adv, song.ext))
                    self.cursor.execute(DC.insert_song %
                                        (song.id, song.title, song.artist, song.bas, song.adv, song.ext))
                except Exception:
                    pass
        self.conn.commit()

    @staticmethod
    def ranking(score_list):
        i = 0
        while i < len(score_list):
            if score_list[i] == "--":
                del score_list[i]
            else:
                i += 1
        if len(score_list) == 0:
            return {"--": "--"}

        score_list.sort(reverse=True)

        i = 1
        rank = [1]
        rank_iterator = 1
        while i < len(score_list):
            rank_iterator += 1
            if score_list[i] == score_list[i - 1]:
                del score_list[i]
            else:
                rank.append(rank_iterator)
                i += 1

        ranking_dict = dict(zip(score_list, rank))
        ranking_dict["--"] = "--"
        print(ranking_dict)
        return ranking_dict

    def get_song_info(self, sid):
        """Get song info."""
        self.cursor.execute(DC.get_song % sid)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            return None
        else:
            song_info = temp[0]
            song_dict = {"sid": sid,
                         "title": song_info[1],
                         "artist": song_info[2],
                         "bas_level": song_info[3],
                         "adv_level": song_info[4],
                         "ext_level": song_info[5]}
            return json.dumps(song_dict)

    def get_song_scores(self, sid):
        """Get song scores."""
        self.cursor.execute(DC.get_player)
        player_list = self.cursor.fetchall()
        if len(player_list) == 0:
            return None
        else:
            output_list = []
            for player in player_list:
                output_dict = {"uid": player[0],
                               "pid": player[1]}
                self.cursor.execute(DC.get_song_score % (output_dict["uid"], sid))
                temp = self.cursor.fetchall()
                if len(temp) == 0:
                    continue
                else:
                    song_scores = temp[0]
                    if song_scores[1] != -1:
                        output_dict["bas_score"] = song_scores[1]
                    else:
                        output_dict["bas_score"] = "--"
                    if song_scores[2] != -1:
                        output_dict["adv_score"] = song_scores[2]
                    else:
                        output_dict["adv_score"] = "--"
                    if song_scores[3] != -1:
                        output_dict["ext_score"] = song_scores[3]
                    else:
                        output_dict["ext_score"] = "--"
                    output_list.append(output_dict)
            if len(output_list) == 0:
                return None
            else:
                bas_list = [output_dict["bas_score"] for output_dict in output_list]
                bas_rank = self.ranking(bas_list)
                adv_list = [output_dict["adv_score"] for output_dict in output_list]
                adv_rank = self.ranking(adv_list)
                ext_list = [output_dict["ext_score"] for output_dict in output_list]
                ext_rank = self.ranking(ext_list)
                for output_dict in output_list:
                    output_dict["bas_rank"] = bas_rank[output_dict["bas_score"]]
                    output_dict["adv_rank"] = adv_rank[output_dict["adv_score"]]
                    output_dict["ext_rank"] = ext_rank[output_dict["ext_score"]]
                return json.dumps(output_list)


class ID(object):
    """???"""
    def __init__(self, pid):
        self.pid = pid
        self.uid = None
        database_info = settings.DATABASES["default"]
        self.conn = m_con(host=database_info["HOST"],
                          user=database_info["USER"],
                          passwd=database_info["PASSWORD"],
                          db=database_info["NAME"])
        self.cursor = self.conn.cursor()
        self.cursor.execute(DC.get_uid % self.pid)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            self.uid = None
        else:
            self.uid = temp[0][0]
