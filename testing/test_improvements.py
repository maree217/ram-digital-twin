"""
Quick test script to verify the improvements work
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

async def test_improvements():
    """Test the key improvements"""
    agent = ConsultancyAgent()
    
    # Test scenarios to verify improvements
    test_cases = [
        {
            "name": "Lead Scoring Test",
            "messages": ["I need help with Dynamics 365 implementation", "Our budget is approved", "Can we schedule a call?"],
            "expected_lead_increase": True
        },
        {
            "name": "Stage Detection Test", 
            "messages": ["Hello", "I'm bored with life", "What's your experience with PMO setup?"],
            "expected_stages": ["greeting", "casual_chat", "expertise_demonstration"]
        },
        {
            "name": "Empathy Test",
            "messages": ["Hi", "My boss hates me", "I'm feeling stressed"],
            "expected_empathy": True
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print("-" * 40)
        
        context = ConversationContext()
        stages = []
        lead_scores = []
        responses = []
        
        for i, message in enumerate(test_case['messages']):
            try:
                response = await agent.handle_interaction(message, context)
                
                print(f"Turn {i+1}:")
                print(f"  User: {message}")
                print(f"  Agent: {response['content'][:100]}...")
                print(f"  Stage: {response['stage']}")
                print(f"  Lead Score: {response['lead_score']}")
                
                stages.append(response['stage'])
                lead_scores.append(response['lead_score'])
                responses.append(response['content'])
                
                # Update context
                context.messages.append({"role": "user", "content": message})
                context.messages.append({"role": "assistant", "content": response['content']})
                context.engagement_stage = response['stage']
                context.lead_score = response['lead_score']
                
            except Exception as e:
                print(f"  ERROR: {e}")
        
        # Check results
        if test_case['name'] == "Lead Scoring Test":
            final_score = lead_scores[-1] if lead_scores else 0
            print(f"✅ Lead score progression: 0 -> {final_score}" if final_score > 0 else "❌ Lead scoring not working")
        
        elif test_case['name'] == "Stage Detection Test":
            expected = test_case['expected_stages']
            actual = stages[:len(expected)]
            matches = sum(1 for e, a in zip(expected, actual) if e == a)
            accuracy = (matches / len(expected)) * 100
            print(f"✅ Stage accuracy: {accuracy:.1f}%" if accuracy >= 70 else f"❌ Stage accuracy: {accuracy:.1f}%")
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual}")
        
        elif test_case['name'] == "Empathy Test":
            # Check if responses contain empathetic language
            empathy_phrases = ['sounds', 'understand', 'challenging', 'difficult', 'frustrating']
            has_empathy = any(phrase in ' '.join(responses).lower() for phrase in empathy_phrases)
            print(f"✅ Empathy detected" if has_empathy else "❌ No empathy detected")

if __name__ == "__main__":
    asyncio.run(test_improvements())