from bs4 import BeautifulSoup
from bs4.element import Tag
from ..util import Player, get_url


def get_nfl_data():
    url = "http://www.rotowire.com/daily/nfl/optimizer.php?site=FanDuel&sport=NFL"
    return [
        Player(p.id, p.name, p.position, p.team_code, p.salary, p.fp)
        for p in process_url(url)
    ]


def get_nba_data():
    url = "http://www.rotowire.com/daily/nba/optimizer.php?site=FanDuel&sport=NBA"
    return process_url(url)


def process_url(url):
    response = get_url(url)
    players = []
    soup = BeautifulSoup(response.read(), 'html.parser')

    for tbody in [t for t in soup.find_all("tbody", id="players") if type(t) == Tag]:
        for row in [r for r in tbody.contents if type(r) == Tag]:
            try:
                id = row.attrs["data-playerid"]
                pos = row.attrs["data-pos"]
                name = row.find("a", class_="dplayer-link").text
                s = int(row.find("td", class_="rwo-salary").attrs["data-salary"].replace(',', ''))
                fp = float(row.find("td", class_="rwo-points").attrs["data-points"])
                team = row.find("td", class_="rwo-team").attrs["data-team"]

                players.append(Player(pos + id, name, pos, team, s, fp))

            except KeyError:
                pass

    return players
