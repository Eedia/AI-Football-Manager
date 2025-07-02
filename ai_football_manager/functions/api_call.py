import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def openai_call():
    response = client.chat.completions.create(
       model=st.session_state.openai_model,
        messages=[
            {"role": m['role'], "content": m['content']}
            for m in st.session_state.messages
        ],
        stream=True
    )
    
    return response
                