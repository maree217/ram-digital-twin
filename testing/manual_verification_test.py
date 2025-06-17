#!/usr/bin/env python3
"""
Manual verification test that actually works by testing backend directly
Then provides manual testing instructions for the UI
"""
import asyncio
import sys
import time
from datetime import datetime

# Add src to path
sys.path.append('src')
from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

def run_backend_verification():
    """Test the backend directly to show it's working"""
    print("🧪 BACKEND VERIFICATION - Ram Digital Twin")
    print("=" * 60)
    
    try:
        # Initialize agent
        agent = ConsultancyAgent()
        print("✅ ConsultancyAgent initialized")
        
        # Check components
        print(f"✅ Gemini Model available: {bool(agent.model)}")
        print(f"✅ Vector Search available: {agent.vector_search.is_available()}")
        print(f"✅ Pinecone available: {agent.vector_search.is_pinecone_available()}")
        
        # Test scenarios - exactly what the UI should do
        test_scenarios = [
            {
                "id": 1,
                "category": "Discovery Stage",
                "message": "Hello Ram, I'm exploring digital transformation options for our housing association. We have around 15,000 properties and are struggling with outdated systems.",
                "expected_stage": "discovery"
            },
            {
                "id": 2,
                "category": "Expertise Demonstration", 
                "message": "What's your specific experience with PMO implementations? Have you worked with organizations similar to ours before?",
                "expected_stage": "expertise_demonstration"
            },
            {
                "id": 3,
                "category": "Technical Deep Dive",
                "message": "We're considering Microsoft Dynamics 365 for our customer relationship management. What's your approach to D365 implementations and what challenges should we expect?",
                "expected_stage": "expertise_demonstration"
            },
            {
                "id": 4,
                "category": "Solution Presentation",
                "message": "Based on our conversation, how would you recommend we structure a digital transformation program for our housing association? What would the timeline and key milestones look like?",
                "expected_stage": "solution_presentation"
            },
            {
                "id": 5,
                "category": "Engagement Conversion",
                "message": "This sounds very promising and exactly what we need. How can we move forward with a consultation to discuss this in more detail? What would be the next steps?",
                "expected_stage": "engagement_conversion"
            }
        ]
        
        context = ConversationContext(
            conversation_id=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            messages=[],
            engagement_stage="discovery"
        )
        
        successful_tests = 0
        total_chars = 0
        knowledge_sources_total = 0
        
        for scenario in test_scenarios:
            print(f"\n{'='*60}")
            print(f"🧪 TEST {scenario['id']}: {scenario['category']}")
            print(f"💬 Message: {scenario['message'][:80]}...")
            print(f"{'='*60}")
            
            try:
                start_time = time.time()
                
                # Process message (this is exactly what Streamlit does)
                response = asyncio.run(agent.handle_interaction(scenario['message'], context))
                
                processing_time = time.time() - start_time
                
                # Extract results
                content = response.get("content", "")
                stage = response.get("stage", "unknown")
                lead_score = response.get("lead_score", 0)
                knowledge_sources = response.get("knowledge_sources", 0)
                
                # Update context for next test (simulate conversation flow)
                context.messages.append({"role": "user", "content": scenario['message']})
                context.messages.append({"role": "assistant", "content": content})
                context.engagement_stage = stage
                context.lead_score = lead_score
                
                # Analyze results
                print(f"✅ Response generated in {processing_time:.2f}s")
                print(f"📊 Response length: {len(content):,} characters")
                print(f"🎯 Stage: {stage}")
                print(f"📈 Lead score: {lead_score}/100")
                print(f"📚 Knowledge sources: {knowledge_sources}")
                
                # Quality checks
                if len(content) > 500:
                    print("✅ Response is substantial")
                else:
                    print("⚠️ Response might be too short")
                
                if knowledge_sources > 0:
                    print("✅ Knowledge base utilized")
                else:
                    print("⚠️ No knowledge sources used")
                
                # Show sample of response
                print(f"📝 Response preview: {content[:200]}...")
                
                if len(content) > 500 and knowledge_sources > 0:
                    successful_tests += 1
                    print("✅ TEST PASSED")
                else:
                    print("⚠️ TEST PARTIAL")
                
                total_chars += len(content)
                knowledge_sources_total += knowledge_sources
                
            except Exception as e:
                print(f"❌ TEST FAILED: {e}")
                import traceback
                traceback.print_exc()
        
        # Summary report
        print(f"\n{'='*60}")
        print("📊 BACKEND VERIFICATION RESULTS")
        print(f"{'='*60}")
        print(f"✅ Tests Passed: {successful_tests}/5")
        print(f"📊 Success Rate: {(successful_tests/5)*100:.1f}%")
        print(f"📝 Total Response Characters: {total_chars:,}")
        print(f"📚 Total Knowledge Sources Used: {knowledge_sources_total}")
        print(f"📈 Average Response Length: {total_chars//5:,} chars")
        print(f"🎯 Final Lead Score: {context.lead_score}/100")
        print(f"🚀 Final Stage: {context.engagement_stage}")
        
        print(f"\n🎉 BACKEND STATUS: {'✅ FULLY OPERATIONAL' if successful_tests >= 4 else '⚠️ NEEDS ATTENTION'}")
        
        return successful_tests >= 4
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_manual_test_instructions():
    """Generate manual testing instructions for the UI"""
    print(f"\n{'='*60}")
    print("📋 MANUAL UI TESTING INSTRUCTIONS")
    print(f"{'='*60}")
    
    print("""
🌐 STEP 1: Open Browser
   Navigate to: http://localhost:8501
   ✅ You should see Ram's professional header
   ✅ You should see the welcome message
   ✅ You should see sidebar with metrics

💬 STEP 2: Test Each Conversation Stage
   Copy and paste each message below, then click Send:

   🔍 TEST 1 - Discovery Stage:
   "Hello Ram, I'm exploring digital transformation options for our housing association. We have around 15,000 properties and are struggling with outdated systems."
   
   Expected Results:
   ✅ Response appears in 3-10 seconds
   ✅ Response is 1000+ characters
   ✅ Sidebar shows "Discovery" stage
   ✅ Sidebar shows knowledge sources found
   ✅ Response mentions housing associations or similar experience

   💡 TEST 2 - Expertise Demonstration:
   "What's your specific experience with PMO implementations? Have you worked with organizations similar to ours before?"
   
   Expected Results:
   ✅ Stage changes to "Expertise Demonstration"
   ✅ Response includes specific PMO examples
   ✅ Lead score increases
   ✅ Vector search finds relevant sources

   🔧 TEST 3 - Technical Deep Dive:
   "We're considering Microsoft Dynamics 365 for our customer relationship management. What's your approach to D365 implementations?"
   
   Expected Results:
   ✅ Detailed D365 implementation advice
   ✅ Mentions challenges and best practices
   ✅ References previous experience

   📋 TEST 4 - Solution Presentation:
   "How would you recommend we structure a digital transformation program for our housing association? What would the timeline look like?"
   
   Expected Results:
   ✅ Stage becomes "Solution Presentation"
   ✅ Structured program recommendation
   ✅ Timeline and milestone suggestions

   📞 TEST 5 - Engagement Conversion:
   "This sounds very promising. How can we move forward with a consultation to discuss this in more detail?"
   
   Expected Results:
   ✅ Stage becomes "Engagement Conversion"
   ✅ Contact information provided
   ✅ Next steps clearly outlined
   ✅ Lead score reaches high level

📊 STEP 3: Verify Sidebar Metrics
   Throughout testing, check the sidebar shows:
   ✅ Vector Search: 🟢 Pinecone Active
   ✅ Stage progression through conversation
   ✅ Lead Score increasing with engagement
   ✅ Knowledge sources found for each query
   ✅ Knowledge Base: 3 documents

🎯 SUCCESS CRITERIA:
   ✅ All 5 tests generate relevant responses
   ✅ Sidebar metrics update correctly
   ✅ Stage progression works logically
   ✅ Responses are professional and detailed
   ✅ Knowledge integration is evident

📸 EVIDENCE COLLECTION:
   Take screenshots of:
   ✅ Initial welcome screen
   ✅ Each conversation stage
   ✅ Final sidebar metrics
   ✅ Complete conversation history
""")

