#!/usr/bin/env python3
"""
Test the live Streamlit app to diagnose the chat input issue
"""
import time
import requests
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def test_streamlit_interface():
    """Test the actual Streamlit interface"""
    print("🚀 Testing Live Streamlit Interface")
    print("=" * 50)
    
    # Start Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app.py", "--server.port=8502"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    time.sleep(8)  # Wait longer for startup
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Go to the app
            page.goto("http://localhost:8502")
            
            # Wait for Streamlit to load
            try:
                page.wait_for_selector('[data-testid="stApp"]', timeout=15000)
                print("✅ Streamlit app loaded successfully")
            except:
                print("❌ Streamlit app failed to load")
                return False
            
            # Check page title
            title = page.title()
            print(f"📄 Page title: {title}")
            
            # Look for all possible chat input selectors
            input_selectors = [
                '[data-testid="stChatInput"]',
                '[data-testid="stChatInput"] input',
                'input[placeholder*="Ask me"]',
                'input[placeholder*="ask me"]',
                'textarea[placeholder*="Ask me"]',
                'textarea[placeholder*="ask me"]',
                '.stChatInput input',
                '.stTextInput input',
                'input[type="text"]',
                'textarea'
            ]
            
            print(f"\n🔍 Searching for chat input elements:")
            found_inputs = []
            
            for selector in input_selectors:
                try:
                    elements = page.locator(selector).all()
                    if elements:
                        print(f"   ✅ Found {len(elements)} elements with: {selector}")
                        for i, elem in enumerate(elements):
                            try:
                                placeholder = elem.get_attribute("placeholder") or "No placeholder"
                                visible = elem.is_visible()
                                print(f"      {i+1}. Placeholder: '{placeholder}', Visible: {visible}")
                                if visible:
                                    found_inputs.append((selector, elem))
                            except:
                                print(f"      {i+1}. Could not get attributes")
                    else:
                        print(f"   ❌ No elements found with: {selector}")
                except Exception as e:
                    print(f"   ❌ Error with selector {selector}: {e}")
            
            # Check for any error messages on the page
            print(f"\n🔍 Checking for error messages:")
            try:
                page_text = page.content()
                if "having trouble processing" in page_text.lower():
                    print("   ❌ Found 'having trouble processing' error message")
                if "technical issue" in page_text.lower():
                    print("   ❌ Found 'technical issue' error message")
                if "exception" in page_text.lower():
                    print("   ❌ Found 'exception' in page content")
                if "error" in page_text.lower():
                    print("   ⚠️ Found 'error' mentioned in page")
                else:
                    print("   ✅ No obvious error messages found")
            except Exception as e:
                print(f"   ❌ Could not check page content: {e}")
            
            # Try to interact with found inputs
            if found_inputs:
                print(f"\n💬 Testing chat interaction with first available input:")
                selector, input_elem = found_inputs[0]
                
                try:
                    # Try to type a message
                    test_message = "Hello test"
                    input_elem.fill(test_message)
                    print(f"   ✅ Successfully typed: '{test_message}'")
                    
                    # Look for submit button or try Enter
                    submit_buttons = page.locator('button').all()
                    found_submit = False
                    
                    for button in submit_buttons:
                        try:
                            text = button.text_content() or ""
                            if any(word in text.lower() for word in ['send', 'submit', '▶', '→']):
                                button.click()
                                print(f"   ✅ Clicked submit button: '{text}'")
                                found_submit = True
                                break
                        except:
                            continue
                    
                    if not found_submit:
                        # Try pressing Enter
                        input_elem.press("Enter")
                        print(f"   ✅ Pressed Enter")
                    
                    # Wait for response
                    time.sleep(3)
                    
                    # Check if response appeared
                    new_content = page.content()
                    if "ram:" in new_content.lower() or "response" in new_content.lower():
                        print(f"   ✅ Response detected on page")
                    else:
                        print(f"   ❌ No response detected")
                        
                except Exception as e:
                    print(f"   ❌ Error during interaction: {e}")
            else:
                print(f"\n❌ No usable chat inputs found")
            
            # Take a screenshot for debugging
            try:
                page.screenshot(path="streamlit_debug.png")
                print(f"\n📸 Screenshot saved as 'streamlit_debug.png'")
            except:
                print(f"\n❌ Could not save screenshot")
            
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
    
    return True

if __name__ == "__main__":
    test_streamlit_interface()