import pandas as pd
import numpy as np
from datetime import datetime
from soccerdata import Understat, ClubElo


def calculate_form(df: pd.DataFrame, team_name: str, n: int) -> float:
    """
    경기 단위 match_stats 기반으로 최근 n경기 폼 점수 계산.
    승=3, 무=1, 패=0
    """
    form = []
    for row in df.head(n).itertuples():
        is_home = (row.home_team == team_name)
        gf = row.home_goals if is_home else row.away_goals
        ga = row.away_goals if is_home else row.home_goals

        if gf > ga:
            form.append(3)
        elif gf == ga:
            form.append(1)
        else:
            form.append(0)

    return sum(form) / n if form else np.nan



def get_model_input(home_team: str, away_team: str, match_date: str = None) -> dict:
    """
    홈팀/원정팀 이름과 경기 날짜를 기반으로 21개 모델 입력 피처를 생성합니다.
    - Elo, xG, Form, 날짜 파생 feature 자동 계산
    - 확률 피처(prob_*)는 아직 미구현이며 추후 api-football로 보완 예정
    """
    
    if match_date is None:
        match_date = datetime.today().strftime("%Y-%m-%d")
    match_date = pd.to_datetime(match_date)
    prev_date = (match_date - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # --- Elo 데이터 ---
    elo = ClubElo()
    elo_data = elo.read_by_date(match_date.strftime("%Y-%m-%d"))
    prev_elo_data = elo.read_by_date(prev_date)

    home_elo = elo_data.loc[home_team, "elo"]
    away_elo = elo_data.loc[away_team, "elo"]
    elo_diff = home_elo - away_elo

    elo_change_home = home_elo - prev_elo_data.loc[home_team, "elo"]
    elo_change_away = away_elo - prev_elo_data.loc[away_team, "elo"]

    # print("Elo 데이터 인덱스 샘플:", elo_data.index[:10])
    # print("전체 인덱스:", elo_data.index.tolist())


    # --- 날짜 파생 피처 ---
    month = match_date.month
    weekday = match_date.weekday()

    # --- Understat xG (match-level) ---
    understat = Understat(leagues="ENG-Premier League", seasons=[2021, 2022, 2023, 2024, 2025])
    xg_df = understat.read_team_match_stats()
    xg_df["date"] = pd.to_datetime(xg_df["date"])

    match_row = xg_df[
        (xg_df["home_team"] == home_team) &
        (xg_df["away_team"] == away_team) &
        (xg_df["date"] < match_date)
    ].sort_values("date", ascending=False).head(1)

    if match_row.empty:
        print(f"[ ! ] xG 데이터 없음: {home_team} vs {away_team}")
        h_xg = a_xg = xG_diff = xg_margin = xg_ratio = np.nan
    else:
        h_xg = match_row["home_xg"].values[0]
        a_xg = match_row["away_xg"].values[0]
        xG_diff = h_xg - a_xg
        xg_margin = abs(xG_diff)
        xg_ratio = h_xg / (h_xg + a_xg + 1e-6)

    # --- Understat 경기별 기록 (Form + 롤링 xG)
    # team별 최근 경기 추출
    team_results_home = xg_df[
        ((xg_df["home_team"] == home_team) | (xg_df["away_team"] == home_team)) &
        (xg_df["date"] < match_date)
    ].sort_values("date", ascending=False)

    team_results_away = xg_df[
        ((xg_df["home_team"] == away_team) | (xg_df["away_team"] == away_team)) &
        (xg_df["date"] < match_date)
    ].sort_values("date", ascending=False)

    # 롤링 평균 계산 (홈으로 출전한 경기만)
    home_xg_list = team_results_home[team_results_home["home_team"] == home_team]["home_xg"]
    away_xg_list = team_results_away[team_results_away["away_team"] == away_team]["away_xg"]

    rolling_xg_home_5 = home_xg_list.head(5).mean() if not home_xg_list.empty else np.nan
    rolling_xg_away_5 = away_xg_list.head(5).mean() if not away_xg_list.empty else np.nan

    # 최근 폼 점수
    Form3Home = calculate_form(team_results_home, home_team, 3)
    Form5Home = calculate_form(team_results_home, home_team, 5)
    Form3Away = calculate_form(team_results_away, away_team, 3)
    Form5Away = calculate_form(team_results_away, away_team, 5)


    # 반환
    return {
        "HomeElo": home_elo,
        "AwayElo": away_elo,
        "elo_diff": elo_diff,
        "elo_change_home": elo_change_home,
        "elo_change_away": elo_change_away,
        "Form3Home": Form3Home,
        "Form5Home": Form5Home,
        "Form3Away": Form3Away,
        "Form5Away": Form5Away,
        "h_xg": h_xg,
        "a_xg": a_xg,
        "xG_diff": xG_diff,
        "xg_margin": xg_margin,
        "xg_ratio": xg_ratio,
        "rolling_xg_home_5": rolling_xg_home_5,
        "rolling_xg_away_5": rolling_xg_away_5,
        "month": month,
        "weekday": weekday,
        "prob_home": np.nan,   # 추후 api-football로 채울 예정 혹은 삭제
        "prob_draw": np.nan,
        "prob_away": np.nan
    }

# if __name__ == "__main__":
#     features = get_model_input("Everton", "Liverpool", "2024-11-26")
#     print(pd.DataFrame([features]).T.sort_index())
    
