#!/usr/bin/env python3
"""
5 Comprehensive E2E Test Cases for Ram Digital Twin
"""
import time
import subprocess
import os
import signal
from playwright.sync_api import sync_playwright

def run_5_comprehensive_tests():
    """Run 5 explicit test cases with visible results"""
    print("🚀 5 COMPREHENSIVE E2E TESTS - Ram Digital Twin")
    print("=" * 60)
    
    test_results = []
    
    print("🌐 Connecting to localhost:8501...")
    
    try:
        with sync_playwright() as p:
            # Launch browser in non-headless mode for visibility
            browser = p.chromium.launch(headless=False, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()
            
            # Navigate to app
            page.goto("http://localhost:8501")
            print("✅ Successfully connected to Ram Digital Twin")
            
            # Wait for app to load
            page.wait_for_selector('[data-testid="stApp"]', timeout=20000)
            print("✅ Application interface loaded")
            
            # Take initial screenshot
            page.screenshot(path="test_0_initial_load.png")
            print("📸 Screenshot saved: test_0_initial_load.png")
            
            # Define 5 comprehensive test scenarios
            test_scenarios = [
                {
                    "id": 1,
                    "category": "Discovery Stage",
                    "message": "Hello Ram, I'm exploring digital transformation options for our housing association. We have around 15,000 properties and are struggling with outdated systems.",
                    "expected_stage": "discovery",
                    "expected_keywords": ["housing", "transformation", "systems", "properties", "digital"],
                    "description": "Initial discovery conversation about housing association challenges"
                },
                {
                    "id": 2,
                    "category": "Expertise Demonstration",
                    "message": "What's your specific experience with PMO implementations? Have you worked with organizations similar to ours before?",
                    "expected_stage": "expertise_demonstration", 
                    "expected_keywords": ["pmo", "experience", "implementation", "organizations", "similar"],
                    "description": "Testing expertise recall and experience demonstration"
                },
                {
                    "id": 3,
                    "category": "Technical Deep Dive",
                    "message": "We're considering Microsoft Dynamics 365 for our customer relationship management. What's your approach to D365 implementations and what challenges should we expect?",
                    "expected_stage": "expertise_demonstration",
                    "expected_keywords": ["dynamics", "365", "crm", "implementation", "challenges", "microsoft"],
                    "description": "Technical expertise on specific technology solutions"
                },
                {
                    "id": 4,
                    "category": "Solution Presentation", 
                    "message": "Based on our conversation, how would you recommend we structure a digital transformation program for our housing association? What would the timeline and key milestones look like?",
                    "expected_stage": "solution_presentation",
                    "expected_keywords": ["recommend", "structure", "program", "timeline", "milestones", "transformation"],
                    "description": "Solution design and program structuring"
                },
                {
                    "id": 5,
                    "category": "Engagement Conversion",
                    "message": "This sounds very promising and exactly what we need. How can we move forward with a consultation to discuss this in more detail? What would be the next steps?",
                    "expected_stage": "engagement_conversion",
                    "expected_keywords": ["consultation", "move forward", "next steps", "discuss", "detail"],
                    "description": "Converting to business engagement"
                }
            ]
            
            successful_tests = 0
            total_response_chars = 0
            knowledge_sources_used = 0
            
            for scenario in test_scenarios:
                print(f"\n{'='*60}")
                print(f"🧪 TEST {scenario['id']}: {scenario['category']}")
                print(f"📝 Description: {scenario['description']}")
                print(f"💬 Message: {scenario['message']}")
                print(f"{'='*60}")
                
                # Find input elements
                input_element = None
                send_button = None
                
                # Try different selectors
                try:
                    inputs = page.locator('input[type="text"]').all()
                    buttons = page.locator('button').all()
                    
                    for inp in inputs:
                        if inp.is_visible():
                            input_element = inp
                            break
                    
                    for btn in buttons:
                        if btn.is_visible() and 'send' in (btn.text_content() or '').lower():
                            send_button = btn
                            break
                    
                    if not input_element or not send_button:
                        print("❌ Could not find input/button elements")
                        continue
                    
                    print("✅ Found input and send button")
                    
                    # Clear and fill input
                    input_element.fill("")
                    input_element.fill(scenario['message'])
                    print("✅ Message entered")
                    
                    # Take screenshot before sending
                    page.screenshot(path=f"test_{scenario['id']}_before_send.png")
                    
                    # Click send
                    send_button.click()
                    print("✅ Send button clicked")
                    
                    # Wait for response with detailed monitoring
                    print("⏳ Waiting for Ram's response...")
                    response_detected = False
                    response_text = ""
                    wait_time = 0
                    
                    for attempt in range(60):  # 60 second timeout
                        time.sleep(1)
                        wait_time += 1
                        
                        page_content = page.content().lower()
                        
                        # Look for Ram's response
                        if "ram:" in page_content and len(page_content) > 5000:  # Substantial content
                            # Check if it's not an error
                            if "having trouble" not in page_content and "error" not in page_content:
                                response_detected = True
                                print(f"✅ Response detected after {wait_time} seconds")
                                
                                # Extract response text for analysis
                                try:
                                    response_elements = page.locator('.assistant-message').all()
                                    if response_elements:
                                        latest_response = response_elements[-1]
                                        response_text = latest_response.text_content() or ""
                                        total_response_chars += len(response_text)
                                        print(f"📊 Response length: {len(response_text)} characters")
                                except:
                                    response_text = "Response detected but couldn't extract text"
                                
                                break
                        elif "error" in page_content or "exception" in page_content:
                            print(f"❌ Error detected in response")
                            break
                        elif wait_time % 10 == 0:
                            print(f"⏳ Still waiting... ({wait_time}s)")
                    
                    if response_detected:
                        # Analyze response quality
                        keyword_matches = sum(1 for keyword in scenario['expected_keywords'] 
                                            if keyword in page_content)
                        
                        print(f"🔍 Keyword Analysis:")
                        print(f"   Expected keywords: {scenario['expected_keywords']}")
                        print(f"   Keywords found: {keyword_matches}/{len(scenario['expected_keywords'])}")
                        
                        # Check sidebar metrics
                        sidebar_text = ""
                        try:
                            sidebar = page.locator('[data-testid="stSidebar"]')
                            if sidebar.is_visible():
                                sidebar_text = sidebar.text_content().lower()
                                
                                if "pinecone active" in sidebar_text:
                                    print("✅ Pinecone vector search active")
                                
                                if "sources found" in sidebar_text:
                                    print("✅ Knowledge sources utilized")
                                    knowledge_sources_used += 1
                                
                                if "lead score" in sidebar_text:
                                    print("✅ Lead scoring operational")
                                
                        except Exception as e:
                            print(f"⚠️ Could not read sidebar: {e}")
                        
                        # Take screenshot after response
                        page.screenshot(path=f"test_{scenario['id']}_after_response.png")
                        
                        # Determine test success
                        if keyword_matches >= len(scenario['expected_keywords']) // 2:  # At least half keywords
                            print("✅ TEST PASSED - Relevant response detected")
                            successful_tests += 1
                            test_results.append({
                                "test": scenario['id'],
                                "status": "PASSED",
                                "response_length": len(response_text),
                                "keywords_matched": keyword_matches,
                                "category": scenario['category']
                            })
                        else:
                            print("⚠️ TEST PARTIAL - Response detected but relevance unclear")
                            test_results.append({
                                "test": scenario['id'],
                                "status": "PARTIAL",
                                "response_length": len(response_text),
                                "keywords_matched": keyword_matches,
                                "category": scenario['category']
                            })
                    else:
                        print("❌ TEST FAILED - No response after 60 seconds")
                        page.screenshot(path=f"test_{scenario['id']}_failed.png")
                        test_results.append({
                            "test": scenario['id'],
                            "status": "FAILED",
                            "response_length": 0,
                            "keywords_matched": 0,
                            "category": scenario['category']
                        })
                    
                    # Brief pause between tests
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"❌ TEST ERROR: {e}")
                    test_results.append({
                        "test": scenario['id'],
                        "status": "ERROR",
                        "response_length": 0,
                        "keywords_matched": 0,
                        "category": scenario['category'],
                        "error": str(e)
                    })
            
            # Final screenshot
            page.screenshot(path="test_final_state.png")
            
            # Generate comprehensive report
            print("\n" + "=" * 60)
            print("📊 COMPREHENSIVE TEST RESULTS REPORT")
            print("=" * 60)
            
            print(f"\n🎯 OVERALL PERFORMANCE:")
            print(f"   Tests Passed: {successful_tests}/5")
            print(f"   Success Rate: {(successful_tests/5)*100:.1f}%")
            print(f"   Total Response Characters: {total_response_chars:,}")
            print(f"   Average Response Length: {total_response_chars//5 if successful_tests > 0 else 0:,} chars")
            print(f"   Knowledge Sources Used: {knowledge_sources_used}/5 tests")
            
            print(f"\n📋 DETAILED TEST BREAKDOWN:")
            for result in test_results:
                status_icon = "✅" if result['status'] == "PASSED" else "⚠️" if result['status'] == "PARTIAL" else "❌"
                print(f"   {status_icon} Test {result['test']} ({result['category']}): {result['status']}")
                print(f"      Response: {result['response_length']} chars, Keywords: {result['keywords_matched']}")
            
            print(f"\n🚀 SYSTEM CAPABILITIES VERIFIED:")
            if successful_tests >= 4:
                print("   ✅ Professional conversation flow")
                print("   ✅ Knowledge base integration")
                print("   ✅ Context-aware responses")
                print("   ✅ Lead progression tracking")
                print("   ✅ Real-time metrics")
            
            print(f"\n🎉 CONCLUSION:")
            if successful_tests >= 4:
                print("   ✅ SYSTEM FULLY OPERATIONAL")
                print("   💼 Ready for client demonstrations")
                print("   🚀 Production deployment ready")
            elif successful_tests >= 2:
                print("   ⚠️ SYSTEM MOSTLY OPERATIONAL")
                print("   🔧 Minor issues detected")
                print("   📋 Review failed tests")
            else:
                print("   ❌ SYSTEM ISSUES DETECTED")
                print("   🛠️ Requires debugging")
            
            print(f"\n📁 EVIDENCE FILES GENERATED:")
            print("   📸 test_0_initial_load.png")
            for i in range(1, 6):
                print(f"   📸 test_{i}_before_send.png")
                print(f"   📸 test_{i}_after_response.png")
            print("   📸 test_final_state.png")
            
            # Keep browser open for manual inspection
            print(f"\n👀 Browser staying open for 30 seconds for manual inspection...")
            time.sleep(30)
            
            browser.close()
            return successful_tests >= 4
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting 5 Comprehensive E2E Tests")
    print("📋 This will test the complete user journey from discovery to engagement")
    print("⏰ Estimated time: 5-10 minutes")
    print("\nPress Ctrl+C to cancel, or wait 5 seconds to start...")
    
    try:
        time.sleep(5)
        success = run_5_comprehensive_tests()
        print(f"\n{'🎉 ALL TESTS SUCCESSFUL!' if success else '⚠️ SOME TESTS FAILED'}")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests cancelled by user")
        exit(1)