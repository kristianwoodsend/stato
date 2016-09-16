import csv
import os
from itertools import product


from util import Player, print_team
from optimise import optimise


def read_projection_file(input_file):
    players = {}
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            player_id = row["player_id"]
            try:
                p = players[player_id]
            except KeyError:
                players[player_id] = row
                p = players[player_id]
            # get projection from this source for this player
            p[row['source']] = row['projected']
    return players



def create_player_list(players, weights):
    # Create list of players from input dictionaries

    player_list = []
    sources = weights.keys()

    for (k, v) in players.items():
        # if v['final_score']=='':
        #     continue

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


def float_or_zero(number):
    try:
        return float(number)
    except ValueError:
        return 0.0


input_file = os.path.join(os.getcwd(), '../projections/week2.csv')
players = read_projection_file(input_file)

STEPS = 2
for (rw, nf, rg) in product(range(STEPS), range(STEPS), range(STEPS)):
    if rw==nf==rg==0.0:
        continue
    weights = {'RotoWire': float(rw), 'NumberFire': float(nf), 'RotoGrinders': float(rg)}
    player_list = create_player_list(players, weights)
    player_list = filter(lambda p: p.name != 'David Johnson', player_list)
    score, team = optimise(player_list)
    actual_score = sum([float_or_zero(players[t.id]['final_score']) for t in team])
    print
    print weights
    print_team('final_score', team, score)
    if actual_score > 150.0:
        print weights, '\t', 'Actual Score: ', actual_score
