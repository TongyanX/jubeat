# -*- coding: utf-8 -*-
"""Classes & Operations"""
from jubeat import settings
from jubeat_online.dataClasses import SongScores, SongInfo
from sqlite3 import connect as s_con
from MySQLdb import connect as m_con
import os
import json


def empty_score(score):
    """Change -1 to "--"."""
    if score == -1:
        return "--"
    else:
        return score


def fc_or_not(fc):
    """Change 0, 1 to "", "√"."""
    if fc == 1:
        return "√"
    else:
        return ""


def add_lv(lv):
    """Add "Lv" before level."""
    return "Lv" + str(lv)


def ranking(score_list):
    """Calculate ranking."""
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
    return ranking_dict


def rating(score):
    """Return rating."""
    if score == 1000000:
        return "EXC"
    elif score >= 980000:
        return "SSS"
    elif score >= 950000:
        return "SS"
    elif score >= 900000:
        return "S"
    elif score >= 850000:
        return "A"
    elif score >= 800000:
        return "B"
    elif score >= 700000:
        return "C"
    elif score >= 500000:
        return "D"
    elif score != -1:
        return "E"
    else:
        return "NP"


class Player(object):
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

        if self.wal is not None:
            cursor.execute("PRAGMA wal_autocheckpoint=0")

        statement = "SELECT ZTUNEID, ZSCOBAS, ZSCOADV, ZSCOEXT, ZFCBAS, ZFCADV, ZFCEXT, ZPLAYCOUNT FROM ZSCORERECORD"
        cursor.execute(statement)
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

        statement = "CREATE TABLE IF NOT EXISTS {}(" \
                    "SID INT, " \
                    "BAS_Score INT DEFAULT -1, " \
                    "ADV_Score INT DEFAULT -1, " \
                    "EXT_Score INT DEFAULT -1, " \
                    "BAS_FC INT DEFAULT 0, " \
                    "ADV_FC INT DEFAULT 0, " \
                    "EXT_FC INT DEFAULT 0, " \
                    "Play_Count INT DEFAULT 0, " \
                    "PRIMARY KEY(SID))".format(self.uid)
        self.cursor.execute(statement)

        for song in score_list:
            try:
                statement = "INSERT INTO {} VALUES (%d, %d, %d, %d, %d, %d, %d, %d)".format(self.uid)
                self.cursor.execute(statement % (song.id, song.bas, song.adv, song.ext,
                                                 song.fc_bas, song.fc_adv, song.fc_ext, song.pc))
            except Exception:
                statement = "UPDATE {} SET " \
                            "BAS_Score = %d, " \
                            "ADV_Score = %d, " \
                            "EXT_Score = %d, " \
                            "BAS_FC = %d, " \
                            "ADV_FC = %d, " \
                            "EXT_FC = %d, " \
                            "Play_Count = %d " \
                            "WHERE SID = %d".format(self.uid)
                self.cursor.execute(statement % (song.bas, song.adv, song.ext, song.fc_bas,
                                                 song.fc_adv, song.fc_ext, song.pc, song.id))
        self.conn.commit()
        os.remove("%s%s.sqlite" % (settings.BASE_DIR + settings.ACCESSORY_DIR, self.pid))

        return True

    def get_from_database(self):
        """Get scores from online database."""
        statement = "SELECT * FROM {} AS t JOIN Song AS s ON t.SID = s.SID".format(self.uid)
        self.cursor.execute(statement)
        song_list = self.cursor.fetchall()

        output_list = []
        for song in song_list:
            song = [song[0]] + list(song[9: 11]) + list(map(add_lv, song[11:])) + [song[7]] + \
                   list(map(empty_score, song[1: 4])) + list(map(fc_or_not, song[4: 7])) + \
                   list(map(rating, song[1: 4]))
            output_dict = dict(zip(["SID", "Title", "Artist", "BAS_Level", "ADV_Level", "EXT_Level", "Play_Count",
                                    "BAS_Score", "ADV_Score", "EXT_Score", "BAS_FC", "ADV_FC", "EXT_FC",
                                    "BAS_Rating", "ADV_Rating", "EXT_Rating"], song))
            output_list.append(output_dict)
        return json.dumps(output_list)

    def average_and_rating(self, level):
        """Generate average list and rating list."""
        statement = "SELECT t.BAS_Score FROM {} AS t JOIN Song AS s ON t.SID = s.SID " \
                    "WHERE s.BAS_Level = {}".format(self.uid, level)
        self.cursor.execute(statement)
        score_list = [score[0] for score in self.cursor.fetchall()]

        statement = "SELECT t.ADV_Score FROM {} AS t JOIN Song AS s ON t.SID = s.SID " \
                    "WHERE s.ADV_Level = {}".format(self.uid, level)
        self.cursor.execute(statement)
        score_list += [score[0] for score in self.cursor.fetchall()]

        statement = "SELECT t.EXT_Score FROM {} AS t JOIN Song AS s ON t.SID = s.SID " \
                    "WHERE s.EXT_Level = {}".format(self.uid, level)
        self.cursor.execute(statement)
        score_list += [score[0] for score in self.cursor.fetchall()]

        average_list = filter(lambda x: x != -1, score_list)
        rating_list = list(map(rating, score_list))

        return average_list, rating_list

    def get_score_summary(self, whole_level_dict):
        """Generate personal summary."""
        level_list = []
        total_list = []
        for level in range(1, 11):
            average_list, rating_list = self.average_and_rating(level)
            total_list += average_list

            average = sum(average_list) / len(average_list) if len(average_list) != 0 else "--"
            level_dict = dict(Level=level, Average=average)

            for rating in rating_list:
                if rating not in level_dict:
                    level_dict[rating] = 0
                level_dict[rating] += 1

            if "NP" not in level_dict:
                level_dict["NP"] = 0
            if len(whole_level_dict[level]) != len(rating_list):
                level_dict["NP"] += len(whole_level_dict[level]) - len(rating_list)
            level_dict["Total"] = len(whole_level_dict[level])

            level_list.append(level_dict)

        average = sum(total_list) / len(total_list) if len(total_list) != 0 else "--"
        total_dict = dict(Level="Total", Average=average)
        for rating in ["Total", "NP", "E", "D", "C", "B", "A", "S", "SS", "SSS", "EXC"]:
            total_dict[rating] = sum([data.get(rating, 0) for data in level_list])

        output = sorted(level_list, key=lambda x: int(x["Level"]))
        output.append(total_dict)

        return json.dumps(output)

    def id_checker(self):
        """Check player_id and user_id."""
        try:
            statement = "INSERT INTO ID VALUES (\"%s\", \"%s\")"
            self.cursor.execute(statement % (self.uid, self.pid))
            pid = self.pid
        except Exception:
            statement = "SELECT PID FROM ID WHERE UID = \"%s\""
            self.cursor.execute(statement % self.uid)
            pid = self.cursor.fetchone()[0]

            statement = "UPDATE ID SET PID = \"%s\" WHERE UID = \"%s\""
            self.cursor.execute(statement % (self.pid, self.uid))
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

    def reset_song_table(self):
        """Reset song table"""
        statement = "DROP TABLE IF EXISTS Song"
        self.cursor.execute(statement)

        statement = "CREATE TABLE IF NOT EXISTS Song(" \
                    "SID INT, " \
                    "Title TEXT, " \
                    "Artist TEXT, " \
                    "BAS_Level INT, " \
                    "ADV_Level INT, " \
                    "EXT_Level INT, " \
                    "PRIMARY KEY(SID))"

        self.cursor.execute(statement)
        self.conn.commit()

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
                    statement = "INSERT INTO Song VALUES (%d, \"%s\", \"%s\", %d, %d, %d)"
                    self.cursor.execute(statement % (song.id, song.title, song.artist, song.bas, song.adv, song.ext))
                except Exception:
                    pass
                self.conn.commit()

    def get_song_info(self, sid):
        """Get song info."""
        statement = "SELECT * FROM Song WHERE SID = {}".format(sid)
        self.cursor.execute(statement)
        song_info = self.cursor.fetchone()

        if song_info is None:
            return None
        else:
            song_dict = dict(zip(["SID", "Title", "Artist", "BAS_Level", "ADV_Level", "EXT_Level"],
                                 list(map(str, song_info))))
            return json.dumps(song_dict)

    def song_classification(self):
        """Classify songs through level."""
        statement = "SELECT * FROM Song"
        self.cursor.execute(statement)
        song_list = self.cursor.fetchall()

        level_dict = {}
        for song in song_list:
            if song[0] not in [100050010, 100050011, 100050031]:  # These 3 songs only have EXT chart
                if song[3] not in level_dict:
                    level_dict[song[3]] = []
                level_dict[song[3]].append(dict(SID=song[0], Title=song[1], Artist=song[2], Difficulty="BAS"))
                if song[4] not in level_dict:
                    level_dict[song[4]] = []
                level_dict[song[4]].append(dict(SID=song[0], Title=song[1], Artist=song[2], Difficulty="ADV"))

            if song[5] not in level_dict:
                level_dict[song[5]] = []
            level_dict[song[5]].append(dict(SID=song[0], Title=song[1], Artist=song[2], Difficulty="EXT"))
        return level_dict

    def get_song_scores(self, sid):
        """Get song scores."""
        statement = "SELECT * FROM ID"
        self.cursor.execute(statement)
        player_list = self.cursor.fetchall()

        if len(player_list) == 0:
            return None
        else:
            output_list = []
            for player in player_list:
                uid = player[0]
                pid = player[1]
                statement = "SELECT * FROM {} WHERE SID = {}".format(uid, sid)
                self.cursor.execute(statement)
                song_scores = self.cursor.fetchone()

                if song_scores is None:
                    continue
                else:
                    song_scores = [song_scores[0]] + list(map(empty_score, song_scores[1: 4])) + \
                                  list(map(rating, song_scores[1: 4])) + \
                                  list(map(fc_or_not, song_scores[4: 7])) + [song_scores[7]]
                    output_dict = dict(zip(["SID", "BAS_Score", "ADV_Score", "EXT_Score", "BAS_Rating", "ADV_Rating",
                                            "EXT_Rating", "BAS_FC", "ADV_FC", "EXT_FC", "Play_Count"], song_scores))
                    output_dict.update(dict(UID=uid, PID=pid))
                    output_list.append(output_dict)
            if len(output_list) == 0:
                return None
            else:
                bas_list = [output_dict["BAS_Score"] for output_dict in output_list]
                bas_rank = ranking(bas_list)
                adv_list = [output_dict["ADV_Score"] for output_dict in output_list]
                adv_rank = ranking(adv_list)
                ext_list = [output_dict["EXT_Score"] for output_dict in output_list]
                ext_rank = ranking(ext_list)
                for output_dict in output_list:
                    output_dict["BAS_Rank"] = bas_rank[output_dict["BAS_Score"]]
                    output_dict["ADV_Rank"] = adv_rank[output_dict["ADV_Score"]]
                    output_dict["EXT_Rank"] = ext_rank[output_dict["EXT_Score"]]
                return json.dumps(output_list)


