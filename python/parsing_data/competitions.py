import re
import os
import json
from file_management import write_dicts_to_file


def parse_competitions(path):
    competitions = []
    index = 0
    for dirpath, _, names in os.walk(path):
        for name in filter( lambda n: 'json' in n, names):
            index += 1
            with open(os.path.join(dirpath, name)) as f:
                match_dicts = json.load(f)
                for competition in map(parse_competition, match_dicts):
                    if competition not in competitions:
                        competitions.append(competition)
                print("Parsed file No. " + str(index))
    nonempty = list(filter( lambda d: d != {}, competitions))
    write_dicts_to_file(nonempty, os.path.join(path, 'competitions.csv'))


def parse_competition(match):
    result = {}
    if match['ids']['competition'] is not None:
        comp = match['competition']
        round_re = re.compile(r'\d+')
        year = match['date'][:4]
        gender, u_category = parse_category(comp['category'])
        result = {
            'id': int(match['ids']['competition']),
            'name': comp.get('name', ''),
            'year': int(year),
            'gender': gender,
            'u_category': u_category,
            'phase': comp.get('phase', ''),
            'round': int(re.search(round_re, comp.get('round', -1))[0]),
        }
    return result


def parse_category(category):
    men_re = re.compile(r'(muži|junioři|kadeti|žáci)')
    cat = re.search(men_re, category)
    if cat is not None:
        gender = 'm'
    else:
        gender = 'ž'
    age_re = re.compile(r'U(\d+)')
    age_found = re.search(age_re, category)
    if age_found is not None:
        age = int(age_found[1])
    else:
        age = 100
    return gender, age
