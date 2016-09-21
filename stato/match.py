import math
from fuzzywuzzy import process
from util import *


def fuzzy_match(options, text):
    match = process.extract(text, options, limit=1)
    if len(match) == 1:
        match, score = match[0]
        if score >= 80:
            return match
    return None


def avg_team(players_full, teams):
    players = {p.id: [] for p in players_full}

    for team in teams:
        for p in team:
            try:
                players[p.id].append(p)
            except KeyError as e:
                print p.id
                raise e

    avg = []
    for name, source_players in players.iteritems():
        if len(source_players) > 0:
            fp = round(math.fsum([p.fp for p in source_players]) / len(source_players), 2)
            p = source_players[0]
            avg.append(Player(p.id, p.name, p.position, p.team_code, p.salary, fp))
    return avg


def match_player_ids(players_full, player_merge):
    player_tuples = [(p.name, p.team_code, p.position) for p in players_full]
    teams = {p.team_code for p in players_full}

    matched_players = []

    for p in [p for p in player_merge if p.team_code in teams]:

        match_name = None

        if (p.name, p.team_code, p.position) in player_tuples:
            match_name = p.name
        else:
            potential_matches = [m for m in player_tuples
                                 if m[1] == p.team_code and m[2] == p.position]
            match_name = fuzzy_match([m[0] for m in potential_matches], p.name)

        if match_name:
            match = filter(lambda sp: sp.name == match_name and
                                      sp.position == p.position and
                                      sp.team_code == p.team_code, players_full)[0]

            matched_players.append(Player(
                match.id, p.name, p.position, p.team_code, p.salary, p.fp
            ))

    return matched_players
