import streamlit as st
import io
import re
from contextlib import redirect_stdout

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.wikipedia import WikipediaTools
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv

# Set page configuration as the very first Streamlit command
st.set_page_config(page_title="Ayurvedic Medicine Assistant", layout="wide")

# Load environment variables
load_dotenv()

# Sidebar configuration
st.sidebar.title("Important Information")
st.sidebar.markdown("**🚑Ambulance Number (India):** 108")
st.sidebar.markdown("**🏋🏻Diet Plan:** [Click here](https://www.healthline.com/nutrition/best-diet-plans)")
st.sidebar.markdown("**💪Enhance Immunity:** [Click here](https://www.health.harvard.edu/staying-healthy/how-to-boost-your-immune-system)")

# Initialize the medicine assistant agent with bullet point instructions
medicine_agent = Agent(
    name="Ayurvedic Medicine Assistant",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[WikipediaTools(), DuckDuckGo()],
    instructions=[
        "You are a medical assistant providing general health information and ayurvedic medication recommendations based on established medical guidelines.",
        "When a user enters their symptoms, identify the relevant symptoms and map them to common ayurvedic medication options.",
        "Format your response as a list of bullet points. For each symptom, include its recommended ayurvedic medication and usage instructions/dosage. For example:",
        "   - **Cold**: Recommend [medication] with dosage [instructions].",
        "   - **Headache**: Recommend [medication] with dosage [instructions].",
        "Include a clear disclaimer: 'I am not a doctor. This information is for general informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.'",
        "If symptoms are severe, ambiguous, or concerning, advise the user to seek professional medical help immediately.",
        "Encourage the user to consult a healthcare professional before taking any medication."
    ],
    show_tool_calls=True,
    markdown=True,
)

# Utility functions to clean ANSI escape sequences and box-drawing characters
def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def remove_box_drawing(text):
    box_chars = "┏┓┗┛┃━"
    for ch in box_chars:
        text = text.replace(ch, "")
    return text

def clean_output(text):
    text = strip_ansi_codes(text)
    text = remove_box_drawing(text)
    return text

# Initialize session state for chat history if not already set
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a placeholder container for the chat history
chat_container = st.empty()

# Function to render chat messages in a fixed-height scrollable container
def display_chat_history():
    chat_html = '<div style="height: 500px; overflow-y: scroll; padding: 10px; border: 1px solid #ddd;">'
    for message in st.session_state.messages:
        if message["sender"] == "user":
            chat_html += (
                f'<div style="text-align: right; background-color: #DCF8C6; color: black; '
                f'padding: 10px; border-radius: 10px; margin: 5px 0;">{message["text"]}</div>'
            )
        else:
            chat_html += (
                f'<div style="text-align: left; background-color: #F1F0F0; color: black; '
                f'padding: 10px; border-radius: 10px; margin: 5px 0;">{message["text"]}</div>'
            )
    chat_html += '</div>'
    chat_container.markdown(chat_html, unsafe_allow_html=True)

# Main UI setup
st.title("Ayurvedic Medicine AI Chatbot")
st.write("Enter your symptoms, and get Ayurvedic medicine recommendations as bullet points.")

# Display chat history (this will be updated dynamically in the placeholder)
display_chat_history()

# Input for user's symptoms
user_input = st.text_input("Enter your symptoms:", key="user_input")

# When the user clicks the button, process input and update chat history
if st.button("Get Medicine Advice") and user_input:
    # Append user's message to chat history
    st.session_state.messages.append({"sender": "user", "text": user_input})
    
    with st.spinner("Fetching recommendations..."):
        buf = io.StringIO()
        with redirect_stdout(buf):
            medicine_agent.print_response(user_input, stream=True)
        response = buf.getvalue()
        clean_response = clean_output(response)
        # Append agent's response to chat history
        st.session_state.messages.append({"sender": "bot", "text": clean_response})
    
    # Update the chat container display only once
    display_chat_history()
