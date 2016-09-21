import csv
import os
from itertools import product


from util import Player, print_team
from optimise import optimise
from download import get_data, load_obj, projection_sources
from match import merge_sources, create_player_list

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




def float_or_zero(number):
    try:
        return float(number)
    except ValueError:
        return 0.0


if __name__ == "__main__":
    get_data()
    main = load_obj("fd_players_final")
    player_dict_list = merge_sources(main, projection_sources)
    # for p, v in player_dict_list.items():
    #     print p, v


    STEPS = 2
    for (rw, nf, rg, dfc) in product(range(STEPS), range(STEPS), range(STEPS), range(STEPS)):
        if rw == nf == rg == dfc == 0.0:
            continue
        weights = {'RotoWire': float(rw), 'NumberFire': float(nf), 'RotoGrinders': float(rg), 'DFCafe': float(dfc)}
        player_list = create_player_list(player_dict_list, weights)
        player_list = filter(lambda p: p.name != 'David Johnson', player_list)
        score, team = optimise(player_list)
        actual_score = sum([float_or_zero(player_dict_list[t.id]['final_score']) for t in team])
        print "Actual:\t{actual}\tProj:\t{proj}\tWeights: ".format(
            actual=actual_score, proj=score), weights
        # print_team('final_score', team, score)
        # if actual_score > 150.0:
        #     print weights, '\t', 'Actual Score: ', actual_score
