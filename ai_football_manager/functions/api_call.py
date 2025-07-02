import streamlit as st
# from tool_call_handler import tools
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def web_search_4o(messages:list):
    response = client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=messages,
        tools=[{"type": "web_search_preview"}],
        stream=True
    )

    return response

def openai_call(messages:list):
    response = client.chat.completions.create(
        model=st.session_state.openai_model,
        messages=messages,
        stream=True
    )
    
    return response
                