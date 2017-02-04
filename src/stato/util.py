from collections import namedtuple
from tabulate import tabulate
import click
import ConfigParser
import re
import threading
import random
import math

import urllib2
import os
import hashlib


SportConfig = namedtuple('SportConfig', "salary_cap max_players formation team_limit")
Player = namedtuple("Player", "id name position team_code salary fp")

ConfigDef = namedtuple("ConfigDef", "use_cache")


def set_config(use_cache):
    global config
    config = ConfigDef(use_cache)


set_config(use_cache=False)


def print_player_list(player_list, fppd=True):
    if fppd:
        data = [[p.position, p.id, p.name, p.team_code, p.salary, p.fp, (float(p.fp)/(int(p.salary)/1000))]
                for p in player_list]
        headers = ['Pos', 'ID', 'Name', 'Team', 'Salary', 'FP', 'FP/$k']
    else:
        data = [[p.position, p.id, p.name, p.team_code, p.salary, p.fp] for p in player_list]
        headers = ['Pos', 'ID', 'Name', 'Team', 'Salary', 'FP']

    table = tabulate(
        sorted(data, cmp=lambda x, y: cmp(str(x[0])+str(x[1]),
                                          str(y[0])+str(y[1]))),
        headers=headers
    )
    echo(table)


def print_team(title, team, score):
    echo("")
    echo(title)
    print_player_list(sorted(team, key=lambda player: player.position+player.name))
    echo("Team Score: " + str(score))
    echo("Team Salary: " + str(sum([int(p.salary) for p in team])))


def print_all_in_pos(player_list, pos, fppd=True):
    print_player_list(sorted([p for p in player_list if p.position == pos and p.fp > 0]), fppd)


def get_url(url, headers=None):
    pattern = re.compile('[\W_]+', re.UNICODE)
    file = os.path.join(os.path.expanduser('~'), '.stato', 'cache', pattern.sub('_', url))

    if not config.use_cache or not os.path.exists(file):

        request = urllib2.Request(url)
        if headers:
            for name, value in headers:
                request.add_header(name, value)

        response = urllib2.urlopen(request)
        with open(file, "w") as f:
            f.write(response.read())
    else:
        warn("Using cached http response for {}".format(url))

    return open(file, "r")


def process_urls(urls, parser):
    players = []
    process_threads = []
    for url in urls:
        process_threads.append(threading.Thread(
            target=lambda url, parse, players: players.extend(parser(get_url(url))),
            args=(url, parser, players))
        )

    for t in process_threads:
        t.start()
    for t in process_threads:
        t.join()

    return players


def warn(warnings):
    for warning in (warnings if type(warnings) == list else [warnings]):
        click.secho("WARNING: {}".format(warning), fg='red', bold=True)


def echo(msgs, **kwargs):
    for msg in (msgs if type(msgs) == list else [msgs]):
        click.secho(msg, **kwargs)


def map_nfl_team_code(team_code):
    mappings = {
        "GBP": "GB",
        "KCC": "KC",
        "SFO": "SF",
        "SDC": "SD",
        "TBB": "TB",
        "NEP": "NE",
        "NOS": "NO",
        "JAX": "JAC",
        "LAR": "LA",
        "WSH": "WAS"
    }
    return team_code if team_code not in mappings else mappings[team_code]


def team_code_translations(sport):
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read(os.path.expanduser('~/.stato/translations.cfg'))

    try:
        return dict(config.items("{}-team-code".format(sport.lower())))
    except:
        return {}


def average_projections(player_projections, noise=1.0):
    avg = []
    for _, projections in player_projections.iteritems():
        n = 1 + (((random.random() * noise) - (noise/2.0)) / 100)
        fp = round(math.fsum([p.fp for p in projections]) / len(projections), 2) * n
        p = projections[0]
        avg.append(Player(p.id, p.name, p.position, p.team_code, p.salary, fp))

    return avg
