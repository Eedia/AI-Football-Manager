import requests
from datetime import datetime
from dateutil.parser import parse
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("X_RAPIDAPI_KEY")

def get_fixture_info(api_key, match_date, team_name):
    """
    API-Football를 사용하여 프리미어리그 경기 정보를 가져오는 함수.
    특정 날짜에 주어진 팀이 관련된 경기의 홈/어웨이 팀 정보를 반환합니다.

    - match_date: 경기 날짜 (YYYY-MM-DD 형식)
    - team_name: 검색할 팀의 이름 (영문)

    - 반환값: 홈팀과 어웨이팀의 이름을 포함한 딕셔너리, 없으면 None
    """
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    params = {
        "date": match_date,
        "league": 39,  # 프리미어리그의 리그 ID
        "season": 2024 # Assuming current season is 2024-2025, so season parameter should be 2024
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status() # Raise an exception for HTTP errors
    data = response.json()

    for fixture in data["response"]:
        home = fixture["teams"]["home"]["name"].lower()
        away = fixture["teams"]["away"]["name"].lower()

        if team_name.lower() in [home, away]:
            return {
                "home_team": fixture["teams"]["home"]["name"],
                "away_team": fixture["teams"]["away"]["name"]
            }

    return None


def extract_match_parameters(user_input: str) -> dict:
    """
    사용자 입력에서 경기 날짜와 팀 정보를 파싱하고,
    API를 통해 홈/어웨이 팀을 확정하여 반환합니다.
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

    # 팀 파싱 (첫 번째로 찾은 팀만 사용)
    found_team = None
    for kor, eng in team_kor_to_eng.items():
        if kor in user_input:
            found_team = eng
            break # 첫 번째 팀을 찾으면 멈춤
    
    print(f"[DEBUG] 파싱된 날짜: {match_date}, 찾은 팀: {found_team}")

    if not found_team:
        return {"match_date": str(match_date), "home_team": None, "away_team": None}

    # API를 통해 홈/어웨이 정보 확정
    # team1 대신 found_team을 전달하여 해당 팀이 포함된 경기를 검색
    fixture = get_fixture_info(api_key, str(match_date), found_team)
    if fixture:
        print(f"[DEBUG] API에서 찾은 경기 정보: {fixture}")
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