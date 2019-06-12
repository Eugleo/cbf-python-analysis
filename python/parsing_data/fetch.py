import json
import re
import os
import requests
from pathlib import Path

from games import parse_game, brew


def parse_header(tag) -> str:
    try:
        a1, a2, a3 = tag.find('th').find_all('a')
    except ValueError as e:
        print(e)
        return None

    s1, s2, s3 = list(map( lambda s: s.text.strip(), [a1, a2, a3]))
    cat_re = re.compile(r'(.+), (.+)')
    category, name = cat_re.search(s1).groups()
    return {"name": name, "category": category, "phase": s2, "round": s3}


def games(soup):
    table = soup.find("table")
    competition = ''
    for r in table.find_all("tr"):
        if r.find('th'):
            competition = parse_header(r)
        else:
            game = parse_game(r)
            if game:
                game['competition'] = competition
                yield game

            else:
                continue


def next_url(soup):
    days = soup(title=re.compile(r'seznam \w+ dne'))
    return "http://www.cbf.cz" + days[3]['href']


def url_from_date(date):
    return "http://www.cbf.cz/souteze/aktualni-utkani/utkani_" + date + ".html"


def date_from_url(url):
    return re.compile(r'\d{8}').search(url).group(0)


def parse_date(date):
    return (date[:4], date[4:6], date[6:])


def write_games(start_date, end_date):
    root = 'data/games'
    current_url = url_from_date(start_date)
    last_url = next_url(brew(url_from_date(end_date)))
    counter = 0
    games_no = 0
    while current_url != last_url:
        counter += 1
        current_soup = brew(current_url)
        gs = list(games(current_soup))
        if gs:
            current_date = date_from_url(current_url)
            y, m, d = parse_date(current_date)
            for g in gs:
                g['date'] = current_date
            path = root + "/" + y + "/" + m
            if not os.path.exists(path):
                os.makedirs(path)
            games_no += len(gs)
            with open(path + "/" + d + '.json', 'w') as f:
                json.dump(gs, f, ensure_ascii=False, indent=4)
                print(f"Games from {d}. {m}. {y} just written!")
        current_url = next_url(current_soup)
    print(f"Done! Crawled {counter} sites and parsed {games_no} games. Phew!")


def download_player_stats():
    urls = []
    for root, _, files in os.walk("./data/games"):
        for file in filter( lambda s: "json" in s, files):
            with open(os.path.join(root, file)) as f:
                for game in json.load(f):
                    competition = game["ids"]["competition"]
                    match = game["ids"]["match"]
                    if competition is not None and match is not None:
                        base = "http://www.cbf.cz/souteze/zapas_"
                        url = base + str(match) + "_soutez_" + competition + ".html"
                        urls.append({'link': url, 'id': competition + match})
    index = 0
    for url in urls:
        index += 1
        if index > 5497:
            link = url['link']
            match_id = url['id']
            response = requests.get(link)
            path = 'data/players/' + match_id + '.json'
            if Path(path).exists():
                match_id += ' (error)'
            with open('data/players/' + match_id + '.json', 'w') as f:
                response.encoding = 'utf-8'
                f.write(response.text)
                print("Written file No. " + str(index) + " with id: " + match_id)
