#!/usr/bin/env python3

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext
from src.knowledge.knowledge_search import SimpleKnowledgeSearch

async def test_basic_conversation():
    """Test basic conversation flow without API keys"""
    print("🚀 Testing Ram Digital Twin - Basic Conversation Flow")
    print("=" * 60)
    
    # Initialize components
    agent = ConsultancyAgent()
    knowledge_search = SimpleKnowledgeSearch()
    
    # Test knowledge base loading
    documents = knowledge_search.get_document_list()
    print(f"📚 Knowledge Base: {len(documents)} documents loaded")
    for doc in documents:
        print(f"   - {doc}")
    print()
    
    # Test knowledge search
    test_queries = [
        "PMO setup experience",
        "Dynamics 365 implementation", 
        "housing association transformation",
        "change management approach"
    ]
    
    print("🔍 Testing Knowledge Search:")
    for query in test_queries:
        results = knowledge_search.search(query, max_results=2)
        print(f"Query: '{query}'")
        print(f"Results: {len(results)} documents found")
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['document']} (score: {result['score']:.1f})")
                if result['chunks']:
                    chunk = result['chunks'][0][:100] + "..." if len(result['chunks'][0]) > 100 else result['chunks'][0]
                    print(f"      Preview: {chunk}")
        print()
    
    # Test conversation context and flow
    print("💬 Testing Conversation Flow:")
    context = ConversationContext()
    
    # Test different conversation stages
    test_scenarios = [
        {
            "message": "Hello, I'm interested in setting up a PMO for our organization",
            "expected_stage": "rapport_building"
        },
        {
            "message": "What's your experience with housing association transformations?",
            "expected_stage": "expertise_demonstration"
        },
        {
            "message": "How would you recommend we approach our digital transformation?",
            "expected_stage": "solution_presentation"
        },
        {
            "message": "Can we schedule a meeting to discuss this further?",
            "expected_stage": "engagement_conversion"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Scenario {i}: {scenario['message']}")
        
        # Test stage determination
        stage = agent._determine_engagement_stage(scenario['message'], context)
        print(f"   Detected stage: {stage}")
        print(f"   Expected stage: {scenario['expected_stage']}")
        print(f"   ✅ Match" if stage == scenario['expected_stage'] else "❌ Mismatch")
        
        # Update context for next scenario
        context.messages.append({"role": "user", "content": scenario['message']})
        context.engagement_stage = stage
        
        # Test lead scoring
        agent._update_lead_score(context, scenario['message'], {"content": "test response"})
        print(f"   Lead score: {context.lead_score}")
        print()
    
    # Test API availability (without making actual calls)
    print("🔌 API Configuration Check:")
    if agent.model:
        print("   ✅ Gemini API: Configured")
    else:
        print("   ❌ Gemini API: Not configured (set GOOGLE_API_KEY in .env)")
    print()
    
    print("✨ Basic testing completed!")
    print("\n🚀 To run the full application:")
    print("   1. Set up your .env file with API keys")
    print("   2. Run: streamlit run streamlit_app.py")
    print("   3. Open http://localhost:8501 in your browser")

def test_knowledge_base_content():
    """Test the quality and coverage of knowledge base content"""
    print("\n📋 Knowledge Base Content Analysis:")
    print("=" * 50)
    
    knowledge_search = SimpleKnowledgeSearch()
    documents = knowledge_search.get_document_list()
    
    for doc_name in documents:
        content = knowledge_search.get_document_content(doc_name)
        word_count = len(content.split())
        char_count = len(content)
        
        print(f"\n📄 {doc_name}:")
        print(f"   Words: {word_count:,}")
        print(f"   Characters: {char_count:,}")
        
        # Check for key topics
        key_topics = [
            'PMO', 'Dynamics', 'transformation', 'change management',
            'housing', 'implementation', 'ROI', 'methodology'
        ]
        
        found_topics = []
        for topic in key_topics:
            if topic.lower() in content.lower():
                found_topics.append(topic)
        
        print(f"   Key topics covered: {', '.join(found_topics)}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_basic_conversation())
    test_knowledge_base_content()