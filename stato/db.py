import sqlite3
import re
from os import listdir, path


def execute(query):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


def select(query, params=None):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def select_one_column(query, params=None):
    return [row[0] for row in select(query, params)]


def table_exists(name):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
    return len(select(query, params=(name,))) == 1


def update_exists(number):
    query = "SELECT file_number FROM db_updates WHERE file_number=?;"
    return len(select(query, params=(number,))) == 1


def init():
    if not table_exists("db_updates"):
        execute("""
        CREATE TABLE db_updates (
            file_number INTEGER,
            file_name VARCHAR(255),
            date_updated DATETIME
        )
        """)


def do_file(file_name):
    file_number = int(re.sub(".*/(\\d*)_.*.sql", "\\1", file_name))

    if not update_exists(file_number):
        print "Running update {}: {}".format(file_number, file_name)
        with open(file_name, "r") as f, \
                sqlite3.connect('data.db') as conn:

            sql = f.read()
            cursor = conn.cursor()
            for statement in sql.split(';'):
                cursor.execute(statement)

            cursor.execute(
                "INSERT INTO db_updates VALUES (?, ?, date('now'))",
                (file_number, file_name)
            )


def do_updates():
    init()
    sql_path = 'stato/sql/'
    [do_file(path.join(sql_path, file)) for file in listdir(sql_path)]
