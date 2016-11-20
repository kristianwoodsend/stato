#! /usr/bin/env python
import click
from stato.download import load_obj, projection_sources
from stato.match import match_player_ids, avg_team
from stato.optimise import optimise
from stato.util import print_team
from stato.db import do_updates


@click.group()
def cli():
    do_updates()


##################################################
# DATA
@cli.group()
def data():
    pass


@data.command()
def list():
    pass


@data.command()
def scrape():
    pass


@data.command()
@click.argument('filename')
def archive(filename):
    pass


def exclude_player(*args, **kwargs):
    pass
    # print args
    # print kwargs


##################################################
# PROJECTIONS
@cli.command()
@click.option("--src", "-s", "src", help="CSV containing projections")
@click.option("--res", "-r", "res", help="CSV game results")
@click.option("--exclude_source", "-xs", "xs", help="Exclude a data source from projections", multiple="True")
@click.option("--exclude_player", "-xp", "xp", help="Exclude a player from projections", multiple="True")
@click.option("--force_player", "-fp", "fp", help="Force a player into projectioned team", multiple="True")
@click.option("--random", "-r", "r", help="Modify player scores by a random amount", default=None)
def projections(src, res, xs, xp, fp, r):
    fd_players = load_obj("fd_players")
    if xp:
        fd_players = filter(lambda p: p.id not in xp, fd_players)

    exclude_sources = xs or []

    print fd_players

    matched_players = [(title, match_player_ids(fd_players, load_obj(source)))
                       for title, source, _ in projection_sources
                       if source not in exclude_sources]

    # for title, src_players, in matched_players:
    #     score, team = optimise(src_players, force_players=args.fp, stack_teams=args.stack)
    #     print_team(title, team, score)

    avg = avg_team(fd_players, [team for _, team in matched_players])
    score, team = optimise(avg, force_players=fp, stack_teams=None)
    print_team('Averaged', team, score)

if __name__ == "__main__":
    cli(obj={})
