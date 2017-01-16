import pulp
from .util import SportConfig


def get_config(sport):
    if sport == 'NFL':
        return SportConfig(
            salary_cap=60000.0,
            max_players=9,
            formation=[
                {'pos': 'QB', 'n': 1},
                {'pos': 'RB', 'n': 2},
                {'pos': 'WR', 'n': 3},
                {'pos': 'TE', 'n': 1},
                {'pos': 'K',  'n': 1},
                {'pos': 'D',  'n': 1},
            ],
            team_limit=4
        )
    elif sport == 'NBA':
        return SportConfig(
            salary_cap=60000.0,
            max_players=9,
            formation=[
                {'pos': 'PG', 'n': 2},
                {'pos': 'SG', 'n': 2},
                {'pos': 'SF', 'n': 2},
                {'pos': 'PF', 'n': 2},
                {'pos': 'C', 'n': 1},
            ],
            team_limit=4
        )
    else:
        raise Exception()


def optimise_team(player_list, sport, force_players=None, stack_teams=None):
    config = get_config(sport)
    player_list = [p for p in player_list if p.salary > 0]

    var_list = [pulp.LpVariable('P' + str(p.id), cat='Binary') for p in player_list]
    d_players = dict((v.name, p) for (v, p) in zip(var_list, player_list))

    prob = pulp.LpProblem("Highest scoring team", pulp.LpMaximize)

    force_players = force_players or []
    for v in var_list:
        if v.name[1:] in force_players:
            prob += v == 1

    # add constraints to problem
    # number of players in team -- needed to handle variable formations
    prob += pulp.lpSum([v for v in var_list]) == config.max_players

    # total salary cap
    salaries = [p.salary for p in player_list]
    prob += pulp.lpDot(var_list, salaries) <= config.salary_cap

    # limit the number in each player position
    for position in config.formation:
        prob += pulp.lpSum([v for v in var_list
                            if d_players[v.name].position == position['pos']]) == position['n']

    # max of 4 players from each team
    teams = set([p.team_code for p in player_list])
    for team in teams:
        prob += pulp.lpSum([v for v in var_list if d_players[v.name].team_code == team]) \
            <= config.team_limit

    # stack teams
    stack_teams = stack_teams or []
    for team_code, min_players in stack_teams:
        prob += pulp.lpSum([v for v in var_list if d_players[v.name].team_code == team_code]) \
            >= min_players

    # objective: maximise the total final score
    scores = [p.fp for p in player_list]
    prob += pulp.lpDot(var_list, scores)

    # solve the optimisation problem
    pulp.PULP_CBC_CMD().solve(prob)

    team = []

    for v in prob.variables():
        if v.varValue == 1:
            team.append([p for p in player_list if str(p.id) == v.name[1:]][0])

    return pulp.value(prob.objective), team
