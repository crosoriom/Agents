import streamlit as st
import sys
import io
from contextlib import redirect_stdout
from dotenv import load_dotenv

# Import the agent's core components
from knowledge_base import KnowledgeBase
from llm_agent import LLMAgent
from discovery import find_local_stores, get_national_stores, get_international_stores, verify_communication_methods

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon="🤖",
    layout="wide"
)

# --- Agent Setup Function ---
# This is a modified version of the setup logic from main.py, adapted for Streamlit
def setup_agent(kb, location):
    """Performs the discovery and populates the KB."""
    st.write(f"📍 Performing store discovery for location: '{location}'...")
    all_stores = []
    all_stores.extend(find_local_stores(location))
    all_stores.extend(get_national_stores())
    all_stores.extend(get_international_stores())

    st.write("📡 Verifying communication methods for all discovered stores...")
    for store in all_stores:
        verified_methods = verify_communication_methods(store['name'])
        kb.add_shop(
            name=store['name'],
            scope=store['scope'],
            mcp_enabled=verified_methods.get('mcp_enabled', False),
            mcp_url=verified_methods.get('mcp_url'),
            api_enabled=verified_methods.get('api_enabled', False),
            api_url=verified_methods.get('api_url'),
            scraping_enabled=True
        )
    st.write("✅ Knowledge Base is populated and ready.")

# --- Session State Initialization ---
# This ensures our agent and KB persist across user interactions
if 'agent' not in st.session_state:
    st.session_state.agent = None
    st.session_state.kb = None
    st.session_state.setup_complete = False
    st.session_state.logs = ""
    st.session_state.recommendation = ""


# --- Main Application UI ---
st.title("🤖 AI Shopping Agent Dashboard")
st.info(
    "This dashboard provides a graphical interface for the self-learning AI Shopping Agent. "
    "Start by initializing the agent, then enter your product query to get a recommendation."
)

# --- Setup Section ---
with st.expander("Step 1: Initial Agent Setup", expanded=not st.session_state.setup_complete):
    location = st.text_input(
        "Enter your location to find local stores (e.g., 'New York, NY')",
        ""
    )
    
    if st.button("Initialize Agent"):
        if not location:
            st.error("Please enter a location.")
        else:
            with st.spinner("Performing first-time setup... This may take a moment."):
                # Capture print statements as logs
                log_capture_string = io.StringIO()
                with redirect_stdout(log_capture_string):
                    # Initialize KB and Agent, storing them in the session state
                    st.session_state.kb = KnowledgeBase()
                    setup_agent(st.session_state.kb, location)
                    st.session_state.agent = LLMAgent(knowledge_base=st.session_state.kb)
                
                st.session_state.logs = log_capture_string.getvalue()
                st.session_state.setup_complete = True
                st.success("Agent initialized successfully!")
                # We don't need a rerun here, Streamlit will handle it.

# --- Search Section ---
if st.session_state.setup_complete:
    st.header("Step 2: Find a Product")
    
    query = st.text_input(
        "What product are you looking for?",
        placeholder="e.g., cheap 4k oled tv from Best Buy"
    )

    if st.button("Search for Products", type="primary"):
        if not query:
            st.error("Please enter a product query.")
        else:
            with st.spinner("🤖 AI Agent is thinking... Calling APIs and analyzing results..."):
                # Capture logs for this specific query
                log_capture_string = io.StringIO()
                with redirect_stdout(log_capture_string):
                    recommendation = st.session_state.agent.process_user_query(query)
                
                # Store results in session state to display them
                st.session_state.recommendation = recommendation
                # Prepend new logs to existing logs
                st.session_state.logs = log_capture_string.getvalue() + "\n" + st.session_state.logs

# --- Results Section ---
if st.session_state.recommendation:
    st.header("Agent's Recommendation")
    st.markdown(st.session_state.recommendation, unsafe_allow_html=True)

    with st.expander("View Agent's Thought Process (Logs)"):
        st.text_area("Logs", st.session_state.logs, height=400, key="logs_textarea")

else:
    if st.session_state.setup_complete:
        st.info("Enter a query above and click 'Search' to get a recommendation.")
