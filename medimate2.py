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
st.set_page_config(page_title="Hotel FAQ Assistant", layout="wide")

# Load environment variables
load_dotenv()

# Sidebar configuration with hotel-specific information
st.sidebar.title("Hotel Information")
st.sidebar.markdown("**📞 Front Desk:** +1-800-123-4567")
st.sidebar.markdown("**🕒 Check-in/Out:** 3:00 PM / 11:00 AM")
st.sidebar.markdown("**🏨 Rooms Available:** Standard, Deluxe, Suite")
st.sidebar.markdown("**🍽 Dining Options:** Restaurant, Room Service (7:00 AM - 10:00 PM)")
st.sidebar.markdown("**🏊 Facilities:** Pool, Fitness Center, Spa")

# Initialize the hotel FAQ agent with bullet point instructions
hotel_agent = Agent(
    name="Hotel FAQ Assistant",
    model=Groq(id="llama-3.1-8b-instant"),
    tools=[WikipediaTools(), DuckDuckGo()],
    instructions=[
        "Your hotel name is JB Hotels",
        "You are developed by Jeet Bobde",
        "You are a hotel FAQ assistant providing information about our hotel services and policies.",
        "When a guest asks about hotel facilities, services, or policies, provide accurate information based on established hotel guidelines.",
        "Format your response as a list of bullet points. For each question, include the relevant information. For example:",
        "   - **Check-in time:** 3:00 PM",
        "   - **Cancellation policy:** 24 hours notice required for full refund",
        "Include a clear disclaimer: 'I am an AI assistant. This information is provided for general informational purposes only. For specific inquiries, please contact our front desk directly.'",
        "If the question is unclear or requires personalized attention, advise the guest to contact the front desk for assistance.",
        "Encourage guests to visit the front desk for any special requests or concerns."
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
    chat_html = '<div style="height: 400px; overflow-y: scroll; padding: 10px; border: 1px solid #ddd;">'
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
st.title("Hotel FAQ AI Chatbot")
st.write("Ask questions about our hotel services, policies, or amenities.")

# Display chat history (this will be updated dynamically in the placeholder)
display_chat_history()

# Input for user's questions
user_input = st.text_input("Enter your question:", key="user_input")

# When the user clicks the button, process input and update chat history
if st.button("Ask Question") and user_input:
    # Append user's message to chat history
    st.session_state.messages.append({"sender": "user", "text": user_input})
    
    with st.spinner("Fetching information..."):
        buf = io.StringIO()
        with redirect_stdout(buf):
            hotel_agent.print_response(user_input, stream=True)
        response = buf.getvalue()
        clean_response = clean_output(response)
        # Append agent's response to chat history
        st.session_state.messages.append({"sender": "bot", "text": clean_response})
    
    # Update the chat container display only once
    display_chat_history()
