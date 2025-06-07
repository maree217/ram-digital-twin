#!/usr/bin/env python3
"""
Pinecone setup script for Ram Digital Twin project
Creates index and uploads knowledge base documents
"""
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict
import asyncio

# Add src to path
sys.path.append('src')

from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_pinecone_index():
    """Set up Pinecone index and upload knowledge documents"""
    
    try:
        from pinecone import Pinecone, ServerlessSpec
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        logger.info("🚀 Setting up Pinecone vector database...")
        
        # Initialize Pinecone
        if not settings.pinecone_api_key:
            logger.error("❌ PINECONE_API_KEY not found in environment")
            return False
        
        pc = Pinecone(api_key=settings.pinecone_api_key)
        
        # Get available indexes
        indexes = pc.list_indexes()
        index_name = settings.pinecone_index_name
        
        logger.info(f"📋 Existing indexes: {[idx.name for idx in indexes]}")
        
        # Check if index exists
        index_exists = any(idx.name == index_name for idx in indexes)
        
        if not index_exists:
            logger.info(f"🔨 Creating new index: {index_name}")
            
            # Create index with serverless spec (free tier)
            pc.create_index(
                name=index_name,
                dimension=384,  # all-MiniLM-L6-v2 embedding dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'  # Free tier region
                )
            )
            
            logger.info(f"✅ Index '{index_name}' created successfully")
        else:
            logger.info(f"✅ Index '{index_name}' already exists")
        
        # Connect to index
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        logger.info(f"📊 Index stats: {stats}")
        
        # Initialize embedding model
        logger.info("🤖 Loading embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load and process knowledge documents
        knowledge_dir = Path("knowledge_base")
        if not knowledge_dir.exists():
            logger.error(f"❌ Knowledge base directory not found: {knowledge_dir}")
            return False
        
        # Process each document
        documents = []
        for txt_file in knowledge_dir.glob("*.txt"):
            logger.info(f"📄 Processing: {txt_file.name}")
            
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into chunks for better retrieval
            chunks = split_into_chunks(content, max_length=1000, overlap=200)
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{txt_file.stem}_chunk_{i}"
                documents.append({
                    'id': doc_id,
                    'text': chunk,
                    'source': txt_file.stem,
                    'chunk_index': i
                })
        
        logger.info(f"📚 Prepared {len(documents)} document chunks")
        
        # Generate embeddings and upload to Pinecone
        if documents:
            logger.info("🔄 Generating embeddings and uploading to Pinecone...")
            
            # Process in batches to avoid memory issues
            batch_size = 50
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(documents))
                batch_docs = documents[start_idx:end_idx]
                
                logger.info(f"📦 Processing batch {batch_idx + 1}/{total_batches}")
                
                # Generate embeddings for batch
                texts = [doc['text'] for doc in batch_docs]
                embeddings = model.encode(texts, convert_to_tensor=False)
                
                # Prepare vectors for Pinecone
                vectors = []
                for doc, embedding in zip(batch_docs, embeddings):
                    vectors.append({
                        'id': doc['id'],
                        'values': embedding.tolist(),
                        'metadata': {
                            'text': doc['text'][:1000],  # Truncate for metadata limits
                            'source': doc['source'],
                            'chunk_index': doc['chunk_index']
                        }
                    })
                
                # Upload to Pinecone
                index.upsert(vectors)
                logger.info(f"✅ Uploaded batch {batch_idx + 1}/{total_batches}")
        
        # Final index stats
        final_stats = index.describe_index_stats()
        logger.info(f"🎯 Final index stats: {final_stats}")
        
        # Test search functionality
        logger.info("🔍 Testing search functionality...")
        test_query = "PMO setup experience"
        test_embedding = model.encode([test_query])
        
        search_results = index.query(
            vector=test_embedding[0].tolist(),
            top_k=3,
            include_metadata=True
        )
        
        logger.info(f"🔎 Test search results for '{test_query}':")
        for i, match in enumerate(search_results.matches, 1):
            logger.info(f"  {i}. Score: {match.score:.3f} | Source: {match.metadata.get('source', 'unknown')}")
            logger.info(f"     Text: {match.metadata.get('text', '')[:100]}...")
        
        logger.info("🎉 Pinecone setup completed successfully!")
        
        # Update .env with correct environment
        update_env_file()
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("Run: pip install pinecone-client sentence-transformers")
        return False
    except Exception as e:
        logger.error(f"❌ Error setting up Pinecone: {e}")
        return False

def split_into_chunks(text: str, max_length: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for better retrieval"""
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed max_length, save current chunk
        if len(current_chunk) + len(paragraph) > max_length and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + "\n\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def update_env_file():
    """Update .env file with correct Pinecone environment"""
    env_file = Path(".env")
    
    if env_file.exists():
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update Pinecone environment to us-east-1 (serverless)
        content = content.replace(
            "PINECONE_ENVIRONMENT=your_pinecone_environment",
            "PINECONE_ENVIRONMENT=us-east-1"
        )
        
        # Write back
        with open(env_file, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated .env file with Pinecone environment")

if __name__ == "__main__":
    success = setup_pinecone_index()
    sys.exit(0 if success else 1)