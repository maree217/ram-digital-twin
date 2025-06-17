#!/usr/bin/env python3
"""
Comprehensive E2E test to diagnose and test the system
"""
import time
import subprocess
import os
import signal
import asyncio
import sys
from playwright.sync_api import sync_playwright

# Add src to path
sys.path.append('src')
from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

def test_backend_directly():
    """Test the backend components directly"""
    print("🔧 Testing Backend Components")
    print("-" * 30)
    
    try:
        # Test agent
        agent = ConsultancyAgent()
        context = ConversationContext()
        
        print("✅ Agent initialized")
        print(f"   Model available: {bool(agent.model)}")
        print(f"   Vector search available: {agent.vector_search.is_available()}")
        print(f"   Pinecone available: {agent.vector_search.is_pinecone_available()}")
        
        # Test a simple interaction
        response = asyncio.run(agent.handle_interaction("Hello, tell me about PMO", context))
        
        content = response.get("content", "")
        if len(content) > 100:
            print("✅ Agent response working")
            print(f"   Response length: {len(content)} chars")
            print(f"   Sources: {response.get('knowledge_sources', 0)}")
            print(f"   Stage: {response.get('stage', 'unknown')}")
            return True
        else:
            print("❌ Agent response too short or empty")
            print(f"   Content: '{content}'")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_streamlit_and_test():
    """Run Streamlit and test with Playwright"""
    print("\n🌐 Testing Streamlit Interface")
    print("-" * 30)
    
    # Kill any existing processes
    os.system("pkill -f streamlit")
    time.sleep(2)
    
    # Start simple streamlit app
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Use original app
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port=8506"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    # Wait for startup
    print("⏳ Starting Streamlit app...")
    time.sleep(10)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Run visible for debugging
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate
            page.goto("http://localhost:8506")
            
            # Wait for app
            page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
            print("✅ Streamlit app loaded")
            
            # Take screenshot
            page.screenshot(path="app_loaded.png")
            print("📸 Screenshot saved: app_loaded.png")
            
            # Check page content
            page_text = page.content()
            print(f"📄 Page loaded, content length: {len(page_text)}")
            
            # Look for ANY input elements
            all_inputs = page.locator('input').all()
            all_textareas = page.locator('textarea').all()
            all_buttons = page.locator('button').all()
            
            print(f"🔍 Found {len(all_inputs)} inputs, {len(all_textareas)} textareas, {len(all_buttons)} buttons")
            
            # Check each input
            for i, inp in enumerate(all_inputs):
                try:
                    inp_type = inp.get_attribute("type") or "unknown"
                    placeholder = inp.get_attribute("placeholder") or "no placeholder"
                    visible = inp.is_visible()
                    print(f"   Input {i+1}: type={inp_type}, placeholder='{placeholder}', visible={visible}")
                except:
                    print(f"   Input {i+1}: Could not get attributes")
            
            # Check each button
            for i, btn in enumerate(all_buttons):
                try:
                    text = btn.text_content() or "no text"
                    visible = btn.is_visible()
                    print(f"   Button {i+1}: text='{text}', visible={visible}")
                except:
                    print(f"   Button {i+1}: Could not get attributes")
            
            # Try to find working elements
            working_input = None
            working_button = None
            
            for inp in all_inputs:
                if inp.is_visible():
                    working_input = inp
                    break
            
            for btn in all_buttons:
                if btn.is_visible() and 'send' in (btn.text_content() or '').lower():
                    working_button = btn
                    break
            
            if working_input and working_button:
                print("\n💬 Testing interaction with found elements:")
                
                test_message = "What's your PMO experience?"
                working_input.fill(test_message)
                print(f"   ✅ Filled input: '{test_message}'")
                
                working_button.click()
                print(f"   ✅ Clicked button")
                
                # Wait for response with timeout
                print(f"   ⏳ Waiting for response...")
                
                start_time = time.time()
                response_found = False
                
                for attempt in range(30):  # 30 second timeout
                    time.sleep(1)
                    current_content = page.content()
                    
                    # Look for response indicators
                    if "ram:" in current_content.lower() and "having trouble" not in current_content.lower():
                        response_found = True
                        print(f"   ✅ Response detected after {time.time() - start_time:.1f}s")
                        break
                    elif "error" in current_content.lower() or "exception" in current_content.lower():
                        print(f"   ❌ Error detected in response")
                        break
                    elif "thinking" in current_content.lower():
                        print(f"   ⏳ Still processing... ({attempt+1}s)")
                
                if not response_found:
                    print(f"   ❌ No valid response after 30 seconds")
                    
                    # Save debug info
                    page.screenshot(path="no_response.png")
                    with open("page_content_debug.html", "w") as f:
                        f.write(page.content())
                    print(f"   📸 Debug files saved")
                
            else:
                print("❌ Could not find working input/button combination")
                
                # Save debug screenshot
                page.screenshot(path="no_elements.png")
                print("📸 Debug screenshot saved: no_elements.png")
            
            # Keep browser open for manual inspection
            print("\n⏳ Keeping browser open for 10 seconds for manual inspection...")
            time.sleep(10)
            
            browser.close()
            
    finally:
        # Cleanup
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
        except:
            pass

def main():
    """Run comprehensive test"""
    print("🚀 Comprehensive E2E Test for Ram Digital Twin")
    print("=" * 50)
    
    # Test 1: Backend
    backend_ok = test_backend_directly()
    
    # Test 2: Frontend
    if backend_ok:
        run_streamlit_and_test()
    else:
        print("❌ Skipping frontend test due to backend issues")
    
    print("\n🎯 Test Summary:")
    print(f"   Backend: {'✅ Working' if backend_ok else '❌ Failed'}")
    print("   Frontend: See output above")
    
    if backend_ok:
        print("\n💡 The backend is working correctly!")
        print("   If the frontend has issues, it's likely a Streamlit rendering problem.")
        print("   Try running the app manually: streamlit run streamlit_app.py")
    else:
        print("\n💡 Fix the backend issues first before testing frontend.")

if __name__ == "__main__":
    main()