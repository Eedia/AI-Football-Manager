from openai import OpenAI
from config import OPENAI_API_KEY
from utils import prompt_templates, token_manager
from agents import news_analysis_agent, prediction_agent, team_player_agent #도 여기에 있다고 가정

client = OpenAI(api_key=OPENAI_API_KEY)

model_name = 'gpt-4.1'

# 1. 각 에이전트별 도구(Tool) 함수 정의
# 이 함수들은 OpenAI 모델에게 어떤 기능을 수행하는지 설명하는 역할을 합니다.

def get_team_player_info_tool(query: str, chat_history: list):
    """
    축구 팀이나 선수에 대한 정보를 검색합니다.
    사용자가 특정 팀, 선수, 그들의 통계, 또는 이들과 관련된 일반적인 정보를 요청할 때 이 도구를 사용.
    """
    print("-> 팀/선수 정보 에이전트 호출 (Function Call)")
    return team_player_agent.get_team_player_info(query, chat_history) 

def analyze_news_tool(query: str, chat_history: list):
    """
    축구 뉴스를 분석하고 통찰력을 제공합니다.
    사용자가 최신 축구 이벤트에 대한 뉴스 분석, 요약 또는 의견을 요청할 때 이 도구를 사용.
    """
    print("-> 뉴스/분석 정보 에이전트 호출 (Function Call)")
    return news_analysis_agent.analyze_news(query, chat_history)

def predict_match_tool(query: str, chat_history: list):
    """
    축구 경기의 결과를 예측합니다.
    사용자가 경기 예측, 점수, 또는 승률을 요청할 때 이 도구를 사용.
    """
    print("-> 승부 예측 에이전트 호출 (Function Call)")
    return prediction_agent.predict_match(query, chat_history)

def handle_general_query_tool(query: str, chat_history: list):
    """
    다른 범주에 속하지 않는 일반적인 축구 관련 질문을 처리합니다.
    특정 데이터 검색이나 분석이 필요 없는 일반적인 대화나 질문에 이 도구를 사용.
    """
    print("-> 일반 응답 처리 (Function Call)")
    general_messages = [
        {"role": "system", "content": prompt_templates.GENERAL_SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    # 도구 호출 자체를 위한 토큰 관리는 메인 호출에서 처리하므로 여기서는 생략
    response = client.chat.completions.create(
        model=model_name,
        messages=general_messages,
        temperature=0.7 # 일반적인 응답을 위해 좀 더 창의적으로
    )
    return response.choices[0].message.content.strip()


# OpenAI API에 전달할 도구(Tool) 정의 목록
# 이 정보는 모델이 어떤 도구가 있고 어떻게 사용하는지 이해하는 데 사용.
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_team_player_info_tool",
            "description": "축구 팀이나 선수에 대한 정보를 검색합니다. 사용자가 특정 팀, 선수, 그들의 통계, 또는 이들과 관련된 일반적인 정보를 요청할 때 이 도구를 사용하십시오.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "사용자의 원래 질문."},
                    "chat_history": {
                        "type": "array",
                        "description": "현재 채팅 기록.",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant"]},
                                "content": {"type": "string"}
                            },
                            "required": ["role", "content"]
                        }
                    },
                },
                "required": ["query", "chat_history"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_news_tool",
            "description": "축구 뉴스를 분석하고 통찰력을 제공합니다. 사용자가 최신 축구 이벤트에 대한 뉴스 분석, 요약 또는 의견을 요청할 때 이 도구를 사용하십시오.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "사용자의 원래 질문."},
                    "chat_history": {
                        "type": "array",
                        "description": "현재 채팅 기록.",
                        "items": { 
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant"]},
                                "content": {"type": "string"}
                            },
                            "required": ["role", "content"]
                        }
                    },
                },
                "required": ["query", "chat_history"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predict_match_tool",
            "description": "축구 경기의 결과를 예측합니다. 사용자가 경기 예측, 점수, 또는 승률을 요청할 때 이 도구를 사용하십시오.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "사용자의 원래 질문."},
                    "chat_history": {
                        "type": "array",
                        "description": "현재 채팅 기록.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant"]},
                                "content": {"type": "string"}
                            },
                            "required": ["role", "content"]
                        }
                    },
                },
                "required": ["query", "chat_history"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "handle_general_query_tool",
            "description": "다른 범주에 속하지 않는 일반적인 축구 관련 질문을 처리합니다. 이 도구를 일반적인 대화나 특정 데이터 검색 또는 분석이 필요 없는 질문에 사용하십시오.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "사용자의 원래 질문."},
                    "chat_history": {
                        "type": "array",
                        "description": "현재 채팅 기록.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {"type": "string", "enum": ["user", "assistant"]},
                                "content": {"type": "string"}
                            },
                            "required": ["role", "content"]
                        }
                    },
                },
                "required": ["query", "chat_history"],
            },
        },
    },
]

