from stato.download import get_data, projection_sources
from stato.util import *

from fuzzywuzzy import process

from itertools import product
from util import Player, print_team
from optimise import optimise


def match(main, src):
    pairs = []
    for pos in POSITIONS:
        main_players = [p for p in main if p.position == pos]
        player_names = [p.name for p in main_players]
        matched = [p for p in src if p.position == pos and p.name in player_names]
        unmatched = [p for p in src if p.position == pos and p.name not in player_names]

        # find exact matches
        for p in matched:
            m = [pl for pl in main_players if pl.name == p.name][0]
            pairs.append((m, p))
            main_players.remove(m)

        # match the others based on Levenshtein distance
        player_names = [p.name for p in main_players]
        # print "{pos}: {num}".format(pos=pos, num=len(unmatched))
        for p in unmatched:
            match = process.extract(p.name, player_names, limit=1)
            if len(match) == 1:
                match, score = match[0]
                if score >= 80:
                    # print "{} = {} ({})".format(p.name, match, score)
                    m = [pl for pl in main_players if pl.name == match][0]
                    pairs.append((m, p))
                else:
                    print "POOR MATCH FOR {} = {} ({})".format(p.name, match, score)
            else:
                print "NO MATCH FOR {}".format(p.name)

    return pairs



def create_player_list(players, weights):
    # Create list of players from input dictionaries

    player_list = []
    sources = weights.keys()

    for k, v in players.items():
        # if v['final_score']=='':
        #     continue

        try:
            name = v['name']
        except KeyError:
            name = v['first_name'] + ' ' + v['last_name']
        points = 0
        weight = 0
        for source in sources:
            try:
                fp = float(v[source])
                points += fp * weights[source]
                weight += weights[source]
            except (KeyError, ValueError):
                # print v['first_name'], v['last_name']
                pass
                # fp = 0.0
                # points += fp * weights[source]
                # weight += weights[source]
        if weight > 0:
            points = points / weight
        player_list.append(Player(v['player_id'], name, v['position'], v['team_code'], float(v['salary']), points))
    return player_list


#
# for title, data, _ in projections:
#     score, team = optimise(load_obj(data))
#     print_team(title, team, score)
#

get_data()

main = load_obj("fd_players")

player_dict_list = {}
for (src_name, src_file, src_fn) in projection_sources:
    print src_name, src_file
    src_data = load_obj(src_file)
    pairs = match(main, src_data)

    for (m, p) in pairs:
        try:
            pd = player_dict_list[m.id]
        except KeyError:
            player_dict_list[m.id] = {'player_id': m.id, 'name': m.name, 'position': m.position, 'team_code': m.team_code, 'salary': m.salary}
            pd = player_dict_list[m.id]
        pd[src_name] = p.fp

for p, v in player_dict_list.items():
    print p, v

STEPS = 2
for (rw, nf, rg, dfc) in product(range(STEPS), range(STEPS), range(STEPS), range(STEPS)):
    if rw == nf == rg == dfc == 0.0:
        continue
    weights = {'RotoWire': float(rw), 'NumberFire': float(nf), 'RotoGrinders': float(rg), 'DFCafe': float(dfc)}
    player_list = create_player_list(player_dict_list, weights)
    score, team = optimise(player_list)
    print
    print weights
    print_team('final_score', team, score)
    print
