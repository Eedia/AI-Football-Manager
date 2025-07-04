import requests
from datetime import datetime
from dateutil.parser import parse
from dotenv import load_dotenv
import os

'''
api 로 어느팀이 home/away인지 판별하는 함수
'''
load_dotenv()
api_key = os.getenv("X_RAPIDAPI_KEY")

def get_fixture_info(api_key, match_date, team1, team2):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    params = {
        "date": match_date,
        "league": 39,
        "season": 2024
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    for fixture in data["response"]:
        home = fixture["teams"]["home"]["name"].lower()
        away = fixture["teams"]["away"]["name"].lower()

        if team1.lower() in [home, away] and team2.lower() in [home, away]:
            return {
                "home_team": fixture["teams"]["home"]["name"],
                "away_team": fixture["teams"]["away"]["name"]
            }

    return None


def extract_match_parameters(user_input: str) -> dict:
    """
    사용자 입력 → match_date, home_team, away_team (API-Football 기반)
    """

    team_kor_to_eng = {
        "아스널": "Arsenal", "아스톤 빌라": "Aston Villa", "본머스": "Bournemouth", "브렌트포드": "Brentford",
        "브라이턴": "Brighton", "첼시": "Chelsea", "크리스탈 팰리스": "Crystal Palace", "에버턴": "Everton",
        "풀럼": "Fulham", "리즈": "Leeds United", "리버풀": "Liverpool", "맨시티": "Man City",
        "맨체스터 시티": "Man City", "맨유": "Man Utd", "맨체스터 유나이티드": "Man Utd",
        "뉴캐슬": "Newcastle", "노팅엄 포레스트": "Nottingham Forest", "사우샘프턴": "Southampton",
        "토트넘": "Tottenham", "스퍼스": "Spurs", "웨스트햄": "West Ham", "울브스": "Wolves", "울버햄튼": "Wolves"
    }

    # 날짜 파싱
    try:
        match_date = parse(user_input, fuzzy=True).date()
    except Exception:
        return {"match_date": None, "home_team": None, "away_team": None}

    # 팀 파싱
    found_teams = []
    for kor, eng in team_kor_to_eng.items():
        if kor in user_input and eng not in found_teams:
            found_teams.append(eng)

    if len(found_teams) < 2:
        return {"match_date": str(match_date), "home_team": None, "away_team": None}

    # home/away 정보는 API를 통해 확정
    fixture = get_fixture_info(api_key, str(match_date), found_teams[0], found_teams[1])
    if fixture:
        return {
            "match_date": str(match_date),
            "home_team": fixture["home_team"],
            "away_team": fixture["away_team"]
        }
    else:
        return {
            "match_date": str(match_date),
            "home_team": None,
            "away_team": None
        }