class ID(object):
    """Connection between uid and pid."""
    def __init__(self, pid=0, uid=0):
        self.pid = pid
        self.uid = uid
        database_info = settings.DATABASES["default"]
        self.conn = m_con(host=database_info["HOST"],
                          user=database_info["USER"],
                          passwd=database_info["PASSWORD"],
                          db=database_info["NAME"])
        self.cursor = self.conn.cursor()

    def reset_id_table(self):
        """Reset id table."""
        statement = "DROP TABLE IF EXISTS ID"
        self.cursor.execute(statement)

        statement = "CREATE TABLE IF NOT EXISTS ID(" \
                    "UID TEXT, " \
                    "PID TEXT, " \
                    "PRIMARY KEY(UID))"

        self.cursor.execute(statement)
        self.conn.commit()

    def get_uid(self):
        """Get uid when pid is given or get pid when uid is given."""
        if self.uid == 0:
            statement = "SELECT UID FROM ID WHERE PID = \"%s\""
            self.cursor.execute(statement % self.pid)
            temp = self.cursor.fetchone()
            if temp is not None:
                self.uid = temp[0]

    def get_pid(self):
        """Get pid when uid is given."""
        if self.pid == 0:
            statement = "SELECT PID FROM ID WHERE UID = \"%s\""
            self.cursor.execute(statement % self.uid)
            temp = self.cursor.fetchone()
            if temp is not None:
                self.pid = temp[0]
