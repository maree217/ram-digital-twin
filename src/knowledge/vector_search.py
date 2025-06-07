import logging
import asyncio
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from src.config import settings

logger = logging.getLogger(__name__)

class VectorKnowledgeSearch:
    """Enhanced knowledge search using Pinecone vector database"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the embedding model and Pinecone connection"""
        try:
            # Initialize embedding model
            logger.info("🤖 Loading embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Pinecone if configured
            if settings.pinecone_api_key and settings.pinecone_index_name:
                self._initialize_pinecone()
            else:
                logger.warning("⚠️ Pinecone not configured, falling back to simple search")
                
        except Exception as e:
            logger.error(f"❌ Error initializing vector search: {e}")
            self.model = None
            self.index = None
    
    def _initialize_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index = pc.Index(settings.pinecone_index_name)
            
            logger.info(f"✅ Connected to Pinecone index: {settings.pinecone_index_name}")
            
        except ImportError:
            logger.warning("⚠️ Pinecone package not installed")
        except Exception as e:
            logger.error(f"❌ Error connecting to Pinecone: {e}")
            self.index = None
    
    async def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search for relevant knowledge using vector similarity
        """
        if not self.model:
            logger.warning("⚠️ Vector search not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = await asyncio.to_thread(
                self.model.encode, [query]
            )
            
            if self.index:
                # Use Pinecone for semantic search
                return await self._search_pinecone(query_embedding[0], max_results)
            else:
                # Fallback to simple search
                logger.info("📝 Using fallback simple search")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in vector search: {e}")
            return []
    
    async def _search_pinecone(self, query_embedding, max_results: int) -> List[Dict]:
        """Search using Pinecone vector database"""
        try:
            # Query Pinecone
            search_results = await asyncio.to_thread(
                self.index.query,
                vector=query_embedding.tolist(),
                top_k=max_results,
                include_metadata=True
            )
            
            # Format results
            results = []
            for match in search_results.matches:
                results.append({
                    'document': match.metadata.get('source', 'unknown'),
                    'score': float(match.score),
                    'chunks': [match.metadata.get('text', '')],
                    'chunk_index': match.metadata.get('chunk_index', 0),
                    'id': match.id
                })
            
            logger.info(f"🔍 Found {len(results)} relevant chunks from Pinecone")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching Pinecone: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if vector search is available"""
        return self.model is not None
    
    def is_pinecone_available(self) -> bool:
        """Check if Pinecone is available"""
        return self.index is not None
    
    async def add_document(self, document_id: str, text: str, metadata: Dict) -> bool:
        """Add a document to the vector database"""
        if not self.model or not self.index:
            return False
        
        try:
            # Generate embedding
            embedding = await asyncio.to_thread(
                self.model.encode, [text]
            )
            
            # Upload to Pinecone
            await asyncio.to_thread(
                self.index.upsert,
                vectors=[{
                    'id': document_id,
                    'values': embedding[0].tolist(),
                    'metadata': metadata
                }]
            )
            
            logger.info(f"✅ Added document to vector database: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding document: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """Get vector database statistics"""
        if not self.index:
            return {"available": False}
        
        try:
            stats = await asyncio.to_thread(self.index.describe_index_stats)
            return {
                "available": True,
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "metric": stats.metric,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"available": False, "error": str(e)}