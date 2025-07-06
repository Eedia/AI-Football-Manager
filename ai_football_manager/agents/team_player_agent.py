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
                model='gpt-4o',
                messages=messages,
                stream=True,
                temperature=1.2
            )

        else:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"응답 생성 중 오류 발생: {e}")
        return "선수/팀 정보 검색 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."

def get_team_player_info(user_query: str, chat_history: list) -> str:
    # 사용자의 축구 팀 또는 선수 정보 관련 질문을 처리하고 답변을 반환

    # 1. 정보 추출 단계 (기존 방식 유지)
    extraction_prompt = f"""
    사용자의 질문에서 축구 선수 또는 팀의 이름과 관련 시즌(연도)을 JSON형식으로 추출해.
    질문이 선수에 대한 것이라면 "type": "player", 팀에 대한 것이라면 "type": "team"으로 지정해.
    정보가 없다면 null로 처리해.
    
    이전 대화 내용도 참고해서 맥락을 이해해:
    - "그 선수", "그 팀"이라고 하면 이전에 언급된 선수/팀을 의미
    - "그것보다 더 자세히"라고 하면 이전 질문과 동일한 대상에 대한 추가 정보 요청
    
    예시:
    - "손흥민 최근 골 기록은?" => {{"type": "player", "name": "Son Heung-min", "team": null, "season": null}}
    - "토트넘의 손흥민 2023-2024 시즌 기록" => {{"type": "player", "name": "Son Heung-min", "team": "Tottenham", "season": 2023}}
    - "맨체스터 시티 2023년 성적 알려줘" => {{"type": "team", "name": "Manchester City", "team": null, "season": 2023}}
    
    사용자 질문: {user_query}
    """

    # 맥락 정보 추출을 위해 chat_history도 포함
    extraction_messages = chat_history.copy() if chat_history else []
    
    # 시스템 메시지가 없으면 추가
    if not extraction_messages or extraction_messages[0].get("role") != "system":
        extraction_messages.insert(0, {
            "role": "system", 
            "content": "너는 사용자 질문에서 핵심 정보를 추출하여 JSON으로 반환하는 AI다. 이전 대화 맥락을 참고해서 '그 선수', '그 팀' 같은 표현을 이해해야 한다."
        })
    
    extraction_messages.append({"role": "user", "content": extraction_prompt})

    # 토큰 관리 (추출 단계)
    extraction_messages = token_manager.manage_history_tokens(extraction_messages, max_tokens=2000)

    extracted_info_json = _generate_response(extraction_messages, stream=False)
    if '```' in extracted_info_json:
        start_index = extracted_info_json.find('{')
        end_index = extracted_info_json.find('}')
        if start_index != -1 and end_index != -1:
            extracted_info_json = extracted_info_json[start_index:end_index+1]

    try:
        extracted_info = json.loads(extracted_info_json)
        entity_type = extracted_info.get("type")
        name = extracted_info.get("name")
        season = extracted_info.get("season")
        team_name = extracted_info.get("team")
    except json.JSONDecodeError:
        print(f"LLM이 생성한 JSON 파싱 실패: {extracted_info_json}")
        entity_type = "unknown"
        name = None
        season = None

    if entity_type == "unknown" or not name:
        return "죄송합니다. 질문에서 어떤 선수나 팀 정보를 찾으시는지 명확하게 파악하기 어렵습니다. 이전 대화 내용을 참고하여 다시 질문해주시거나, 구체적인 선수명이나 팀명을 알려주세요."
    
    # 2. API 데이터 조회
    raw_api_data = {}
    if entity_type == "player":
        print(f"선수 통계 조회: {name}, 팀: {team_name}, 시즌: {season}")
        raw_api_data = sports_data_api.get_player_stats(name, season, team_name)
    
    elif entity_type == "team":
        print(f"팀 통계 조회: {name}, 시즌: {season}")
        raw_api_data = sports_data_api.get_team_stats(name, season)

    if not raw_api_data:
        # API에서 데이터를 가져오지 못한 경우
        # 대체로 웹 검색을 통해 정보를 제공
        response = client.responses.create(
            model='gpt-4o',
            tools=[{"type": "web_search_preview"}],
            input = user_query
        )
        return (response.output_text)

    # 3. 최종 답변 생성 - chat_history 포함
    parsed_info_for_llm = data_parser.format_api_data_for_llm(raw_api_data, entity_type)

    if not parsed_info_for_llm:
        return "가져온 데이터를 해석하여 답변을 생성하는 데 문제가 발생했습니다."
    
    # chat_history를 기반으로 최종 메시지 구성
    final_messages = chat_history.copy() if chat_history else []
    
    # 시스템 메시지가 없으면 추가
    if not final_messages or final_messages[0].get("role") != "system":
        final_messages.insert(0, {"role": "system", "content": prompt_templates.TEAM_PLAYER_SYSTEM_PROMPT})
    
    # 현재 질문과 조회된 데이터 추가
    detailed_query = f"""사용자 질문: {user_query}

        다음은 조회된 선수/팀 정보입니다:
        {parsed_info_for_llm}

        이 정보를 바탕으로 사용자 질문에 대해 상세하고 명확하게 답변해주세요.
        이전 대화 내용과 연관이 있다면 그 맥락도 고려해서 답변해주세요.
        불필요한 서론 없이 핵심 정보만 요약하여 전달하세요."""
    
    final_messages.append({"role": "user", "content": detailed_query})

    # 토큰 관리로 대화 기록 조정
    final_messages = token_manager.manage_history_tokens(final_messages, max_tokens=4000)

    final_answer = _generate_response(final_messages, stream=True)
    
    return final_answer