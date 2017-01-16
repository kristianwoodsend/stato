import csv
from ..util import Player


def parse_players_csv(input_file):
    players = []
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row['First Name'] + ' ' + row['Last Name']
            pos = row['Position']
            team = row['Team']
            player_id = row["Id"].split('-')[1]
            salary = row['Salary']
            fd_points = row['FPPG']

            players.append(Player(player_id, name, pos, team, salary, fd_points))

    return players


def parse_final_scores_csv(input_file):
    players = []
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row['first_name'] + ' ' + row['last_name']
            pos = row['position']
            team = row['team_code']
            player_id = row["player_id"]
            salary = row['salary']
            fd_points = row['final_score']
            players.append(Player(player_id, name, pos, team, salary, fd_points))

    return players
