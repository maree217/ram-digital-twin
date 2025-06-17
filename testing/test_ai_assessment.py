#!/usr/bin/env python3
"""
Quick test to verify AI readiness assessment functionality
"""
import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

async def test_ai_assessment_flow():
    """Test the AI readiness assessment flow"""
    
    print("🧪 Testing AI Readiness Assessment Flow")
    print("=" * 50)
    
    agent = ConsultancyAgent()
    context = ConversationContext(conversation_id="test_ai_assessment")
    
    # Test 1: AI interest detection
    print("\n📍 Test 1: AI Interest Detection")
    user_message_1 = "We're thinking about implementing AI in our organization"
    response_1 = await agent.handle_interaction(user_message_1, context)
    
    print(f"User: {user_message_1}")
    print(f"Agent: {response_1['content'][:200]}...")
    print(f"Stage: {response_1['stage']}")
    print(f"Lead Score: {response_1['lead_score']}")
    
    # Add message to context
    context.messages.append({
        "role": "user", 
        "content": user_message_1,
        "stage": response_1['stage']
    })
    
    # Test 2: Assessment acceptance
    print("\n📍 Test 2: Assessment Acceptance")
    user_message_2 = "Yes, I'd like to go through the assessment"
    response_2 = await agent.handle_interaction(user_message_2, context)
    
    print(f"User: {user_message_2}")
    print(f"Agent: {response_2['content'][:200]}...")
    print(f"Stage: {response_2['stage']}")
    print(f"Lead Score: {response_2['lead_score']}")
    
    # Add message to context
    context.messages.append({
        "role": "user", 
        "content": user_message_2,
        "stage": response_2['stage']
    })
    
    # Test 3: Challenge identification
    print("\n📍 Test 3: Challenge Response")
    user_message_3 = "Our main challenge is budget constraints and unclear ROI"
    response_3 = await agent.handle_interaction(user_message_3, context)
    
    print(f"User: {user_message_3}")
    print(f"Agent: {response_3['content'][:300]}...")
    print(f"Stage: {response_3['stage']}")
    print(f"Lead Score: {response_3['lead_score']}")
    
    # Test 4: Check philosophy integration
    print("\n📍 Test 4: Philosophy Integration Check")
    if "Democratic Technology Building" in response_3['content'] or "everyone is a technology builder" in response_3['content'].lower():
        print("✅ Philosophy successfully integrated!")
    else:
        print("❌ Philosophy not detected in response")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"   Final Lead Score: {response_3['lead_score']}")
    print(f"   Final Stage: {response_3['stage']}")
    print(f"   Assessment Flow: {'✅ Working' if response_3['stage'] == 'ai_readiness_assessment' else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_ai_assessment_flow())