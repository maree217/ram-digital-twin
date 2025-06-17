#!/usr/bin/env python3
"""
Debug the Streamlit app error and test functionality
"""
import asyncio
import sys
import os
sys.path.append('src')

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

async def test_agent_directly():
    """Test the agent directly to see if the error is in the agent or Streamlit"""
    print("🔍 Testing ConsultancyAgent directly...")
    
    try:
        # Initialize agent
        agent = ConsultancyAgent()
        print(f"✅ Agent initialized: {agent.name}")
        print(f"   Model available: {'Yes' if agent.model else 'No'}")
        print(f"   Vector search available: {'Yes' if agent.vector_search.is_available() else 'No'}")
        
        # Create context
        context = ConversationContext()
        
        # Test interaction
        user_message = "Tell me about PMO setup"
        print(f"\n💬 Testing message: '{user_message}'")
        
        response = await agent.handle_interaction(user_message, context)
        
        print(f"✅ Response received:")
        print(f"   Content length: {len(response.get('content', ''))}")
        print(f"   Stage: {response.get('stage', 'unknown')}")
        print(f"   Lead score: {response.get('lead_score', 0)}")
        print(f"   Knowledge sources: {response.get('knowledge_sources', 0)}")
        print(f"   Vector search used: {response.get('vector_search_available', False)}")
        
        # Print first 200 chars of response
        content = response.get('content', '')
        if content:
            print(f"\n📝 Response preview:")
            print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
        else:
            print(f"\n❌ Empty response content!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_search_directly():
    """Test vector search directly"""
    print("\n🔍 Testing Vector Search directly...")
    
    try:
        from src.knowledge.vector_search import VectorKnowledgeSearch
        
        vector_search = VectorKnowledgeSearch()
        print(f"✅ Vector search initialized")
        print(f"   Model available: {'Yes' if vector_search.is_available() else 'No'}")
        print(f"   Pinecone available: {'Yes' if vector_search.is_pinecone_available() else 'No'}")
        
        if vector_search.is_available():
            results = await vector_search.search("PMO setup", max_results=2)
            print(f"   Search results: {len(results)} found")
            for i, result in enumerate(results, 1):
                print(f"     {i}. {result['document']} (score: {result['score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector search: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\n🔧 Testing Configuration...")
    
    try:
        from src.config import settings
        
        print(f"✅ Configuration loaded")
        print(f"   Google API Key: {'Set' if settings.google_api_key else 'Missing'}")
        print(f"   Pinecone API Key: {'Set' if settings.pinecone_api_key else 'Missing'}")
        print(f"   Pinecone Index: {settings.pinecone_index_name}")
        
        # Test Gemini configuration
        if settings.google_api_key:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            print(f"   Gemini model: ✅ Configured")
        else:
            print(f"   Gemini model: ❌ API key missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_gemini_call():
    """Test a simple Gemini API call"""
    print("\n🤖 Testing Gemini API directly...")
    
    try:
        from src.config import settings
        import google.generativeai as genai
        
        if not settings.google_api_key:
            print("❌ No API key available")
            return False
        
        genai.configure(api_key=settings.google_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Simple test
        response = await asyncio.to_thread(
            model.generate_content,
            "Say hello world",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=100,
                top_p=0.8,
            )
        )
        
        print(f"✅ Gemini response: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all diagnostic tests"""
    print("🚀 Ram Digital Twin - Error Diagnosis")
    print("=" * 50)
    
    # Test each component
    tests = [
        ("Configuration", test_config),
        ("Gemini API", test_simple_gemini_call),
        ("Vector Search", test_vector_search_directly),
        ("Agent Logic", test_agent_directly),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n🎯 Diagnostic Summary:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🚀 Overall Status: {'✅ READY' if all_passed else '❌ NEEDS ATTENTION'}")
    
    if not all_passed:
        print(f"\n💡 Likely issue: The error you're seeing is probably due to:")
        if not results.get("Configuration"):
            print("   - Missing or incorrect API keys in .env file")
        if not results.get("Gemini API"):
            print("   - Gemini API key invalid or quota exceeded")
        if not results.get("Vector Search"):
            print("   - Pinecone connection issues")
        if not results.get("Agent Logic"):
            print("   - Agent initialization or processing error")

if __name__ == "__main__":
    asyncio.run(main())