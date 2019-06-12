import json
import os
import re
from pathlib import Path
from requests_html import HTML
from file_management import write_dicts_to_file
from stats import scrape_teams


def parse_matches(path):
    matches = []
    index = 0
    for dirpath, _, names in os.walk(path):
        for name in filter( lambda n: 'json' in n, names):
            index += 1
            with open(os.path.join(dirpath, name)) as f:
                match_dicts = json.load(f)
                matches.extend(list(map(parse_match, match_dicts)))
                print("Parsed file No. " + str(index))
    nonempty = list(filter( lambda d: d != {}, matches))
    write_dicts_to_file(nonempty, os.path.join(path, 'matches.csv'))


def flatten_match(match):
    team_a_pts = match['team_a_pts']
    match['team_a_q1_pts'] = team_a_pts[0] if team_a_pts else -1
    match['team_a_q2_pts'] = team_a_pts[1] if len(team_a_pts) > 1 else -1
    match['team_a_q3_pts'] = team_a_pts[2] if len(team_a_pts) > 2 else -1
    match['team_a_q4_pts'] = team_a_pts[3] if len(team_a_pts) > 3 else -1
    match['team_a_q5_pts'] = team_a_pts[4] if len(team_a_pts) > 4 else -1
    del match['team_a_pts']
    team_b_pts = match['team_b_pts']
    match['team_b_q1_pts'] = team_b_pts[0] if team_b_pts else -1
    match['team_b_q2_pts'] = team_b_pts[1] if len(team_b_pts) > 1 else -1
    match['team_b_q3_pts'] = team_b_pts[2] if len(team_b_pts) > 2 else -1
    match['team_b_q4_pts'] = team_b_pts[3] if len(team_b_pts) > 3 else -1
    match['team_b_q5_pts'] = team_b_pts[4] if len(team_b_pts) > 4 else -1
    del match['team_b_pts']
    referees = match['referees']
    match['referee1'] = referees[0] if referees else ''
    match['referee2'] = referees[1] if len(referees) > 1 else ''
    match['referee3'] = referees[2] if len(referees) > 2 else ''
    del match['referees']


def parse_match(match_dict):
    match = {}
    match_id = match_dict['ids']['match']
    competition_id = match_dict['ids']['competition']
    if match_id is not None and competition_id is not None:
        path = 'data/players/' + competition_id + match_id + '.json'
        if Path(path).exists():
            with open(path) as f:
                html = HTML(html=f.read())
                table = html.find('table', first=True)
                match['id'] = match_id
                match['competition_id'] = competition_id
                match['date'] = match_dict['date']
                _, t_a_id, _, t_b_id = scrape_teams(table)
                match['team_a_id'] = t_a_id
                match['team_b_id'] = t_b_id
                match['place'] = parse_place(html)
                match['time'] = parse_time(html)
                match['referees'] = parse_referees(html)
                match['comissars'] = parse_comissars(html)
                match['number_of_fans'] = parse_number_of_fans(html)
                match['team_a_pts'] = match_dict['pts']['teamA']
                match['team_b_pts'] = match_dict['pts']['teamB']
                flatten_match(match)
    return match


def team_id(row):
    team = row.find('tr > th > a', first=True)
    re_id = re.compile(r'detail_(\d+)_')
    return re.search(re_id, team.attrs['href'])[1]


def parse_place(html):
    place_re = re.compile(r'místo: ((\w|\W)+)')
    place_p = html.find('div.content > p', containing='místo', first=True)
    found_place = re.search(place_re, place_p.text)
    result = ''
    if found_place is not None:
        result = found_place[1]
    else:
        print(place_p.text)
    return result


def parse_time(html):
    time_re = re.compile(r'(\d+):(\d+)')
    time_p = html.find('div.content > p', containing='datum', first=True)
    time_found = re.search(time_re, time_p.text)
    return int(time_found[1]) * 60 + int(time_found[2])


def parse_referees(html):
    referee_re = re.compile(r'(\w+\s\w+)+')
    referee_p = html.find('div.content > p', containing='rozhodčí', first=True)
    result = []
    if referee_p is not None:
        result = re.findall(referee_re, referee_p.text)
    return result


def parse_comissars(html):
    comissar_re = re.compile(r'(\w+\s\w+)+')
    comissar_p = html.find('div.content > p', containing='komisař', first=True)
    result = ''
    if comissar_p is not None:
        result = re.search(comissar_re, comissar_p.text)[1]
    return result


def parse_number_of_fans(html):
    fans_re = re.compile(r'\d+')
    fans_p = html.find('div.content > p', containing='divák', first=True)
    result = -1
    if fans_p is not None:
        result = int(re.search(fans_re, fans_p.text)[0])
    return result
