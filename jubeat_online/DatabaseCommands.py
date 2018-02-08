# -*- coding: utf-8 -*-

create_score = "create table if not exists %s(" \
               "sid int," \
               "bas_score int," \
               "adv_score int," \
               "ext_score int," \
               "primary key(sid))"

insert_score = "insert into %s " \
               "(sid, bas_score, adv_score, ext_score) " \
               "values (%d, %d, %d, %d)"

update_score = "update %s set " \
               "bas_score = %d," \
               "adv_score = %d," \
               "ext_score = %d " \
               "where sid = %d"

get_score = "select * from %s"

get_song_score = "select * from %s where sid = %d"

insert_id = "insert into id (uid, pid) values ('%s', '%s')"

get_pid = "select pid from id where uid = '%s'"

get_uid = "select uid from id where pid = '%s'"

update_id = "update id set pid = '%s' where uid = '%s'"

insert_song = "insert into song " \
              "(sid, title, artist, bas_level, adv_level, ext_level) " \
              "values (%d, '%s', '%s', %d, %d, %d)"

get_song = "select * from song where sid = %d"

get_player = "select * from id"
