from openai import OpenAI
from config import OPENAI_API_KEY
from utils import prompt_templates, token_manager
from agents import news_analysis_agent, prediction_agent, team_player_agent

client = OpenAI(api_key=OPENAI_API_KEY)

model_name = 'gpt-4.1'

# 1. 각 에이전트별 도구(Tool) 함수 정의
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
    이전 대화 맥락을 고려하여 자연스러운 대화를 제공합니다.
    """
    print("-> 일반 응답 처리 (Function Call)")
    
    # chat_history를 기반으로 메시지 구성
    messages = chat_history.copy() if chat_history else []
    
    # 시스템 메시지가 없으면 추가
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": prompt_templates.GENERAL_SYSTEM_PROMPT})
    
    # 현재 질문 추가
    messages.append({"role": "user", "content": query})
    
    # 토큰 관리로 대화 기록 조정
    messages = token_manager.manage_history_tokens(messages, max_tokens=3000)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"일반 응답 생성 중 오류 발생: {e}")
        return "죄송합니다. 응답 생성 중 문제가 발생했습니다. 다시 시도해주세요."

# OpenAI API에 전달할 도구(Tool) 정의 목록
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

def integrate_multiple_results(user_query: str, tool_results: list, chat_history: list) -> str:
    """
    다중 도구 호출 결과를 OpenAI를 통해 통합하여 일관된 응답을 생성합니다.
    """
    # 도구 결과들을 하나의 텍스트로 결합
    combined_results = "\n\n".join(tool_results)

    # print(combined_results)
    
    integration_prompt = f"""
사용자가 다음과 같이 질문했습니다: "{user_query}"

여러 AI 에이전트들이 각각 다음과 같은 정보를 제공했습니다:

{combined_results}

위의 정보들을 종합하여 사용자의 질문에 대한 통합적이고 일관된 답변을 제공해주세요.
만약 predict_match_tool이 호출되었다면, 경기 예측 결과를 포함하고(), 
get_team_player_info_tool이 호출되었다면, 팀이나 선수에 대한 정보를 포함하며 
analyze_news_tool이 호출되었다면, 뉴스 분석 결과를 포함해주세요. (링크도 포함)
handle_general_query_tool이 호출되었다면, 일반적인 응답을 포함해주세요.
각 정보를 적절히 연결하고, 중복되는 내용은 정리하며, 사용자가 이해하기 쉽도록 구성해주세요.
호출된 tool은 보여주지 말고, 통합된 답변만 제공해주세요.
답변은 친근하고 전문적인 톤으로 작성해주세요.
"""
    
    integration_messages = [
        {"role": "system", "content": "당신은 여러 AI 에이전트의 결과를 통합하여 일관된 답변을 제공하는 전문가입니다. 사용자에게 유용하고 명확한 통합 답변을 제공하세요."},
        {"role": "user", "content": integration_prompt}
    ]
    
    try:
        print("[DEBUG] 다중 결과 통합 중...")
        response = client.chat.completions.create(
            model=model_name,
            messages=integration_messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"결과 통합 중 오류: {e}")
        # 통합에 실패하면 개별 결과를 그대로 반환
        return f"다음은 각 분야별 정보입니다:\n\n{combined_results}"

def route_query(user_query: str, chat_history: list) -> str:
    # OpenAI 모델이 도구 사용 여부를 결정하도록 메시지 준비
    # chat_history를 기반으로 메시지 구성
    messages = chat_history.copy() if chat_history else []
    
    # 시스템 메시지가 없으면 추가
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": prompt_templates.ROUTER_SYSTEM_PROMPT})
    
    # 현재 사용자 질문 추가
    messages.append({"role": "user", "content": user_query})
    
    before_tokens = sum(token_manager.calculate_message_tokens(msg, model_name) for msg in messages)
   
    # 토큰 관리로 적절한 길이로 조정
    messages = token_manager.manage_history_tokens(
        messages, max_tokens=2000, model_name=model_name
    )

    after_tokens = sum(token_manager.calculate_message_tokens(msg, model_name) for msg in messages)
    print(f"[DEBUG] 메시지 토큰 수 조정: {before_tokens} -> {after_tokens}")
    
    try:
        print("[DEBUG] 라우팅 시작")
        # 도구를 활성화하여 모델 호출
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )

        # 도구 호출 여부 확인을 위해 응답 처리
        full_response_content = ""
        tool_calls = []

        print(f"[DEBUG] 라우팅 요청: {user_query}")
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                # 도구 호출 축적
                if delta.tool_calls:
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
                    full_response_content += delta.content

        # 도구 호출이 감지되면 실행
        if tool_calls:
            # print(f"[DEBUG] 도구 호출 감지: {tool_calls}")
            
            # 단일 도구 호출인 경우
            if len(tool_calls) == 1:
                tool_call = tool_calls[0]
                function_name = tool_call["function"]["name"]
                function_args = {}
                try:
                    import json
                    function_args = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError as e:
                    print(f"도구 인자 디코딩 오류: {e}")
                    return "죄송합니다, 도구 호출 인자를 처리하는 데 문제가 발생했습니다."

                if function_name in available_functions:
                    print(f"단일 도구 실행 중: {function_name}")
                    final_answer = available_functions[function_name](user_query, chat_history)
                    return final_answer
                else:
                    return "죄송합니다, 요청하신 작업을 처리할 수 있는 도구를 찾을 수 없습니다."
            
            # 다중 도구 호출인 경우
            else:
                print(f"[DEBUG] 다중 도구 호출 감지: {len(tool_calls)}개")
                tool_results = []
                
                for i, tool_call in enumerate(tool_calls):
                    function_name = tool_call["function"]["name"]
                    function_args = {}
                    try:
                        import json
                        function_args = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError as e:
                        print(f"도구 {i+1} 인자 디코딩 오류: {e}")
                        tool_results.append(f"도구 {i+1} 처리 중 오류가 발생했습니다.")
                        continue

                    if function_name in available_functions:
                        print(f"다중 도구 {i+1} 실행 중: {function_name}")
                        try:
                            result = available_functions[function_name](user_query, chat_history)
                            
                            if hasattr(result, '__iter__') and not isinstance(result, str):
                                # 스트림인 경우 텍스트로 변환
                                converted_result = ""
                                for chunk in result:
                                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                                        converted_result += chunk.choices[0].delta.content
                                tool_results.append(f"**{function_name} 결과:**\n{converted_result}")
                            else:
                                tool_results.append(f"**{function_name} 결과:**\n{result}")

                        except Exception as e:
                            print(f"도구 {function_name} 실행 오류: {e}")
                            tool_results.append(f"**{function_name}** 실행 중 오류가 발생했습니다.")
                    else:
                        tool_results.append(f"**{function_name}**을 찾을 수 없습니다.")
                
                # 다중 결과를 OpenAI를 통해 통합
                return integrate_multiple_results(user_query, tool_results, chat_history)
        else:
            # 도구 호출이 없으면 축적된 콘텐츠 반환
            print("[DEBUG] 도구 호출 없음, 직접 응답 반환.")
            if not full_response_content:
                return "현재 질문에 답변하기 어렵습니다."
            return full_response_content

    except Exception as e:
        print(f'라우팅 중 오류 발생: {e}')
        return "질문의 의도를 정확히 파악하기 어렵습니다. 다시 질문해주세요."