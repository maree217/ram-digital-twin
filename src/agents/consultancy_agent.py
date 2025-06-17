import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from src.config import settings
from src.knowledge.vector_search import VectorKnowledgeSearch
from src.analytics.conversation_tracker import ConversationTracker

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# --- Constants for Agent Response Dictionary Keys ---
# These are the keys used in the dictionary returned by handle_interaction and its sub-methods
KEY_CONTENT = "content"
KEY_STAGE = "stage"
KEY_LEAD_SCORE = "lead_score"
KEY_KNOWLEDGE_SOURCES = "knowledge_sources"
KEY_VECTOR_SEARCH_AVAILABLE = "vector_search_available"
# Internal keys for context or messages
KEY_ROLE = "role"
KEY_SOURCES = "sources"
KEY_CONTEXT = "context"
KEY_SEARCH_TYPE = "search_type"
KEY_DOCUMENT = "document"
KEY_CHUNKS = "chunks"


ENGAGEMENT_STAGE_CONFIG = [
    {
        "name": "greeting",
        "patterns": ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
        "logic": lambda msg, ctx: ctx.messages == [] and any(msg.startswith(p) or msg == p for p in ENGAGEMENT_STAGE_CONFIG[0]["patterns"])
    },
    {
        "name": "casual_chat",
        "patterns": [
            'weather', 'day', 'feeling', 'tired', 'stressed', 'crap', 'bad',
            'bored', 'life', 'personal', 'wife', 'boss', 'beat up', 'hate',
            'just browsing', 'looking around', 'not sure'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[1]["patterns"])
    },
    {
        "name": "ai_readiness_assessment",
        "patterns": [
            'ai', 'artificial intelligence', 'machine learning', 'automation',
            'ai challenges', 'ai implementation', 'ai readiness', 'ai adoption',
            'digital transformation', 'technology challenges', 'ai benefits',
            'ai risks', 'implementing ai', 'ai solutions', 'ai strategy',
            'ai challenge', 'ai problem', 'ai issue', 'ai difficulty',
            'technology challenge', 'digital challenge', 'automation challenge',
            'implementation challenge', 'adoption challenge'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[2]["patterns"])
    },
    {
        "name": "engagement_conversion",
        "patterns": [
            'schedule a call', 'book a meeting', 'consultation', 'discuss further',
            'help us', 'schedule', 'when can we', 'available for', 'set up a call',
            'talk to someone', 'speak with', 'contact', 'reach out'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[3]["patterns"])
    },
    {
        "name": "solution_presentation",
        "patterns": [
            'how to', 'what should', 'recommend', 'approach', 'strategy',
            'need to', 'want to', 'best way', 'help with', 'solution for',
            'implement', 'set up', 'establish', 'create', 'build'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[4]["patterns"])
    },
    {
        "name": "expertise_demonstration",
        "patterns": [
            'experience', 'have you', 'can you', 'dynamics', 'pmo', 'transformation',
            'worked with', 'familiar with', 'know about', 'expertise in',
            'background', 'qualifications', 'track record', 'delivered',
            'case studies', 'references', 'results', 'prove'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[5]["patterns"])
    },
    {
        "name": "solution_presentation", # Duplicated for business_patterns, will follow order
        "patterns": [
            'digital transformation', 'business', 'organization', 'company',
            'systems', 'processes', 'operations', 'efficiency', 'automation'
        ],
        "logic": lambda msg, ctx: any(p in msg for p in ENGAGEMENT_STAGE_CONFIG[6]["patterns"])
    },
    {
        "name": "rapport_building",
        "patterns": [], # No specific patterns, logic based on message_count and other stages
        "logic": lambda msg, ctx: len(ctx.messages) < 3 and not any(
            stage_config["logic"](msg, ctx)
            for stage_config in ENGAGEMENT_STAGE_CONFIG[2:7] # Check against business/solution stages
        )
    }
]

