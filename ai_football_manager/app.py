import streamlit as st
import functions.api_call as api

def main():
    st.session_state.setdefault('openai_model', 'gpt-4.1')
    st.session_state.setdefault('messages', [])

    st.title('AI Football Manager')

    for msg in st.session_state.messages:
        with st.chat_message(name=msg['role'], avatar=msg['role']):
            st.markdown(msg['content'])

    if prompt := st.chat_input("무엇이 궁금하신가요?"):
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = api.openai_call()
            
            # 스트리밍 응답 처리 (타이핑 효과)
            message_placeholder = st.empty()
            full_response = ""
            for chunk in stream:
                full_response += (chunk.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

if __name__ == "__main__":
    main()