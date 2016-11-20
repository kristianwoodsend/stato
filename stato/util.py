import pickle
from collections import namedtuple
from tabulate import tabulate


from ref_data import TEAM_CODE_MAPPINGS, TEAM_NAME_MAPPINGS

SportConfig = namedtuple('SportConfig', "salary_cap max_players formation team_limit")
Player = namedtuple("Player", "id name position team_code salary fp")
POSITIONS = ['QB', 'WR', 'RB', 'TE', 'K', 'D']


def save_obj(obj, name):
    with open('data/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    try:
        with open('data/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None


def skip_last(iterator):
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item


def print_player_list(player_list, fppd=True):
    if fppd:
        data = [[p.position, p.id, p.name, p.team_code, p.salary, p.fp, (float(p.fp)/(int(p.salary)/1000))]
                for p in player_list]
        headers = ['Pos', 'ID', 'Name', 'Team', 'Salary', 'FP', 'FP/$k']
    else:
        data = [[p.position, p.id, p.name, p.team_code, p.salary, p.fp] for p in player_list]
        headers = ['Pos', 'ID', 'Name', 'Team', 'Salary', 'FP']

    print tabulate(sorted(data, cmp=lambda x, y: cmp(str(x[0])+str(x[len(x)-1]),
                                                     str(y[0])+str(y[len(x)-1]))*-1),
                   headers=headers)


def print_team(title, team, score):
    sorted(team, key=lambda player: player.position+player.name)

    print ""
    print title
    print print_player_list(sorted(team, key=lambda player: player.position+player.name))
    print "Team Score: " + str(score)
    print "Team Salary: " + str(sum([int(p.salary) for p in team]))


def print_all_in_pos(player_list, pos, fppd=True):
    print_player_list(sorted([p for p in player_list if p.position == pos and p.fp > 0]), fppd)


def map_team_code(code):
    code = code.strip()
    if code in TEAM_CODE_MAPPINGS:
        code = TEAM_CODE_MAPPINGS.get(code)
    return code


def map_team_name(code):

    if code == 'GB':
        print 'GB FOUND'
        print TEAM_NAME_MAPPINGS.get(map_team_code(code))
    else:
        print code

    return TEAM_NAME_MAPPINGS.get(map_team_code(code))


def normalise_team(name, team, pos):
    team = str(map_team_code(team))
    if pos == 'D':
        name = map_team_name(team)
    return (name, team)


def float_or_zero(number):
    try:
        return float(number)
    except ValueError:
        return 0.0


def get_player(player_list, id):
    for player in player_list:
        if player.id == id:
            return player
    return None
