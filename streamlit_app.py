import streamlit as st
import asyncio
import logging
from datetime import datetime
from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext
from src.knowledge.knowledge_search import SimpleKnowledgeSearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Ram Senthil-Maree - Digital Transformation Consultant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

.user-message {
    background-color: #f0f9ff;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #3b82f6;
}

.assistant-message {
    background-color: #f8fafc;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #10b981;
}

.metrics-container {
    background-color: #f1f5f9;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
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
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if "engagement_stage" not in st.session_state:
        st.session_state.engagement_stage = "discovery"
    
    if "lead_score" not in st.session_state:
        st.session_state.lead_score = 0
    
    if "agent" not in st.session_state:
        st.session_state.agent = ConsultancyAgent()
    
    if "knowledge_search" not in st.session_state:
        st.session_state.knowledge_search = SimpleKnowledgeSearch()

def display_header():
    """Display the professional header"""
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin-bottom: 0.5rem;">Ram Senthil-Maree</h1>
        <h3 style="color: #e8f4fd; margin-bottom: 0.5rem;">Digital Transformation Consultant</h3>
        <p style="color: #b3d9ff; margin-bottom: 0;">
            Specializing in PMO Setup, Microsoft Dynamics 365, and Public Sector Transformation
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_welcome_message():
    """Display initial welcome message if no conversation has started"""
    if not st.session_state.messages:
        welcome_msg = """
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
        
        st.markdown("""
        <div class="assistant-message">
        """ + welcome_msg + """
        </div>
        """, unsafe_allow_html=True)

async def process_user_input(user_input: str):
    """Process user input through the ConsultancyAgent"""
    try:
        # Create conversation context
        context = ConversationContext(
            conversation_id=st.session_state.conversation_id,
            messages=st.session_state.messages,
            engagement_stage=st.session_state.engagement_stage
        )
        context.lead_score = st.session_state.lead_score
        
        # Search knowledge base for relevant context
        knowledge_results = st.session_state.knowledge_search.search(user_input)
        
        # Add knowledge context to the agent if available
        if knowledge_results:
            knowledge_context = "\n\n".join([
                f"Relevant experience: {result['chunks'][0] if result['chunks'] else ''}"
                for result in knowledge_results[:2]
            ])
            user_input_with_context = f"{user_input}\n\nContext from knowledge base:\n{knowledge_context}"
        else:
            user_input_with_context = user_input
        
        # Get response from agent
        response = await st.session_state.agent.handle_interaction(user_input_with_context, context)
        
        # Update session state
        st.session_state.engagement_stage = response.get("stage", context.engagement_stage)
        st.session_state.lead_score = response.get("lead_score", context.lead_score)
        
        return response["content"]
        
    except Exception as e:
        logger.error(f"Error processing user input: {str(e)}")
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
        
        stage_icon = stage_colors.get(st.session_state.engagement_stage, "💬")
        st.markdown(f"**Stage:** {stage_icon} {st.session_state.engagement_stage.replace('_', ' ').title()}")
        
        # Lead score
        score = st.session_state.lead_score
        score_color = "🔴" if score < 30 else "🟡" if score < 60 else "🟢"
        st.markdown(f"**Lead Score:** {score_color} {score}/100")
        
        # Message count
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
        
        # Conversation ID
        st.markdown(f"**ID:** `{st.session_state.conversation_id}`")
        
        # Knowledge base status
        doc_count = len(st.session_state.knowledge_search.get_document_list())
        st.markdown(f"**Knowledge Base:** {doc_count} documents")

def main():
    """Main application function"""
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Main chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display welcome message if first visit
        display_welcome_message()
        
        # Display conversation history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>Ram:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask me about digital transformation, PMO setup, Dynamics 365, or any business challenge...")
        
        if user_input:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Process input and get response
            with st.spinner("Ram is thinking..."):
                response = asyncio.run(process_user_input(user_input))
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to display new messages
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display metrics in sidebar
    display_conversation_metrics()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        💼 <strong>Ready for a consultation?</strong> Contact Ram directly: <a href="mailto:ram@senthilmaree.com">ram@senthilmaree.com</a><br>
        🔗 Connect on <a href="https://linkedin.com/in/ramsenthilmaree" target="_blank">LinkedIn</a> | 
        📱 Schedule a call: <a href="https://calendly.com/ram-senthil-maree" target="_blank">Calendly</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()