# -*- coding: utf-8 -*-
"""Skill Point Table Related Operations"""
from jubeat import settings
from MySQLdb import connect
from jubeat_online.keyOperations import Songs
import csv


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
                    "DIFFICULTY TEXT, " \
                    "MAC_LEVEL TEXT, " \
                    "MIC_LEVEL TEXT, " \
                    "NOTE INT, " \
                    "PRIMARY KEY(SID))"

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
        current_list = self.get_current_data()

        csv_dir = settings.BASE_DIR + settings.SKP_CSV_DIR
        file_name = "jubeat_plus_lv.10_skp_v5.0.7.csv"
        f = open("%s%s" % (csv_dir, file_name))
        csv_data = csv.reader(f)

        for song in whole_list:
            if song["SID"] not in current_list:
                pass

        f.close()

        for song in whole_list:
            if song["SID"] not in current_list:
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

                statement = "INSERT INTO SkillPoint VALUES (%d, \"%s\", %f, \"%s\", %d)"
                self.cursor.execute(statement % (song["SID"], song["Difficulty"], mac, mic, note))
                self.conn.commit()

    def load_from_csv(self):
        """a"""
        csv_dir = settings.BASE_DIR + settings.SKP_CSV_DIR
        file_name = "jubeat_plus_lv.10_skp_v5.0.7.csv"
        f = open("%s%s" % (csv_dir, file_name))
        csv_data = csv.reader(f)
        print(list(csv_data))

        f.close()


obj = SkillPoint()
# obj.reset_skp_table()
# obj.input_skp_data()
obj.load_from_csv()
