# -*- coding: utf-8 -*-
"""Data Classes"""


class SongScores(object):
    """Song scores."""
    def __init__(self, data_tuple):
        self.id = int(data_tuple[0])
        self.bas = int(data_tuple[1])
        self.adv = int(data_tuple[2])
        self.ext = int(data_tuple[3])
        self.fc_bas = int(data_tuple[4])
        self.fc_adv = int(data_tuple[5])
        self.fc_ext = int(data_tuple[6])
        self.pc = int(data_tuple[7])


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
            self.artist = info_dict["string"][0] if info_dict["string"][0] is not None else None
            self.bas = int(info_dict["integer"][1])
            self.adv = int(info_dict["integer"][0])
            self.ext = int(info_dict["integer"][2])

        if (self.id > 100050000) and (self.id < 100060000):
            self.title += " [2]"
