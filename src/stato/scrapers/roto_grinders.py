import csv
from ..util import Player, process_urls


def get_nfl_data():
    return process_urls([
            'https://rotogrinders.com/projected-stats/nfl-qb.csv?site=fanduel',
            'https://rotogrinders.com/projected-stats/nfl-rb.csv?site=fanduel',
            'https://rotogrinders.com/projected-stats/nfl-wr.csv?site=fanduel',
            'https://rotogrinders.com/projected-stats/nfl-te.csv?site=fanduel',
            'https://rotogrinders.com/projected-stats/nfl-kicker.csv?site=fanduel',
            'https://rotogrinders.com/projected-stats/nfl-defense.csv?site=fanduel',
    ], parser)


def get_nba_data():
    return process_urls(
        ['https://rotogrinders.com/projected-stats/nba-player.csv?site=fanduel'],
        parser
    )


def parser(http_response):
    players = []
    reader = csv.reader(http_response)
    index = 1
    for row in skip_last(reader):
        name = row[0]
        pos = row[3]
        team = row[2]
        sal = int(row[1])
        fp = float(row[7])

        players.append(Player(pos + str(index), name, pos, team, sal, fp))
        index += 1

    return players


def skip_last(iterator):
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item
