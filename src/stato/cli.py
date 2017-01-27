#! /usr/bin/env python
import click
import os
from importlib import import_module
import shutil

from tabulate import tabulate


from .optimise import optimise_team
from .util import print_team, print_player_list, Player, warn, echo, set_config, \
    team_code_translations, average_projections
from .db import do_updates
from .data import (
    create_slate, get_slate_players_projections, create_slate_projections,
    list_slates, list_sources
)
from .scrapers.fanduel import parse_players_csv


@click.group()
def main():
    home = os.path.expanduser('~')
    if not os.path.exists(os.path.join(home, '.stato')):
        os.mkdir(os.path.join(home, '.stato'))
        os.mkdir(os.path.join(home, '.stato', 'db'))
        os.mkdir(os.path.join(home, '.stato', 'cache'))

    if not os.path.exists(os.path.join(home, '.stato', 'translations.cfg')):
        shutil.copy2(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config', 'translations.cfg'),
            os.path.join(home, '.stato', 'translations.cfg')
        )

    do_updates()


@main.command()
@click.argument('sport')
def list(sport):
    for slate in list_slates(sport):
        echo(slate)


@main.command()
@click.argument('sport')
@click.argument('name')
@click.argument('filename')
@click.pass_context
def add(ctx, sport, name, filename):
    players = parse_players_csv(filename)
    create_slate(sport, name, players)
    create_slate_projections(sport, name, 'FanDuel', players)

    report = {}
    for p in players:
        report.setdefault(str(p.team_code), []).append(p)

    echo(
        tabulate([[k, len(p)] for k, p in report.iteritems()],headers=['Team', 'Num Players'])
    )

    ctx.invoke(update, sport=sport, name=name)
    ctx.invoke(optimise, sport=sport, name=name)


@main.command()
@click.argument('sport')
@click.argument('name')
@click.option("--source", "-s", "src", help="Filter by source")
@click.option("--position", "-p", "pos", help="Filter by position")
@click.option("--team", "-t", "team_code", help="Filter by team code")
@click.option("-fp", "fp", type=click.FLOAT, help="Filter by minimum Fantasy Points")
@click.option("-fppk", "fppk", type=click.FLOAT, help="Filter by minimum Fantasy Points Per $1000")
def view(sport, name, src, pos, team_code, fp, fppk):
    projections = get_slate_players_projections(sport, name)

    for source, players in projections.iteritems():

        if src and src != source:
            continue

        echo('')
        echo(source)

        if pos:
            players = filter(lambda p: p.position == pos, players)

        if team_code:
            players = filter(lambda p: p.team_code == team_code, players)

        if fp:
            players = filter(lambda p: p.fp >= fp, players)

        if fppk:
            players = filter(lambda p: (float(p.fp)/(int(p.salary)/1000)) >= fppk, players)

        print_player_list(players)


@main.command()
@click.argument('sport')
@click.argument('name')
@click.option("--exclude_source", "-xs", help="Exclude a projection source", multiple=True)
@click.option("--exclude_player", "-xp", help="Exclude a player", multiple=True)
@click.option("--force_player", "-fp", help="Force a player", multiple=True)
@click.option("--noise", "-n", type=click.INT, default=0, help="% weighting spread on projections")
def optimise(sport, name, exclude_source, exclude_player, force_player, noise):
    projections = get_slate_players_projections(sport, name)

    for source in exclude_source:
        if source in projections.keys():
            projections.pop(source)
        else:
            warn('Source "{}" not found in projections'.format(source))

    player_projections = {}

    for source, players in projections.iteritems():
        for p in players:
            player_projections.setdefault(str(p.id), []).append(p)

    for player_id in exclude_player:
        if player_id in player_projections.keys():
            player_projections.pop(player_id)
        else:
            warn('Player {} not found in projections'.format(player_id))

    force_players = []
    for player_id in force_player:
        if player_id in player_projections.keys():
            force_players.append(player_id)
        else:
            warn('Player {} not found in projections'.format(player_id))

    avg = average_projections(player_projections, noise)
    score, team = optimise_team(avg, sport, force_players=force_players)
    print_team('Optimised Team', team, score)


@main.command()
@click.argument('sport')
@click.argument('name')
@click.option("--source", "-s", "source_filter", help="Update a specific source", multiple=True)
@click.option("--exclude_source", "-xs", help="Ignore a source while updating", multiple=True)
@click.option("--use_cache", "-c", help="Use cached http responses", is_flag=True)
def update(sport, name, source_filter, exclude_source, use_cache):
    set_config(use_cache)

    team_mappings = team_code_translations(sport.lower())

    for source in list_sources(sport):
        source_name = source[1]
        package = source[3]
        module = source[4]
        method = source[5]

        if source_name == 'FanDuel' or source_name in exclude_source:
            continue

        if len(source_filter) > 0 and source_name not in source_filter:
            continue

        echo("Processing {} projections from {}".format(sport, source_name), bold=True)
        scraper_module = import_module("{}.{}".format(package, module))
        scraper_method = getattr(scraper_module, method)

        # call scraper method and fix team_codes on returned players
        players = [
            Player(
                p.id,
                p.name,
                p.position,
                (p.team_code if p.team_code not in team_mappings else team_mappings[p.team_code]),
                p.salary,
                p.fp,
            )
            for p in scraper_method()
        ]

        matched = create_slate_projections(sport, name, source_name, players)
        echo("Matched {}/{} players".format(matched, len(players)))
        echo("")


@main.command()
@click.argument('sport')
@click.argument('name')
@click.option("--iterations", "-i", default=10, help="Number of optimisations to run")
@click.option("--exclude_source", "-xs", help="Exclude a projection source", multiple=True)
@click.option("--exclude_player", "-xp", help="Exclude a player", multiple=True)
@click.option("--noise", "-n", type=click.INT, default=5, help="% weighting spread on projections")
def noise_test(sport, name, iterations, exclude_source, exclude_player, noise):
    projections = get_slate_players_projections(sport, name)

    for source in exclude_source:
        if source in projections.keys():
            projections.pop(source)
        else:
            warn('Source "{}" not found in projections'.format(source))

    player_projections = {}

    for source, players in projections.iteritems():
        for p in players:
            player_projections.setdefault(str(p.id), []).append(p)

    for player_id in exclude_player:
        if player_id in player_projections.keys():
            player_projections.pop(player_id)
        else:
            warn('Player {} not found in projections'.format(player_id))

    positions = {}
    for i in range(0, iterations):
        avg = average_projections(player_projections, noise)
        score, team = optimise_team(avg, sport)

        for p in team:
            positions.setdefault(p.position, {}).setdefault(p.id, []).append(p)

    echo("Ran {} iterations with {}% noise".format(iterations, noise), bold=True)
    for pos in sorted(positions.keys()):
        players = positions[pos]

        echo("")
        echo("Position: {}".format(pos), bold=True)

        chosen = []
        for id, p in players.iteritems():
            chosen.append((p[0].id, p[0].name, p[0].salary, len(p)))

        table = tabulate(
            sorted(chosen, cmp=lambda x, y: cmp(y[3], x[3])),
            headers=['ID', 'Player', 'Salary', '# Picks']
        )
        echo(table)


if __name__ == "__main__":
    main(obj={})
