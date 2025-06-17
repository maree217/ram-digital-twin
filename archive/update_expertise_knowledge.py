#!/usr/bin/env python3
"""
Update the knowledge base with impressive expertise examples
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append('src')
from src.knowledge.vector_search import VectorKnowledgeSearch

async def update_expertise_knowledge():
    """Add impressive expertise examples to vector database"""
    print("🚀 Updating Knowledge Base with WOW Expertise Examples")
    print("=" * 60)
    
    vector_search = VectorKnowledgeSearch()
    
    if not vector_search.is_pinecone_available():
        print("❌ Pinecone not available - cannot update knowledge base")
        return False
    
    # Read the new expertise file
    expertise_file = Path("knowledge_base/wow_expertise_examples.md")
    if not expertise_file.exists():
        print(f"❌ Expertise file not found: {expertise_file}")
        return False
    
    with open(expertise_file, 'r') as f:
        content = f.read()
    
    print(f"📖 Loaded expertise content: {len(content):,} characters")
    
    # Split into logical chunks
    sections = content.split('## ')
    chunks = []
    
    for i, section in enumerate(sections):
        if section.strip():
            if i == 0:
                # First section includes title
                chunk_content = section.strip()
            else:
                # Add back the ## prefix
                chunk_content = "## " + section.strip()
            
            if len(chunk_content) > 100:  # Only add substantial chunks
                chunks.append({
                    'text': chunk_content,
                    'source': 'wow_expertise_examples',
                    'chunk_id': f"expertise_chunk_{i}"
                })
    
    print(f"📊 Created {len(chunks)} expertise chunks")
    
    # Index each chunk
    successful_uploads = 0
    
    for chunk in chunks:
        try:
            # Create embeddings
            embedding = vector_search.model.encode([chunk['text']])[0].tolist()
            
            # Upload to Pinecone
            vector_search.index.upsert(
                vectors=[{
                    'id': chunk['chunk_id'],
                    'values': embedding,
                    'metadata': {
                        'text': chunk['text'][:1000] + "...",  # Truncate for metadata
                        'source': chunk['source'],
                        'full_text': chunk['text']
                    }
                }]
            )
            
            successful_uploads += 1
            print(f"✅ Uploaded expertise chunk {successful_uploads}: {chunk['chunk_id']}")
            
        except Exception as e:
            print(f"❌ Failed to upload chunk {chunk['chunk_id']}: {e}")
    
    print(f"\n📊 Update Summary:")
    print(f"   Total chunks processed: {len(chunks)}")
    print(f"   Successfully uploaded: {successful_uploads}")
    print(f"   Upload success rate: {(successful_uploads/len(chunks))*100:.1f}%")
    
    if successful_uploads > 0:
        print(f"\n🎉 Knowledge base updated with impressive expertise examples!")
        print(f"   The chatbot now has access to specific, wow-factor case studies")
        print(f"   Including £50M+ transformations and measurable results")
        return True
    else:
        print(f"\n❌ Failed to update knowledge base")
        return False

async def test_new_knowledge():
    """Test that the new knowledge is accessible"""
    print(f"\n🧪 Testing New Knowledge Access")
    print("=" * 40)
    
    vector_search = VectorKnowledgeSearch()
    
    test_queries = [
        "£50M transformation housing association",
        "PMO implementation results",
        "Dynamics 365 case studies",
        "change management 85% adoption"
    ]
    
    for query in test_queries:
        try:
            results = await vector_search.search(query, max_results=2)
            
            if results:
                print(f"✅ Query: '{query}'")
                print(f"   Found {len(results)} relevant results")
                for result in results:
                    if 'wow_expertise' in result.get('document', ''):
                        print(f"   🎯 Found new expertise content!")
                        break
            else:
                print(f"❌ Query: '{query}' - No results found")
                
        except Exception as e:
            print(f"❌ Query failed: '{query}' - {e}")
    
    print(f"\n✅ Knowledge access test completed")

async def main():
    """Update expertise knowledge and test"""
    success = await update_expertise_knowledge()
    
    if success:
        await test_new_knowledge()
        print(f"\n🚀 Expertise knowledge update COMPLETE!")
        print(f"   The chatbot now has access to impressive case studies")
        print(f"   Ready to wow clients with specific examples and results")
    else:
        print(f"\n❌ Knowledge update FAILED - check Pinecone connection")

if __name__ == "__main__":
    asyncio.run(main())