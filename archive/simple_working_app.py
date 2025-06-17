import streamlit as st
import asyncio
import sys
import os

# Add src to path
sys.path.append('src')

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

# Simple working app for testing
st.title("🚀 Ram Senthil-Maree - Digital Transformation Consultant")
st.markdown("**Testing the core chat functionality**")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = ConsultancyAgent()

# Display conversation
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Ram:** {message['content']}")

# Simple input form
st.markdown("---")
user_input = st.text_input("Ask Ram about PMO, Dynamics 365, or digital transformation:", key="chat_input")

if st.button("Send Message") and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get agent response
    with st.spinner("Ram is thinking..."):
        try:
            context = ConversationContext()
            response = asyncio.run(st.session_state.agent.handle_interaction(user_input, context))
            content = response.get("content", "I'm having trouble right now.")
        except Exception as e:
            content = f"Error: {str(e)}"
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": content})
    
    # Rerun to show new messages
    st.rerun()

# Show status
st.sidebar.markdown("### Status")
st.sidebar.markdown(f"Messages: {len(st.session_state.messages)}")
if hasattr(st.session_state.agent, 'vector_search'):
    if st.session_state.agent.vector_search.is_pinecone_available():
        st.sidebar.markdown("🟢 Pinecone: Active")
    else:
        st.sidebar.markdown("🟡 Vector Search: Local only")
else:
    st.sidebar.markdown("🔴 Vector Search: Not available")