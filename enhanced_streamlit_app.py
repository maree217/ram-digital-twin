import streamlit as st
import streamlit.components.v1 as components
import json
import time
from datetime import datetime
from src.agents.consultancy_agent import ConsultancyAgent
from src.analytics.conversation_tracker import ConversationTracker
from src.knowledge.knowledge_search import KnowledgeSearch

# Page config
st.set_page_config(
    page_title="Ram Senthil-Maree - Digital Transformation Consultant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional chat interface
chat_css = """
<style>
/* AI Consultant Digital Twin - Enhanced Streamlit Stylesheet */
:root {
    --primary-color: #005A9E;
    --secondary-color: #003366;
    --accent-color: #E67E22;
    --background-color: #F4F7F9;
    --surface-color: #FFFFFF;
    --text-primary-color: #212529;
    --text-secondary-color: #6C757D;
    --bot-message-bg: #E9ECEF;
    --user-message-bg: #005A9E;
    --user-message-text: #FFFFFF;
    --font-family: 'Inter', sans-serif;
    --border-radius: 12px;
    --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Hide Streamlit default elements */
.stApp > header {visibility: hidden;}
.stApp > div[data-testid="stDecoration"] {visibility: hidden;}
.stMainBlockContainer {padding-top: 0rem;}

/* Main chat container */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    height: 90vh;
    background-color: var(--surface-color);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Professional header */
.chat-header {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    padding: 24px;
    color: white;
    text-align: center;
}

.header-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header-subtitle {
    font-size: 1.1rem;
    font-weight: 400;
    opacity: 0.9;
    margin-bottom: 16px;
}

.header-tagline {
    font-size: 0.95rem;
    opacity: 0.8;
    font-style: italic;
}

/* Status indicator */
.status-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background-color: rgba(255,255,255,0.15);
    padding: 8px 16px;
    border-radius: 20px;
    margin-top: 16px;
    font-size: 0.875rem;
    font-weight: 500;
}

.status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #4CAF50;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Welcome section */
.welcome-section {
    padding: 32px 24px;
    background: linear-gradient(to bottom, #f8f9fa, #ffffff);
    border-bottom: 1px solid #e9ecef;
}

.welcome-message {
    background: var(--bot-message-bg);
    padding: 20px;
    border-radius: var(--border-radius);
    margin-bottom: 24px;
    border-left: 4px solid var(--primary-color);
}

.welcome-message h3 {
    color: var(--primary-color);
    margin-bottom: 12px;
    font-size: 1.2rem;
}

.expertise-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
    margin: 20px 0;
}

.expertise-card {
    background: white;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}

.expertise-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.expertise-title {
    font-weight: 600;
    color: var(--primary-color);
    margin-bottom: 8px;
}

/* Quick start prompts */
.quick-prompts {
    margin-top: 24px;
}

.quick-prompts h4 {
    color: var(--text-primary-color);
    margin-bottom: 16px;
    font-size: 1.1rem;
}

.prompt-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
}

.prompt-card {
    background: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: left;
}

.prompt-card:hover {
    border-color: var(--primary-color);
    background: var(--primary-color);
    color: white;
    transform: translateY(-1px);
}

.prompt-icon {
    font-size: 1.5rem;
    margin-bottom: 8px;
}

.prompt-text {
    font-weight: 500;
    font-size: 0.95rem;
    line-height: 1.4;
}

/* Chat messages area */
.chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 24px;
    max-height: 400px;
}

.message {
    display: flex;
    margin-bottom: 20px;
    animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message.user {
    justify-content: flex-end;
}

.message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: var(--border-radius);
    line-height: 1.6;
}

.message.bot .message-content {
    background-color: var(--bot-message-bg);
    color: var(--text-primary-color);
    border-top-left-radius: 4px;
}

.message.user .message-content {
    background-color: var(--user-message-bg);
    color: var(--user-message-text);
    border-top-right-radius: 4px;
}

.message-time {
    font-size: 0.75rem;
    color: var(--text-secondary-color);
    margin-top: 4px;
    text-align: right;
}

/* Input area styling */
.input-section {
    padding: 24px;
    border-top: 1px solid #e9ecef;
    background: white;
}

/* Contact section */
.contact-section {
    background: var(--background-color);
    padding: 24px;
    text-align: center;
    border-top: 1px solid #e9ecef;
}

.contact-links {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-top: 16px;
    flex-wrap: wrap;
}

.contact-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: var(--primary-color);
    color: white;
    text-decoration: none;
    border-radius: 6px;
    font-size: 0.9rem;
    transition: background-color 0.3s;
}

.contact-link:hover {
    background: var(--secondary-color);
    color: white;
    text-decoration: none;
}

/* Responsive design */
@media (max-width: 768px) {
    .chat-container {
        height: 100vh;
        border-radius: 0;
    }
    
    .expertise-grid,
    .prompt-grid {
        grid-template-columns: 1fr;
    }
    
    .contact-links {
        flex-direction: column;
        align-items: center;
    }
}
</style>
"""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = f"conv_{int(time.time())}"

# Initialize components
@st.cache_resource
def initialize_components():
    try:
        agent = ConsultancyAgent()
        tracker = ConversationTracker()
        knowledge = KnowledgeSearch()
        return agent, tracker, knowledge
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None

# Main app
def main():
    # Inject CSS
    st.markdown(chat_css, unsafe_allow_html=True)
    
    # Load Google Fonts
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Main container
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            <h1 class="header-title">Ram Senthil-Maree</h1>
            <p class="header-subtitle">Digital Transformation Consultant</p>
            <p class="header-tagline">Specializing in PMO Setup, Microsoft Dynamics 365, and Public Sector Transformation</p>
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span>Available for consultation</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome section with expertise
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-section">
            <div class="welcome-message">
                <h3>👋 Welcome! I'm Ram Senthil-Maree</h3>
                <p>I'm a digital transformation consultant with extensive experience helping organizations achieve their strategic goals through technology and process optimization.</p>
            </div>
            
            <div class="expertise-grid">
                <div class="expertise-card">
                    <div class="expertise-title">🎯 PMO Setup</div>
                    <p>Establishing Program Management Offices that deliver measurable results and drive organizational success.</p>
                </div>
                <div class="expertise-card">
                    <div class="expertise-title">💼 Microsoft Dynamics 365</div>
                    <p>Implementation and optimization for maximum ROI, streamlining business processes across your organization.</p>
                </div>
                <div class="expertise-card">
                    <div class="expertise-title">🏛️ Public Sector Transformation</div>
                    <p>Specialized experience with housing associations, councils, and government organizations.</p>
                </div>
                <div class="expertise-card">
                    <div class="expertise-title">🔄 Change Management</div>
                    <p>Ensuring smooth adoption and cultural transformation throughout your digital journey.</p>
                </div>
            </div>
            
            <div class="quick-prompts">
                <h4>How can I help you today? Try asking about:</h4>
                <div class="prompt-grid">
                    <div class="prompt-card" onclick="selectPrompt('Setting up a PMO for your organization')">
                        <div class="prompt-icon">🎯</div>
                        <div class="prompt-text">Setting up a PMO for your organization</div>
                    </div>
                    <div class="prompt-card" onclick="selectPrompt('Microsoft Dynamics 365 implementation strategy')">
                        <div class="prompt-icon">💼</div>
                        <div class="prompt-text">Microsoft Dynamics 365 implementation strategy</div>
                    </div>
                    <div class="prompt-card" onclick="selectPrompt('Digital transformation roadmap for public sector')">
                        <div class="prompt-icon">🏛️</div>
                        <div class="prompt-text">Digital transformation roadmap for public sector</div>
                    </div>
                    <div class="prompt-card" onclick="selectPrompt('Change management best practices')">
                        <div class="prompt-icon">🔄</div>
                        <div class="prompt-text">Change management best practices</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat messages display
    if st.session_state.messages:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            message_class = "user" if message["role"] == "user" else "bot"
            timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
            
            st.markdown(f"""
            <div class="message {message_class}">
                <div class="message-content">
                    {message["content"]}
                    <div class="message-time">{timestamp}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    # Initialize components
    agent, tracker, knowledge = initialize_components()
    
    if agent:
        # Chat input
        user_input = st.chat_input("Type your message here... Ask me about PMO setup, Dynamics 365, or digital transformation!")
        
        if user_input:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Generate response
            with st.spinner("Thinking..."):
                try:
                    response = agent.process_message(
                        user_input, 
                        st.session_state.conversation_id,
                        st.session_state.messages
                    )
                    
                    # Add bot response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    
                    # Track conversation
                    if tracker:
                        tracker.track_interaction(
                            st.session_state.conversation_id,
                            user_input,
                            response
                        )
                    
                except Exception as e:
                    st.error(f"Sorry, I encountered an error: {e}")
                    # Fallback response
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "I apologize, but I'm experiencing technical difficulties. Please try again, or feel free to contact me directly to discuss your digital transformation needs.",
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
            
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Contact section
    st.markdown("""
    <div class="contact-section">
        <h3>Ready to Transform Your Organization?</h3>
        <p>Let's discuss how I can help accelerate your digital transformation journey.</p>
        <div class="contact-links">
            <a href="mailto:ram@example.com" class="contact-link">
                📧 Schedule Consultation
            </a>
            <a href="https://linkedin.com/in/ramsenthilmaree" class="contact-link" target="_blank">
                💼 LinkedIn Profile
            </a>
            <a href="tel:+1234567890" class="contact-link">
                📞 Call Direct
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript for prompt selection
    st.markdown("""
    <script>
    function selectPrompt(promptText) {
        // This would integrate with Streamlit's input system
        // For now, we'll just log it
        console.log('Selected prompt:', promptText);
        
        // In a real implementation, you'd send this to the Streamlit backend
        // using session state or a callback mechanism
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()