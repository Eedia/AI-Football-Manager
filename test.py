import asyncio
import datetime
import aiohttp
import pandas as pd
import joblib
from understat import Understat

# ---- 1. 최근 경기 데이터를 Understat에서 가져오는 함수 ----
async def fetch_recent_team_data(team_name: str, is_home: bool = True, last_n: int = 5):
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        year = datetime.datetime.now().year
        matches = await understat.get_team_results(team_name, year)
        matches = sorted(matches, key=lambda x: x["datetime"], reverse=True)

        # 홈/원정 필터링
        if is_home:
            matches = [m for m in matches if m["h"]["title"] == team_name]
        else:
            matches = [m for m in matches if m["a"]["title"] == team_name]

        matches = matches[:last_n]
        if not matches:
            raise ValueError(f"No recent matches found for {team_name} (is_home={is_home})")

        xg_list = [float(m["xG"]["h"] if is_home else m["xG"]["a"]) for m in matches]
        goals_list = [int(m["goals"]["h"] if is_home else m["goals"]["a"]) for m in matches]
        conceded_list = [int(m["goals"]["a"] if is_home else m["goals"]["h"]) for m in matches]

        form = sum(1 if gf > ga else 0.5 if gf == ga else 0 for gf, ga in zip(goals_list, conceded_list))

        return {
            "avg_xg": sum(xg_list) / len(xg_list),
            "form": form,
        }

# ---- 2. 모델 입력값을 생성하는 함수 ----
async def get_model_input_understat(home_team: str, away_team: str):
    home_data = await fetch_recent_team_data(home_team, is_home=True)
    away_data = await fetch_recent_team_data(away_team, is_home=False)

    h_xg = home_data["avg_xg"]
    a_xg = away_data["avg_xg"]

    return {
        "HomeElo": 1700,
        "AwayElo": 1680,
        "elo_diff": 1700 - 1680,
        "Form3Home": home_data["form"],
        "Form5Home": home_data["form"],
        "Form3Away": away_data["form"],
        "Form5Away": away_data["form"],
        "prob_home": 0.45,
        "prob_draw": 0.3,
        "prob_away": 0.25,
        "h_xg": h_xg,
        "a_xg": a_xg,
        "xG_diff": h_xg - a_xg,
        "xg_margin": abs(h_xg - a_xg),
        "xg_ratio": h_xg / (h_xg + a_xg + 1e-6),
        "rolling_xg_home_5": h_xg,
        "rolling_xg_away_5": a_xg,
        "elo_change_home": 5,
        "elo_change_away": -3,
        "month": datetime.datetime.now().month,
        "weekday": datetime.datetime.now().weekday()
    }

# ---- 3. 실행 및 예측 ----
if __name__ == "__main__":
    home_team = "Manchester City"
    away_team = "Liverpool"

    input_dict = asyncio.run(get_model_input_understat(home_team, away_team))

    features = [
        'HomeElo', 'AwayElo', 'elo_diff',
        'Form3Home', 'Form5Home', 'Form3Away', 'Form5Away',
        'prob_home', 'prob_draw', 'prob_away',
        'h_xg', 'a_xg', 'xG_diff', 'xg_margin', 'xg_ratio',
        'rolling_xg_home_5', 'rolling_xg_away_5',
        'elo_change_home', 'elo_change_away',
        'month', 'weekday'
    ]

    df_input = pd.DataFrame([input_dict])[features]

    model = joblib.load("xgb_model.pkl")
    proba = model.predict_proba(df_input)[0]
    pred = model.predict(df_input)[0]

    print("------ 예측 결과 ------")
    print(f"Home Team: {home_team}")
    print(f"Away Team: {away_team}")
    print(f"예측 결과: {'홈 승리' if pred == 1 else '무승부 또는 원정 승리'}")
    print(f"홈 승 확률: {proba[1]*100:.2f}%")
    print(f"무/원정 승 확률: {proba[0]*100:.2f}%")
