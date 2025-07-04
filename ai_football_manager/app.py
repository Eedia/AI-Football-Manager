import streamlit as st
from types import GeneratorType
from agents import router_agent


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

                if isinstance(response_stream_from_agent, GeneratorType):
                    for chunk in response_stream_from_agent:
                        if chunk and chunk.choices and chunk.choices[0].delta:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                full_response += (chunk.choices[0].delta.content or "")
                                message_placeholder.markdown(full_response + "▌")
                
                    message_placeholder.markdown(full_response)

                else:
                    full_response = response_stream_from_agent
                    message_placeholder.markdown(full_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })

if __name__ == "__main__":
    main()