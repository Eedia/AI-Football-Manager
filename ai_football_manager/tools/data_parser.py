import json

def format_api_data_for_llm(api_data: dict, entity_type: str) -> str:
    
    if not api_dat:
        return ""
    
    formatted_string = ""

    if entity_type == "player":
        name = api_data.get("name", "알 수 없음")
        firstname = api_data.get("firstname", "")
        lastname = api.data.get("lastname", "")
        age = api_data.get("age", "알 수 없음")
        nationality = api_data.get("nationality", "알 수 없음")

        formatted_string += f"선수 이름: {firstname}{lasname}({name})\n"
        formatted_string += f"나이: {age}\n"
        formatted_string += f"국적: {nationality}\n\n"

        stats_by_league = api_data.get("stats_by_league", [])
        if stats_by_league:
            formatted_string += "--- 리그별 통계 ---\n"
            for stats in stats_by_league:
                formatted_string_string += f"  리그: {stats.get('league_name', '알 수 없음')} ({stats.get('league_country', '')})\n"
                formatted_string_string += f"  소속팀: {stats.get('team_name', '알 수 없음')}\n"
                formatted_string_string += f"  출전 경기: {stats.get('appearances', 'N/A')}\n"
                formatted_string_string += f"  출전 시간: {stats.get('minutes', 'N/A')}분\n"
                formatted_string_string += f"  총 득점: {stats.get('goals', 'N/A')}골\n"
                formatted_string_string += f"  어시스트: {stats.get('assists', 'N/A')}\n"
                formatted_string_string += f"  경고: {stats.get('yellow_cards', 'N/A')}회, 퇴장: {stats.get('red_cards', 'N/A')}회\n\n"

        else:
            formatted_string += "최근 시즌 통계 정보를 찾을 수 없습니다.\n"

    elif entity_type == "team":
        team_name = api_data.get("team_name", "알 수 없음")
        league_name = api_data.get("league_name", "알 수 없음")
        season = api.data.get("season", "알 수 없음")
        
        formatted_string_string += f"팀 이름: {team_name}\n"
        formatted_string_string += f"리그: {league_name} ({season} 시즌)\n\n"

        fixtures = api_data.get("fixtures", {})
        formatted_string_string += f"--- 경기 기록 ---\n"
        formatted_string_string += f"  총 경기: {fixtures.get('played', 'N/A')}\n"
        formatted_string_string += f"  승리: {fixtures.get('wins', {}).get('total', 'N/A')}\n"
        formatted_string_string += f"  무승부: {fixtures.get('draws', {}).get('total', 'N/A')}\n"
        formatted_string_string += f"  패배: {fixtures.get('loses', {}).get('total', 'N/A')}\n"
        
        goals = api_data.get("goals", {})   
        formatted_string_string += f"--- 득실 기록 ---\n"
        formatted_string_string += f"  득점: {goals.get('for', {}).get('total', 'N/A')}골\n"       
        formatted_string_string += f"  실점: {goals.get('against', {}).get('total', 'N/A')}골\n\n"

        clean_sheet = api_data.get("clean_sheet", {})
        formatted_string += f"클린 시트: {clean_sheet.get('total','N/A')}회\n"
        failed_to_score = api_data.get("failed_to_score", {})
        formatted_string += f"득점 실패 경기: {failed_to_score.get('total', 'N/A')}회\n"

    return formatted_string.strip()