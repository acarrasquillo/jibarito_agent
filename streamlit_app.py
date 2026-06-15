import streamlit as st
import requests
import json
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Jibarito - Agricultural Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS theme
try:
    with open(".streamlit/custom_theme.css") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    # Fallback inline CSS for Streamlit Cloud
    st.markdown("""
    <style>
    /* Dark theme colors */
    :root {
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --green-primary: #1F6B3A;
    }

    /* Main styling */
    .stApp { color: var(--text-primary); }

    /* Chat message styling */
    .stChatMessage [data-testid="stChatMessageContent"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    /* Input styling */
    [data-testid="stChatInputContainer"] input {
        background-color: #243044 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stChatInputContainer"] input::placeholder {
        color: #64748B !important;
    }

    /* Button styling */
    .stButton > button {
        background-color: #182235 !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    .stButton > button:hover {
        background-color: var(--green-primary) !important;
        color: white !important;
    }

    /* Sidebar styling - mobile responsive */
    [data-testid="stSidebar"] {
        min-width: 300px;
    }

    /* Sidebar button styling */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #182235 !important;
        color: var(--text-secondary) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--green-primary) !important;
        color: white !important;
    }

    /* Mobile: Sidebar toggle button styling */
    [data-testid="stSidebarNav"] {
        background-color: var(--green-primary) !important;
        border-radius: 8px !important;
    }

    /* Mobile: Hide sidebar on small screens by default, show toggle */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            min-width: 280px;
        }

        /* Better spacing for mobile sidebar */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding: 0.5rem;
        }

        /* Make buttons full width on mobile */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
        }
    }

    /* Caption styling - FIX for dark background */
    .stCaption {
        color: var(--text-secondary) !important;
    }

    /* Headers */
    h1 { color: var(--text-primary) !important; }
    h2 { color: var(--text-primary) !important; }
    h3 { color: var(--text-secondary) !important; }

    /* Markdown text */
    .stMarkdown p { color: var(--text-secondary) !important; }

    /* Divider */
    .stDivider { border-color: rgba(255,255,255,0.08) !important; }
    </style>
    """, unsafe_allow_html=True)

# Header with logo
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image("images/jibarito_simple_logo.svg", width=60)
    except:
        st.markdown("🌾")

with col2:
    st.title("Jibarito")
    st.markdown('<p style="color: #CBD5E1; font-size: 0.875rem; margin-top: -0.5rem;">Agricultural Intelligence for the US Caribbean & Tropical Regions</p>', unsafe_allow_html=True)

# Configuration
AGENT_ENDPOINT = st.secrets.get("agent_endpoint", "")
NEO4J_CLIENT_ID = st.secrets.get("neo4j_client_id", "")
NEO4J_CLIENT_SECRET = st.secrets.get("neo4j_client_secret", "")

if not AGENT_ENDPOINT or not NEO4J_CLIENT_ID or not NEO4J_CLIENT_SECRET:
    st.error("""
    ⚠️ Missing configuration. Please set in `.streamlit/secrets.toml`:
    ```
    agent_endpoint = "https://api.neo4j.io/..."
    neo4j_client_id = "your_client_id"
    neo4j_client_secret = "your_client_secret"
    ```
    """)
    st.stop()

