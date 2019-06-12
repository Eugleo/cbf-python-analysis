import json
import re
import os
from requests_html import HTML
from stats import player_id, int_or_default
from file_management import write_dicts_to_file
from functools import reduce


def parse_all_shots(path):
    shots = []
    index = 0
    for dirpath, _, names in os.walk(path):
        for name in filter( lambda n: 'json' in n, names):
            index += 1
            with open(os.path.join(dirpath, name)) as f:
                match_dicts = json.load(f)
                shots.extend(concat_map(parse_shots_from_match, match_dicts))
                print("Parsed file No. " + str(index))
    nonempty = list(filter( lambda d: d != {}, shots))
    write_dicts_to_file(nonempty, os.path.join(path, 'shots.csv'))


def concat_map(f, l):
    lol = map(f, l)
    return list(reduce( lambda x, y: x + y, lol))


def parse_shots_from_match(match):
    shots = match['shots']
    match_id = match['ids']['match']
    comp_id = match['ids']['competition']
    result = []
    players_per_match = {}
    if shots is not None and match_id is not None and comp_id is not None:
        key = comp_id + match_id
        if key not in players_per_match:
            players = parse_players('data/players/' + key + '.json')
            players_per_match[key] = players
        else:
            players = players_per_match[key]
        quarter_re = re.compile(r'\d+')
        for q, v in shots['teamA'].items():
            for s in v:
                quarter = re.search(quarter_re, q)
                result.append(shot(s, quarter[0], players['teamA'], match_id))
        for q, v in shots['teamB'].items():
            for s in v:
                quarter = re.search(quarter_re, q)
                result.append(shot(s, quarter[0], players['teamB'], match_id))
    return result


def shot(s, quarter, players, match_id):
    player_no = int(s['player_no'])
    return {
        'match_id': match_id,
        'author_id': int(players.get(player_no, -1)),
        'x': int(s['x']),
        'y': int(s['y']),
        'quarter': int(quarter),
        'is_goal': 'True' if s['is_goal'] else 'False',
    }


def parse_players(path):
    with open(path) as f:
        html = HTML(html=f.read())
        table = html.find('table', first=True)
        a_xp = (
            "//tr[count(preceding-sibling::tr[@class='hdr'])=1 and"
            "count(following-sibling::tr[@class='ftr'])=2]"
        )
        team_a_rows = table.xpath(a_xp)
        team_a_players = {}
        for k, v in map(player, team_a_rows):
            team_a_players[k] = v
        b_xp = (
            "//tr[count(preceding-sibling::tr[@class='hdr'])=2 and"
            "count(following-sibling::tr[@class='ftr'])=1]"
        )
        team_b_rows = table.xpath(b_xp)
        team_b_players = {}
        for k, v in map(player, team_b_rows):
            team_b_players[k] = v
        return {'teamA': team_a_players, 'teamB': team_b_players}


def player(row):
    cells = row.find('td')
    number = -1
    if cells[0].find('strong', first=True) is not None:
        number = int_or_default(cells[0].find('strong', first=True).text)
    else:
        number = int_or_default(cells[0].text)
    return (number, player_id(row))
