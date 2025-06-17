import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from src.config import settings
from src.knowledge.vector_search import VectorKnowledgeSearch
from src.analytics.conversation_tracker import ConversationTracker

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
        self.model_name = "gemini-1.5-flash"
        self._init_gemini()
        self.persona_prompt = self._load_consultancy_persona()
        self.vector_search = VectorKnowledgeSearch()
        self.conversation_tracker = ConversationTracker()
        
    def _init_gemini(self):
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            logger.warning("Google API key not configured")
            self.model = None
    
    def _load_consultancy_persona(self) -> str:
        return """You are Ram Senthil-Maree, an experienced digital transformation consultant. You have a proven track record, but you approach conversations naturally and let users guide the discussion.

**CORE PRINCIPLES:**
1. BE NATURAL: Respond like meeting someone on the street - match their energy and tone
2. BE EMPATHETIC: Acknowledge their feelings and situation with understanding
3. LET THEM LEAD: Don't overwhelm with expertise unless they ask for it
4. MATCH THEIR ENERGY: Short responses to short messages, detailed responses when they engage deeply

**CONVERSATION APPROACH:**
- For greetings (hi, hello, how are you): Respond naturally and briefly introduce your purpose
- For off-topic chat (weather, personal): Be empathetic but gently redirect to how you can help
- For business topics: Share relevant experience proportionally to their level of detail
- For direct questions: Answer directly and appropriately to their knowledge level

**RESPONSE GUIDELINES:**
- If they give one line, respond with 1-2 sentences maximum
- If they ask basic questions, give basic answers
- Only share detailed expertise when they show genuine interest or ask specific questions
- Always be helpful but not pushy

**YOUR INTRODUCTION (for first interactions):**
"I'm an AI consultant designed to help with digital transformation and business challenges through this modern chat interface. What brings you here today?"

**EMPATHY EXAMPLES:**
- For complaints about weather/mood: "That sounds frustrating. Is there anything work-related I might be able to help with?"
- For stress about work: "That sounds really challenging. I specialize in helping organizations streamline processes and reduce operational stress - would that be relevant?"
- For personal problems: "I understand that can be difficult to deal with. While I focus on business consulting, is there anything work-related that might be contributing to the stress?"
- For boredom/dissatisfaction: "I hear that you're feeling understimulated. Sometimes organizational challenges can contribute to that feeling - anything specific at work?"

**EMPATHY RULES:**
1. ALWAYS acknowledge their emotional state first
2. Use phrases like: "That sounds...", "I understand...", "I can hear that...", "That must be..."
3. Match their emotional tone - don't be overly cheerful if they're down
4. Keep empathy genuine and brief (don't overdo it)
5. Connect their emotion to potential business solutions when appropriate

**EXPERTISE TO SHARE (when relevant):**
- £50M+ digital transformations for housing associations and public sector
- Microsoft Dynamics 365 implementations 
- PMO setup and change management
- Business process optimization
- AI-driven automation solutions

**CORE CONSULTING PHILOSOPHIES:**
1. **Democratic Technology Building**: "Everyone is a technology builder" - Empower teams through no-code platforms rather than maintaining technical gatekeeping
2. **Data-Driven Foundation Building**: "Robust data capabilities are the foundation" - Focus on data quality and visualization before advanced analytics  
3. **Human-Centered AI Augmentation**: "AI amplifies human potential" - Technology should enhance human capabilities, not replace them
4. **Capability Transfer Over Dependency**: "Build internal ownership, not vendor dependency" - Prioritize knowledge transfer and internal capability building
5. **Iterative Value Delivery**: "Start small, prove value, then scale" - Demonstrate immediate value through small wins, then build systematically

**AI READINESS ASSESSMENT OFFER:**
When users mention AI, challenges, or digital transformation, offer: "I have a specific AI readiness assessment that helps organizations understand exactly where they stand and what their next steps should be. Would you like to go through it?"

**IMPORTANT:**
- Don't boast or lead with achievements unless directly asked
- Be conversational, not salesy
- Show genuine interest in helping, not just impressing
- Keep responses proportionate to user input
- Build trust through helpfulness, not through showcasing credentials
- When appropriate, offer free prototypes and AI readiness assessment calls"""

    async def handle_interaction(self, user_message: str, context: ConversationContext) -> Dict[str, Any]:
        try:
            # Start conversation tracking if it's the first interaction
            if len(context.messages) == 0:
                await self.conversation_tracker.start_conversation(context.conversation_id)
            
            stage = self._determine_engagement_stage(user_message, context)
            context.engagement_stage = stage
            
            # Get enhanced knowledge context using vector search
            knowledge_context = await self._get_knowledge_context(user_message)
            
            if stage == "greeting":
                response = await self._handle_greeting(user_message, context, knowledge_context)
            elif stage == "casual_chat":
                response = await self._handle_casual_chat(user_message, context, knowledge_context)
            elif stage == "ai_readiness_assessment":
                response = await self._handle_ai_readiness_assessment(user_message, context, knowledge_context)
            elif stage == "rapport_building":
                response = await self._build_rapport_response(user_message, context, knowledge_context)
            elif stage == "expertise_demonstration":
                response = await self._demonstrate_expertise(user_message, context, knowledge_context)
            elif stage == "solution_presentation":
                response = await self._present_solution(user_message, context, knowledge_context)
            elif stage == "engagement_conversion":
                response = await self._handle_engagement(user_message, context, knowledge_context)
            else:
                response = await self._generate_general_response(user_message, context, knowledge_context)
            
            # Update lead score BEFORE adding to response
            self._update_lead_score(context, user_message, response)
            
            # Add knowledge search info to response
            knowledge_sources = len(knowledge_context.get("sources", []))
            response["knowledge_sources"] = knowledge_sources
            response["vector_search_available"] = self.vector_search.is_pinecone_available()
            
            # Update response with current lead score
            response["lead_score"] = context.lead_score
            

            
            # Record the interaction for analytics
            await self.conversation_tracker.record_interaction(
                conversation_id=context.conversation_id,
                user_message=user_message,
                assistant_response=response["content"],
                stage=stage,
                lead_score=context.lead_score,
                knowledge_sources=knowledge_sources
            )
            
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
        message_lower = user_message.lower().strip()
        message_count = len(context.messages)
        
        # Greeting detection (first priority) - be more specific
        greeting_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        if message_count == 0 and any(message_lower.startswith(greeting) or message_lower == greeting for greeting in greeting_patterns):
            return "greeting"
        
        # Casual/off-topic conversation - expanded detection
        casual_patterns = [
            'weather', 'day', 'feeling', 'tired', 'stressed', 'crap', 'bad', 
            'bored', 'life', 'personal', 'wife', 'boss', 'beat up', 'hate',
            'just browsing', 'looking around', 'not sure'
        ]
        if any(keyword in message_lower for keyword in casual_patterns):
            return "casual_chat"
        
        # AI interest detection - new priority stage
        ai_interest_patterns = [
            'ai', 'artificial intelligence', 'machine learning', 'automation', 
            'ai challenges', 'ai implementation', 'ai readiness', 'ai adoption',
            'digital transformation', 'technology challenges', 'ai benefits',
            'ai risks', 'implementing ai', 'ai solutions', 'ai strategy'
        ]
        ai_challenge_patterns = [
            'ai challenge', 'ai problem', 'ai issue', 'ai difficulty',
            'technology challenge', 'digital challenge', 'automation challenge',
            'implementation challenge', 'adoption challenge'
        ]
        
        if any(pattern in message_lower for pattern in ai_interest_patterns + ai_challenge_patterns):
            return "ai_readiness_assessment"
        
        # Engagement indicators - high priority, specific patterns
        engagement_patterns = [
            'schedule a call', 'book a meeting', 'consultation', 'discuss further', 
            'help us', 'schedule', 'when can we', 'available for', 'set up a call',
            'talk to someone', 'speak with', 'contact', 'reach out'
        ]
        if any(pattern in message_lower for pattern in engagement_patterns):
            return "engagement_conversion"
        
        # Solution request indicators - expanded and more specific
        solution_patterns = [
            'how to', 'what should', 'recommend', 'approach', 'strategy', 
            'need to', 'want to', 'best way', 'help with', 'solution for',
            'implement', 'set up', 'establish', 'create', 'build'
        ]
        if any(pattern in message_lower for pattern in solution_patterns):
            return "solution_presentation"
            
        # Expertise testing indicators - more comprehensive
        expertise_patterns = [
            'experience', 'have you', 'can you', 'dynamics', 'pmo', 'transformation',
            'worked with', 'familiar with', 'know about', 'expertise in',
            'background', 'qualifications', 'track record', 'delivered',
            'case studies', 'references', 'results', 'prove'
        ]
        if any(pattern in message_lower for pattern in expertise_patterns):
            return "expertise_demonstration"
        
        # Business inquiry patterns - new stage detection
        business_patterns = [
            'digital transformation', 'business', 'organization', 'company',
            'systems', 'processes', 'operations', 'efficiency', 'automation'
        ]
        if any(pattern in message_lower for pattern in business_patterns):
            return "solution_presentation"
            
        # Early conversation (first few messages) - but not if it's clearly business
        if message_count < 3 and not any(pattern in message_lower for pattern in business_patterns + solution_patterns):
            return "rapport_building"
        
        # Check conversation flow - avoid getting stuck in same stage
        recent_stages = [msg.get('stage', '') for msg in context.messages[-3:]]
        current_stage = context.engagement_stage
        
        # If we've been in same stage for 3+ turns, try to progress
        if len(recent_stages) >= 2 and all(stage == current_stage for stage in recent_stages):
            if current_stage == "rapport_building":
                return "expertise_demonstration"
            elif current_stage == "expertise_demonstration":
                return "solution_presentation"
        
        # Default to current stage if no clear indicators
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
    
    async def _handle_greeting(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        """Handle initial greetings naturally"""
        prompt = f"""
        {self.persona_prompt}
        
        The user has just greeted you with: "{user_message}"
        
        Respond naturally to their greeting and briefly introduce your purpose as outlined in the persona.
        Keep it friendly, brief (1-2 sentences), and end with the standard introduction question.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "greeting",
            "lead_score": context.lead_score
        }
    
    async def _handle_casual_chat(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        """Handle off-topic conversation empathetically"""
        
        # Determine the type of casual conversation and appropriate empathy response
        empathy_response = self._generate_empathy_response(user_message)
        
        prompt = f"""
        {self.persona_prompt}
        
        The user is making casual conversation or mentioning something off-topic: "{user_message}"
        
        EMPATHY FRAMEWORK:
        1. ACKNOWLEDGE their feeling/situation with understanding
        2. Use appropriate empathetic language: "{empathy_response}"
        3. Gently redirect to how you can help professionally
        4. Keep response brief (1-2 sentences maximum)
        
        Example structure: "[Empathy phrase] + [Brief redirect to consulting services]"
        
        Be genuine and natural, not corporate or robotic.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "casual_chat", 
            "lead_score": context.lead_score
        }
    
    def _generate_empathy_response(self, user_message: str) -> str:
        """Generate appropriate empathy response based on user's emotional state"""
        message_lower = user_message.lower()
        
        # Map emotional indicators to empathy responses
        if any(word in message_lower for word in ['bored', 'boring', 'nothing to do']):
            return "That sounds frustrating when you're feeling understimulated"
        
        elif any(word in message_lower for word in ['hate', 'hates', 'boss']):
            return "That sounds like a challenging work situation"
        
        elif any(word in message_lower for word in ['stressed', 'pressure', 'overwhelmed']):
            return "I understand that can feel overwhelming"
        
        elif any(word in message_lower for word in ['tired', 'exhausted', 'drained']):
            return "That sounds exhausting to deal with"
        
        elif any(word in message_lower for word in ['problem', 'issue', 'trouble']):
            return "That sounds like a difficult situation"
        
        elif any(word in message_lower for word in ['personal', 'wife', 'family']):
            return "I understand personal situations can be challenging"
        
        elif any(word in message_lower for word in ['beat up', 'fight', 'angry']):
            return "I can hear that you're feeling frustrated"
        
        elif any(word in message_lower for word in ['weather', 'day', 'morning']):
            return "I hope things improve for you"
        
        else:
            return "I understand that can be challenging"
    
    async def _handle_ai_readiness_assessment(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        """Handle AI interest and offer readiness assessment"""
        
        # Check if they've already mentioned challenges in previous conversation
        previous_challenges = self._extract_mentioned_challenges(context.messages)
        
        # Check if they're responding to assessment offer
        if any(phrase in user_message.lower() for phrase in ['yes', 'sure', 'okay', 'go ahead', 'let\'s do it']):
            return await self._conduct_assessment_flow(user_message, context, knowledge_context, previous_challenges)
        
        # Check if they're declining assessment
        if any(phrase in user_message.lower() for phrase in ['no', 'not now', 'maybe later', 'not interested']):
            return await self._handle_assessment_decline(user_message, context, knowledge_context)
        
        # Initial AI interest detected - offer assessment
        assessment_offer = self._generate_assessment_offer(user_message, previous_challenges)
        
        prompt = f"""
        {self.persona_prompt}
        
        The user has shown interest in AI or mentioned AI challenges: "{user_message}"
        
        {assessment_offer}
        
        Respond naturally and offer the AI readiness assessment in a consultative way.
        Keep it conversational, not formal or salesy.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "ai_readiness_assessment",
            "lead_score": context.lead_score
        }
    
    def _extract_mentioned_challenges(self, messages: List[Dict]) -> List[str]:
        """Extract any challenges already mentioned in the conversation"""
        challenges = []
        challenge_keywords = {
            'budget': ['budget', 'cost', 'expensive', 'funding', 'roi'],
            'expertise': ['expertise', 'skills', 'knowledge', 'capability', 'staff', 'team'],
            'risks': ['risk', 'risky', 'danger', 'disrupt', 'failure', 'break'],
            'understanding': ['understand', 'unclear', 'confused', 'benefits', 'what ai', 'how ai']
        }
        
        for message in messages:
            content = message.get('content', '').lower()
            for challenge_type, keywords in challenge_keywords.items():
                if any(keyword in content for keyword in keywords):
                    challenges.append(challenge_type)
        
        return list(set(challenges))  # Remove duplicates
    
    def _generate_assessment_offer(self, user_message: str, previous_challenges: List[str]) -> str:
        """Generate appropriate assessment offer based on context"""
        if previous_challenges:
            challenge_text = ', '.join(previous_challenges)
            return f"""
            I notice you've mentioned some challenges around {challenge_text}. 
            
            I have a specific AI readiness assessment that helps organizations understand exactly where they stand and what their next steps should be. 
            
            Would you like to go through it? It's just a few questions about your main challenges and where you want to be.
            """
        else:
            return """
            That's great that you're thinking about AI implementation. 
            
            I have a specific AI readiness assessment that helps organizations understand exactly where they stand and what their next steps should be.
            
            Would you like to go through it? It's just a few questions about your main challenges and where you want to be.
            """
    
    async def _conduct_assessment_flow(self, user_message: str, context: ConversationContext, knowledge_context: Dict, previous_challenges: List[str]) -> Dict[str, Any]:
        """Conduct the AI readiness assessment flow"""
        
        # If they already mentioned challenges, acknowledge and continue
        if previous_challenges:
            challenge_focus = previous_challenges[0]  # Focus on first mentioned
            return await self._address_specific_challenge(challenge_focus, user_message, context, knowledge_context)
        
        # Ask about main challenges with multiple choice
        prompt = f"""
        {self.persona_prompt}
        
        The user wants to do the AI readiness assessment. Start by asking about their main challenges.
        
        Use this structure:
        "Great! Let's start with understanding your main challenges. What do you think your biggest concerns are when it comes to adopting AI?
        
        I often see organizations face similar challenges:
        • Budget constraints and unclear ROI
        • Staff lacking technical capabilities or expertise  
        • Concerns about risks and process disruption
        • Unclear understanding of what benefits AI could bring
        
        Do any of these resonate with you?"
        
        Keep it conversational and consultative.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "ai_readiness_assessment",
            "lead_score": context.lead_score
        }
    
    async def _address_specific_challenge(self, challenge_type: str, user_message: str, context: ConversationContext, knowledge_context: Dict) -> Dict[str, Any]:
        """Address specific challenge with relevant philosophy"""
        
        # Map challenges to core philosophies
        philosophy_mapping = {
            'budget': {
                'philosophy': 'Democratic Technology Building',
                'message': 'Everyone is a technology builder. In the age of LLMs and no-code platforms, your existing team can create solutions without big IT investments. This democratization reduces costs and accelerates innovation.'
            },
            'expertise': {
                'philosophy': 'Capability Transfer Over Dependency', 
                'message': 'I believe in building internal ownership, not vendor dependency. My approach prioritizes knowledge transfer and ensuring your team can own, operate, and evolve solutions independently.'
            },
            'risks': {
                'philosophy': 'Iterative Value Delivery',
                'message': 'I always start small, prove value, then scale systematically. This contrasts with "big bang" approaches and ensures continuous learning while minimizing risks.'
            },
            'understanding': {
                'philosophy': 'Data-Driven Foundation Building',
                'message': 'Robust data capabilities are the foundation of all transformation. I focus on practical data capabilities and creating self-learning systems before attempting advanced analytics.'
            }
        }
        
        philosophy_info = philosophy_mapping.get(challenge_type, philosophy_mapping['understanding'])
        
        prompt = f"""
        {self.persona_prompt}
        
        The user has indicated their main challenge is around {challenge_type}. 
        
        Apply this core philosophy in your response:
        
        **{philosophy_info['philosophy']}:**
        {philosophy_info['message']}
        
        Then ask about their future state vision:
        "Where do you want your organization to be in terms of AI capabilities? How do you think your business would benefit?"
        
        After they respond, offer next steps:
        "Based on what you've shared, here's what I'd recommend as next steps:
        
        We start small and prove value through free prototypes. I can help you build proof-of-concept solutions to see what's possible before any major commitment. This iterative approach removes risk and builds confidence.
        
        Would you like to schedule a call to discuss a specific prototype we could build for your organization? I typically do these as AI readiness assessments where we map out exactly what would work best for your situation."
        
        Keep it natural and consultative. Weave the philosophy naturally into addressing their concern.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "ai_readiness_assessment", 
            "lead_score": context.lead_score
        }
    
    async def _handle_assessment_decline(self, user_message: str, context: ConversationContext, knowledge_context: Dict) -> Dict[str, Any]:
        """Handle when user declines the assessment"""
        
        prompt = f"""
        {self.persona_prompt}
        
        The user declined the AI readiness assessment: "{user_message}"
        
        Respond naturally and respectfully. Keep the door open and offer alternative ways to help.
        Ask what specific aspect of AI they're most curious about or how you can best help them.
        
        Don't be pushy, just helpful and available.
        """
        
        response_content = await self._generate_response(prompt, context)
        return {
            "content": response_content,
            "stage": "solution_presentation",  # Move to general solution stage
            "lead_score": context.lead_score
        }
    
    async def _build_rapport_response(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
        
        prompt = f"""
        {self.persona_prompt}
        
        This is early in the conversation. The user said: "{user_message}"
        
        Respond naturally and proportionally to their input. If they're being brief, keep your response brief.
        Focus on understanding what they need rather than showcasing expertise.
        Ask one simple, relevant question to understand how you can help.
        
        {context_section}
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
        
        The user is asking about your expertise or experience: "{user_message}"
        
        Share relevant experience proportionally to their question level. If they ask a simple question, give a simple answer.
        Only provide detailed examples if they're asking for specifics. Always match their energy level.
        
        Previous context: {self._format_conversation_history(context)}{context_section}
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
        
        The user is asking for solutions or recommendations: "{user_message}"
        
        Provide helpful recommendations proportional to their request. Match their level of detail.
        If they ask a broad question, give a broad answer. If they want specifics, provide specifics.
        Be helpful without overwhelming them.
        
        Previous context: {self._format_conversation_history(context)}{context_section}
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
        initial_score = context.lead_score
        
        # Technical depth indicators (high value)
        technical_keywords = ['dynamics', 'pmo', 'transformation', 'implementation', 'system', 'platform', 'integration']
        if any(keyword in message_lower for keyword in technical_keywords):
            context.lead_score += 15
        
        # Budget indicators (very high value)
        budget_keywords = ['budget', 'investment', 'cost', 'roi', 'money', 'funding', 'approve']
        if any(keyword in message_lower for keyword in budget_keywords):
            context.lead_score += 20
        
        # Timeline urgency (medium value)
        urgency_keywords = ['urgent', 'asap', 'soon', 'immediately', 'quick', 'fast']
        if any(keyword in message_lower for keyword in urgency_keywords):
            context.lead_score += 10
        
        # Authority indicators (high value)
        authority_keywords = ['we need', 'our organization', 'decision', 'i decide', 'cto', 'ceo', 'director', 'manager']
        if any(keyword in message_lower for keyword in authority_keywords):
            context.lead_score += 15
        
        # AI Interest indicators (high value)
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'automation', 'ai readiness', 'ai challenges']
        if any(keyword in message_lower for keyword in ai_keywords):
            context.lead_score += 18
        
        # Assessment acceptance (very high value)
        assessment_keywords = ['yes', 'sure', 'okay', 'go ahead', 'let\'s do it', 'assessment']
        if any(keyword in message_lower for keyword in assessment_keywords) and context.engagement_stage == "ai_readiness_assessment":
            context.lead_score += 30
        
        # Engagement indicators (very high value)
        engagement_keywords = ['meeting', 'call', 'consultation', 'help us', 'schedule', 'discuss', 'talk']
        if any(keyword in message_lower for keyword in engagement_keywords):
            context.lead_score += 25
        
        # Call scheduling interest (highest value)
        call_scheduling_keywords = ['schedule a call', 'book a meeting', 'ai readiness assessment call', 'consultation call']
        if any(keyword in message_lower for keyword in call_scheduling_keywords):
            context.lead_score += 35
        
        # Organization size indicators (medium-high value)
        size_keywords = ['organization', 'company', 'team', 'properties', 'housing association', 'council']
        if any(keyword in message_lower for keyword in size_keywords):
            context.lead_score += 12
        
        # Problem severity indicators (medium value)
        problem_keywords = ['problem', 'issue', 'failing', 'broken', 'crisis', 'help']
        if any(keyword in message_lower for keyword in problem_keywords):
            context.lead_score += 8
        
        # Negative indicators (reduce score)
        negative_keywords = ['just browsing', 'bored', 'maybe', 'not sure', 'thinking about']
        if any(keyword in message_lower for keyword in negative_keywords):
            context.lead_score = max(0, context.lead_score - 5)
        
        # Off-topic indicators (reduce score)
        off_topic_keywords = ['weather', 'personal', 'wife', 'boss', 'beat up', 'life']
        if any(keyword in message_lower for keyword in off_topic_keywords):
            context.lead_score = max(0, context.lead_score - 3)
        
        # Cap the score at 100
        context.lead_score = min(context.lead_score, 100)
        
        # Log scoring changes for debugging
        if context.lead_score != initial_score:
            score_change = context.lead_score - initial_score
            logger.debug(f"Lead score updated: {initial_score} -> {context.lead_score} (change: {score_change:+d}) for message: '{user_message[:50]}...')")