from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib2
import requests
import csv
import re
import json
from fake_useragent import UserAgent

from stato.util import *


def get_rw_data(data_file):
    url = "http://www.rotowire.com/daily/nfl/optimizer.php?site=FanDuel&sport=NFL"

    response = urllib2.urlopen(url)
    players = []
    soup = BeautifulSoup(response.read(), 'html.parser')

    for tbody in [t for t in soup.find_all("tbody", id="players") if type(t) == Tag]:
        for row in [r for r in tbody.contents if type(r) == Tag]:
            try:
                id = row.attrs["data-playerid"]
                pos = row.attrs["data-pos"]
                name = row.find("a", class_="dplayer-link").text
                s = int(row.find("td", class_="rwo-salary").attrs["data-salary"].replace(',' , ''))
                fp = float(row.find("td", class_="rwo-points").attrs["data-points"])
                team = row.find("td", class_="rwo-team").attrs["data-team"]

                players.append(Player(pos + id, name, pos, team, s, fp))

            except KeyError:
                pass

    save_obj(list(set(players)), data_file)


def get_rg_data(data_file):
    urls = [
            ('QB', 'https://rotogrinders.com/projected-stats/nfl-qb.csv?site=fanduel'),
            ('RB', 'https://rotogrinders.com/projected-stats/nfl-rb.csv?site=fanduel'),
            ('WR', 'https://rotogrinders.com/projected-stats/nfl-wr.csv?site=fanduel'),
            ('TE', 'https://rotogrinders.com/projected-stats/nfl-te.csv?site=fanduel'),
            ('K', 'https://rotogrinders.com/projected-stats/nfl-kicker.csv?site=fanduel'),
            ('D', 'https://rotogrinders.com/projected-stats/nfl-defense.csv?site=fanduel'),
    ]

    players = []

    for type, url in urls:
        response = urllib2.urlopen(url)
        reader = csv.reader(response)
        index = 1
        for row in skip_last(reader):
            players.append(
                Player(type + str(index), row[0], type, row[2], int(row[1]), float(row[7])))
            index += 1

    save_obj(list(set(players)), data_file)


def get_nf_data(data_file):
    urls = [
        ('qb', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/qb'),
        ('rb', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/rb'),
        ('wr', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/wr'),
        ('te', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/te'),
        ('k', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/k'),
        ('d', 'https://www.numberfire.com/nfl/fantasy/fantasy-football-projections/d'),
    ]

    players = []

    for pos, url in urls:
        response = urllib2.urlopen(url)
        soup = BeautifulSoup(response.read(), 'html.parser')

        players_dict = {}
        for table in soup.find_all("table", class_="projection-table"):
            for row in [r for r in table.tbody.contents if type(r) == Tag]:

                indx = row.attrs["data-row-index"]
                if indx not in players_dict:
                    players_dict[indx] = {}

                player = row.find("td", class_="player")
                if player:
                    players_dict[indx]["name"] = player.a.find("span", class_="full").text
                    players_dict[indx]["pos"] = player.contents[2].strip()[1:-1].split(",")[0]
                    players_dict[indx]["team"] = player.contents[2].strip()[1:-1].split(",")[1]

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
            Player(pos + k, v.get("name"), v.get("pos"), v.get("team"), v.get("cost"), v.get("fp"))
            for k, v in players_dict.iteritems() if v.get('cost') != 'N/A']
        )

    save_obj(list(set(players)), data_file)


def get_daily_fantasy_cafe_data(data_file):
    url = 'https://www.dailyfantasycafe.com/tools/lineupoptimizer/nfl'
    response = urllib2.urlopen(url)
    players = []
    soup = BeautifulSoup(response.read(), 'html.parser')
    print soup
    vars = soup.find_all("script")[1].string
    p = re.compile('players\s=\s(.*);')
    m = p.findall(vars)
    v = json.loads(m[0])
    print v
    print
    for p in v:
        try:
            player_id = p['id']
            name = p['name']['fanduel']
            pos = p['position']['fanduel']
            fp = p['projections']['fanduel_gpp']
            team = p['team']
            salary = p['salaries']['fanduel']
            print name, pos, fp, team, salary
            players.append(Player(pos + str(player_id), name, pos, team, salary, fp))
        except KeyError:
            print '** ', p
    save_obj(list(set(players)), data_file)


def get_player_data(data_file):
    urls = [
        ('qb', 'http://www.footballdb.com/players/current.html?pos=QB'),
        ('rb', 'http://www.footballdb.com/players/current.html?pos=RB'),
        ('wr', 'http://www.footballdb.com/players/current.html?pos=WR'),
        ('te', 'http://www.footballdb.com/players/current.html?pos=TE'),
        ('k', 'http://www.footballdb.com/players/current.html?pos=K'),
    ]

    players = []

    for pos, url in urls:
        headers = {'User-Agent': UserAgent().random}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        i = 0
        for table in soup.find_all("table", class_="statistics"):
            for row in [r for r in table.tbody.contents if type(r) == Tag]:

                name = row.contents[0].a.text.split(",")
                name = name[1].strip() + ' ' + name[0].strip()
                pos = row.contents[1].text
                team = row.contents[2].a.text

                players.append(Player(pos + str(i), name, pos, team, None, None))

    save_obj(list(set(players)), data_file)


projection_sources = [
    ("NumberFire", "nf_data", get_nf_data),
    ("RotoGrinders", "rg_data", get_rg_data),
    ("RotoWire", "rw_data", get_rw_data),
    ("DFCafe", "dfc_data", get_daily_fantasy_cafe_data),
]


def get_game_data_from_fd_csv(input_file, data_file):
    players = []
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row['First Name'] + ' ' + row['Last Name']
            pos = row['Position']
            team = row['Team']
            player_id = row["Id"].split('-')[1]
            salary = row['Salary']
            fd_points = row['FPPG']
            players.append(Player(player_id, name, pos, team, salary, fd_points))

    save_obj(list(set(players)), data_file)


def get_data():

    if load_obj("fd_players"):
        print "Team players already exists"
    else:
        print "Processing team players"
        fd_filename = '/Users/kristianwoodsend/Downloads/FanDuel-NFL-2016-09-18-16345-players-list.csv'
        get_game_data_from_fd_csv(fd_filename, "fd_players")


    for title, data_file, func in projection_sources:
        if load_obj(data_file):
            print "{} already exists".format(title)
        else:
            print "Processing {}".format(title)
            func(data_file)

get_data()
