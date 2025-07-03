import pandas as pd
from soccerdata import Understat, ClubElo
from datetime import datetime

def get_model_input(home_team, away_team, match_date_str):
    # ▶ 날짜 변환
    match_date = pd.to_datetime(match_date_str)
    date_str = match_date.strftime("%Y-%m-%d")

    # ▶ 데이터 수집기
    understat = Understat(leagues="ENG-Premier League")
    elo = ClubElo()

    # ▶ Elo 점수 수집 (팀 이름은 인덱스로 존재)
    elo_df = elo.read_by_date(match_date)

    print("[DEBUG] elo_df columns:", elo_df.columns.tolist())
    print(elo_df.head())

    if home_team not in elo_df.index or away_team not in elo_df.index:
        raise ValueError(f"[ERROR] Elo 데이터에 팀이 없습니다. 사용 가능한 팀: {elo_df.index.tolist()}")

    home_elo = elo_df.loc[home_team, 'elo']
    away_elo = elo_df.loc[away_team, 'elo']
    elo_diff = home_elo - away_elo

    # ▶ xG 수집
    home_stats = understat.read_team_match_stats(home_team)
    away_stats = understat.read_team_match_stats(away_team)

    if date_str not in home_stats['date'].values:
        raise ValueError(f"[ERROR] {home_team}의 {date_str} 경기 xG 정보 없음")
    if date_str not in away_stats['date'].values:
        raise ValueError(f"[ERROR] {away_team}의 {date_str} 경기 xG 정보 없음")

    h_xg = home_stats.loc[home_stats['date'] == date_str, 'xG'].values[0]
    a_xg = away_stats.loc[away_stats['date'] == date_str, 'xG'].values[0]
    xg_diff = h_xg - a_xg

    # ▶ 피처 반환
    return {
        "elo_home": home_elo,
        "elo_away": away_elo,
        "elo_diff": elo_diff,
        "h_xg": h_xg,
        "a_xg": a_xg,
        "xG_diff": xg_diff
    }




