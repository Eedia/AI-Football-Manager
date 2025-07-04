import tiktoken

def get_token_count(text: str, model_name: str = "gpt-4o") -> int:
    # 주어진 텍스트 토큰 수 계산
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
  
    except KeyError:
        # 모델 이름을 찾을 수 없을 경우
        encoding = tiktoken.get_encoding("cl100k_base")  # 기본 인코딩
        return len(encoding.encode(text))


def manage_history_tokens(messages: list, max_tokens: int, model_name: str = "gpt-4o", for_classification: bool = False):
    # 대화 기록 메시지 리스트의 토큰 수 를 관리 -> 최대 토큰 수를 초과하지 않도록 함
    sys_msg_content = ""
    if messages and messages[0]["role"] == "system":
        sys_msg_content = messages[0]["content"]
        current_tokens = get_token_count(sys_msg_content, model_name)
        processed_messages = [messages[0]]
        available_chat_tokens = max_tokens - current_tokens
        chat_history_only = messages[1:]
  
    else:
        current_tokens = 0
        processed_messages = []
        available_chat_tokens = max_tokens
        chat_history_only = messages

    if for_classification and chat_history_only:
        last_user_message = chat_history_only[-1]
        last_user_tokens = get_token_count(last_user_message["content"], model_name)

        if current_tokens + last_user_tokens <= max_tokens:
            if messages and messages[0]["role"] == "system":
                return [messages[0], last_user_message]
                
            else:
                return [last_user_message]        
        else:
            if messages and messages[0]["role"] == "system":
                return [messages[0], {"role": "user", "content": "질문이 너무 길어 처리할 수 없음."}]
            else:    
                return [messages[0], {"role": "user", "content": "질문이 너무 길어 처리할 수 없음."}]

    temp_messages = []
    for i in range(len(chat_history_only) - 1, -1, -1):  # 마지막 메시지부터 역순으로
        msg = chat_history_only[i]
        # 각 메시지당 role, content 키 등에 사용되는 약 4토큰 추가
        msg_tokens = get_token_count(msg["content"], model_name) + 4

        if current_tokens + msg_tokens <= available_chat_tokens:
            temp_messages.insert(0, msg)  # 최신 메시지를 앞에 추가
            current_tokens += msg_tokens

        else:
            break

    if processed_messages:
        return processed_messages + temp_messages
    else:
        return temp_messages