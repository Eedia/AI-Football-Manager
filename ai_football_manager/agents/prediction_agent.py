from openai import OpenAI
from config import OPENAI_API_KEY
from utils import prompt_templates, token_manager
from tools import prediction_tools

client = OpenAI(api_key=OPENAI_API_KEY)

def _generate_response(messages: list , stream: bool = True) -> str:
    """OpenAI API를 호출하여 응답을 생성하는 함수"""
    try:
        if stream:
            return client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                temperature=0.5   ,  # 약간의 창의성 허용
                stream=stream      # 스트리밍 모드 활성화
            )
        else:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                temperature=0.5,   # 약간의 창의성 허용
                max_tokens=500     # 최대 토큰 수 지정
            )
            return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"응답 생성 중 오류 발생: {e}")
        return "경기 예측 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요."

def predict_match(user_query: str, chat_history: list) -> str:
    """
    사용자의 경기 예측 관련 질문을 처리하고 답변을 반환하는 메인 함수
    """
    print(f"경기 예측 요청: '{user_query}'")
    
    try:
        # 1. 모델 기반 예측 수행
        prediction_result = prediction_tools.get_match_prediction(user_query, chat_history)
        
        if prediction_result is None:
            return "경기 정보를 찾을 수 없습니다. 날짜와 팀명을 정확히 입력해주세요. (예: '2025년 5월 18일 아스널과 뉴캐슬 경기 예측해줘')"
        
        # 2. chat_history를 기반으로 메시지 구성
        messages = chat_history.copy() if chat_history else []
        
        # 시스템 메시지가 없으면 추가
        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": prompt_templates.PREDICTION_SYSTEM_PROMPT})
        
        # 예측 결과를 포함한 현재 질문 추가
        detailed_query = f"""
            사용자 질문: {user_query}

            경기 예측 결과:
            - 경기: {prediction_result['HomeTeam']} vs {prediction_result['AwayTeam']}
            - 경기 날짜: {prediction_result['MatchDate']}
            - 예측 결과: {prediction_result['Pred_Result']}
            - 원정팀 승리 확률: {prediction_result['AwayWin_Prob']:.1%}
            - 홈팀 승리 확률: {(1 - prediction_result['AwayWin_Prob']):.1%}

            추가 정보:
            - 홈팀 Elo: {prediction_result.get('HomeElo', 'N/A')}
            - 원정팀 Elo: {prediction_result.get('AwayElo', 'N/A')}
            - Elo 차이: {prediction_result.get('elo_diff', 'N/A')}

            위 데이터를 바탕으로 전문적이고 흥미로운 경기 예측 분석을 제공해주세요.
            예측 근거, 주의할 점, 경기 관전 포인트 등을 포함해주세요.
        """
        
        messages.append({"role": "user", "content": detailed_query})
        
        # 토큰 관리로 대화 기록 조정
        messages = token_manager.manage_history_tokens(messages, max_tokens=4000)
        
        # 3. AI 해설 생성
        ai_analysis = _generate_response(messages, stream=True)
        
        return ai_analysis
        
    except Exception as e:
        print(f"경기 예측 중 오류 발생: {e}")
        return "경기 예측 중 문제가 발생했습니다. 입력 형식을 확인하고 다시 시도해주세요."