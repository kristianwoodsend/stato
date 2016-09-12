import pulp
from collections import namedtuple


def optimise(player_list):

    # Find the highest scoring team for a given game_id and list of players
    # game_id, player_list = game_row

    player_list = [p for p in player_list if p.salary > 0]

    SportConfig = namedtuple('SportConfig', "salary_cap max_players formation team_limit")

    config = SportConfig(salary_cap=60000.0,
                         max_players=9,
                         formation=[
                             {'pos': 'QB', 'n': 1},
                             {'pos': 'RB', 'n': 2},
                             {'pos': 'WR', 'n': 3},
                             {'pos': 'TE', 'n': 1},
                             {'pos': 'K',  'n': 1},
                             {'pos': 'D',  'n': 1},
                         ],
                         team_limit=4)

    var_list = [pulp.LpVariable('P' + p.id, cat='Binary') for p in player_list]
    d_players = dict((v.name, p) for (v, p) in zip(var_list, player_list))

    prob = pulp.LpProblem("Highest scoring team", pulp.LpMaximize)

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

    # objective: maximise the total final score
    scores = [p.fp for p in player_list]
    prob += pulp.lpDot(var_list, scores)

    # solve the optimisation problem
    # the precompiled cbc solver file needs to be supplied by spark-submit
    # cbc_path = pyspark.SparkFiles.get('cbc')
    # solver = pulp.solvers.COIN_CMD(path=cbc_path)

    pulp.PULP_CBC_CMD().solve(prob)

    team = []

    for v in prob.variables():
        if v.varValue == 1:
            team.append([p for p in player_list if str(p.id) == v.name[1:]][0])

    return pulp.value(prob.objective), team
