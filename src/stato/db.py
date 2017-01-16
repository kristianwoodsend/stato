import sqlite3
import re
from os import listdir, path, makedirs
from shutil import copyfile
from datetime import datetime

from .util import echo

DB_DIR = path.join(path.expanduser('~'), '.stato', 'db')
DB_FILE = 'data.db'


def connect():
    return sqlite3.connect(path.join(DB_DIR, DB_FILE))


def execute(query):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query)


def select(query, params=None):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def select_one_column(query, params=None):
    return [row[0] for row in select(query, params)]


def table_exists(name):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
    return len(select(query, params=(name,))) == 1


def update_exists(number):
    if not table_exists("db_updates"):
        return False
    query = "SELECT file_number FROM db_updates WHERE file_number=?;"
    return len(select(query, params=(number,))) == 1


def do_file(file_number, file_name):
    echo("Running update {}: {}".format(file_number, file_name))
    with open(file_name, "r") as f, \
            connect() as conn:

        sql = f.read()
        cursor = conn.cursor()
        for statement in sql.split(';'):
            try:
                cursor.execute(statement)
            except Exception as e:
                echo(statement)
                raise e

        cursor.execute(
            "INSERT INTO db_updates VALUES (?, ?, datetime('now'))",
            (file_number, file_name)
        )


def do_updates():

    sql_path = path.join(path.dirname(path.realpath(__file__)), 'sql')
    db_backed_up = False
    has_updates = False
    for file in listdir(sql_path):
        file_name = path.join(sql_path, file)
        file_number = int(re.sub(".*/(\\d*)_.*.sql", "\\1", file_name))
        if not update_exists(file_number):

            if not has_updates:
                echo('DB updates required.')
                has_updates = True

            if not db_backed_up:
                db_path = path.join(DB_DIR, DB_FILE)
                backup_file = '{}.{}.bak'.format(db_path,
                                                 datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
                echo("Backing up db to {}".format(backup_file))
                copyfile(db_path, backup_file)
                db_backed_up = True

            do_file(file_number, file_name)

    if has_updates:
        echo('---------------')
