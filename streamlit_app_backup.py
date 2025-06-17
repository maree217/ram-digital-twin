import streamlit as st
import asyncio
import logging
from datetime import datetime
import google.api_core.exceptions
from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext
from src.knowledge.knowledge_search import SimpleKnowledgeSearch
from src.knowledge.vector_search import VectorKnowledgeSearch

# Server configuration handled via command line arguments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants for Session State Keys and Roles ---
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
SESSION_MESSAGES = "messages"
SESSION_CONVERSATION_ID = "conversation_id"
SESSION_ENGAGEMENT_STAGE = "engagement_stage"
SESSION_LEAD_SCORE = "lead_score"
SESSION_AGENT = "agent"
SESSION_KNOWLEDGE_SEARCH = "knowledge_search"
SESSION_VECTOR_SEARCH = "vector_search"
SESSION_LAST_RESPONSE_INFO = "last_response_info"

# --- Constants for Dictionary Keys (Agent Response) ---
KEY_CONTENT = "content"
KEY_STAGE = "stage"
KEY_LEAD_SCORE = "lead_score"
KEY_KNOWLEDGE_SOURCES = "knowledge_sources"
KEY_VECTOR_SEARCH_AVAILABLE = "vector_search_available"


# --- Constants for CSS and HTML ---
ADDITIONAL_CSS = """
<style>
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

.metrics-container {
    background-color: rgba(241, 245, 249, 0.9);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}

.stButton > button {
    width: 100%;
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #1e40af;
}
</style>
"""

HEADER_HTML = """
<div class="main-header">
    <h1 style="color: white; margin-bottom: 0.5rem;">Ram Senthil-Maree</h1>
    <h3 style="color: #e8f4fd; margin-bottom: 0.5rem;">Digital Transformation Consultant</h3>
    <p style="color: #b3d9ff; margin-bottom: 0;">
        Specializing in PMO Setup, Microsoft Dynamics 365, and Public Sector Transformation
    </p>
</div>
"""

WELCOME_MESSAGE_CONTAINER_HTML = '<div class="assistant-message">{}</div>'
WELCOME_MESSAGE_CONTENT = """
👋 **Welcome! I'm Ram Senthil-Maree**

I'm a digital transformation consultant with extensive experience in:

• **PMO Setup** - Establishing Program Management Offices that deliver results
• **Microsoft Dynamics 365** - Implementation and optimization for maximum ROI
• **Public Sector Transformation** - Housing associations, councils, and government organizations
• **Change Management** - Ensuring smooth adoption and cultural transformation

**How can I help you today?**

You might want to ask about:
- Setting up a PMO for your organization
- Dynamics 365 implementation challenges
- Digital transformation strategy
- Process optimization and automation
- Change management best practices
"""

USER_MESSAGE_HTML_TEMPLATE = '<div class="user-message"><strong>You:</strong> {}</div>'
ASSISTANT_MESSAGE_HTML_TEMPLATE = '<div class="assistant-message"><strong>Ram:</strong> {}</div>'

CHAT_CONTAINER_OPEN_HTML = '<div class="chat-container">'
CHAT_CONTAINER_CLOSE_HTML = '</div>'

FOOTER_HTML = """
<div style="text-align: center; color: #6b7280; padding: 1rem;">
    💼 <strong>Ready for a consultation?</strong> Contact Ram directly: <a href="mailto:ram@senthilmaree.com">ram@senthilmaree.com</a><br>
    🔗 Connect on <a href="https://linkedin.com/in/ramsenthilmaree" target="_blank">LinkedIn</a> |
    📱 Schedule a call: <a href="https://calendly.com/ram-senthil-maree" target="_blank">Calendly</a>
</div>
"""

# Function to load local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Ram Senthil-Maree - Digital Transformation Consultant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS file
local_css("style.css")