LEAD_SCORING_RULES = [
    {"group": "technical_depth", "keywords": ['dynamics', 'pmo', 'transformation', 'implementation', 'system', 'platform', 'integration'], "score": 15},
    {"group": "budget", "keywords": ['budget', 'investment', 'cost', 'roi', 'money', 'funding', 'approve'], "score": 20},
    {"group": "urgency", "keywords": ['urgent', 'asap', 'soon', 'immediately', 'quick', 'fast'], "score": 10},
    {"group": "authority", "keywords": ['we need', 'our organization', 'decision', 'i decide', 'cto', 'ceo', 'director', 'manager'], "score": 15},
    {"group": "ai_interest", "keywords": ['ai', 'artificial intelligence', 'machine learning', 'automation', 'ai readiness', 'ai challenges'], "score": 18},
    {
        "group": "assessment_acceptance",
        "keywords": ['yes', 'sure', 'okay', 'go ahead', 'let\'s do it', 'assessment'],
        "score": 30,
        "condition": lambda ctx: ctx.engagement_stage == "ai_readiness_assessment"
    },
    {"group": "engagement", "keywords": ['meeting', 'call', 'consultation', 'help us', 'schedule', 'discuss', 'talk'], "score": 25},
    {"group": "call_scheduling", "keywords": ['schedule a call', 'book a meeting', 'ai readiness assessment call', 'consultation call'], "score": 35},
    {"group": "organization_size", "keywords": ['organization', 'company', 'team', 'properties', 'housing association', 'council'], "score": 12},
    {"group": "problem_severity", "keywords": ['problem', 'issue', 'failing', 'broken', 'crisis', 'help'], "score": 8},
    {"group": "negative", "keywords": ['just browsing', 'bored', 'maybe', 'not sure', 'thinking about'], "score": -5},
    {"group": "off_topic", "keywords": ['weather', 'personal', 'wife', 'boss', 'beat up', 'life'], "score": -3},
]

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
        persona_file_path = os.path.join(os.path.dirname(__file__), "prompts", "consultancy_persona.md")
        try:
            # Ensure the prompts directory exists (though it should have been created by the tool)
            prompts_dir = os.path.dirname(persona_file_path)
            if not os.path.exists(prompts_dir):
                os.makedirs(prompts_dir)
                logger.info(f"Created directory: {prompts_dir}")

            with open(persona_file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Persona file not found at {persona_file_path}. Returning default persona.")
            return "You are a helpful AI assistant." # Fallback basic persona
        except Exception as e:
            logger.error(f"Error loading persona file: {e}. Returning default persona.")
            return "You are a helpful AI assistant." # Fallback basic persona


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
            knowledge_sources_count = len(knowledge_context.get(KEY_SOURCES, []))
            response[KEY_KNOWLEDGE_SOURCES] = knowledge_sources_count
            response[KEY_VECTOR_SEARCH_AVAILABLE] = self.vector_search.is_pinecone_available()
            
            # Update response with current lead score
            response[KEY_LEAD_SCORE] = context.lead_score
            

            
            # Record the interaction for analytics
            await self.conversation_tracker.record_interaction(
                conversation_id=context.conversation_id,
                user_message=user_message,
                assistant_response=response[KEY_CONTENT],
                stage=stage,
                lead_score=context.lead_score,
                knowledge_sources=knowledge_sources_count
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in handle_interaction: {str(e)}")
            return {
                KEY_CONTENT: "I'm experiencing a technical issue. Could you please rephrase your question? If the issue persists, you can reach Ram directly at ram@senthilmaree.com",
                KEY_STAGE: context.engagement_stage,
                KEY_LEAD_SCORE: context.lead_score,
                KEY_KNOWLEDGE_SOURCES: 0,
                KEY_VECTOR_SEARCH_AVAILABLE: False
            }
    
    def _determine_engagement_stage(self, user_message: str, context: ConversationContext) -> str:
        message_lower = user_message.lower().strip()

        for stage_config in ENGAGEMENT_STAGE_CONFIG:
            if stage_config["logic"](message_lower, context):
                # Prevent staying in the same stage if it's not greeting or ai_readiness_assessment
                if stage_config["name"] == context.engagement_stage and stage_config["name"] not in ["greeting", "ai_readiness_assessment", "engagement_conversion"]:
                    # Check conversation flow - avoid getting stuck in same stage
                    recent_stages = [msg.get('stage', '') for msg in context.messages[-2:]] # Check last 2 relevant messages
                    if len(recent_stages) == 2 and all(stage == context.engagement_stage for stage in recent_stages):
                        if context.engagement_stage == "rapport_building":
                            logger.debug(f"Flow override: {context.engagement_stage} -> expertise_demonstration")
                            return "expertise_demonstration"
                        elif context.engagement_stage == "expertise_demonstration":
                            logger.debug(f"Flow override: {context.engagement_stage} -> solution_presentation")
                            return "solution_presentation"
                        elif context.engagement_stage == "casual_chat":
                             logger.debug(f"Flow override: {context.engagement_stage} -> rapport_building")
                             return "rapport_building"
                return stage_config["name"]

        # Default to current stage if no clear indicators match
        return context.engagement_stage

    def _build_prompt(self, specific_instructions: str, user_message: str, context: ConversationContext, knowledge_context: Optional[Dict] = None) -> str:
        """Builds a standardized prompt for the generative model."""
        
        # Add knowledge context if available
        context_section = ""
        if knowledge_context and knowledge_context.get("context"):
            context_section = f"\n\nRelevant experience context:\n{knowledge_context['context']}"
            
        history_section = self._format_conversation_history(context)

        prompt = f"""
        {self.persona_prompt}

        {specific_instructions}

        User message: "{user_message}"
        
        Previous conversation context:
        {history_section}
        {context_section}
        """
        return prompt

    async def _get_knowledge_context(self, user_message: str) -> Dict[str, Any]:
        """Get relevant knowledge context using vector search"""
        try:
            if self.vector_search.is_available():
                # Use vector search for semantic retrieval
                search_results = await self.vector_search.search(user_message, max_results=3)
                
                if search_results:
                    context_text = "\n\n".join([
                        f"From {result[KEY_DOCUMENT]}: {result[KEY_CHUNKS][0][:500]}..."
                        for result in search_results if result[KEY_CHUNKS]
                    ])
                    
                    return {
                        KEY_CONTEXT: context_text,
                        KEY_SOURCES: [r[KEY_DOCUMENT] for r in search_results],
                        KEY_SEARCH_TYPE: "vector" if self.vector_search.is_pinecone_available() else "semantic"
                    }
            
            # Fallback: return empty context
            return {KEY_CONTEXT: "", KEY_SOURCES: [], KEY_SEARCH_TYPE: "none"}
            
        except Exception as e:
            logger.error(f"Error getting knowledge context: {e}")
            return {KEY_CONTEXT: "", KEY_SOURCES: [], KEY_SEARCH_TYPE: "error"}
    
    async def _handle_greeting(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        """Handle initial greetings naturally"""
        specific_instructions = """
        The user has just greeted you.
        Respond naturally to their greeting and briefly introduce your purpose as outlined in the persona.
        Keep it friendly, brief (1-2 sentences), and end with the standard introduction question.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "greeting",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _handle_casual_chat(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        """Handle off-topic conversation empathetically"""
        
        # Determine the type of casual conversation and appropriate empathy response
        empathy_response = self._generate_empathy_response(user_message)
        specific_instructions = f"""
        The user is making casual conversation or mentioning something off-topic.
        
        EMPATHY FRAMEWORK:
        1. ACKNOWLEDGE their feeling/situation with understanding
        2. Use appropriate empathetic language: "{empathy_response}"
        3. Gently redirect to how you can help professionally
        4. Keep response brief (1-2 sentences maximum)
        
        Example structure: "[Empathy phrase] + [Brief redirect to consulting services]"
        
        Be genuine and natural, not corporate or robotic.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "casual_chat",
            KEY_LEAD_SCORE: context.lead_score
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
        specific_instructions = f"""
        The user has shown interest in AI or mentioned AI challenges.
        
        {assessment_offer}
        
        Respond naturally and offer the AI readiness assessment in a consultative way.
        Keep it conversational, not formal or salesy.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "ai_readiness_assessment",
            KEY_LEAD_SCORE: context.lead_score
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
            content = message.get(KEY_CONTENT, '').lower()
            for challenge_type, keywords in challenge_keywords.items():
                if any(keyword in content for keyword in keywords):
        
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
        
        specific_instructions = """
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
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "ai_readiness_assessment",
            KEY_LEAD_SCORE: context.lead_score
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
        specific_instructions = f"""
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
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "ai_readiness_assessment",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _handle_assessment_decline(self, user_message: str, context: ConversationContext, knowledge_context: Dict) -> Dict[str, Any]:
        """Handle when user declines the assessment"""
        
        specific_instructions = """
        The user declined the AI readiness assessment.
        
        Respond naturally and respectfully. Keep the door open and offer alternative ways to help.
        Ask what specific aspect of AI they're most curious about or how you can best help them.
        
        Don't be pushy, just helpful and available.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "solution_presentation",  # Move to general solution stage
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _build_rapport_response(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        specific_instructions = """
        This is early in the conversation.
        Respond naturally and proportionally to their input. If they're being brief, keep your response brief.
        Focus on understanding what they need rather than showcasing expertise.
        Ask one simple, relevant question to understand how you can help.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "rapport_building",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _demonstrate_expertise(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        specific_instructions = """
        The user is asking about your expertise or experience.
        Share relevant experience proportionally to their question level. If they ask a simple question, give a simple answer.
        Only provide detailed examples if they're asking for specifics. Always match their energy level.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "expertise_demonstration",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _present_solution(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        specific_instructions = """
        The user is asking for solutions or recommendations.
        Provide helpful recommendations proportional to their request. Match their level of detail.
        If they ask a broad question, give a broad answer. If they want specifics, provide specifics.
        Be helpful without overwhelming them.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "solution_presentation",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _handle_engagement(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        specific_instructions = """
        The user is showing interest in further engagement. Focus on:
        1. Confirming their specific needs and timeline
        2. Explaining how you can help with their challenges
        3. Suggesting appropriate next steps (consultation call, assessment, etc.)
        4. Providing clear contact information and availability
        
        Guide them toward scheduling a consultation to discuss their needs in detail.
        """
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: "engagement_conversion",
            KEY_LEAD_SCORE: context.lead_score
        }
    
    async def _generate_general_response(self, user_message: str, context: ConversationContext, knowledge_context: Dict = None) -> Dict[str, Any]:
        specific_instructions = "Respond as Ram would, maintaining the professional consultancy conversation."
        prompt = self._build_prompt(specific_instructions, user_message, context, knowledge_context)
        response_content = await self._generate_response(prompt, context)
        return {
            KEY_CONTENT: response_content,
            KEY_STAGE: context.engagement_stage,
            KEY_LEAD_SCORE: context.lead_score
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
            role = msg.get(KEY_ROLE, 'user') # Assuming 'user' as default role if not found
            content = msg.get(KEY_CONTENT, '')
            history.append(f"{role}: {content}")
        
        return "\n".join(history)
    
    def _update_lead_score(self, context: ConversationContext, user_message: str, response: Dict[str, Any]):
        message_lower = user_message.lower().strip()
        initial_score = context.lead_score

        for rule in LEAD_SCORING_RULES:
            if "condition" in rule and not rule["condition"](context):
                continue
            if any(keyword in message_lower for keyword in rule["keywords"]):
                context.lead_score += rule["score"]

        # Ensure score is not negative after deductions
        context.lead_score = max(0, context.lead_score)
        # Cap the score at 100
        context.lead_score = min(context.lead_score, 100)

        if context.lead_score != initial_score:
            score_change = context.lead_score - initial_score
            logger.debug(f"Lead score updated: {initial_score} -> {context.lead_score} (change: {score_change:+d}) for message: '{user_message[:50]}...' based on rules: {[r['group'] for r in LEAD_SCORING_RULES if any(k in message_lower for k in r['keywords'])]}")