from openai import OpenAI
from config import OPENAI_API_KEY
from utils import prompt_templates

client = OpenAI(api_key=OPENAI_API_KEY)

# print 관련 문은 실행 확인을 위해 사용


def _call_for_classifcation(messages: list) -> str:
    # 메시지를 보내 질문 분류 결과를 받아오는 내부함수
    try:
        response = client.chat.complications.create(
            model='gpt-4.1',
            messages=messages,
            temperature=0.0     # 정확성 우선
            max_tokens=50       # 분류 결과는 짧게
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f'분류 중 오류 발생: {e}')
        return "ERROR_CLASSIFICATION_FAILED'

def route_query(user_query: str, chat_history: list) -> str:
    # 최종 답변을 받아 반환하는 메인 라우팅 함수
    
    classification_messages=[
        {"role": "system", "content": prompt_templates.ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    # 토큰 관리 유틸리티를 추가하면 비용절감 가능 -> 일단 나중에

    print(f"질문 분류 중: '{user_query}'") 
    classification_result = _call_for_classifcation(classification_messages)

    if classification_result == "ERROR_CLASSIFICATION_FAILED" OR classification_result not in ["TEAM_PLAYER","NEWS_ANALYSIS","PREDICTION","GENERAL"]:
        return "질문의 의도를 정확히 파악하기 어렵습니다. 다시 질문해주세요."
    
    # 분류 결과에 따라 적절한 전문 에이전트에게 위임
    finial_response = ""
    
    if classification_result == "TEAM_PLAYER":
        print("-> 팀/선수 정보 에이전트 호출")
        # finial_response = team_player_agent.get_team_player_info(user_query, chat_history)

    elif classification_result == "NEWS_ANALYSIS":
        print("-> 뉴스/분석 정보 에이전트 호출")
        # finial_response = news_analysis_agent.analyze_news(user_query, chat_history)
    
    elif classification_result == "PREDICTION":
        print("-> 승부 예측 에이전트 호출")
        # finial_response = prediction_agent.predict_match(user_query, chat_history)
    
    elif classification_result == "GENERAL":
        print("-> 일반 응답 처리")
        general_messages = [
            {"role": "system", "content": prompt_templates.GENERAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]
        finial_response = _call_for_classifcation(general_messages)
        if finial_response == "ERROR_CLASSIFICATION_FAILED":
            finial_response = "현재 질문에 답변하기 어렵습니다."
    
    else:
        finial_response = "질문 분류에 실패했습니다. 다시 시도해주세요."

    return finial_response