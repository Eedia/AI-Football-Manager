import pandas as pd
from soccerdata import FiveThirtyEight
import datetime
import os

def get_model_input(home_team: str, away_team: str) -> dict:
    # 데이터 로드
    try:
        data_src = FiveThirtyEight()
        df = data_src.read_games()
        df = df[df['league'] == "ENG Premier League"]
        df = df[df['date'] < datetime.datetime.now()]
    except Exception as e:
        raise RuntimeError(f"경기 데이터를 불러오는 데 실패했습니다: {e}")

    # 최근 5경기 가져오기
    home_matches = df[df['team1'] == home_team].sort_values('date', ascending=False).head(5)
    away_matches = df[df['team2'] == away_team].sort_values('date', ascending=False).head(5)

    if len(home_matches) < 2 or len(away_matches) < 2:
        raise ValueError(f"'{home_team}' 또는 '{away_team}'의 최근 경기 정보가 부족합니다.")

    # Elo (SPI)
    home_elo = home_matches.iloc[0]['spi1']
    away_elo = away_matches.iloc[0]['spi2']
    elo_diff = home_elo - away_elo

    # Form 계산
    def calc_form(matches, gf_col, ga_col):
        form = 0.0
        for _, row in matches.iterrows():
            gf, ga = row[gf_col], row[ga_col]
            if pd.isna(gf) or pd.isna(ga):
                continue
            if gf > ga:
                form += 1.0
            elif gf == ga:
                form += 0.5
        return form

    form3_home = calc_form(home_matches.head(3), 'score1', 'score2')
    form5_home = calc_form(home_matches, 'score1', 'score2')
    form3_away = calc_form(away_matches.head(3), 'score2', 'score1')
    form5_away = calc_form(away_matches, 'score2', 'score1')

    # xG 관련
    h_xg = home_matches['xg1'].mean()
    a_xg = away_matches['xg2'].mean()
    xG_diff = h_xg - a_xg
    xg_margin = abs(xG_diff)
    xg_ratio = h_xg / (h_xg + a_xg + 1e-6)

    # 마지막 elo 변화량
    elo_change_home = home_matches.iloc[0]['spi1'] - home_matches.iloc[1]['spi1']
    elo_change_away = away_matches.iloc[0]['spi2'] - away_matches.iloc[1]['spi2']

    # 결과 패킹
    input_data = {
        'HomeElo': home_elo,
        'AwayElo': away_elo,
        'elo_diff': elo_diff,
        'Form3Home': form3_home,
        'Form5Home': form5_home,
        'Form3Away': form3_away,
        'Form5Away': form5_away,
        'prob_home': 0.5,  # 베팅 확률 미사용 중
        'prob_draw': 0.25,
        'prob_away': 0.25,
        'h_xg': h_xg,
        'a_xg': a_xg,
        'xG_diff': xG_diff,
        'xg_margin': xg_margin,
        'xg_ratio': xg_ratio,
        'rolling_xg_home_5': h_xg,
        'rolling_xg_away_5': a_xg,
        'elo_change_home': elo_change_home,
        'elo_change_away': elo_change_away,
        'month': datetime.datetime.now().month,
        'weekday': datetime.datetime.now().weekday()
    }

    return input_data
