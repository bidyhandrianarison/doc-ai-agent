import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

from ingest import index_data
from search_agent import init_agent
import logs

load_dotenv()

# -----------------------------
# INITIALIZATION (cached)
# -----------------------------
@st.cache_resource
def initialize():
    index = index_data(
        repo_owner="langchain-ai",
        repo_name="langchain",
        branch="master"
    )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing.")

    agent = init_agent(index=index, api_key=api_key)
    return agent

agent = initialize()

# -----------------------------
# SESSION STATE (chat memory)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# UI
# -----------------------------
st.title("📚 LangChain Doc Agent")
st.write("Ask questions about LangChain documentation.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------
if prompt := st.chat_input("Ask a question..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        placeholder = st.empty()

        async def run_agent():
            result = await agent.run(prompt)
            return result

        result = asyncio.run(run_agent())

        response_text = result.output

        placeholder.markdown(response_text)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text
    })

    # -----------------------------
    # LOGGING
    # -----------------------------
    logs.log_interaction_to_file(
        logs.log_entry(
            agent_name=agent.name,
            system_prompt="N/A",
            model_name=agent.model.model_name,
            question=prompt,
            answer=response_text,
            search_results="N/A",  # improve later
            source="streamlit"
        )
    )