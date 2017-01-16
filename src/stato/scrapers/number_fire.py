from bs4 import BeautifulSoup
from bs4.element import Tag
import string

from ..util import Player, process_urls


# ARI, ATL, BAL, BUF, CHI, CIN, CLE, DAL
# DEN, DET, GB, HOU, IND, JAC, KC, MIN
# NE, NO, NYG, OAK, PHI, PIT, SD, SF, TB
# TEN

def get_nfl_data():
    players = process_urls([
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/qb',
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/rb',
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/wr',
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/te',
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/k',
        'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/d',
    ], parse_nfl)

    def fix_name(name):
        return name[:-5] if name.endswith("D/ST") else name

    return [
        Player(p.id, fix_name(p.name), p.position, p.team_code, p.salary, p.fp)
        for p in players
    ]


def get_nba_data():
    return process_urls([
        'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections/pg',
        'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections/sg',
        'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections/sf',
        'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections/pf',
        'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections/c',
    ], parse_nba)


def parse_nfl(http_response):
    html = BeautifulSoup(http_response.read(), 'html.parser')
    players = []

    players_dict = {}
    for table in html.find_all("table", class_="projection-table"):
        for row in [r for r in table.tbody.contents if type(r) == Tag]:

            indx = row.attrs["data-row-index"]
            if indx not in players_dict:
                players_dict[indx] = {}

            player = row.find("td", class_="player")
            if player:
                name = player.a.find("span", class_="full").text
                pos = player.contents[2].strip()[1:-1].split(",")[0]
                team = player.contents[2].strip()[1:-1].split(",")[1]

                players_dict[indx]["name"] = name
                players_dict[indx]["pos"] = pos
                players_dict[indx]["team"] = team.strip()

            cost = row.find("td", class_="fanduel_cost")
            if cost:
                cost = cost.text.strip()
                if cost != "N/A":
                    cost = int(cost[1:])
                players_dict[indx]["cost"] = cost

            fp = row.find("td", class_="fanduel_fp")
            if fp:
                players_dict[indx]["fp"] = float(fp.text.strip())

    players.extend([
        Player(k, v.get("name"), v.get("pos"), v.get("team"), v.get("cost"), v.get("fp"))
        for k, v in players_dict.iteritems() if v.get('cost') != 'N/A'
    ])

    return players


def parse_nba(http_response):
    html = BeautifulSoup(http_response.read(), 'html.parser')
    players = []

    players_dict = {}
    for table in html.find_all("table", class_="projection-table"):
        for row in [r for r in table.tbody.contents if type(r) == Tag]:

            indx = row.attrs["data-row-index"]
            if indx not in players_dict:
                players_dict[indx] = {}

            player = row.find("span", class_="player-info")
            if player:
                name = player.find("a", class_="full").text
                pos = player.find("span", class_="player-info--position").text
                team = player.find("span", class_="team-player__team active").text

                players_dict[indx]["name"] = name.strip()
                players_dict[indx]["pos"] = pos
                players_dict[indx]["team"] = team.strip()

            cost = row.find("td", class_="cost")
            if cost:
                cost = ''.join([s for s in cost.text if s in string.digits])
                if cost != "N/A":
                    cost = int(cost)
                players_dict[indx]["cost"] = cost

            fp = row.find("td", class_="fp")
            if fp:
                players_dict[indx]["fp"] = float(fp.text.strip())

    players.extend([
        Player(k, v.get("name"), v.get("pos"), v.get("team"), v.get("cost"), v.get("fp"))
        for k, v in players_dict.iteritems() if v.get('cost') != 'N/A']
    )

    return players
