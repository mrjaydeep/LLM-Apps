from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model=genai.GenerativeModel("gemini-pro")
chat=model.start_chat(history=[])

def get_gemini_response(question):
    response=chat.send_message(question,stream=True)
    return response


st.set_page_config(page_title="Q&A Bot")

st.header("Gemini LLM App")

if'chat_history' not in st.session_state:
    st.session_state["chat_history"]= []
    
input=st.text_input("Input: ",key="input")

submit= st.button("Ask the question")

if submit and input:
    response=get_gemini_response(input)
    #add user query and response to chat history
    st.session_state["chat_history"].append(("user_query",input))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot",chunk.text))
        
st.subheader("Chat History")

for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")