import json
import re

from bs4 import BeautifulSoup
from ..util import Player, get_url


def get_nfl_data():
    return process_url('https://www.dailyfantasycafe.com/tools/lineupoptimizer/nfl')


def get_nba_data():
    return process_url('https://www.dailyfantasycafe.com/tools/lineupoptimizer/nba')


def get_mlb_data():
    return process_url('https://www.dailyfantasycafe.com/tools/lineupoptimizer/mlb')


def process_url(url):
    response = get_url(url)
    players = []
    soup = BeautifulSoup(response.read(), 'html.parser')

    # find script block with player data
    p = re.compile('players\s=\s(.*);')
    for script in soup.find_all("script"):
        m = p.findall(script.string or '')
        if m:
            break

    v = json.loads(m[0])
    for p in v:
        try:
            player_id = p['id']
            name = p["full_name"] if type(p["name"]) is list else p['name']['fanduel']
            pos = p['position']['fanduel']
            fp = float(p['projections']['fanduel_gpp'])
            team = p['team']
            salary = p['salaries']['fanduel']

            if fp > 4:
                players.append(Player(pos + str(player_id), name, pos, team, salary, fp))
        except KeyError:
            pass

    return players