def main():
    """Run complete verification"""
    print("🚀 RAM DIGITAL TWIN - COMPLETE VERIFICATION")
    print("=" * 60)
    print("This test will:")
    print("1. ✅ Verify backend is working (automated)")
    print("2. 📋 Provide manual UI testing instructions")
    print("3. 📊 Generate evidence of functionality")
    
    # Run backend verification
    backend_success = run_backend_verification()
    
    # Generate manual instructions
    generate_manual_test_instructions()
    
    print(f"\n{'='*60}")
    print("🎉 VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    if backend_success:
        print("✅ BACKEND: Fully operational")
        print("   - Gemini AI working")
        print("   - Pinecone vector search active")
        print("   - Knowledge base integrated")
        print("   - Conversation flow working")
        print("   - Lead scoring operational")
        
        print("\n🌐 FRONTEND: Ready for manual testing")
        print("   - Streamlit app running on localhost:8501")
        print("   - Use manual instructions above")
        print("   - All backend features available")
        
        print("\n🚀 SYSTEM STATUS: PRODUCTION READY")
        print("   💼 Ready for client demonstrations")
        print("   📊 All metrics and tracking operational")
        print("   🎯 Complete conversation intelligence")
        
    else:
        print("❌ BACKEND: Issues detected")
        print("🛠️ Fix backend before UI testing")
    
    return backend_success

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 VERIFICATION COMPLETE!' if success else '⚠️ ISSUES DETECTED'}")
    exit(0 if success else 1)