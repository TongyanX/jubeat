# -*- coding: utf-8 -*-
"""Skill Point Table Related Operations"""
from jubeat import settings
from MySQLdb import connect
from jubeat_online.keyOperations import Songs, empty_score, fc_or_not, ranking
import csv
import json


class SkillPoint(object):
    """Skill point."""
    def __init__(self):
        database_info = settings.DATABASES["default"]
        self.conn = connect(host=database_info["HOST"],
                            user=database_info["USER"],
                            passwd=database_info["PASSWORD"],
                            db=database_info["NAME"])
        self.cursor = self.conn.cursor()

    def reset_skp_table(self):
        """Reset skp table."""
        statement = "DROP TABLE IF EXISTS SkillPoint"
        self.cursor.execute(statement)

        statement = "CREATE TABLE IF NOT EXISTS SkillPoint(" \
                    "SID INT, " \
                    "Difficulty TEXT, " \
                    "MAC_Level TEXT, " \
                    "MIC_Level TEXT, " \
                    "Note INT)"

        self.cursor.execute(statement)
        self.conn.commit()

    def get_current_data(self):
        """Get current skp data."""
        statement = "SELECT SID FROM SkillPoint"
        self.cursor.execute(statement)
        current_list = [sid[0] for sid in self.cursor.fetchall()]
        return current_list

    def input_skp_data(self):
        """Input skp data."""
        song_obj = Songs()
        whole_list = song_obj.song_classification()[10]
        whole_sid_list = [song["SID"] for song in whole_list]
        current_sid_list = self.get_current_data()

        csv_dir = settings.BASE_DIR + settings.SKP_CSV_DIR
        file_name = "jubeat_plus_lv.10_skp_v5.0.7.csv"
        f = open("%s%s" % (csv_dir, file_name))
        csv_data = csv.reader(f)

        for song in csv_data:
            if int(song[0]) in whole_sid_list and int(song[0]) not in current_sid_list:
                statement = "INSERT INTO SkillPoint VALUES (%d, \"%s\", \"%s\", \"%s\", %d)"
                print(song[0])
                self.cursor.execute(statement % (int(song[0]), song[3], song[4], song[5], int(song[6])))
                self.conn.commit()

        f.close()
        current_sid_list = self.get_current_data()

        for song in whole_list:
            if song["SID"] not in current_sid_list:
                print("\nTitle:\t{}\nArtist:\t{}\nChart:\t{}\n".format(song["Title"], song["Artist"], song["Difficulty"]))

                while True:
                    command = raw_input("New Level: ")
                    if len(command.split()) == 2:
                        mac = command.split()[0]
                        mic = command.split()[1]
                        if mac in ["9.25", "9.50", "9.75", "10.00", "10.25", "10.50", "10.75", "11.00"] and \
                                mic.lower() in ["high", "mid", "low"]:
                            mic = mic.lower().title()
                            break
                    print("Invalid Input.")

                while True:
                    note = raw_input("Note: ")
                    try:
                        note = int(note)
                        break
                    except ValueError:
                        print("Invalid Input.")

                statement = "INSERT INTO SkillPoint VALUES (%d, \"%s\", \"%s\", \"%s\", %d)"
                self.cursor.execute(statement % (song["SID"], song["Difficulty"], mac, mic, note))
                self.conn.commit()

    @staticmethod
    def level_calc(mac_level, mic_level):
        """Combine mac level and mic level."""
        new_level = float(mac_level) - 7
        if mic_level.lower() == "low":
            new_level -= 0.25 / 3
        elif mic_level.lower() == "high":
            new_level += 0.25 / 3
        return new_level

    @staticmethod
    def complete_calc(score):
        """Calculate complete ratio."""
        if score > 950000:
            return (float(score) - 950000) / 50000
        else:
            return 0

    @staticmethod
    def bonus_calc(score):
        """Calculate bonus point."""
        if score >= 999000:
            return 1
        elif score > 998000:
            return (float(score) - 998000) / 1000
        else:
            return 0

    @staticmethod
    def skp_calc(new_level, complete_ratio, bonus):
        """Calculate skp value."""
        skp = 100 * new_level * (complete_ratio + 0.05 * bonus)
        return skp

    @staticmethod
    def gr_calc(score, note):
        """Calculate efficient gr value."""
        gr = (1000000 - float(score)) / 270000 * float(note)
        return gr

    def get_skp_result(self, uid):
        """Get skp results of a player."""
        statement = "SELECT t.SID, s.Title, s.Artist, sp.Difficulty, sp.MAC_Level, sp.MIC_Level, " \
                    "t.BAS_Score, t.ADV_Score, t.EXT_Score, t.BAS_FC, t.ADV_FC, t.EXT_FC, " \
                    "sp.Note, t.Play_Count FROM {} AS t " \
                    "JOIN SkillPoint AS sp ON t.SID = sp.SID " \
                    "JOIN Song AS s ON t.SID = s.SID".format(uid)
        self.cursor.execute(statement)
        song_list = list(self.cursor.fetchall())

        output_list = []
        for song in song_list:
            output_dict = dict(SID=song[0], Title=song[1], Artist=song[2], Difficulty=song[3],
                               MAC_Level=song[4], MIC_Level=song[5], Note=song[12], Play_Count=song[13])
            if song[3] == "BAS":
                output_dict["Score"] = empty_score(song[6])
                output_dict["FC"] = fc_or_not(song[9])
            elif song[3] == "ADV":
                output_dict["Score"] = empty_score(song[7])
                output_dict["FC"] = fc_or_not(song[10])
            elif song[3] == "EXT":
                output_dict["Score"] = empty_score(song[8])
                output_dict["FC"] = fc_or_not(song[11])
            else:
                output_dict["Score"] = empty_score(-1)
                output_dict["FC"] = fc_or_not("")

            new_level = self.level_calc(output_dict["MAC_Level"], output_dict["MIC_Level"])
            complete_ratio = self.complete_calc(output_dict["Score"])
            bonus = self.bonus_calc(output_dict["Score"])
            output_dict["SKP"] = round(self.skp_calc(new_level, complete_ratio, bonus), 2)
            output_dict["MAX_SKP"] = round(self.skp_calc(new_level, 1, 1), 2)
            output_dict["GR"] = round(self.gr_calc(output_dict["Score"], output_dict["Note"]), 1)
            output_list.append(output_dict)

        if len(output_list) == 0:
            return None
        else:
            score_list = [output_dict["Score"] for output_dict in output_list]
            score_rank = ranking(score_list)
            skp_list = [output_dict["SKP"] for output_dict in output_list]
            skp_rank = ranking(skp_list)
            for output_dict in output_list:
                output_dict["Score_Rank"] = score_rank[output_dict["Score"]]
                output_dict["SKP_Rank"] = skp_rank[output_dict["SKP"]]
            return json.dumps(output_list)


obj = SkillPoint()
# obj.reset_skp_table()
# obj.input_skp_data()
obj.get_skp_result("T_6E6A7FCA_4A96_4007_A46A_0C1C66941E5D")
