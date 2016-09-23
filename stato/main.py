import argparse
from util import *
from match import match_player_ids, avg_team
from optimise import optimise, NFL_CONFIG
from download import projection_sources


def optimize_team(args):
    fd_players = load_obj("fd_players")
    if args.xp:
        fd_players = filter(lambda p: p.id not in args.xp, fd_players)

    exclude_sources = args.xs or []

    matched_players = [(title, match_player_ids(fd_players, load_obj(source)))
                       for title, source, _ in projection_sources
                       if source not in exclude_sources]

    config = NFL_CONFIG

    for title, src_players, in matched_players:
        score, team = optimise(src_players, config, force_players=args.fp)
        print_team(title, team, score)

    avg = avg_team(fd_players, [team for _, team in matched_players])
    score, team = optimise(avg, config, force_players=args.fp)
    print_team('Averaged', team, score)


def list_sources():
    print '\nAvailable projection sources;'
    for title, source, _ in projection_sources:
        print '{}: {}'.format(title, source)


def list_player(args):
    fd_players = load_obj("fd_players")
    players = match_player_ids(fd_players, load_obj(args.p))
    print '\nPlayer projections from {}'.format(args.p)
    print_player_list(players)


def list_pos(args):
    fd_players = load_obj("fd_players")
    matched_players = [(title, match_player_ids(fd_players, load_obj(source)))
                       for title, source, _ in projection_sources]

    for title, team, in matched_players:
        print '\n{}'.format(title)
        print_all_in_pos(team, args.pos)

    avg = avg_team(fd_players, [team for _, team in matched_players])
    print '\nAveraged'
    print_all_in_pos(avg, args.pos)


def main():
    parser = argparse.ArgumentParser(description="NFL Team Optimiser")
    parser.add_argument('-ls', default=False, action='store_true',
                        help='List available sources')
    parser.add_argument('-p', metavar='src', help='List players for a source')
    parser.add_argument('-pos', metavar='pos', help='List players in a position')
    parser.add_argument('-xp', metavar='pid', nargs='+', help='Exclude players from optimisations')
    parser.add_argument('-xs', metavar='src', nargs='+', help='Exclude projection source from optimisations')
    parser.add_argument('-fp', metavar='pid', nargs='+', help='Force specific player for optimisations')

    args = parser.parse_args()

    if args.ls:
        list_sources()
    elif args.p:
        list_player(args)
    elif args.pos:
        list_pos(args)
    else:
        optimize_team(args)

if __name__ == "__main__":
    main()
