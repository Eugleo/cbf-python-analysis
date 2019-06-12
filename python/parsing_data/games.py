import re
from typing import Dict, Any

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup


def brew(url, parser="html.parser"):
    try:
        html = urlopen(url)
    except HTTPError:
        return None

    except URLError:
        print("No connection")
        return None

    if html is None:
        print("URL not found")
        return None

    else:
        return BeautifulSoup(html.read(), parser)


def parse_game(tag) -> Dict[str, Any]:
    if tag('td') is None:
        return None

    number, teamA, _, teamB, players_url_td, detail_url_td, *_ = tag("td")
    parsed_number = re.compile(r'\d+').search(number.text)
    pts = parse_scores(tag)
    players_url_a = players_url_td.find('a')
    if players_url_a and 'href' in players_url_a.attrs:
        url = players_url_a['href']
        match_id, competition_id = ids_from_players_url(url)
    else:
        match_id = None
        competition_id = None
    detail_url_a = detail_url_td.find('a')
    if (
        detail_url_a and
        'href' in detail_url_a.attrs and
        is_valid_detail_url(detail_url_a['href'])
    ):
        url = detail_url_a['href']
        shots = parse_shotchart(urlopen(shotchart_url(brew(url))).read())
        acc_id = id_from_details_url(url)[0]
    else:
        shots = None
        acc_id = None
    return {
        'teamA': teamA.text,
        'teamB': teamB.text,
        'number': parsed_number.group() if parsed_number else None,
        'pts': pts,
        'shots': shots,
        'ids': {"match": match_id, "competition": competition_id, "account": acc_id},
    }


def ids_from_players_url(url):
    return re.compile(r'zapas_(\d+)_soutez_(\d+)').search(url).groups()


def id_from_details_url(url):
    return re.compile(r'acc=(\d+)').search(url).groups()


def players_url_from_ids(ids):
    base = "http://www.cbf.cz/souteze/zapas_"
    return base + ids[0] + "_soutez_" + ids[1] + ".html"


def details_url_from_ids(ids):
    base = "http://live.fibaeurope.com/www/Game.aspx?acc="
    return base + ids[0] + "&game_number=" + ids[1]


def is_valid_detail_url(url):
    reg = re.compile(r'live\.fibaeurope\.com').search(url)
    return reg is not None and reg.group() is not None


def parse_scores(tag):
    scores_13_td = tag("td")[5]
    score_4_td = tag("td")[4]
    teamA_pts = []
    teamB_pts = []
    scores_13_reg = re.compile(r"\d+")
    scores_13 = scores_13_td.find(string=scores_13_reg)
    if scores_13:
        matches = scores_13_reg.findall(scores_13)
        teamA_pts = matches[::2]
        teamB_pts = matches[1::2]
    score_4_reg = re.compile(r"(\d+):(\d+)")
    score_4 = score_4_td.find(string=score_4_reg)
    if score_4:
        match = score_4_reg.search(score_4)
        teamA_pts.append(match.group(1))
        teamB_pts.append(match.group(2))
    ints_A = list(map(int, teamA_pts))
    for i, score in enumerate(ints_A):
        if i > 0:
            teamA_pts[i] = score - ints_A[i - 1]
        else:
            teamA_pts[i] = score
    ints_B = list(map(int, teamB_pts))
    for i, score in enumerate(ints_B):
        if i > 0:
            teamB_pts[i] = score - ints_B[i - 1]
        else:
            teamB_pts[i] = score
    return {"teamA": teamA_pts, "teamB": teamB_pts}


def parse_shotchart(txt):
    sc = BeautifulSoup(txt, "lxml")
    shots = sc.shots
    shotchart = {"teamA": {}, "teamB": {}}
    if shots:
        for s in shots('s'):
            shot = {}
            shot['is_goal'] = s['m'] == '0'
            shot['player_no'] = s['player']
            shot['time'] = s['t']  # mm:ss in terms of current quarter
            quarter = 'q' + s['quarter']
            team = 'teamA' if s['team'] == '0' else 'teamB'
            shot['x'] = s['x']
            shot['y'] = s['y']
            shotchart[team].setdefault(quarter, []).append(shot)
    else:
        print(txt)
    return shotchart


def shotchart_url(soup):
    scripts = soup('script')
    if scripts:
        script = scripts[-1]
        accID_m = re.compile(r"accountID = (\d+)").search(script.string)
        gameID_m = re.compile(r"gameID = (\d+)").search(script.string)
        if accID_m and gameID_m:
            base = "http://live.fibaeurope.com/www/ShotChart.ashx?acc="
            lang = "&lng=en&gameID="
            return base + accID_m.group(1) + lang + gameID_m.group(1)

        else:
            return None

    else:
        return None
