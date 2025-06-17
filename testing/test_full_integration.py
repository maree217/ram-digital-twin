#!/usr/bin/env python3
"""
Test the complete integration with Pinecone, Gemini, and enhanced agent
"""
import asyncio
import sys
import os
sys.path.append('src')

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext
from src.knowledge.vector_search import VectorKnowledgeSearch
from src.config import settings

async def test_full_integration():
    """Test the complete system integration"""
    print("🚀 Testing Full System Integration")
    print("=" * 50)
    
    # Test configuration
    print("🔧 Configuration Check:")
    print(f"   Google API Key: {'✅ Set' if settings.google_api_key else '❌ Missing'}")
    print(f"   Pinecone API Key: {'✅ Set' if settings.pinecone_api_key else '❌ Missing'}")
    print(f"   Pinecone Index: {settings.pinecone_index_name}")
    print()
    
    # Test vector search
    print("🔍 Testing Vector Search:")
    vector_search = VectorKnowledgeSearch()
    print(f"   Model Available: {'✅ Yes' if vector_search.is_available() else '❌ No'}")
    print(f"   Pinecone Available: {'✅ Yes' if vector_search.is_pinecone_available() else '❌ No'}")
    
    if vector_search.is_available():
        # Test search
        search_results = await vector_search.search("PMO setup experience", max_results=2)
        print(f"   Search Results: {len(search_results)} found")
        for i, result in enumerate(search_results, 1):
            print(f"     {i}. {result['document']} (score: {result['score']:.3f})")
    
    # Get vector database stats
    stats = await vector_search.get_stats()
    if stats.get("available"):
        print(f"   Vector Count: {stats.get('total_vectors', 0)}")
        print(f"   Dimension: {stats.get('dimension', 0)}")
    print()
    
    # Test consultancy agent
    print("🤖 Testing Consultancy Agent:")
    agent = ConsultancyAgent()
    print(f"   Agent Initialized: {'✅ Yes' if agent else '❌ No'}")
    print(f"   Gemini Model: {'✅ Available' if agent.model else '❌ Not configured'}")
    print(f"   Vector Search: {'✅ Available' if agent.vector_search.is_available() else '❌ Not available'}")
    print()
    
    # Test conversation scenarios
    test_scenarios = [
        {
            "message": "What's your experience with PMO implementations?",
            "expected_stage": "expertise_demonstration"
        },
        {
            "message": "How would you recommend setting up a PMO for a housing association?",
            "expected_stage": "solution_presentation"
        },
        {
            "message": "Can we schedule a consultation to discuss our needs?",
            "expected_stage": "engagement_conversion"
        }
    ]
    
    print("💬 Testing Conversation Scenarios:")
    context = ConversationContext()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['message'][:50]}...")
        
        try:
            response = await agent.handle_interaction(scenario['message'], context)
            
            print(f"     Stage: {response.get('stage', 'unknown')}")
            print(f"     Lead Score: {response.get('lead_score', 0)}")
            print(f"     Knowledge Sources: {response.get('knowledge_sources', 0)}")
            print(f"     Vector Search Used: {'✅' if response.get('vector_search_available') else '❌'}")
            
            # Check if response is reasonable
            content = response.get('content', '')
            if len(content) > 50:
                print(f"     Response Length: {len(content)} chars ✅")
            else:
                print(f"     Response Length: {len(content)} chars ⚠️ (too short)")
            
            # Update context for next scenario
            context.messages.append({"role": "user", "content": scenario['message']})
            context.messages.append({"role": "assistant", "content": content})
            context.engagement_stage = response.get('stage', context.engagement_stage)
            context.lead_score = response.get('lead_score', context.lead_score)
            
        except Exception as e:
            print(f"     ❌ Error: {str(e)}")
    
    print("\n🎯 Integration Test Summary:")
    print("   Core Components:")
    print(f"     - Configuration: {'✅' if settings.google_api_key else '❌'}")
    print(f"     - Vector Search: {'✅' if vector_search.is_available() else '❌'}")
    print(f"     - Pinecone DB: {'✅' if vector_search.is_pinecone_available() else '❌'}")
    print(f"     - Gemini AI: {'✅' if agent.model else '❌'}")
    print(f"     - Agent Logic: {'✅' if agent else '❌'}")
    
    # Overall readiness assessment
    all_ready = (
        settings.google_api_key and
        vector_search.is_available() and
        agent.model and
        vector_search.is_pinecone_available()
    )
    
    print(f"\n🚀 System Status: {'✅ READY FOR FULL TESTING' if all_ready else '⚠️ NEEDS CONFIGURATION'}")
    
    if not all_ready:
        print("\n📋 Missing Components:")
        if not settings.google_api_key:
            print("   - Add GOOGLE_API_KEY to .env file")
        if not vector_search.is_pinecone_available():
            print("   - Check Pinecone configuration and connection")
        if not agent.model:
            print("   - Verify Gemini API key and model access")
    
    return all_ready

if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    sys.exit(0 if success else 1)