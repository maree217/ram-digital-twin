import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.knowledge.knowledge_search import SimpleKnowledgeSearch

@pytest.mark.unit
class TestKnowledgeSearch:
    
    @pytest.fixture
    def temp_knowledge_base(self):
        """Create temporary knowledge base for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test documents
            test_docs = {
                "pmo_experience": """
                PMO Setup and Program Management Office establishment
                Ram has led PMO establishment for multiple organizations with budgets exceeding £50M.
                Key achievements include designing enterprise PMO framework for housing association
                managing 50,000+ properties. Established governance structures reducing project 
                delivery time by 35%. Created standardized project methodologies improving 
                success rates from 60% to 85%.
                """,
                "dynamics_expertise": """
                Microsoft Dynamics 365 implementation and optimization
                Extensive experience in Dynamics 365 implementation across public and private sectors.
                Led full Dynamics 365 rollout for housing association with 2,000+ users.
                Designed custom workflows reducing manual processing by 60%.
                Implemented Power Platform solutions automating 15 core business processes.
                """,
                "transformation_methods": """
                Digital transformation methodologies and frameworks
                The Ram Digital Transformation Framework is a proven 5-phase methodology.
                Phase 1: Discovery & Assessment. Phase 2: Strategy & Vision.
                Phase 3: Foundation Building. Phase 4: Transformation Delivery.
                Phase 5: Optimization & Sustainment. Typical ROI of 300% within 18 months.
                """
            }
            
            for filename, content in test_docs.items():
                file_path = Path(temp_dir) / f"{filename}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
            
            yield temp_dir
    
    @pytest.fixture
    def knowledge_search(self, temp_knowledge_base):
        """Create SimpleKnowledgeSearch instance with test data"""
        return SimpleKnowledgeSearch(temp_knowledge_base)
    
    def test_initialization_with_valid_path(self, temp_knowledge_base):
        """Test initialization with valid knowledge base path"""
        ks = SimpleKnowledgeSearch(temp_knowledge_base)
        assert len(ks.documents) == 3
        assert "pmo_experience" in ks.documents
        assert "dynamics_expertise" in ks.documents
        assert "transformation_methods" in ks.documents
    
    def test_initialization_with_invalid_path(self):
        """Test initialization with non-existent path"""
        ks = SimpleKnowledgeSearch("non_existent_directory")
        assert len(ks.documents) == 0
    
    def test_document_loading(self, knowledge_search):
        """Test that documents are loaded correctly"""
        docs = knowledge_search.documents
        
        # Check document structure
        for doc_name, doc_data in docs.items():
            assert 'content' in doc_data
            assert 'path' in doc_data
            assert 'size' in doc_data
            assert len(doc_data['content']) > 0
            assert doc_data['size'] == len(doc_data['content'])
    
    def test_keyword_extraction(self, knowledge_search):
        """Test keyword extraction from queries"""
        test_cases = [
            ("PMO setup experience", ["pmo", "setup", "experience"]),
            ("What is your Dynamics 365 background?", ["dynamics", "background"]),
            ("Tell me about transformation", ["tell", "transformation"]),
            ("How do you handle change management?", ["handle", "change", "management"])
        ]
        
        for query, expected_keywords in test_cases:
            keywords = knowledge_search._extract_keywords(query)
            for expected in expected_keywords:
                assert expected in keywords
    
    def test_keyword_extraction_filters_stop_words(self, knowledge_search):
        """Test that stop words are filtered out"""
        query = "What is the best approach for this?"
        keywords = knowledge_search._extract_keywords(query)
        
        stop_words = ["what", "is", "the", "for", "this"]
        for stop_word in stop_words:
            assert stop_word not in keywords
    
    def test_search_pmo_keywords(self, knowledge_search):
        """Test search with PMO-related keywords"""
        results = knowledge_search.search("PMO setup governance", max_results=2)
        
        assert len(results) > 0
        
        # Should find PMO document
        pmo_found = any("pmo" in result['document'].lower() for result in results)
        assert pmo_found
        
        # Check result structure
        for result in results:
            assert 'document' in result
            assert 'score' in result
            assert 'chunks' in result
            assert 'path' in result
            assert result['score'] > 0
    
    def test_search_dynamics_keywords(self, knowledge_search):
        """Test search with Dynamics-related keywords"""
        results = knowledge_search.search("Dynamics 365 implementation", max_results=2)
        
        assert len(results) > 0
        
        # Should find Dynamics document
        dynamics_found = any("dynamics" in result['document'].lower() for result in results)
        assert dynamics_found
    
    def test_search_transformation_keywords(self, knowledge_search):
        """Test search with transformation keywords"""
        results = knowledge_search.search("digital transformation methodology", max_results=2)
        
        assert len(results) > 0
        
        # Should find transformation document
        transformation_found = any("transformation" in result['document'].lower() for result in results)
        assert transformation_found
    
    def test_search_no_matches(self, knowledge_search):
        """Test search with keywords that don't match"""
        results = knowledge_search.search("quantum computing blockchain")
        
        # Should return empty results or very low scores
        assert len(results) == 0 or all(result['score'] < 0.1 for result in results)
    
    def test_search_max_results_limit(self, knowledge_search):
        """Test that search respects max_results parameter"""
        results = knowledge_search.search("project management", max_results=1)
        assert len(results) <= 1
        
        results = knowledge_search.search("project management", max_results=2)
        assert len(results) <= 2
    
    def test_relevance_scoring(self, knowledge_search):
        """Test that relevance scoring works correctly"""
        # Search for very specific terms
        specific_results = knowledge_search.search("PMO establishment governance")
        general_results = knowledge_search.search("work project")
        
        if specific_results and general_results:
            # More specific search should have higher scores
            max_specific_score = max(r['score'] for r in specific_results)
            max_general_score = max(r['score'] for r in general_results)
            assert max_specific_score >= max_general_score
    
    def test_chunk_extraction(self, knowledge_search):
        """Test that relevant chunks are extracted"""
        results = knowledge_search.search("PMO framework housing association")
        
        if results:
            result = results[0]
            assert len(result['chunks']) > 0
            
            # Chunks should contain relevant keywords
            chunk_text = " ".join(result['chunks']).lower()
            relevant_terms = ["pmo", "framework", "housing"]
            assert any(term in chunk_text for term in relevant_terms)
    
    def test_get_document_list(self, knowledge_search):
        """Test getting list of available documents"""
        doc_list = knowledge_search.get_document_list()
        
        assert len(doc_list) == 3
        assert "pmo_experience" in doc_list
        assert "dynamics_expertise" in doc_list
        assert "transformation_methods" in doc_list
    
    def test_get_document_content(self, knowledge_search):
        """Test getting content of specific document"""
        content = knowledge_search.get_document_content("pmo_experience")
        
        assert len(content) > 0
        assert "PMO" in content
        assert "housing association" in content
    
    def test_get_document_content_nonexistent(self, knowledge_search):
        """Test getting content of non-existent document"""
        content = knowledge_search.get_document_content("nonexistent_doc")
        assert content == ""
    
    def test_search_results_sorted_by_score(self, knowledge_search):
        """Test that search results are sorted by relevance score"""
        results = knowledge_search.search("PMO Dynamics transformation")
        
        if len(results) > 1:
            scores = [result['score'] for result in results]
            # Should be sorted in descending order
            assert scores == sorted(scores, reverse=True)
    
    def test_search_with_empty_query(self, knowledge_search):
        """Test search with empty query"""
        results = knowledge_search.search("")
        assert len(results) == 0
    
    def test_search_case_insensitive(self, knowledge_search):
        """Test that search is case insensitive"""
        upper_results = knowledge_search.search("PMO DYNAMICS")
        lower_results = knowledge_search.search("pmo dynamics")
        
        # Should return similar results regardless of case
        assert len(upper_results) > 0
        assert len(lower_results) > 0
    
    def test_multiple_keyword_matching(self, knowledge_search):
        """Test matching multiple keywords increases score"""
        single_keyword = knowledge_search.search("PMO")
        multiple_keywords = knowledge_search.search("PMO governance framework")
        
        if single_keyword and multiple_keywords:
            # Document matching multiple keywords should score higher
            single_max = max(r['score'] for r in single_keyword)
            multiple_max = max(r['score'] for r in multiple_keywords)
            
            # Multiple keywords should generally score higher
            assert multiple_max >= single_max