@st.cache_data(ttl=3600)
def get_bearer_token():
    """Generate a new bearer token using OAuth2 client credentials flow"""
    try:
        token_response = requests.post(
            "https://api.neo4j.io/oauth/token",
            auth=(NEO4J_CLIENT_ID, NEO4J_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
            timeout=10
        )
        token_response.raise_for_status()

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if access_token:
            return access_token
        else:
            st.error(f"❌ No access token in response: {token_data}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to generate bearer token: {str(e)}")
        return None

# Get fresh bearer token for this session
BEARER_TOKEN = get_bearer_token()

if not BEARER_TOKEN:
    st.error("Unable to authenticate with Neo4j. Please check your credentials.")
    st.stop()

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

# Render sidebar FIRST to capture button clicks
with st.sidebar:
    if st.button("🗑️ Clear Chat History", key="clear_top", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 💡 Example Questions")
    st.markdown("Click any to ask:")

    sample_questions = [
        "How many tomatoes were grown in Puerto Rico in 2022?",
        "What should I not plant next to tomatoes?",
        "What should I plant after tomatoes?",
        "If I planted tomatoes today, when can I harvest them?",
        "What crops are grown in Hawaii?",
        "What pests attack peppers?",
        "¿Qué cultivos se producen en Puerto Rico?"
    ]

    for question in sample_questions:
        if st.button(question, key=f"sidebar_{question}", use_container_width=True):
            st.session_state.selected_question = question

# Display conversation history
for message in st.session_state.messages:
    avatar = "👨‍🌾" if message["role"] == "user" else "🌾"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Initialize prompt variable
prompt = None

# Check if a sidebar question was selected
if st.session_state.selected_question:
    prompt = st.session_state.selected_question
    st.session_state.selected_question = None

# Chat input (can override sidebar selection)
user_input = st.chat_input("Ask about crops, companion planting, pests, or production...")
if user_input:
    prompt = user_input

# Process user input/selected question
if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar="👨‍🌾"):
        st.markdown(prompt)

    # Get response from Aura Agent
    with st.chat_message("assistant", avatar="🌾"):
        with st.spinner("Thinking..."):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {BEARER_TOKEN}"
                }

                payload = {"input": prompt}

                response = requests.post(
                    AGENT_ENDPOINT,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()

                result = response.json()

                # Extract the agent's response from the structured JSON
                agent_response = None

                # Aura Agent returns: {"type": "message", "content": [...], ...}
                if isinstance(result.get("content"), list):
                    # Find the text content in the content array
                    for item in result.get("content", []):
                        if item.get("type") == "text":
                            agent_response = item.get("text", "")
                            break

                # Fallback for other response formats
                if not agent_response:
                    if "output" in result:
                        agent_response = result["output"]
                    elif "answer" in result:
                        agent_response = result["answer"]
                    else:
                        agent_response = "No response from agent"

                st.markdown(agent_response)

                # Add assistant message to history (for persistence across reruns)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_response
                })

            except requests.exceptions.RequestException as e:
                error_msg = f"❌ Error connecting to agent: {str(e)}"
                st.error(error_msg)
            except json.JSONDecodeError:
                error_msg = "❌ Error parsing agent response"
                st.error(error_msg)
            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                st.error(error_msg)

# Continue sidebar with information
with st.sidebar:
    st.divider()

    st.markdown("### About Jibarito")
    st.markdown("""
    **Jibarito** (ji-bah-REE-to) = Puerto Rican farmer/campesino

    An AI agent that helps farmers, gardeners, and researchers make decisions about:
    - 🌱 What crops grow in your region
    - 🤝 Companion planting strategies
    - 🐛 Pest and disease management
    - 📊 Production statistics
    - 🌍 Climate and growing requirements
    """)

    st.markdown("### Coverage")
    st.markdown("""
    **Territories**: Puerto Rico, US Virgin Islands, Hawaii, Florida

    **Data Sources**:
    - USDA NASS agricultural statistics
    - CropGraph companion planting & pest data
    - USDA PLANTS botanical information
    """)

    st.markdown("### Languages")
    st.markdown("English & Spanish 🇺🇸 🇵🇷")

    st.divider()

    st.markdown("### Data Sources")
    st.markdown("""
    - [USDA NASS Quick Stats](https://www.nass.usda.gov/Quick_Stats/) - Crop production statistics
    - [USDA Census](https://www.nass.usda.gov/AgCensus/) - Farm operations & demographics
    - [CropGraph API](https://cropgraph.com/) - Companion planting, rotation, spacing
    - [USDA PLANTS](https://plants.sc.egov.usda.gov/) - Plant traits & hardiness zones
    """)

    st.markdown("### Powered By")
    try:
        st.image("images/logo-lockup-horizontal-white.png", width=180)
    except:
        st.markdown("**Neo4j AuraDB & Neo4j Aura Agent**")
    st.caption("Built with Neo4j Aura Agent & AuraDB")

