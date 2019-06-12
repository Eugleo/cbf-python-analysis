import matplotlib.pyplot as plt
import analyze as al


def burlesque():
    '''
    Show four heatmaps:
    (1) NBL, Muži, 2016 - distribution of shot locations
    (2) NBL, Muži, 2016 - rate of success on a given location
    (3) ŽBL, Ženy, 2016 - distribution of shot locations
    (4) ŽBL, Ženy, 2016 - rate of success on a given location
    '''
    df = al.read_existing()
    df_zbl = df[df['comp_id'] == 1798]
    df_nbl = df[df['comp_id'] == 1762]
    zbl_total = al.shots_ratio(* al.throw_into_bin(df_zbl, rows=120))
    zbl_ratios = al.goals_ratio(* al.throw_into_bin(df_zbl, rows=60))
    nbl_total = al.shots_ratio(* al.throw_into_bin(df_nbl, rows=120))
    nbl_ratios = al.goals_ratio(* al.throw_into_bin(df_nbl, rows=60))
    _, axes = plt.subplots(2, 2, sharex=True, sharey=True)
    al.mk_heatmap(axes[0, 0], zbl_total, 0, 0.001, "Ženy (ŽBL), počet střel")
    al.mk_heatmap(axes[1, 0], zbl_ratios, 0, 0.75, "Ženy (ŽBL) úspěšnost")
    al.mk_heatmap(axes[0, 1], nbl_total, 0, 0.001, "Muži (NBL), počet střel")
    al.mk_heatmap(axes[1, 1], nbl_ratios, 0, 0.75, "Muži (NBL), úspěšnost")
    plt.show()


def ashore():
    '''
    Show ten heatmaps:
    5 different girls (Atina, Menšíková, Laci, Paťorková, Kuběn)
    for each, show the location of their shots and goals
    '''
    df = al.read_existing()
    df_bk = df[df['teamS'] == 'BK Havířov']
    df_ati = df_bk[df_bk['player_no'] == 11]  # K/P
    df_men = df_bk[df_bk['player_no'] == 12]  # R
    df_lac = df_bk[df_bk['player_no'] == 13]  # K
    df_pat = df_bk[df_bk['player_no'] == 14]  # K/P
    df_kub = df_bk[df_bk['player_no'] == 15]  # K
    rows = 40
    ati_t = al.shots_total(* al.throw_into_bin(df_ati, rows=rows))
    ati_r = al.goals_total(* al.throw_into_bin(df_ati, rows=rows))
    men_t = al.shots_total(* al.throw_into_bin(df_men, rows=rows))
    men_r = al.goals_total(* al.throw_into_bin(df_men, rows=rows))
    lac_t = al.shots_total(* al.throw_into_bin(df_lac, rows=rows))
    lac_r = al.goals_total(* al.throw_into_bin(df_lac, rows=rows))
    pat_t = al.shots_total(* al.throw_into_bin(df_pat, rows=rows))
    pat_r = al.goals_total(* al.throw_into_bin(df_pat, rows=rows))
    kub_t = al.shots_total(* al.throw_into_bin(df_kub, rows=rows))
    kub_r = al.goals_total(* al.throw_into_bin(df_kub, rows=rows))
    _, axes = plt.subplots(2, 5, sharex=True, sharey=True)
    al.mk_heatmap(axes[0, 0], ati_t, 0, 2, "Atina - střely")
    al.mk_heatmap(axes[1, 0], ati_r, 0, 1, "Atina - koše")
    al.mk_heatmap(axes[0, 1], pat_t, 0, 2, "A. Paťorková - střely")
    al.mk_heatmap(axes[1, 1], pat_r, 0, 1, "A. Paťorková - koše")
    al.mk_heatmap(axes[0, 2], lac_t, 0, 2, "Laci - střely")
    al.mk_heatmap(axes[1, 2], lac_r, 0, 1, "Laci - koše")
    al.mk_heatmap(axes[0, 3], kub_t, 0, 2, "Kuběn - střely")
    al.mk_heatmap(axes[1, 3], kub_r, 0, 1, "Kuběn - koše")
    al.mk_heatmap(axes[0, 4], men_t, 0, 2, "Menšíková - střely")
    al.mk_heatmap(axes[1, 4], men_r, 0, 1, "Menšíková - koše")
    plt.show()


