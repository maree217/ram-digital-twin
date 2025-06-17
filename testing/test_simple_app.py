#!/usr/bin/env python3
"""
Test the simple working app end-to-end
"""
import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def test_simple_app():
    """Test the simple working app"""
    print("🚀 Testing Simple Working App")
    print("=" * 40)
    
    # Start the simple app
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", "simple_working_app.py", "--server.port=8505"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    time.sleep(8)  # Wait for startup
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to app
            page.goto("http://localhost:8505")
            
            # Wait for app to load
            page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
            print("✅ Simple app loaded successfully")
            
            # Look for input elements
            print("\n🔍 Looking for input elements:")
            
            # Find text input
            text_input = page.locator('input[type="text"]').first
            if text_input.is_visible():
                print("   ✅ Found text input")
                
                # Find send button
                send_button = page.locator('button:has-text("Send Message")').first
                if send_button.is_visible():
                    print("   ✅ Found send button")
                    
                    # Test interaction
                    print("\n💬 Testing chat interaction:")
                    
                    test_message = "What's your experience with PMO setup?"
                    text_input.fill(test_message)
                    print(f"   ✅ Filled input: '{test_message}'")
                    
                    send_button.click()
                    print(f"   ✅ Clicked send button")
                    
                    # Wait for response
                    print(f"   ⏳ Waiting for response (30 seconds)...")
                    
                    # Wait for spinner to disappear and response to appear
                    try:
                        page.wait_for_selector('text=Ram:', timeout=30000)
                        print(f"   ✅ Response received!")
                        
                        # Get the response content
                        response_elements = page.locator('text=Ram:').all()
                        if response_elements:
                            response_text = response_elements[-1].text_content()
                            print(f"   📝 Response preview: {response_text[:100]}...")
                            
                            if "trouble processing" in response_text:
                                print(f"   ❌ Error in response")
                            elif len(response_text) > 50:
                                print(f"   ✅ Valid response received")
                            else:
                                print(f"   ⚠️ Short response")
                        
                    except Exception as e:
                        print(f"   ❌ No response received: {e}")
                        
                        # Check for error messages
                        page_content = page.content()
                        if "error" in page_content.lower():
                            print(f"   📋 Page contains error messages")
                        if "exception" in page_content.lower():
                            print(f"   📋 Page contains exceptions")
                    
                    # Check sidebar status
                    sidebar = page.locator('[data-testid="stSidebar"]')
                    if sidebar.is_visible():
                        sidebar_text = sidebar.text_content()
                        print(f"   📊 Sidebar status: {sidebar_text}")
                    
                else:
                    print("   ❌ Send button not found")
            else:
                print("   ❌ Text input not found")
            
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
    
    print("\n🎯 Simple app test completed!")

if __name__ == "__main__":
    test_simple_app()