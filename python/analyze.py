import os
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.misc import imread


def load_shots():
    shots = []
    for directory, _, files in os.walk("data/games"):
        for file in files:
            try:
                with open(directory + "/" + file) as f:
                    for game in json.load(f):
                        shots += extract_shots(game)
            except UnicodeDecodeError as e:
                print(e)
                continue

    return pd.DataFrame(shots)


def extract_shots(game):
    shots = []
    all_shots = game["shots"]
    if all_shots:
        for team, qs in all_shots.items():
            for quarter, q_shots in qs.items():
                for shot in q_shots:
                    s = {}
                    s["is_goal"] = shot["is_goal"]
                    s["player_no"] = shot["player_no"]
                    s["time"] = str_to_time(shot["time"])
                    s["quarter"] = quarter
                    s["teamS"] = game[team]
                    s["teamG"] = game["teamA" if team == "teamB" else "teamB"]
                    s["comp_name"] = game["competition"]["name"]
                    s["comp_category"] = game["competition"]["category"]
                    s["comp_id"] = game["ids"]["competition"]
                    s["match_id"] = game["ids"]["match"]
                    s["x"] = int(shot["x"])
                    s["y"] = int(shot["y"])
                    shots.append(s)
        return shots

    else:
        return []


def str_to_time(s):
    return float(s[:2]) + int(s[-2:]) / 60


def into_bin(x, y, xspace, yspace):
    c = 0
    r = 0
    for (i,), v in np.ndenumerate(xspace):
        if v < x and x <= xspace[i + 1]:
            c = i
            break

    for (i,), v in np.ndenumerate(yspace):
        if v < y and y < yspace[i + 1]:
            r = i
            break

    return (r, c)


def mk_heatmap(ax, ratios, mn, mx, title, ip="gaussian"):
    extent = [0, 273, 0, 255]
    im = ax.imshow(
        ratios,
        interpolation=ip,
        cmap=plt.get_cmap("viridis"),
        extent=extent,
        vmin=mn,
        vmax=mx,
        origin="lower",
    )
    ax.xaxis.set(visible=False)
    ax.yaxis.set(visible=False)
    ax.imshow(imread("images/half.png"), zorder=0, extent=extent)
    ax.set(xlim=(0, 273), ylim=(0, 255), title=title)
    return im


def read_existing():
    with open("data/main_dataframe.csv") as f:
        df = pd.read_csv(f)
        return df


def write_new():
    with open("data/main_dataframe.csv", "w") as f:
        df = load_shots()
        df.to_csv(f)
        return df


def throw_into_bin(df, rows=None, columns=None, w=273, h=255):
    if rows is None:
        rows = 10
    if columns is None:
        columns = int(w / (h / rows))
    goals = np.zeros((rows, columns))
    misses = np.zeros((rows, columns))
    xspace = np.linspace(0, w, num=columns + 1)
    yspace = np.linspace(0, h, num=rows + 1)
    org_ratio = w / 1500
    df_gxy = zip(df["is_goal"], df["x"], df["y"])
    for is_goal, x, y in df_gxy:
        row, column = into_bin(x * org_ratio, y * org_ratio, xspace, yspace)
        if is_goal:
            goals[row, column] += 1
        else:
            misses[row, column] += 1
    return (goals, misses)


def shots_ratio(goals, misses):
    shots_no = np.sum(goals) + np.sum(misses)
    fold = np.zeros(goals.shape)
    for (r, c), v in np.ndenumerate(goals):
        fold[r, c] = (v + misses[r, c]) / shots_no
    return fold


def goals_ratio(goals, misses):
    fold = np.zeros(goals.shape)
    for (r, c), v in np.ndenumerate(goals):
        if v != 0:
            fold[r, c] = v / (misses[r, c] + v)
    return fold


def shots_total(goals, misses):
    fold = np.zeros(goals.shape)
    for (r, c), v in np.ndenumerate(goals):
        fold[r, c] = misses[r, c] + v
    return fold


def goals_total(goals, _):
    fold = np.zeros(goals.shape)
    for (r, c), v in np.ndenumerate(goals):
        fold[r, c] = v
    return fold