# 도구 이름을 실제 파이썬 함수에 매핑
available_functions = {
    "get_team_player_info_tool": get_team_player_info_tool,
    "analyze_news_tool": analyze_news_tool,
    "predict_match_tool": predict_match_tool,
    "handle_general_query_tool": handle_general_query_tool,
}

def route_query(user_query: str, chat_history: list) -> str:
    # OpenAI 모델이 도구 사용 여부를 결정하도록 메시지 준비
    messages = [
        {"role": "system", "content": prompt_templates.ROUTER_SYSTEM_PROMPT}, # ROUTER_SYSTEM_PROMPT는 모델이 도구를 사용하도록 안내해야 합니다.
        {"role": "user", "content": user_query}
    ]

    # 전체 대화 턴에 대한 토큰 관리 (분류만을 위한 것이 아님)
    messages = token_manager.manage_history_tokens(
        messages, max_tokens=2000, model_name=model_name
    )

    try:
        print("[DEBUG] 라우팅 시작")
        # 2. 도구를 활성화하여 모델 호출
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools, # 정의된 도구 목록 제공
            tool_choice="auto", # 모델이 도구를 호출할지 또는 직접 응답할지 자동으로 결정
            stream=True # 최종 응답을 위해 스트리밍 기능 유지
        )

        # 3. 도구 호출 여부 확인을 위해 응답 처리
        # 모델이 도구를 호출하기로 결정하면, delta에 'tool_calls' 필드가 포함됩니다.
        # 직접 메시지인 경우 'content'에 포함됩니다.

        full_response_content = ""
        tool_calls = []

        print(f"[DEBUG] 라우팅 요청: {user_query}")
        for chunk in response:
            # print(f"[DEBUG] 라우팅 응답 청크: {chunk}")
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                # 도구 호출 축적
                if delta.tool_calls:
                    # print(f"[DEBUG] 도구 호출 델타: {delta.tool_calls}")
                    for tc in delta.tool_calls:
                        if len(tool_calls) <= tc.index:
                            tool_calls.append({"id": "", "function": {"arguments": "", "name": ""}})
                        
                        if tc.id:
                            tool_calls[tc.index]["id"] += tc.id
                        if tc.function.name:
                            tool_calls[tc.index]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments
                
                # 도구 호출이 없으면 콘텐츠 축적
                elif delta.content:
                    # print(f"[DEBUG] 콘텐츠 델타: {delta.content}")
                    full_response_content += delta.content

        # 도구 호출이 감지되면 실행
        if tool_calls:
            print(f"[DEBUG] 도구 호출 감지: {tool_calls}")
            # 도구 호출이 있는 경우, 첫 번째 도구 호출을 처리
            tool_call = tool_calls[0]
            function_name = tool_call["function"]["name"]
            function_args = {}
            try:
                # 도구 호출 인자를 JSON으로 디코딩
                import json
                function_args = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError as e:
                print(f"도구 인자 디코딩 오류: {e}")
                return "죄송합니다, 도구 호출 인자를 처리하는 데 문제가 발생했습니다."

            if function_name in available_functions:
                # 추출된 인자와 함께 도구 함수 실행
                # 도구 정의에 필요한 user_query와 chat_history를 전달
                print(f"도구 실행 중: {function_name} with args: {function_args}")
                
                # 도구가 'query'와 'chat_history'와 같은 특정 인자를 요구하고,
                # 모델이 이를 도구 호출 인자로 직접 제공하는 경우, 해당 인자를 사용
                # 그렇지 않은 경우, 라우팅 컨텍스트의 user_query와 chat_history를 기본값으로 사용.
                
                # 가장 안전한 방법은 컨텍스트 변수를 명시적으로 전달하는 것
                final_answer = available_functions[function_name](user_query, chat_history)
                return final_answer
            else:
                return "죄송합니다, 요청하신 작업을 처리할 수 있는 도구를 찾을 수 없습니다."
        else:
            # 도구 호출이 없으면 축적된 콘텐츠 반환
            print("[DEBUG] 도구 호출 없음, 직접 응답 반환.")
            if not full_response_content:
                # 어떤 이유로든 콘텐츠가 비어 있는 경우 (예: 모델이 응답하지 않기로 결정)
                return "현재 질문에 답변하기 어렵습니다."
            return full_response_content

    except Exception as e:
        print(f'라우팅 중 오류 발생: {e}')
        return "질문의 의도를 정확히 파악하기 어렵습니다. 다시 질문해주세요."
