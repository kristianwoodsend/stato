import sys
import math

from fuzzywuzzy import process

from stato.download import get_data, projection_sources, get_slate_from_csv
from stato.optimise import optimise
from stato.util import *
from stato.ref_data import PLAYERS, TEAM_CODE_MAPPINGS, TEAM_NAME_MAPPINGS


def map_team_name(code):
    code = code.strip()
    if code in TEAM_CODE_MAPPINGS:
        code = TEAM_CODE_MAPPINGS.get(code)
    return TEAM_NAME_MAPPINGS.get(code)


def get_player(player_list, name):
    for player in player_list:
        if player.name == name:
            return player
    return None


def fuzzy_match(options, text):
    match = process.extract(text, options, limit=1)
    if len(match) == 1:
        match, score = match[0]
        if score >= 80:
            return match
    return None


def match_players():
    player_dict = {p[1]: p[0] for p in PLAYERS}
    names = player_dict.keys()
    for title, data, _ in projections:
        player_list = load_obj(data)
        for p in player_list:
            if p.name in names:
                name = p.name
            else:
                name = fuzzy_match(names, map_team_name(p.team_code) if p.position == 'D' else p.name)

            if name:
                print "union select {}, {}, {}, '{}', '{}'".format(16345, player_dict[name], p.fp, title, 'week 2')


def avg_team():
    names = [p[1] for p in PLAYERS]
    players = {p[1]: [] for p in PLAYERS}
    for title, data, _ in projections:
        team = load_obj(data)
        for p in team:
            if p.name in names:
                name = p.name
            else:
                name = fuzzy_match(names, map_team_name(p.team_code) if p.position == 'D' else p.name)

            if name:
                players[name].append(p)
            else:
                print "No match for {}1 - {}".format(p.name, p.team_code)

    avg = []
    for name, source_players in players.iteritems():
        if len(source_players) > 0:
            fp = math.fsum([p.fp for p in source_players]) / len(source_players)
            p = source_players[0]
            avg.append(Player(p.id, p.name, p.position, p.team_code, p.salary, fp))
    return avg


def trim_players_to_slate(player_list, slate):

    slate_players = [(map_team_name(p.team_code) if p.position == 'D' else p.name, map_team_name(p.team_code), p.position) for p in slate]
    slate_teams = {p[1] for p in slate_players}

    final_player_list = []

    potential_players = [p for p in player_list if map_team_name(p.team_code) in slate_teams]

    for p in potential_players:

        name = map_team_name(p.team_code) if p.position == 'D' else p.name
        if (name, map_team_name(p.team_code), p.position) in slate_players:
            final_player_list.append(p)
        else:
            potential_slate_players = [sp for sp in slate_players
                                       if sp[1] == map_team_name(p.team_code) and sp[2] == p.position]

            mname = fuzzy_match([sp[0] for sp in potential_slate_players], name)
            if mname is None:
                print 'no match for - got for {}-{}'.format(name, p.team_code)


#
# names = player_dict.keys()
# for title, data, _ in projections:
#     player_list = load_obj(data)
#     for p in player_list:
#         if p.name in names:
#             name = p.name
#         else:
#             name = fuzzy_match(names, map_team_name(p.team_code) if p.position == 'D' else p.name)
#
#         if name:
#             print "union select {}, {}, {}, '{}', '{}'".format(16345, player_dict[name], p.fp, title, 'week 2')

#
# for title, data, _ in projections:
#     score, team = optimise(load_obj(data))
#     print_team(title, team, score)
#
# avg = avg_team()

# avg = filter(lambda p: p.name != 'Brent Celek', avg)

# score, team = optimise(avg)
# print_team("AVG", team, score)


# print_all_in_pos(avg, "D")


# match_players()

# 4800


def main(args):
    # slate_csv = args[1]
    slate = get_slate_from_csv("slate.csv")
    trim_players_to_slate(load_obj("nf_data"), slate)
    trim_players_to_slate(load_obj("rg_data"), slate)
    trim_players_to_slate(load_obj("rw_data"), slate)


if __name__ == "__main__":
    main(sys.argv)
