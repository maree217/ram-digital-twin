import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from src.config import settings
from src.knowledge.vector_search import VectorKnowledgeSearch

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

class ConversationContext:
    def __init__(self, conversation_id: str = None, messages: List[Dict] = None, 
                 engagement_stage: str = "discovery", user_type: str = "unknown"):
        self.conversation_id = conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages = messages or []
        self.engagement_stage = engagement_stage
        self.user_type = user_type
        self.lead_score = 0
        self.topics_discussed = []

class ConsultancyAgent:
    def __init__(self):
        self.name = "ram_consultancy_advisor"
        self.model_name = "gemini-2.0-flash-exp"
        self._init_gemini()
        self.persona_prompt = self._load_consultancy_persona()
        self.vector_search = VectorKnowledgeSearch()
        
    def _init_gemini(self):
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Google API key not configured")
            self.model = None
    
    def _load_consultancy_persona(self) -> str:
        return """You are Ram Senthil-Maree, a digital transformation consultant with extensive experience in:

**Core Expertise:**
- PMO Setup & Program Management Office establishment
- Microsoft Dynamics 365 implementation and optimization 
- Public sector digital transformation (housing associations, councils)
- Change management and organizational transformation
- Business process optimization and automation

**Professional Approach:**
- Ask insightful questions to understand client challenges
- Provide specific, actionable recommendations based on real experience
- Reference relevant methodologies and frameworks 
- Maintain professional consultancy tone
- Identify opportunities for further engagement when appropriate

**Experience Highlights:**
- Led PMO transformations for organizations with £50M+ budgets
- Implemented Dynamics 365 for housing associations managing 50,000+ properties
- Designed change management programs reducing resistance by 60%
- Delivered digital transformation initiatives improving efficiency by 40%

**Conversation Guidelines:**
- Start by understanding the client's current situation and challenges
- Share relevant experience and case studies (anonymized)
- Provide actionable next steps
- Suggest further consultation when complex issues are identified
- Maintain focus on business value and ROI

Always respond as Ram would - knowledgeable, professional, and solution-focused."""

    async def handle_interaction(self, user_message: str, context: ConversationContext) -> Dict[str, Any]:
        try:
            stage = self._determine_engagement_stage(user_message, context)
            context.engagement_stage = stage
            
            # Get enhanced knowledge context using vector search
            knowledge_context = await self._get_knowledge_context(user_message)
            
            if stage == "rapport_building":
                response = await self._build_rapport_response(user_message, context, knowledge_context)
            elif stage == "expertise_demonstration":
                response = await self._demonstrate_expertise(user_message, context, knowledge_context)
            elif stage == "solution_presentation":
                response = await self._present_solution(user_message, context, knowledge_context)
            elif stage == "engagement_conversion":
                response = await self._handle_engagement(user_message, context, knowledge_context)
            else:
                response = await self._generate_general_response(user_message, context, knowledge_context)
            
            self._update_lead_score(context, user_message, response)
            
            # Add knowledge search info to response
            response["knowledge_sources"] = len(knowledge_context.get("sources", []))
            response["vector_search_available"] = self.vector_search.is_pinecone_available()
            
            return response
            
        except Exception as e:
            logger.error(f"Error in handle_interaction: {str(e)}")
            return {
                "content": "I'm experiencing a technical issue. Could you please rephrase your question? If the issue persists, you can reach Ram directly at ram@senthilmaree.com",
                "stage": context.engagement_stage,
                "lead_score": context.lead_score,
                "knowledge_sources": 0,
                "vector_search_available": False
            }
    
    def _determine_engagement_stage(self, user_message: str, context: ConversationContext) -> str:
        message_lower = user_message.lower()
        message_count = len(context.messages)
        
        # Engagement indicators
        if any(keyword in message_lower for keyword in ['meeting', 'call', 'consultation', 'discuss further', 'help us']):
            return "engagement_conversion"
        
        # Solution request indicators  
        if any(keyword in message_lower for keyword in ['how to', 'what should', 'recommend', 'approach', 'strategy']):
            return "solution_presentation"
            
        # Expertise testing indicators
        if any(keyword in message_lower for keyword in ['experience', 'have you', 'can you', 'dynamics', 'pmo', 'transformation']):
            return "expertise_demonstration"
            
        # Early conversation
        if message_count < 3:
            return "rapport_building"
            
        return context.engagement_stage
    
    async def _get_knowledge_context(self, user_message: str) -> Dict[str, Any]:
        """Get relevant knowledge context using vector search"""
        try:
            if self.vector_search.is_available():
                # Use vector search for semantic retrieval
                search_results = await self.vector_search.search(user_message, max_results=3)
                
                if search_results:
                    context_text = "\n\n".join([
                        f"From {result['document']}: {result['chunks'][0][:500]}..."
                        for result in search_results if result['chunks']
                    ])
                    
                    return {
                        "context": context_text,
                        "sources": [r['document'] for r in search_results],
                        "search_type": "vector" if self.vector_search.is_pinecone_available() else "semantic"
                    }
            
            # Fallback: return empty context
            return {"context": "", "sources": [], "search_type": "none"}
            
        except Exception as e:
            logger.error(f"Error getting knowledge context: {e}")
            return {"context": "", "sources": [], "search_type": "error"}
    
    async def _build_rapport_response(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        This is an early conversation. Focus on:
        1. Understanding the user's role and organization
        2. Identifying initial challenges or needs
        3. Building credibility through relevant questions
        4. Setting the stage for deeper discussion
        
        User message: {user_message}{context_section}
        
        Respond as Ram would in the first few exchanges of a consultancy conversation.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "rapport_building",
            "lead_score": context.lead_score
        }
    
    async def _demonstrate_expertise(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        The user is asking about your expertise or experience. Focus on:
        1. Sharing specific, relevant experience
        2. Providing concrete examples (anonymized)
        3. Demonstrating deep understanding of their domain
        4. Asking follow-up questions to understand their specific situation
        
        User message: {user_message}
        Previous context: {self._format_conversation_history(context)}{context_section}
        
        Share relevant experience and ask insightful questions to understand their needs better.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "expertise_demonstration", 
            "lead_score": context.lead_score
        }
    
    async def _present_solution(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        The user is asking for solutions or recommendations. Focus on:
        1. Providing specific, actionable recommendations
        2. Referencing relevant methodologies and frameworks
        3. Explaining the business value and ROI
        4. Suggesting next steps for implementation
        5. Identifying if this requires deeper consultation
        
        User message: {user_message}
        Previous context: {self._format_conversation_history(context)}{context_section}
        
        Provide thoughtful recommendations and suggest further consultation if the challenge is complex.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "solution_presentation",
            "lead_score": context.lead_score
        }
    
    async def _handle_engagement(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        The user is showing interest in further engagement. Focus on:
        1. Confirming their specific needs and timeline
        2. Explaining how you can help with their challenges
        3. Suggesting appropriate next steps (consultation call, assessment, etc.)
        4. Providing clear contact information and availability
        
        User message: {user_message}
        Previous context: {self._format_conversation_history(context)}{context_section}
        
        Guide them toward scheduling a consultation to discuss their needs in detail.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "engagement_conversion",
            "lead_score": context.lead_score
        }
    
    async def _generate_general_response(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        User message: {user_message}
        Previous context: {self._format_conversation_history(context)}{context_section}
        
        Respond as Ram would, maintaining the professional consultancy conversation.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": context.engagement_stage,
            "lead_score": context.lead_score
        }
    
    async def _generate_response(self, prompt: str, context: ConversationContext) -> str:
        if not self.model:
            return "I'm currently unable to access my AI capabilities. Please contact Ram directly at ram@senthilmaree.com for assistance."
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                    top_p=0.8,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble processing your request right now. Could you please rephrase your question?"
    
    def _format_conversation_history(self, context: ConversationContext) -> str:
        if not context.messages:
            return "No previous conversation."
        
        history = []
        for msg in context.messages[-3:]:  # Last 3 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history.append(f"{role}: {content}")
        
        return "\n".join(history)
    
    def _update_lead_score(self, context: ConversationContext, user_message: str, response: Dict[str, Any]):
        message_lower = user_message.lower()
        
        # Technical depth indicators
        if any(keyword in message_lower for keyword in ['dynamics', 'pmo', 'transformation', 'implementation']):
            context.lead_score += 15
        
        # Budget indicators
        if any(keyword in message_lower for keyword in ['budget', 'investment', 'cost', 'roi']):
            context.lead_score += 20
        
        # Timeline urgency
        if any(keyword in message_lower for keyword in ['urgent', 'asap', 'soon', 'immediately']):
            context.lead_score += 10
        
        # Authority indicators
        if any(keyword in message_lower for keyword in ['we need', 'our organization', 'decision', 'approve']):
            context.lead_score += 15
        
        # Engagement indicators
        if any(keyword in message_lower for keyword in ['meeting', 'call', 'consultation', 'help us']):
            context.lead_score += 25
        
        # Cap the score at 100
        context.lead_score = min(context.lead_score, 100)