import warnings
import os
import logging

# 모든 경고 메시지 숨기기
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# 로깅 레벨을 ERROR로 설정하여 INFO, WARNING 메시지 차단
logging.getLogger().setLevel(logging.ERROR)

import streamlit as st
from agents import router_agent
import openai

# soccerdata 관련 로깅 완전 차단
for name in ['soccerdata', 'understat', 'pandas', 'sklearn', 'urllib3', 'requests']:
    logging.getLogger(name).setLevel(logging.ERROR)
    logging.getLogger(name).disabled = True

# 모든 기존 로거들 차단
for name in logging.root.manager.loggerDict:
    if any(lib in name.lower() for lib in ['soccerdata', 'understat', 'pandas', 'sklearn']):
        logging.getLogger(name).setLevel(logging.ERROR)
        logging.getLogger(name).disabled = True

def init_session_state():
    st.session_state.setdefault('openai_model', 'gpt-4.1')
    st.session_state.setdefault('messages', [])

def main():
    init_session_state()
    st.header('AI Football Manager')
    st.image('./ai_football_manager/images/soccer.jpg')
    
    with st.chat_message(name="assistant", avatar="assistant"):
        st.markdown("무엇이 궁금하신가요?")

    for msg in st.session_state.messages:
        with st.chat_message(name=msg['role'], avatar=msg['role']):
            st.markdown(msg['content'])

    
    if prompt := st.chat_input("메시지를 입력하세요!"):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message(name="user", avatar="user"):
            st.markdown(prompt)

        with st.chat_message(name="assistant", avatar="assistant"):
            current_chat_history = [{"role": m['role'], "content": m['content']} for m in st.session_state.messages]
            
            message_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("생각 중입니다..."):
                response_stream_from_agent = router_agent.route_query(prompt, current_chat_history)

                if isinstance(response_stream_from_agent, openai.Stream): 
                    print("스트리밍 응답을 받는 중...")
                    for chunk in response_stream_from_agent:
                        if chunk and chunk.choices and chunk.choices[0].delta:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                full_response += (chunk.choices[0].delta.content or "")
                                message_placeholder.markdown(full_response + "▌")
                
                    message_placeholder.markdown(full_response)

                else:
                    print("비스트리밍 응답을 받는 중...")
                    full_response = response_stream_from_agent
                    message_placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

if __name__ == "__main__":
    main()
