import tiktoken

def clean_chat_history(chat_history: list) -> list:
    """대화 기록에서 불필요한 내용 제거 및 정리"""
    if not chat_history:
        return []
    
    cleaned = []
    for msg in chat_history:
        if msg.get("role") in ["user", "assistant", "system"]:
            # 내용이 너무 길면 요약
            content = msg.get("content", "")
            if len(content) > 1000:
                content = content[:500] + "...[요약됨]..." + content[-500:]
            
            cleaned.append({
                "role": msg["role"],
                "content": content
            })
    return cleaned

def get_token_count(text: str, model_name: str = "gpt-4o") -> int:
    """주어진 텍스트의 토큰 수 계산"""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
    except KeyError:
        # 모델 이름을 찾을 수 없을 경우 기본 인코딩 사용
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"토큰 계산 오류: {e}")
        # 안전한 fallback: 대략적인 추정
        return len(text) // 3

def calculate_message_tokens(message: dict, model_name: str) -> int:
    """메시지 구조에 맞는 정확한 토큰 계산"""
    try:
        # role 토큰
        role_tokens = get_token_count(message.get("role", ""), model_name)
        
        # content 토큰
        content_tokens = get_token_count(message.get("content", "") or "", model_name)
        
        # ChatML 포맷 오버헤드 (약 4-6 토큰)
        structure_overhead = 6
        
        return role_tokens + content_tokens + structure_overhead
        
    except Exception as e:
        print(f"메시지 토큰 계산 오류: {e}")
        return len(str(message)) // 3

def manage_history_tokens(messages: list, max_tokens: int, model_name: str = "gpt-4o", for_classification: bool = False):
    """대화 기록 메시지 리스트의 토큰 수를 관리하여 최대 토큰 수를 초과하지 않도록 함"""
    
    # 입력 유효성 검사
    if not isinstance(messages, list) or not messages or max_tokens <= 0:
        return []
    
    try:
        # 자동으로 대화 기록 정리
        messages = clean_chat_history(messages)
        
        # 시스템 메시지 처리
        system_tokens = 0
        processed_messages = []
        
        if messages and messages[0].get("role") == "system":
            sys_msg_content = messages[0].get("content", "")
            system_tokens = get_token_count(sys_msg_content, model_name)
            processed_messages = [messages[0]]
            chat_history_only = messages[1:]
        else:
            chat_history_only = messages
        
        available_tokens = max_tokens - system_tokens
        
        # 분류 모드일 때 특별 처리
        if for_classification and chat_history_only:
            last_user_message = chat_history_only[-1]
            last_user_tokens = calculate_message_tokens(last_user_message, model_name)
            
            if system_tokens + last_user_tokens <= max_tokens:
                if processed_messages:  # 시스템 메시지가 있는 경우
                    return processed_messages + [last_user_message]
                else:
                    return [last_user_message]
            else:
                # 토큰 초과시 오류 메시지
                error_msg = {"role": "user", "content": "질문이 너무 길어 처리할 수 없습니다."}
                if processed_messages:
                    return processed_messages + [error_msg]
                else:
                    return [error_msg]
        
        # 일반 모드: 역순으로 메시지 선택
        accumulated_tokens = 0
        temp_messages = []
        
        for i in range(len(chat_history_only) - 1, -1, -1):
            msg = chat_history_only[i]
            msg_tokens = calculate_message_tokens(msg, model_name)
            
            if accumulated_tokens + msg_tokens <= available_tokens:
                temp_messages.insert(0, msg)
                accumulated_tokens += msg_tokens
            else:
                break
        
        return processed_messages + temp_messages
        
    except Exception as e:
        print(f"토큰 관리 중 오류 발생: {e}")
        # 오류 발생시 최소한의 안전한 반환
        if messages:
            return [messages[-1]]  # 최신 메시지만 반환
        return []