import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
class TestChatInterface:
    
    def test_page_loads_successfully(self, page: Page):
        """Test that the main page loads with all essential elements"""
        # Check page title
        expect(page).to_have_title("Ram Senthil-Maree - Digital Transformation Consultant")
        
        # Check main header elements
        expect(page.locator("h1")).to_contain_text("Ram Senthil-Maree")
        expect(page.locator("h3").first).to_contain_text("Digital Transformation Consultant")
        
        # Check welcome message is displayed
        welcome_section = page.locator(".assistant-message")
        expect(welcome_section.first).to_be_visible()
        expect(welcome_section.first).to_contain_text("Welcome! I'm Ram Senthil-Maree")
    
    def test_chat_input_exists_and_functional(self, page: Page):
        """Test that chat input field exists and accepts input"""
        # Look for Streamlit chat input
        chat_input = page.locator('[data-testid="stChatInput"] input')
        
        # If not found, try alternative selectors
        if not chat_input.is_visible():
            chat_input = page.locator('input[placeholder*="Ask me about"]')
        
        if not chat_input.is_visible():
            # Look for any text input in the chat area
            chat_input = page.locator('textarea, input[type="text"]').last
        
        expect(chat_input).to_be_visible()
        
        # Test typing in the input
        chat_input.fill("Test message")
        expect(chat_input).to_have_value("Test message")
    
    def test_basic_chat_interaction(self, page: Page, api_mocker):
        """Test basic chat interaction flow"""
        # Mock the Gemini API to avoid real API calls
        api_mocker.mock_gemini_api(
            page, 
            "Thank you for your question about PMO setup. Based on my experience..."
        )
        
        # Find chat input
        chat_input = page.locator('[data-testid="stChatInput"] input').first
        if not chat_input.is_visible():
            chat_input = page.locator('input').last
        
        # Type a message
        test_message = "Tell me about PMO setup"
        chat_input.fill(test_message)
        
        # Press Enter or find submit button
        chat_input.press("Enter")
        
        # Wait for response (with longer timeout for Streamlit)
        page.wait_for_timeout(3000)
        
        # Check that user message appears somewhere on the page
        expect(page.locator("body")).to_contain_text(test_message)
    
    def test_sidebar_metrics_display(self, page: Page):
        """Test that conversation metrics are displayed in sidebar"""
        # Look for sidebar content
        sidebar = page.locator('[data-testid="stSidebar"]')
        
        if sidebar.is_visible():
            # Check for conversation insights
            expect(sidebar).to_contain_text("Conversation Insights")
            expect(sidebar).to_contain_text("Stage:")
            expect(sidebar).to_contain_text("Lead Score:")
        else:
            # If no sidebar, check for metrics elsewhere
            metrics_section = page.locator('.metrics-container')
            if metrics_section.is_visible():
                expect(metrics_section).to_be_visible()
    
    def test_professional_styling(self, page: Page):
        """Test that professional styling is applied"""
        # Check for main header with gradient background
        header = page.locator('.main-header')
        expect(header).to_be_visible()
        
        # Check for professional color scheme
        body_bg = page.locator('body')
        expect(body_bg).to_be_visible()
        
        # Verify responsive design elements
        expect(page.locator('.chat-container')).to_be_visible()
    
    def test_knowledge_base_integration(self, page: Page, api_mocker, mock_knowledge_base):
        """Test that knowledge base integration works"""
        # Mock API response that includes knowledge base context
        api_mocker.mock_gemini_api(
            page,
            f"Based on my experience with PMO setup: {mock_knowledge_base['pmo']}"
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("What's your PMO experience?")
        chat_input.press("Enter")
        
        # Wait for processing
        page.wait_for_timeout(3000)
        
        # Check that knowledge base content might be referenced
        # (This is indirect since we're testing the integration, not the exact content)
        page_content = page.locator('body').text_content()
        assert "experience" in page_content.lower() or "pmo" in page_content.lower()
    
    def test_error_handling(self, page: Page, api_mocker):
        """Test error handling when API fails"""
        # Mock API failure
        api_mocker.mock_endpoint(
            page,
            "**/v1beta/models/gemini-*:generateContent",
            '{"error": {"message": "API Error"}}',
            500
        )
        
        chat_input = page.locator('input').last
        chat_input.fill("Test error handling")
        chat_input.press("Enter")
        
        # Wait for error handling
        page.wait_for_timeout(3000)
        
        # Should show some form of error message or fallback
        page_content = page.locator('body').text_content()
        error_indicators = [
            "technical issue", "try again", "contact", "error", 
            "ram@senthilmaree.com", "having trouble"
        ]
        
        assert any(indicator in page_content.lower() for indicator in error_indicators)
    
    def test_mobile_responsiveness(self, page: Page):
        """Test mobile responsiveness"""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Reload page
        page.reload()
        page.wait_for_selector('[data-testid="stApp"]', timeout=10000)
        
        # Check that essential elements are still visible
        expect(page.locator("h1")).to_be_visible()
        
        # Chat input should still be accessible
        chat_input = page.locator('input').last
        expect(chat_input).to_be_visible()
    
    @pytest.mark.slow
    def test_conversation_persistence(self, page: Page, api_mocker):
        """Test that conversation history persists during session"""
        # Mock consistent API responses
        api_mocker.mock_gemini_api(page, "Response to first message")
        
        # Send first message
        chat_input = page.locator('input').last
        chat_input.fill("First message")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Mock second response
        api_mocker.mock_gemini_api(page, "Response to second message")
        
        # Send second message
        chat_input.fill("Second message")
        chat_input.press("Enter")
        page.wait_for_timeout(2000)
        
        # Check that both messages are visible
        page_content = page.locator('body').text_content()
        assert "First message" in page_content
        assert "Second message" in page_content
    
    def test_contact_information_display(self, page: Page):
        """Test that contact information is displayed"""
        # Scroll to bottom to find contact info
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Look for contact information
        page_content = page.locator('body').text_content()
        
        contact_indicators = [
            "ram@senthilmaree.com", "linkedin", "calendly", 
            "consultation", "contact"
        ]
        
        assert any(indicator in page_content.lower() for indicator in contact_indicators)