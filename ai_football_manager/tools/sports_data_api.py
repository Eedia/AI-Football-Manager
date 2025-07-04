# print는 확인을 위해서 사용

import requests
from config import X_RAPIDAPI_KEY
import json

API_FOOTBALL_BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"

def _call_api_football(endpoint: str, params: dict) -> dict:
    # RapidAPI의 API-Football을 호출하는 내부 함수
    
    api_key = X_RAPIDAPI_KEY

    if not api_key:
        print("경고: RapidAPI 키가 설정되지 않음. API-Football 호출 수행 불가.")
        return {}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host" : API_FOOTBALL_HOST
    }

    url = f"{API_FOOTBALL_BASE_URL}/{endpoint}"

    try:
        print(f"API-Football 요청: {url} (params: {params})")
        response = response.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("errors"):
            print(f"API-Football 오류 응답: {data['errors']}")
            return {}

        return data.get("response", {})

    except requests.exceptions.RequstException as e:
        print(f"API-Football 호출 중 오류 발생: {e}")
        return {}
    
    except json.JSONDecodeError as e:
        print(f"API-Football 응답 파싱 중 오류 발생: {e}")
        return {}

    except Exception as e:
        print(f"API-Football 호출 중 예상치 못한 오류 발생: {e}")
        return {}

def get_player_stats(player_name: str, season: int = None) -> dict:
    # 선수 이름 기반으로 해당 선수의 통계 조회
    # 선수 ID를 먼저 찾은 후 해당 ID로 통계를 가져옴
    
    search_params = {"search": player_name}
    if season:
        search_params["season"] = season
    
    player_search_results = _call_api_football("players", search_params)

    player_id = None
    if player_search_results and player_search_results.get("response"):
        for player_info in player_search_results["response"]:
            if player_info.get("player", {}).get("name").lower() == player_name.lower():
                player_id = player_info.get("player",{}).get("id")
                print(f"선수 '{player_name}' ID 발견: {player_id}")
                break
        
        if not player_id and player_search_results["response"]:
            player_id = player_search_results["response"][0].get("player", {}).get("id")
            print(f"선수 '{player_name}'의 정확한 ID를 찾지 못하여 첫번째 결과 ID: {player_id} 사용")

        if not player_id:
            print(f"선수 '{player_name}'의 ID를 찾을 수 없음.")
            return {}

        stats_params = {"id": player_id}
        if season:
            stats_params["season"] = season
        else:
            from datetime import datetime
            stats_params["season"] = datetime.now().year
        
        player_stats_results = _call_api_football("players", stats_params)

    if player_search_results and player_search_results.get("response"):
        player_data = player_stats_results["response"][0].get("player", {})
        statistics = player_search_results["response"][0].get("statistics", [])

        parsed_stats = {
            "name": player_data.get("name"),
            "firstname": player_data.get("firstname"),
            "lastname": player_data.get("lastname"),
            "age": player_data.get("age"),
            "nationality": player_data.get("nationality"),
            "photo": player_data.get("photo"),
            "stats_by_league": []
        }

        for stat_entry in statistics:
            league = stat_entry.get("league", {})
            team = stat_entry.get("team", {})
            games = stat_entry.get("games", {})
            goals = stat_entry.get("goals", {})
            cards = stat_entry.get("cards", {})
        
            parsed_stats["stats_by_league"].append({
                "league_name": league.get("name"),
                "league_country": league.get("country"),
                "team_name": team.get("name"),
                "appearances": games.get("appearances"),
                "minutes": games.get("minutes"),
                "goals": goals.get("total"),
                "assists": goals.get("assists"),
                "red_cards": cards.get("red"),
                "yellow_cards": cards.get("yellow")
            })

        return parsed_stats
    return {}

def get_team_stats(team_name: str, season: int = None) -> dict:
    # 팀 이름을 기반으로 해당 팀의 통계 조회
    # 팀 ID를 먼저 찾은 후 해당 ID로 통계를 가져옴

    search_params = {"search": team_name}
    team_search_results = _call_api_football("teams", search_params)

    team_id = None
    if team_search_results and team_search_results.get("response"):
        for team_info in team_search_results["response"]:
            if team_info.get("team", {}).get("name").lower() == team_name.lower():
                team_id = team_info.get("team",{}).get("id")
                print(f"팀 '{team_name}' ID 발견: {team_id}")
                break
        
        if not team_id and team_search_results["response"]:
            team_id = team_search_results["response"][0].get("team", {}).get("id")
            print(f"팀 '{team_name}'의 정확한 ID를 찾지 못하여 첫번째 결과 ID: {team_id} 사용")

        if not team_id:
            print(f"팀 '{team_name}'의 ID를 찾을 수 없음.")
            return {}
    
        stats_params = {"id": team_id}
        if season:
            stats_params["season"] = season
        else:
            from datetime import datetime
            stats_params["season"] = datetime.now().year
        
        team_stats_results = _call_api_football("teams/statistics", stats_params)

    if team_search_results and team_search_results.get("response"):
        stats = team_stats_results["response"]

        parsed_stats = {
            "team_id": stats.get("team", {}).get("id"),
            "team_name": stats.get("team", {}).get("name"),
            "league_name": stats.get("league", {}).get("name"),
            "season": stats.get("league", {}).get("season"),
            "fixtures": stats.get("fixtures", {}),  # 경기 수
            "goals": stats.get("goals", {}),
            "clean_sheet": stats.get("clean_sheet", {}),
            "failed_to_score": stats.get("failed_to_score", {})
        }
        return parsed_stats
    return {}   