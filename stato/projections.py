import sys

from stato.download import projection_sources
from stato.optimise import optimise
from stato.match import match_player_ids, avg_team
from stato.util import *


def main(args):
    fd_players = load_obj("fd_players")

    matched_players = [(title, match_player_ids(fd_players, load_obj(source)))
                       for title, source, _ in projection_sources]

    for title, team, in matched_players:
        score, team = optimise(team)
        print_team(title, team, score)

    score, team = optimise(avg_team(fd_players, [team for _, team in matched_players]))
    print_team("AVG", team, score)


if __name__ == "__main__":
    main(sys.argv)