# Additional CSS for chat container and button styling
st.markdown(ADDITIONAL_CSS, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if SESSION_MESSAGES not in st.session_state:
        st.session_state[SESSION_MESSAGES] = []
    
    if SESSION_CONVERSATION_ID not in st.session_state:
        st.session_state[SESSION_CONVERSATION_ID] = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if SESSION_ENGAGEMENT_STAGE not in st.session_state:
        st.session_state[SESSION_ENGAGEMENT_STAGE] = "discovery" # Initial stage
    
    if SESSION_LEAD_SCORE not in st.session_state:
        st.session_state[SESSION_LEAD_SCORE] = 0
    
    if SESSION_AGENT not in st.session_state:
        st.session_state[SESSION_AGENT] = ConsultancyAgent()
    
    if SESSION_KNOWLEDGE_SEARCH not in st.session_state:
        st.session_state[SESSION_KNOWLEDGE_SEARCH] = SimpleKnowledgeSearch()
    
    if SESSION_VECTOR_SEARCH not in st.session_state:
        st.session_state[SESSION_VECTOR_SEARCH] = VectorKnowledgeSearch()

def display_header():
    """Display the professional header"""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

def display_welcome_message():
    """Display initial welcome message if no conversation has started"""
    if not st.session_state[SESSION_MESSAGES]:
        st.markdown(WELCOME_MESSAGE_CONTAINER_HTML.format(WELCOME_MESSAGE_CONTENT), unsafe_allow_html=True)

async def process_user_input(user_input: str):
    """Process user input through the ConsultancyAgent"""
    try:
        # Create conversation context
        context = ConversationContext(
            conversation_id=st.session_state[SESSION_CONVERSATION_ID],
            messages=st.session_state[SESSION_MESSAGES],
            engagement_stage=st.session_state[SESSION_ENGAGEMENT_STAGE]
        )
        context.lead_score = st.session_state[SESSION_LEAD_SCORE]
        
        # Get response from agent (it handles knowledge search internally now)
        response = await st.session_state[SESSION_AGENT].handle_interaction(user_input, context)

        # Robust response checking
        if not isinstance(response, dict) or KEY_CONTENT not in response:
            logger.error(f"Invalid response structure from agent: {response}")
            return "I received an unexpected response. Please try rephrasing your question."
        
        # Update session state
        st.session_state[SESSION_ENGAGEMENT_STAGE] = response.get(KEY_STAGE, context.engagement_stage)
        st.session_state[SESSION_LEAD_SCORE] = response.get(KEY_LEAD_SCORE, context.lead_score)
        
        # Store additional response info for display
        st.session_state[SESSION_LAST_RESPONSE_INFO] = {
            KEY_KNOWLEDGE_SOURCES: response.get(KEY_KNOWLEDGE_SOURCES, 0),
            KEY_VECTOR_SEARCH_AVAILABLE: response.get(KEY_VECTOR_SEARCH_AVAILABLE, False)
        }
        
        return response[KEY_CONTENT]

    except google.api_core.exceptions.GoogleAPIError as e: # Specific to Google API errors
        logger.error(f"Google API Error processing user input: {str(e)}")
        return "There was an issue communicating with the AI service. Please try again shortly."
    except TimeoutError as e: # For network timeouts
        logger.error(f"TimeoutError processing user input: {str(e)}")
        return "The request timed out. Please try again."
    except IOError as e: # For general network/IO issues
        logger.error(f"IOError processing user input: {str(e)}")
        return "I'm having trouble connecting. Please check your internet connection and try again."
    except Exception as e: # Generic fallback
        logger.error(f"Generic error processing user input: {str(e)}")
        return "I'm experiencing a technical issue. Could you please rephrase your question? If the issue persists, you can reach me directly at ram@senthilmaree.com"

def display_conversation_metrics():
    """Display conversation metrics in sidebar"""
    with st.sidebar:
        st.markdown("### Conversation Insights")
        
        # Engagement stage
        stage_colors = {
            "discovery": "🔍",
            "rapport_building": "🤝", 
            "expertise_demonstration": "💡",
            "solution_presentation": "📋",
            "engagement_conversion": "📞"
        }
        
        stage_icon = stage_colors.get(st.session_state[SESSION_ENGAGEMENT_STAGE], "💬")
        st.markdown(f"**Stage:** {stage_icon} {st.session_state[SESSION_ENGAGEMENT_STAGE].replace('_', ' ').title()}")
        
        # Lead score
        score = st.session_state[SESSION_LEAD_SCORE]
        score_color = "🔴" if score < 30 else "🟡" if score < 60 else "🟢"
        st.markdown(f"**Lead Score:** {score_color} {score}/100")
        
        # Message count
        st.markdown(f"**Messages:** {len(st.session_state[SESSION_MESSAGES])}")
        
        # Conversation ID
        st.markdown(f"**ID:** `{st.session_state[SESSION_CONVERSATION_ID]}`")
        
        # Knowledge base status
        doc_count = len(st.session_state[SESSION_KNOWLEDGE_SEARCH].get_document_list())
        st.markdown(f"**Knowledge Base:** {doc_count} documents")
        
        # Vector search status
        if hasattr(st.session_state, SESSION_VECTOR_SEARCH):
            if st.session_state[SESSION_VECTOR_SEARCH].is_pinecone_available():
                st.markdown("**Vector Search:** 🟢 Pinecone Active")
            elif st.session_state[SESSION_VECTOR_SEARCH].is_available():
                st.markdown("**Vector Search:** 🟡 Local Model")
            else:
                st.markdown("**Vector Search:** 🔴 Unavailable")
        
        # Last response info
        if hasattr(st.session_state, SESSION_LAST_RESPONSE_INFO):
            info = st.session_state[SESSION_LAST_RESPONSE_INFO]
            sources = info.get(KEY_KNOWLEDGE_SOURCES, 0)
            if sources > 0:
                st.markdown(f"**Last Query:** {sources} sources found")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Main chat container
    with st.container():
        st.markdown(CHAT_CONTAINER_OPEN_HTML, unsafe_allow_html=True)
        
        # Display welcome message if first visit
        display_welcome_message()
        
        # Display conversation history
        for message in st.session_state[SESSION_MESSAGES]:
            if message["role"] == ROLE_USER:
                st.markdown(USER_MESSAGE_HTML_TEMPLATE.format(message[KEY_CONTENT]), unsafe_allow_html=True)
            else:
                st.markdown(ASSISTANT_MESSAGE_HTML_TEMPLATE.format(message[KEY_CONTENT]), unsafe_allow_html=True)
        
        # Chat input using form for better compatibility
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            
            with col1:
                user_input = st.text_input(
                    "Your message:",
                    placeholder="Ask me about digital transformation, PMO setup, Dynamics 365, or any business challenge...",
                    key="user_input",
                    label_visibility="collapsed"
                )
            
            with col2:
                submitted = st.form_submit_button("Send", use_container_width=True)
        
        if submitted and user_input:
            # Add user message to history
            st.session_state[SESSION_MESSAGES].append({"role": ROLE_USER, KEY_CONTENT: user_input})
            
            # Process input and get response
            with st.spinner("Ram is thinking..."):
                response_content = asyncio.run(process_user_input(user_input))
            
            # Add assistant response to history
            st.session_state[SESSION_MESSAGES].append({"role": ROLE_ASSISTANT, KEY_CONTENT: response_content})
            
            # Rerun to display new messages
            st.rerun()
        
        st.markdown(CHAT_CONTAINER_CLOSE_HTML, unsafe_allow_html=True)
    
    # Display metrics in sidebar
    display_conversation_metrics()
    
    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

if __name__ == "__main__":
    main()