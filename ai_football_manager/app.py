import streamlit as st
import functions.api_call as api
import json

def init_session_state():
    st.session_state.setdefault('openai_model', 'gpt-4.1')
    st.session_state.setdefault('messages', [])
    st.session_state.setdefault('current_menu', "menu1") # 추후 내용 변경

def main():
    init_session_state()
    st.header('AI Football Manager')
    
    st.sidebar.title("메뉴")
    selected_menu = st.sidebar.radio(
        "원하는 메뉴를 선택하세요:",
        ("menu1", "menu2", "menu3") # 추후 내용 변경
    )
    
    st.markdown(f'현재 메뉴는 "**{st.session_state.current_menu}**"입니다. 무엇이 궁금하신가요?')

    if st.session_state.current_menu != selected_menu:    
        st.session_state.current_menu = selected_menu
        if st.session_state.current_menu == "menu1" or st.session_state.current_menu == "menu2":
            st.session_state.openai_model = 'gpt-4o'
        st.session_state.messages = []
        st.rerun()

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
            messages= [{"role": m['role'], "content": m['content']} for m in st.session_state.messages]
            
            if st.session_state.openai_model == 'gpt-4o':
                stream = api.web_search_4o(messages)
            else:
                stream = api.openai_call(messages)
            
            # 스트리밍 응답 처리 (타이핑 효과)
            message_placeholder = st.empty()
            full_response = ""
            
            if stream:
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        full_response += (chunk.choices[0].delta.content or "")
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

if __name__ == "__main__":
    main()