from stato.download import get_data, projections
from stato.optimise import optimise
from stato.util import *

from fuzzywuzzy import process

get_data()

main = load_obj("players")

nf_data = load_obj("nf_data")


for pos in POSITIONS:
    m = [p.name for p in main if p.position == pos]
    nf = [p for p in nf_data if p.position == pos and p.name not in m]

    print "{pos}: {num}".format(pos=pos, num=len(nf))
    for p in nf:
        match = process.extract(p.name, m, limit=1)
        if len(match) == 1:
            match, score = match[0]
            if score >= 80:
                print "{} = {} ({})".format(p.name, match, score)
            else:
                print "NO MATCH FOR {}".format(p.name)
        else:
            print "NO MATCH FOR {}".format(p.name)

    # print [str(p.name) for p in nf]

#
# for title, data, _ in projections:
#     score, team = optimise(load_obj(data))
#     print_team(title, team, score)
#

