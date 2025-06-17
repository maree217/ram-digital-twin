#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.knowledge.knowledge_search import SimpleKnowledgeSearch

def test_knowledge_base():
    print("🚀 Testing Knowledge Base...")
    
    knowledge_search = SimpleKnowledgeSearch()
    documents = knowledge_search.get_document_list()
    
    print(f"📚 Loaded {len(documents)} documents:")
    for doc in documents:
        print(f"   - {doc}")
    
    # Test search
    query = "PMO setup experience"
    results = knowledge_search.search(query, max_results=2)
    print(f"\n🔍 Search results for '{query}':")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['document']} (score: {result['score']:.1f})")
    
    print("✅ Knowledge base test completed!")

if __name__ == "__main__":
    test_knowledge_base()