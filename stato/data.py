from bs4 import BeautifulSoup
from bs4.element import Tag
import urllib2
import csv
import re
import json
import random

from util import *

from download import get_nf_data, get_rw_data, get_rg_data, get_daily_fantasy_cafe_data, get_random

projection_sources = [
    ("NumberFire", "nf_data", get_nf_data),
    ("RotoGrinders", "rg_data", get_rg_data),
    ("RotoWire", "rw_data", get_rw_data),
    ("DFCafe", "dfc_data", get_daily_fantasy_cafe_data),
    ("Random", "rnd_data", get_random),
]

_SOURCE_DATA = {}


def list_sources():
    return [p[0] for p in projection_sources]


def load_projections(csv_path):
    _SOURCE_DATA = {}

    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            source = row['Source']
            id = row['ID']
            name = row['Name']
            pos = row['Position']
            team = row['Team']
            salary = row['Salary']
            fd_points = row['fp']

            if source not in _SOURCE_DATA:
                _SOURCE_DATA[source] = []

            _SOURCE_DATA[source].append(Player(id, name, pos, team, salary, fd_points))


def get_projections(source):
    return _SOURCE_DATA[source]
