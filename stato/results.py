import sys
from itertools import product
from stato.download import get_data, projection_sources
from stato.optimise import optimise
from stato.util import *
from stato.match import match_player_ids, avg_team


def weight_player(p, weight):
    return Player(p.id, p.name, p.position, p.team_code, p.salary, p.fp * weight)


def main(args):

    STEPS = 2
    fd_players = load_obj("fd_players")
    results = load_obj("fd_players_final")
    weights = [range(STEPS) for _ in projection_sources]
    sources = [source for _, source, _ in projection_sources]

    weighted_result_headers = ['Proj', 'Actual']
    weighted_result_headers.extend([title for title, _, _ in projection_sources])
    weighted_results = []

    for cp in product(*weights):
        if sum(cp) == 0:
            continue

        teams = [match_player_ids(fd_players, [weight_player(p, cp[index])
                                               for p in load_obj(source)
                                               if p.fp * cp[index] > 0])
                 for index, source in enumerate(sources)]

        score, team = optimise(avg_team(fd_players, teams))

        # check team players exist in results
        for p in team:
            if p not in results:
                raise Exception("Player not found in results, [{}] {}".format(p.id, p.name))

        actual = sum([float_or_zero(get_player(results, p.id).fp) for p in team])

        r = [score, actual]
        r.extend(cp)
        weighted_results.append(r)

    weighted_results = sorted(weighted_results, cmp=lambda a, b: cmp(a[1], b[1])*-1)

    print '\nWeighted Optimisations Vs Actual'
    print tabulate(weighted_results, headers=weighted_result_headers)


if __name__ == "__main__":
    main(sys.argv)
