#!/usr/bin/env python3
"""
Test the fixed Streamlit app
"""
import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def test_fixed_app():
    """Test the fixed Streamlit app"""
    print("🚀 Testing Fixed Streamlit App")
    print("=" * 40)
    
    # Start the fixed app
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port=8504"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    time.sleep(10)  # Wait for startup
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to app
            page.goto("http://localhost:8504")
            
            # Wait for app to load
            page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
            print("✅ App loaded successfully")
            
            # Look for form elements
            print("\n🔍 Looking for chat form elements:")
            
            # Check for text input
            text_inputs = page.locator('input[type="text"]').all()
            print(f"   Found {len(text_inputs)} text inputs")
            
            # Check for submit button
            submit_buttons = page.locator('button').all()
            send_buttons = [btn for btn in submit_buttons 
                          if 'send' in (btn.text_content() or '').lower()]
            print(f"   Found {len(send_buttons)} send buttons")
            
            if text_inputs and send_buttons:
                print("\n💬 Testing chat interaction:")
                
                # Fill input
                text_input = text_inputs[0]
                send_button = send_buttons[0]
                
                test_message = "What's your experience with PMO setup?"
                text_input.fill(test_message)
                print(f"   ✅ Filled input: '{test_message}'")
                
                # Click send
                send_button.click()
                print(f"   ✅ Clicked send button")
                
                # Wait for response with longer timeout
                print(f"   ⏳ Waiting for response...")
                time.sleep(15)  # Wait longer for processing
                
                # Check page content for response
                page_content = page.content()
                
                # Look for response indicators
                if "ram:" in page_content.lower():
                    print(f"   ✅ Response detected!")
                elif "thinking" in page_content.lower():
                    print(f"   ⏳ Still processing...")
                elif "trouble processing" in page_content.lower():
                    print(f"   ❌ Error message detected")
                else:
                    print(f"   ❓ Unclear status")
                
                # Check conversation history
                messages = page.locator('.user-message, .assistant-message').all()
                print(f"   📝 Found {len(messages)} messages in history")
                
                # Check sidebar metrics
                sidebar_text = page.locator('[data-testid="stSidebar"]').text_content()
                if sidebar_text:
                    if "pinecone active" in sidebar_text.lower():
                        print(f"   ✅ Pinecone status: Active")
                    if "sources found" in sidebar_text.lower():
                        print(f"   ✅ Knowledge sources detected")
                else:
                    print(f"   ⚠️ No sidebar metrics found")
                
            else:
                print("   ❌ Could not find required form elements")
            
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
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_fixed_app()