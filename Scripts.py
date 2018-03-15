# -*- coding: utf-8 -*-
"""Initialize & Reset Scripts"""
from jubeat import settings
from MySQLdb import connect
from jubeat_online.keyOperations import Songs, ID


def reset_song_table():
    """Reset song table."""
    st = Songs()
    st.reset_song_table()
    st.update_song()


def reset_id_table():
    """Reset id table."""
    it = ID()
    it.reset_id_table()


def reset_db():
    """Reset database."""
    database_info = settings.DATABASES["default"]
    conn = connect(host=database_info["HOST"],
                   user=database_info["USER"],
                   passwd=database_info["PASSWORD"],
                   db=database_info["NAME"])
    cursor = conn.cursor()

    statement = "SELECT CONCAT('DROP TABLE ',table_name) FROM information_schema.`TABLES` " \
                "WHERE table_schema = 'jubeat_scores'"
    cursor.execute(statement)
    statement_list = [statement[0] for statement in cursor.fetchall()]

    for statement in statement_list:
        cursor.execute(statement)

    reset_song_table()
    reset_id_table()


reset_db()
