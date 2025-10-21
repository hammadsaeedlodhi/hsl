import streamlit as st
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


# Load API key
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Streamlit setup
st.set_page_config(page_title="Conversational ChatBot")
st.title("🤖 Hammad Saeed lodhi Conversational Chatbot with Message History")

# Sidebar Controls
model_name = st.sidebar.selectbox(
    "Please Select Groq Model",
    [
        "qwen/qwen3-32b",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-20b"
    ]
)

temperature = st.sidebar.slider(
    "Temperature", 0.0, 1.0, 0.7
)

max_tokens = st.sidebar.slider(
    "Max Tokens", 50, 300, 150
)

# Initialize session state memory and history
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

if "history" not in st.session_state:
    st.session_state.history = []

# User input
user_input = st.chat_input("You: ")

if user_input:
    st.session_state.history.append(("user", user_input))

    llm = ChatGroq(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Build conversation chain with memory
    conv = ConversationChain(
        llm=llm,
        memory=st.session_state.memory,
        verbose=True
    )

    # Get AI response (memory is updated internally)
    ai_response = conv.predict(input=user_input)

    # Append assistant response to history
    st.session_state.history.append(("assistant", ai_response))

# Display chat history
for role, text in st.session_state.history:
    if role == "user":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)
