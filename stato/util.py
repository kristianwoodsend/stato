import pickle
from collections import namedtuple
from tabulate import tabulate

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
        print tabulate([[p.position, p.name, p.team_code, p.salary, p.fp, (p.fp/(p.salary/1000))] for p in player_list],
                       headers=['Pos', 'Name', 'Team', 'Salary', 'FP', 'FP/$k'])
    else:
        print tabulate([[p.position, p.name, p.team_code, p.salary, p.fp] for p in player_list],
                       headers=['Pos', 'Name', 'Team', 'Salary', 'FP'])


def print_team(title, team, score):

    sorted(team, key=lambda player: player.position+player.name)

    print ""
    print title
    print print_player_list(sorted(team, key=lambda player: player.position+player.name))
    print "Team Score: " + str(score)
    print "Team Salary: " + str(sum([p.salary for p in team]))


def print_all_in_pos(player_list, pos, fppd=True):
    print_player_list(sorted([p for p in player_list if p.position == pos]), fppd)
