import re
import os
from requests_html import HTML
from file_management import write_dicts_to_file


def open_match(number):
    with open('data/players/' + str(number) + '.json') as f:
        return f.read()


def scrape_pages(path):
    teams = []
    statistics = []
    players = []
    index = 0
    for dirpath, _, names in os.walk(path):
        for name in filter( lambda n: 'json' in n, names):
            with open(os.path.join(dirpath, name)) as f:
                d = scrape_page(f.read())
                statistics.extend(d['stats'])
                if d['team_a'] not in teams:
                    teams.append(d['team_a'])
                if d['team_b'] not in teams:
                    teams.append(d['team_b'])
                for p in d['players']:
                    if p not in players:
                        players.append(p)
            print("Parsed file No. " + str(index))
            index += 1
    write_dicts_to_file(statistics, os.path.join(path, 'stats.csv'))
    write_dicts_to_file(teams, os.path.join(path, 'teams.csv'))
    write_dicts_to_file(players, os.path.join(path, 'players.csv'))


def scrape_page(text):
    html = HTML(html=text)
    table = html.find('table', first=True)
    return scrape_table(table)


def scrape_table(table):
    a_xp = (
        "//tr[count(preceding-sibling::tr[@class='hdr'])=1 and"
        "count(following-sibling::tr[@class='ftr'])=2]"
    )
    team_a_rows = table.xpath(a_xp)
    b_xp = (
        "//tr[count(preceding-sibling::tr[@class='hdr'])=2 and"
        "count(following-sibling::tr[@class='ftr'])=1]"
    )
    team_b_rows = table.xpath(b_xp)
    team_a_name, team_a_id, team_b_name, team_b_id = scrape_teams(table)
    m_id = match_id(table)
    team_a_stats = map( lambda row: stats(row, m_id), team_a_rows)
    team_b_stats = map( lambda row: stats(row, m_id), team_b_rows)
    players = scrape_players(team_a_rows, team_a_id) + scrape_players(
        team_b_rows, team_b_id
    )
    return {
        'players': players,
        'stats': list(team_a_stats) + list(team_b_stats),
        'team_a': {'id': team_a_id, 'name': team_a_name},
        'team_b': {'id': team_b_id, 'name': team_b_name},
    }


def match_id(table):
    anchor = table.find('tr > th > span.actions > a', first=True)
    match_re = re.compile(r'zapas_(\d+)_')
    match_found = re.search(match_re, anchor.attrs['href'])
    return match_found[0]


def scrape_teams(table):
    a_xp = "//tr[count(following-sibling::tr[@class='hdr'])=2]"
    b_xp = (
        "//tr[preceding-sibling::tr[@class='empty'] and"
        "following-sibling::tr[@class='hdr']]"
    )
    team_a_name = team_name(table.xpath(a_xp, first=True))
    team_b_name = team_name(table.xpath(b_xp, first=True))
    team_a_id = team_id(table.xpath(a_xp, first=True))
    team_b_id = team_id(table.xpath(b_xp, first=True))
    return (team_a_name, team_a_id, team_b_name, team_b_id)


def scrape_players(rows, tm_id):
    players = []
    for row in rows:
        p = player(row)
        p['team_id'] = tm_id
        players.append(p)
    return players


def player(row):
    cells = row.find('td')
    number = -1
    if cells[0].find('strong', first=True) is not None:
        number = int_or_default(cells[0].find('strong', first=True).text)
    else:
        number = int_or_default(cells[0].text)
    return {'id': player_id(row), 'name': cells[1].attrs['title'], 'number': number}


def team_name(row):
    team = row.find('tr > th > a', first=True)
    return team.text


def team_id(row):
    team = row.find('tr > th > a', first=True)
    re_id = re.compile(r'detail_(\d+)_')
    return re.search(re_id, team.attrs['href'])[1]


def stats(row, m_id):
    goals_2p, misses_2p = shots_2p(row)
    goals_3p, misses_3p = shots_3p(row)
    goals_free_throw, misses_free_throw = free_throws(row)
    balls_won, balls_lost = balls(row)
    fauls_won, fauls_lost = fauls(row)
    return {
        'player_id': player_id(row),
        'match_id': m_id,
        'time_in_play': time(row),
        'goals_2p': goals_2p,
        'misses_2p': misses_2p,
        'goals_3p': goals_3p,
        'misses_3p': misses_3p,
        'goals_free_throw': goals_free_throw,
        'misses_free_throw': misses_free_throw,
        'offensive_rebounds': offensive_rebounds(row),
        'deffensive_rebounds': deffensive_rebounds(row),
        'blocks': blocks(row),
        'assists': assists(row),
        'balls_won': balls_won,
        'balls_lost': balls_lost,
        'fauls_won': fauls_won,
        'fauls_lost': fauls_lost,
        'value': value(row),
        'points': points(row),
    }


def time(row):
    cells = row.find('td')
    re_time = re.compile(r'(\d+):(\d+)')
    time_str = re.search(re_time, cells[2].text)
    result = -1
    if time_str is not None:
        result = int(time_str[1]) * 60 + int(time_str[2])
    return result


def player_id(row):
    p = row.find('td > a', first=True)
    re_id = re.compile(r'hrac_(\d+)_')
    result = -1
    if p is not None:
        result = re.search(re_id, p.attrs['href'])[1]
    return result


def shots_2p(row):
    return extract_throws(row, 4)


def shots_3p(row):
    return extract_throws(row, 5)


def free_throws(row):
    return extract_throws(row, 6)


def extract_throws(row, cell_no):
    cells = row.find('td')
    digs = re.search(re.compile(r'(\d+)/(\d+)'), cells[cell_no].text)
    result = (-1, -1)
    if digs is not None:
        result = (int(digs[1]), int(digs[2]))
    return result


def offensive_rebounds(row):
    cells = row.find('td')
    return int_or_default(cells[9].text)


def deffensive_rebounds(row):
    cells = row.find('td')
    return int_or_default(cells[10].text)


def blocks(row):
    cells = row.find('td')
    return int_or_default(cells[11].text)


def assists(row):
    cells = row.find('td')
    return int_or_default(cells[13].text)


def balls(row):
    cells = row.find('td')
    return (int_or_default(cells[14].text), int_or_default(cells[15].text))


def fauls(row):
    cells = row.find('td')
    return (int_or_default(cells[17].text), int_or_default(cells[18].text))


def value(row):
    cells = row.find('td')
    return int_or_default(cells[20].text)


def points(row):
    cells = row.find('td')
    return int_or_default(cells[21].text)


def int_or_default(val):
    try:
        return int(val)

    except ValueError as _:
        return -111
