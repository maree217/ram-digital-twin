import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

@pytest.mark.unit
class TestConsultancyAgent:
    
    @pytest.fixture
    def agent(self):
        """Create ConsultancyAgent instance for testing"""
        with patch('src.agents.consultancy_agent.genai') as mock_genai:
            mock_genai.configure = Mock()
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            agent = ConsultancyAgent()
            agent.model = mock_model
            return agent
    
    @pytest.fixture
    def context(self):
        """Create conversation context for testing"""
        return ConversationContext(
            conversation_id="test_conv_123",
            messages=[],
            engagement_stage="discovery",
            user_type="unknown"
        )
    
    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent.name == "ram_consultancy_advisor"
        assert agent.model_name == "gemini-2.0-flash-exp"
        assert hasattr(agent, 'persona_prompt')
        assert "Ram Senthil-Maree" in agent.persona_prompt
    
    def test_engagement_stage_detection_rapport_building(self, agent, context):
        """Test detection of rapport building stage"""
        user_message = "Hello, I'm new to this and looking for some guidance"
        stage = agent._determine_engagement_stage(user_message, context)
        assert stage == "rapport_building"
    
    def test_engagement_stage_detection_expertise_demonstration(self, agent, context):
        """Test detection of expertise demonstration stage"""
        user_message = "What's your experience with PMO implementations?"
        stage = agent._determine_engagement_stage(user_message, context)
        assert stage == "expertise_demonstration"
    
    def test_engagement_stage_detection_solution_presentation(self, agent, context):
        """Test detection of solution presentation stage"""
        user_message = "How would you recommend we approach our digital transformation?"
        stage = agent._determine_engagement_stage(user_message, context)
        assert stage == "solution_presentation"
    
    def test_engagement_stage_detection_conversion(self, agent, context):
        """Test detection of engagement conversion stage"""
        user_message = "Can we schedule a meeting to discuss this further?"
        stage = agent._determine_engagement_stage(user_message, context)
        assert stage == "engagement_conversion"
    
    def test_lead_scoring_technical_depth(self, agent, context):
        """Test lead scoring for technical depth indicators"""
        initial_score = context.lead_score
        user_message = "We need help with Dynamics 365 implementation and PMO setup"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should increase score for technical keywords
        assert context.lead_score > initial_score
    
    def test_lead_scoring_budget_indicators(self, agent, context):
        """Test lead scoring for budget indicators"""
        initial_score = context.lead_score
        user_message = "What's the typical budget and ROI for this kind of transformation?"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should increase score for budget mentions
        assert context.lead_score > initial_score
    
    def test_lead_scoring_urgency_indicators(self, agent, context):
        """Test lead scoring for urgency indicators"""
        initial_score = context.lead_score
        user_message = "We need this implemented ASAP due to urgent business requirements"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should increase score for urgency
        assert context.lead_score > initial_score
    
    def test_lead_scoring_authority_indicators(self, agent, context):
        """Test lead scoring for authority indicators"""
        initial_score = context.lead_score
        user_message = "Our organization has decided to move forward with this decision"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should increase score for authority indicators
        assert context.lead_score > initial_score
    
    def test_lead_scoring_engagement_indicators(self, agent, context):
        """Test lead scoring for engagement indicators"""
        initial_score = context.lead_score
        user_message = "We'd like to schedule a consultation call to help us with this"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should increase score significantly for engagement
        assert context.lead_score > initial_score + 20
    
    def test_lead_scoring_cap_at_100(self, agent, context):
        """Test that lead scoring caps at 100"""
        context.lead_score = 95
        user_message = "We urgently need a meeting to discuss our budget for this Dynamics PMO transformation"
        response = {"content": "test response"}
        
        agent._update_lead_score(context, user_message, response)
        
        # Should cap at 100
        assert context.lead_score == 100
    
    def test_conversation_history_formatting(self, agent, context):
        """Test conversation history formatting"""
        context.messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
            {"role": "assistant", "content": "Second response"},
            {"role": "user", "content": "Third message"}
        ]
        
        formatted = agent._format_conversation_history(context)
        
        # Should include last 3 messages
        assert "Second response" in formatted
        assert "Third message" in formatted
        # Should not include first message (only last 3)
        assert "First message" not in formatted
    
    def test_conversation_history_empty(self, agent, context):
        """Test conversation history formatting with empty context"""
        context.messages = []
        formatted = agent._format_conversation_history(context)
        assert formatted == "No previous conversation."
    
    @pytest.mark.asyncio
    async def test_handle_interaction_success(self, agent, context):
        """Test successful interaction handling"""
        user_message = "What's your experience with PMO setup?"
        
        # Mock the response generation
        with patch.object(agent, '_generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "I have extensive experience with PMO setup..."
            
            response = await agent.handle_interaction(user_message, context)
            
            assert response["content"] == "I have extensive experience with PMO setup..."
            assert "stage" in response
            assert "lead_score" in response
    
    @pytest.mark.asyncio
    async def test_handle_interaction_error_handling(self, agent, context):
        """Test error handling in interaction"""
        user_message = "Test message"
        
        # Mock an error in processing
        with patch.object(agent, '_determine_engagement_stage', side_effect=Exception("Test error")):
            response = await agent.handle_interaction(user_message, context)
            
            # Should return error message
            assert "technical issue" in response["content"]
            assert "ram@senthilmaree.com" in response["content"]
    
    @pytest.mark.asyncio
    async def test_generate_response_with_model(self, agent, context):
        """Test response generation with model"""
        # Mock successful model response
        mock_response = Mock()
        mock_response.text = "Generated response text"
        
        with patch('asyncio.to_thread', new_callable=AsyncMock) as mock_to_thread:
            mock_to_thread.return_value = mock_response
            
            result = await agent._generate_response("Test prompt", context)
            
            assert result == "Generated response text"
    
    @pytest.mark.asyncio
    async def test_generate_response_without_model(self, agent, context):
        """Test response generation without model (fallback)"""
        agent.model = None
        
        result = await agent._generate_response("Test prompt", context)
        
        assert "unable to access my AI capabilities" in result
        assert "ram@senthilmaree.com" in result
    
    @pytest.mark.asyncio
    async def test_generate_response_api_error(self, agent, context):
        """Test response generation with API error"""
        with patch('asyncio.to_thread', side_effect=Exception("API Error")):
            result = await agent._generate_response("Test prompt", context)
            
            assert "having trouble processing" in result
    
    def test_persona_prompt_content(self, agent):
        """Test that persona prompt contains key elements"""
        persona = agent.persona_prompt
        
        # Check for key expertise areas
        assert "PMO" in persona
        assert "Dynamics 365" in persona
        assert "digital transformation" in persona
        assert "Ram Senthil-Maree" in persona
        
        # Check for professional approach elements
        assert "Ask insightful questions" in persona
        assert "actionable recommendations" in persona
        assert "consultation" in persona
    
    @pytest.mark.asyncio
    async def test_rapport_building_response(self, agent, context):
        """Test rapport building response generation"""
        user_message = "Hello, I'm interested in your services"
        
        with patch.object(agent, '_generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "Welcome! I'd love to help. Tell me about your organization..."
            
            response = await agent._build_rapport_response(user_message, context)
            
            assert response["stage"] == "rapport_building"
            assert "content" in response
    
    @pytest.mark.asyncio
    async def test_expertise_demonstration_response(self, agent, context):
        """Test expertise demonstration response generation"""
        user_message = "What's your experience with transformations?"
        
        with patch.object(agent, '_generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "I've led transformations for organizations with £50M+ budgets..."
            
            response = await agent._demonstrate_expertise(user_message, context)
            
            assert response["stage"] == "expertise_demonstration"
            assert "content" in response
    
    @pytest.mark.asyncio
    async def test_solution_presentation_response(self, agent, context):
        """Test solution presentation response generation"""
        user_message = "How would you approach our transformation?"
        
        with patch.object(agent, '_generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "I recommend a 3-phase approach..."
            
            response = await agent._present_solution(user_message, context)
            
            assert response["stage"] == "solution_presentation"
            assert "content" in response
    
    @pytest.mark.asyncio
    async def test_engagement_conversion_response(self, agent, context):
        """Test engagement conversion response generation"""
        user_message = "Can we schedule a meeting?"
        
        with patch.object(agent, '_generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "I'd be happy to schedule a consultation..."
            
            response = await agent._handle_engagement(user_message, context)
            
            assert response["stage"] == "engagement_conversion"
            assert "content" in response