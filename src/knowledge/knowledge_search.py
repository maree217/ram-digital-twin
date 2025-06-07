import os
import re
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class SimpleKnowledgeSearch:
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.documents = {}
        self._load_documents()
    
    def _load_documents(self):
        """Load all text documents from the knowledge base directory"""
        if not self.knowledge_base_path.exists():
            logger.warning(f"Knowledge base directory {self.knowledge_base_path} does not exist")
            return
        
        for file_path in self.knowledge_base_path.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[file_path.stem] = {
                        'content': content,
                        'path': str(file_path),
                        'size': len(content)
                    }
                logger.info(f"Loaded document: {file_path.stem}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
    
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Simple keyword-based search through documents
        Returns relevant document chunks with scores
        """
        if not self.documents:
            return []
        
        query_terms = self._extract_keywords(query.lower())
        results = []
        
        for doc_name, doc_data in self.documents.items():
            content = doc_data['content'].lower()
            score = self._calculate_relevance_score(content, query_terms)
            
            if score > 0:
                relevant_chunks = self._extract_relevant_chunks(
                    doc_data['content'], query_terms
                )
                
                results.append({
                    'document': doc_name,
                    'score': score,
                    'chunks': relevant_chunks,
                    'path': doc_data['path']
                })
        
        # Sort by relevance score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from the query"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'about',
            'what', 'how', 'when', 'where', 'why', 'who', 'which', 'this', 'that'
        }
        
        # Extract words and filter out stop words
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _calculate_relevance_score(self, content: str, query_terms: List[str]) -> float:
        """Calculate relevance score based on keyword matches"""
        if not query_terms:
            return 0
        
        score = 0
        content_words = content.split()
        total_words = len(content_words)
        
        for term in query_terms:
            # Count exact matches
            exact_matches = content.count(term)
            
            # Count partial matches (word contains the term)
            partial_matches = sum(1 for word in content_words if term in word)
            
            # Calculate term frequency
            tf = (exact_matches * 2 + partial_matches) / total_words if total_words > 0 else 0
            
            # Add to total score
            score += tf * 100
        
        return score
    
    def _extract_relevant_chunks(self, content: str, query_terms: List[str], chunk_size: int = 300) -> List[str]:
        """Extract relevant chunks of text that contain query terms"""
        sentences = re.split(r'[.!?]+', content)
        relevant_chunks = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            sentence_lower = sentence.lower()
            matches = sum(1 for term in query_terms if term in sentence_lower)
            
            if matches > 0:
                # Expand context around matching sentence
                start_idx = max(0, content.find(sentence) - chunk_size // 2)
                end_idx = min(len(content), content.find(sentence) + len(sentence) + chunk_size // 2)
                chunk = content[start_idx:end_idx].strip()
                
                if chunk and chunk not in relevant_chunks:
                    relevant_chunks.append(chunk)
        
        return relevant_chunks[:3]  # Return top 3 chunks
    
    def get_document_list(self) -> List[str]:
        """Get list of available documents"""
        return list(self.documents.keys())
    
    def get_document_content(self, doc_name: str) -> str:
        """Get full content of a specific document"""
        if doc_name in self.documents:
            return self.documents[doc_name]['content']
        return ""