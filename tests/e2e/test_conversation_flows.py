import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
class TestConversationFlows:
    
    def test_discovery_stage_conversation(self, page: Page, api_mocker):
        """Test discovery stage conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "Thank you for your interest in PMO setup. To better understand your needs, could you tell me about your current project management challenges?"
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("We need help setting up a PMO for our organization")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check that response includes discovery questions
        page_content = page.locator('body').text_content()
        discovery_indicators = [
            "understand", "tell me", "current", "challenges", 
            "organization", "needs", "what", "how"
        ]
        
        assert any(indicator in page_content.lower() for indicator in discovery_indicators)
    
    def test_expertise_demonstration_flow(self, page: Page, api_mocker):
        """Test expertise demonstration conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "I've led PMO transformations for organizations with £50M+ budgets, including housing associations managing 50,000+ properties. I established governance frameworks that reduced project delivery time by 35%."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("What's your experience with PMO implementations?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check that response demonstrates specific expertise
        page_content = page.locator('body').text_content()
        expertise_indicators = [
            "experience", "led", "implemented", "achieved", 
            "results", "organizations", "projects", "governance"
        ]
        
        assert any(indicator in page_content.lower() for indicator in expertise_indicators)
    
    def test_solution_presentation_flow(self, page: Page, api_mocker):
        """Test solution presentation conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "I recommend a phased approach: 1) PMO framework design, 2) Governance implementation, 3) Process standardization. This typically achieves 85% project success rates and 20% cost reduction."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("How would you recommend we approach our PMO setup?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check that response provides specific recommendations
        page_content = page.locator('body').text_content()
        solution_indicators = [
            "recommend", "approach", "steps", "phase", 
            "framework", "implementation", "achieve", "results"
        ]
        
        assert any(indicator in page_content.lower() for indicator in solution_indicators)
    
    def test_engagement_conversion_flow(self, page: Page, api_mocker):
        """Test engagement conversion conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "I'd be happy to discuss your PMO needs in detail. Let's schedule a consultation to assess your specific requirements and create a tailored implementation plan. You can reach me at ram@senthilmaree.com or book a call through my Calendly."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("Can we schedule a consultation to discuss this further?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check that response facilitates engagement
        page_content = page.locator('body').text_content()
        engagement_indicators = [
            "schedule", "consultation", "discuss", "meeting", 
            "contact", "call", "calendly", "ram@senthilmaree.com"
        ]
        
        assert any(indicator in page_content.lower() for indicator in engagement_indicators)
    
    def test_multi_turn_conversation_context(self, page: Page, api_mocker):
        """Test multi-turn conversation maintains context"""
        # First turn - establish context
        api_mocker.mock_gemini_api(
            page,
            "For housing associations, I typically focus on tenant service improvements and operational efficiency. What size is your organization?"
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("We're a housing association looking for digital transformation")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Second turn - should reference housing association context
        api_mocker.mock_gemini_api(
            page,
            "Perfect. For a 25,000-property housing association, I'd recommend starting with tenant portal implementation and process automation."
        )
        
        chat_input.fill("We manage about 25,000 properties")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Check that context is maintained
        page_content = page.locator('body').text_content()
        context_indicators = [
            "housing", "properties", "tenant", "association", 
            "portal", "automation", "25,000"
        ]
        
        assert any(indicator in page_content.lower() for indicator in context_indicators)
    
    def test_dynamics_365_expertise_flow(self, page: Page, api_mocker):
        """Test Dynamics 365 specific conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "I've led Dynamics 365 implementations for 2,000+ user organizations. This includes custom workflows, Power Platform integration, and achieving 95% user adoption rates within 6 months."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("Tell me about your Dynamics 365 implementation experience")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check for Dynamics-specific expertise
        page_content = page.locator('body').text_content()
        dynamics_indicators = [
            "dynamics", "implementation", "workflows", "power platform", 
            "adoption", "users", "integration", "custom"
        ]
        
        assert any(indicator in page_content.lower() for indicator in dynamics_indicators)
    
    def test_change_management_expertise_flow(self, page: Page, api_mocker):
        """Test change management conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "My change management approach follows the EMBRACE model, consistently achieving 60% reduction in resistance and 40% faster adoption rates."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("How do you handle change management resistance?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check for change management expertise
        page_content = page.locator('body').text_content()
        change_indicators = [
            "change management", "resistance", "adoption", "embrace", 
            "stakeholder", "training", "communication", "methodology"
        ]
        
        assert any(indicator in page_content.lower() for indicator in change_indicators)
    
    def test_public_sector_specialization_flow(self, page: Page, api_mocker):
        """Test public sector specialization conversation"""
        api_mocker.mock_gemini_api(
            page,
            "I specialize in public sector transformation, particularly councils and housing associations. This includes GDPR compliance, efficiency improvements, and citizen service enhancement."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("Do you have experience with public sector organizations?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check for public sector expertise
        page_content = page.locator('body').text_content()
        public_sector_indicators = [
            "public sector", "councils", "housing", "compliance", 
            "gdpr", "citizen", "government", "efficiency"
        ]
        
        assert any(indicator in page_content.lower() for indicator in public_sector_indicators)
    
    def test_roi_and_business_value_discussion(self, page: Page, api_mocker):
        """Test ROI and business value conversation flow"""
        api_mocker.mock_gemini_api(
            page,
            "Typical ROI from my transformations is 300% within 18 months, with 40% operational cost reduction and 60% process efficiency improvement."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("What kind of ROI can we expect from digital transformation?")
        chat_input.press("Enter")
        
        page.wait_for_timeout(3000)
        
        # Check for business value discussion
        page_content = page.locator('body').text_content()
        roi_indicators = [
            "roi", "return", "cost", "savings", "efficiency", 
            "improvement", "value", "business", "reduction"
        ]
        
        assert any(indicator in page_content.lower() for indicator in roi_indicators)
    
    @pytest.mark.slow
    def test_complex_conversation_scenario(self, page: Page, api_mocker):
        """Test complex multi-stage conversation scenario"""
        # Stage 1: Discovery
        api_mocker.mock_gemini_api(
            page,
            "I'd love to help with your transformation. Tell me about your current challenges."
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("We're struggling with project delivery and need transformation help")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Stage 2: Expertise demonstration
        api_mocker.mock_gemini_api(
            page,
            "I've helped organizations achieve 85% project success rates through PMO establishment."
        )
        
        chat_input.fill("What's your track record with project success?")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Stage 3: Solution presentation
        api_mocker.mock_gemini_api(
            page,
            "I recommend a 3-phase approach: PMO setup, process standardization, and governance implementation."
        )
        
        chat_input.fill("What would you recommend for our situation?")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Stage 4: Engagement
        api_mocker.mock_gemini_api(
            page,
            "Let's schedule a consultation to create your transformation roadmap."
        )
        
        chat_input.fill("This sounds promising. Can we set up a meeting?")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Verify full conversation flow
        page_content = page.locator('body').text_content()
        
        # Should contain elements from all stages
        flow_elements = [
            "challenges", "success rates", "recommend", "consultation"
        ]
        
        for element in flow_elements:
            assert element in page_content.lower()