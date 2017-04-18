import csv
import gzip
import json
import re

from ..util import Player, get_url, team_code_translations


def parse_players_csv(input_file):
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

    return players


def parse_final_scores_csv(input_file):
    players = []
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row['first_name'] + ' ' + row['last_name']
            pos = row['position']
            team = row['team_code']
            player_id = row["player_id"]
            salary = row['salary']
            fd_points = row['final_score']
            players.append(Player(player_id, name, pos, team, salary, fd_points))

    return players


def scrape_uk_soc_players(url):
    p = re.compile(r'/fixtures/(\d*?)/')
    fixture_id = p.findall(url)[0]

    fixture_response = get_url(
        "https://api.fanduel.co.uk/fixture-lists/{}/players".format(fixture_id),
        headers=[(
            "Authorization", "Basic {}".format(get_uk_client_id())
        )]
    ).read()

    fixture_json = json.loads(fixture_response)

    def get_team(id):
        for t in fixture_json["teams"]:
            if t["id"] == id:
                return t["code"]
        return "UNKNOWN"

    team_mappings = team_code_translations("soc")
    players = []
    for p in fixture_json["players"]:
        id = p["id"]
        name = u"{} {}".format(p["first_name"], p["last_name"])
        salary = int(p["salary"])
        fppg = 0 if p["fppg"] is None else float(p["fppg"])
        position = p["position"]
        team_code = get_team(p["team"]["_members"][0])
        players.append(Player(
            id,
            name,
            position,
            (team_code if team_code not in team_mappings else team_mappings[team_code]),
            salary,
            fppg,
        ))

    return players


def get_uk_client_id():
    """
    This ugly ass piece of code will find the client_id to use for api auth by doing the following;
    * download the html from the contests page
    * look for the name of main_{version}.js
    * download main_{version}.js
    * find the client_id
    :return: client_id to use as auth for api calls.
    """

    # get edit entry page
    contests_url = "https://fanduel.co.uk/contests"
    source = gzip.GzipFile(fileobj=get_url(contests_url)).read()

    # look for main.js
    p = re.compile('FanDuelLoader.loadApp\((.*)\);')
    app = p.findall(source)[0]
    for c in '"[]':
        app = app.replace(c, '')
    paths = app.split(",")

    main_js_file_name = paths[-1] + filter(lambda s: 'main' in s, paths[:-1])[0]

    # download main.js
    main_source = gzip.GzipFile(fileobj=get_url("https://fanduel.co.uk"+main_js_file_name)).read()

    # look for client id to use for auth
    p = re.compile('clientId:"(.*?)"')
    return p.findall(main_source)[0]
