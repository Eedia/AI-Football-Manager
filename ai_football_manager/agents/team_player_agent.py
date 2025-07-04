from tools import sports_data_api, data_parser
from utils import prompt_templates, token_manager
from config import OPENAI_API_KEY
from openai import OpenAI
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def _generate_response(messages: list, stream: bool = True) -> str:
    # 메시지를 보내 응답을 생성하는 내부 함수

    try:
        if stream:
            return client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True
            )
        
        else:
            response = client.chat.completions.create(
                model='gpt-4.1',
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"응답 생성 중 오류 발생: {e}")
        return "선수/팀 정보 검색 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."

def get_team_player_info(user_query: str, chat_history: list) -> str:
    # 사용자의 축구 팀 또는 선수 정보 관련 질문을 처리하고 답변을 반환

    messages = token_manager.manage_history_tokens(chat_history, max_tokens=4000)
    messages.insert(0, {"role": "system", "content": prompt_templates.TEAM_PLAYER_SYSTEM_PROMPT})
    messages.append({"role": "user", "content": user_query})

    extraction_prompt = f"""
    사용자의 질문에서 축구 선수 또는 팀의 이름과 관련 시즌(연도)을 JSON형식으로 추출해.
    질문이 선수에 대한 것이라면 "type": "player", 팀에 대한 것이라면 "type": "team"으로 지정해.
    이름은 정확하게 추출하고, 시즌 정보가 없다면 "season": null,로, type을 알 수 없으면 "type": "unknown"으로 해.
    예시:
    - "손흥민 최근 골 기록은?" => {{"type": "player", "name": "Son Heung-min", "season": null}}
    - "첼시 이번 시즌 리그 순위" => {{"type": "team", "name": "Chelsea", "season": null}}
    - "2022년 홀란드 득점왕이었어?" => {{"type": "player", "name": "Erling Haaland", "season": 2022}}
    - "맨체스터 시티 2023년 성적 알려줘" => {{"type": "team", "name": "Manchester City", "season": 2023}}
    - "오늘 날씨 어때?" => {{"type": "unknown", "name": null, "season": null}}

    사용자 질문: {user_query}
    """

    extraction_messages = [
        {"role": "system", "content": "너는 사용자 질문에서 핵심 정보를 추출하여 JSON으로 반환하는 AI다."},
        {"role": "user", "content": extraction_prompt}
    ]

    extracted_info_json = _generate_response(extraction_messages, stream=False)

    try:
        extracted_info = json.loads(extracted_info_json)
        entity_type = extracted_info.get("type")
        name = extracted_info.get("name")
        season = extracted_info.get("season")
    except json.JSONDecodeError:
        print(f"LLM이 생성한 JSON 파싱 실패: {extracted_info_json}")
        entity_type = "unknown"
        name = None
        season = None

    if entity_type == "unknown" or not name:
        return "죄송합니다. 질문에서 어떤 선수나 팀 정보를 찾으시는지 명확하게 파악하기 어렵습니다."
    
    raw_api_data = {}
    if entity_type == "player":
        print(f"선수 통계 조회: {name}, 시즌: {season}")
        raw_api_data = sports_data_api.get_player_stats(name, season)
    elif entity_type == "team":
        print(f"팀 통계 조회: {name}, 시즌: {season}")
        raw_api_data = sports_data_api.get_team_stats(name, season)

    if not raw_api_data:
        return "죄송합니다. 요청하신 선수/팀에 대한 최신 정보를 API에서 찾을 수 없습니다."
    
    parsed_info_for_llm = data_parser.format_api_data_for_llm(raw_api_data, entity_type)

    if not parsed_info_for_llm:
        return "가져온 데이터를 해석하여 답변을 생성하는 데 문제가 발생했습니다."
    
    final_messages = [
        {"role": "system", "content": prompt_templates.TEAM_PLAYER_SYSTEM_PROMPT},
        {"role": "user", "content": f"""사용자 질문: {user_query}\n\n
                                        다음은 조회된 선수/팀 정보입니다:\n{parsed_info_for_llm}\n\n
                                        이 정보를 바탕으로 사용자 질문에 대해 상세하고 명확하게 답변해주세요.                                
                                        불필요한 서론 없이 핵심 정보만 요약하여 전달하세요."""}
    ]

    final_messages = token_manager.manage_history_tokens(final_messages, max_tokens=4000)

    final_answer = _generate_response(final_messages, stream=True)
     
    return final_answer