def mime():
    df = al.read_existing()
    m_nbl = df[df['comp_id'] == 1762]
    m_1l = df[df['comp_id'] == 1764]
    m_u19 = df[df['comp_id'] == 1873]
    m_u17 = df[df['comp_id'] == 1886]
    z_zbl = df[df['comp_id'] == 1798]
    z_1l = df[df['comp_id'] == 1802]
    z_u19 = df[df['comp_id'] == 1817]
    z_u17 = df[df['comp_id'] == 1824]
    rows = 100
    m_nbl_t = al.shots_ratio(* al.throw_into_bin(m_nbl, rows=rows))
    m_1l_t = al.shots_ratio(* al.throw_into_bin(m_1l, rows=rows))
    m_u19_t = al.shots_ratio(* al.throw_into_bin(m_u19, rows=rows))
    m_u17_t = al.shots_ratio(* al.throw_into_bin(m_u17, rows=rows))
    z_zbl_t = al.shots_ratio(* al.throw_into_bin(z_zbl, rows=rows))
    z_1l_t = al.shots_ratio(* al.throw_into_bin(z_1l, rows=rows))
    z_u19_t = al.shots_ratio(* al.throw_into_bin(z_u19, rows=rows))
    z_u17_t = al.shots_ratio(* al.throw_into_bin(z_u17, rows=rows))
    _, axes = plt.subplots(2, 4, sharex=True, sharey=True)
    maximum = 0.0008
    al.mk_heatmap(axes[0, 0], m_u17_t, 0, maximum, "Kadeti U17")
    al.mk_heatmap(axes[1, 0], z_u17_t, 0, maximum, "Kadetky U17")
    al.mk_heatmap(axes[0, 1], m_u19_t, 0, maximum, "Junioři U19")
    al.mk_heatmap(axes[1, 1], z_u19_t, 0, maximum, "Juniorky U19")
    al.mk_heatmap(axes[0, 2], m_1l_t, 0, maximum, "Muži 1. Liga")
    al.mk_heatmap(axes[1, 2], z_1l_t, 0, maximum, "Ženy 1. Liga")
    al.mk_heatmap(axes[0, 3], m_nbl_t, 0, maximum, "Muži NBL")
    al.mk_heatmap(axes[1, 3], z_zbl_t, 0, maximum, "Ženy ŽBL")
    plt.show()


def delicious():
    df = al.read_existing()
    zbl = df[df['comp_id'] == 1798]
    q1 = []
    q2 = []
    q3 = []
    q4 = []
    qs = [q1, q2, q3, q4]
    ms = [zbl[zbl['match_id'] == m_id] for m_id in zbl['match_id'].unique()]
    for match in ms:
        q1.append(len(match[match['quarter'] == 'q1']))
        q2.append(len(match[match['quarter'] == 'q2']))
        q3.append(len(match[match['quarter'] == 'q3']))
        q4.append(len(match[match['quarter'] == 'q4']))
    qs_m = [sum(q) / len(q) for q in qs]
    _, ax = plt.subplots()
    ax.bar([0, 30, 60, 90], qs_m, width=25)
    plt.show()


mime()
# 1762 = muži, NBL, 2016
# 1764 = muži, 1. liga, 2016
# 1873 = Junioři U19, extraliga, 2016
# 1886 = Kadeti U 17, extraliga, 2016
# 1846 = žáci U14, žákovská liga, 2016
# 1798 = ženy, ŽBL, 2016
# 1802 = ženy, 1. liga, 2016
# 1817 = Juniorky U19, extraliga, 2016
# 1824 = kadetky U17, extraliga, 2016
