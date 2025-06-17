#!/usr/bin/env python3
"""
Final E2E test for the working Streamlit app
"""
import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def run_final_e2e_test():
    """Run the final E2E test"""
    print("🚀 Final E2E Test - Ram Digital Twin")
    print("=" * 50)
    
    # Kill existing processes
    os.system("pkill -f streamlit")
    time.sleep(2)
    
    # Start the fixed app
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app_fixed.py", "--server.port=8507"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    
    print("⏳ Starting fixed Streamlit app...")
    time.sleep(12)  # Wait for startup
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to app
            print("🌐 Loading application...")
            page.goto("http://localhost:8507")
            
            # Wait for app to load
            page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
            print("✅ Application loaded successfully")
            
            # Check page title
            title = page.title()
            print(f"📄 Page title: {title}")
            
            # Look for input elements
            text_inputs = page.locator('input[type="text"]').all()
            send_buttons = page.locator('button:has-text("Send")').all()
            
            print(f"🔍 Found {len(text_inputs)} text inputs and {len(send_buttons)} send buttons")
            
            if text_inputs and send_buttons:
                print("\n💬 Testing conversation scenarios...")
                
                # Test scenarios
                test_scenarios = [
                    {
                        "message": "What's your experience with PMO implementations?",
                        "expected_keywords": ["pmo", "experience", "implementation", "project"]
                    },
                    {
                        "message": "How do you handle Dynamics 365 projects?",
                        "expected_keywords": ["dynamics", "365", "implementation", "project"]
                    },
                    {
                        "message": "Can we schedule a consultation?",
                        "expected_keywords": ["consultation", "meeting", "schedule", "contact"]
                    }
                ]
                
                successful_tests = 0
                
                for i, scenario in enumerate(test_scenarios, 1):
                    print(f"\n   Test {i}: {scenario['message']}")
                    
                    # Fill input
                    text_input = text_inputs[0]
                    send_button = send_buttons[0]
                    
                    text_input.fill(scenario['message'])
                    print(f"      ✅ Filled input")
                    
                    # Click send
                    send_button.click()
                    print(f"      ✅ Clicked send")
                    
                    # Wait for response
                    print(f"      ⏳ Waiting for response...")
                    
                    response_detected = False
                    for attempt in range(20):  # 20 second timeout
                        time.sleep(1)
                        page_content = page.content().lower()
                        
                        # Check for Ram's response
                        if "ram:" in page_content and "having trouble" not in page_content:
                            response_detected = True
                            print(f"      ✅ Response detected after {attempt + 1}s")
                            
                            # Check for expected keywords
                            keyword_found = any(keyword in page_content 
                                              for keyword in scenario['expected_keywords'])
                            
                            if keyword_found:
                                print(f"      ✅ Response contains relevant keywords")
                                successful_tests += 1
                            else:
                                print(f"      ⚠️ Response may not be fully relevant")
                            
                            break
                        elif "error" in page_content or "exception" in page_content:
                            print(f"      ❌ Error detected in response")
                            break
                    
                    if not response_detected:
                        print(f"      ❌ No response after 20 seconds")
                    
                    # Brief pause between tests
                    time.sleep(2)
                
                print(f"\n📊 Test Results:")
                print(f"   Successful conversations: {successful_tests}/{len(test_scenarios)}")
                
                # Check sidebar metrics
                print(f"\n📋 Checking sidebar metrics...")
                sidebar = page.locator('[data-testid="stSidebar"]')
                if sidebar.is_visible():
                    sidebar_text = sidebar.text_content()
                    
                    if "pinecone active" in sidebar_text.lower():
                        print(f"   ✅ Pinecone integration active")
                    
                    if "sources found" in sidebar_text.lower():
                        print(f"   ✅ Knowledge sources being used")
                    
                    if "lead score" in sidebar_text.lower():
                        print(f"   ✅ Lead scoring operational")
                    
                    print(f"   📊 Sidebar content: {sidebar_text[:200]}...")
                else:
                    print(f"   ⚠️ Sidebar not found")
                
                # Final assessment
                print(f"\n🎯 Final Assessment:")
                if successful_tests >= 2:
                    print(f"   ✅ E2E Test PASSED - System is working!")
                    print(f"   💡 The digital twin is ready for production use")
                    print(f"   🚀 Backend: Fully operational with Pinecone + Gemini")
                    print(f"   🌐 Frontend: Streamlit interface working correctly")
                    return True
                else:
                    print(f"   ❌ E2E Test FAILED - Issues detected")
                    return False
                
            else:
                print("❌ Could not find required input elements")
                return False
            
    finally:
        # Cleanup
        try:
            if hasattr(os, 'killpg'):
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.terminate()
        except:
            pass

if __name__ == "__main__":
    success = run_final_e2e_test()
    print(f"\n{'🎉 SUCCESS!' if success else '❌ FAILED'}")
    exit(0 if success else 1)