import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Jibarito - Agricultural Intelligence",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Jibarito")
st.subheader("Agricultural Intelligence for the US Caribbean & Tropical Regions")

# Configuration
AGENT_ENDPOINT = st.secrets.get("agent_endpoint", "")
AGENT_BEARER_TOKEN = st.secrets.get("agent_bearer_token", "")

if not AGENT_ENDPOINT or not AGENT_BEARER_TOKEN:
    st.error("""
    ⚠️ Missing configuration. Please set in `.streamlit/secrets.toml`:
    ```
    agent_endpoint = "https://api.neo4j.io/..."
    agent_bearer_token = "your_token_here"
    ```
    """)
    st.stop()

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about crops, companion planting, pests, or production..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Aura Agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {AGENT_BEARER_TOKEN}"
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

                # Extract the agent's response
                # The Aura Agent returns a structured JSON response
                if "output" in result:
                    agent_response = result["output"]
                elif "answer" in result:
                    agent_response = result["answer"]
                else:
                    agent_response = json.dumps(result, indent=2)

                st.markdown(agent_response)

                # Add assistant message to history
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

# Sidebar with information
with st.sidebar:
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

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
