"""
Reranking Service using Cross-Encoder for improved precision
"""
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class RankedDocument:
    """Ranked document with score"""
    def __init__(self, document: Any, score: float, original_rank: int):
        self.document = document
        self.score = score
        self.original_rank = original_rank
        self.reranked_rank = None

    def to_dict(self):
        return {
            'document': self.document,
            'score': float(self.score),
            'original_rank': self.original_rank,
            'reranked_rank': self.reranked_rank
        }


class RerankingService:
    """Service for reranking search results using cross-encoder"""

    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-12-v2'):
        """
        Initialize the reranking service

        Args:
            model_name: Cross-encoder model name from HuggingFace
        """
        self.model_name = model_name
        self.model = None

        logger.info(f"Initializing Reranking Service with model: {model_name}")

    def _load_model(self):
        """Lazy load the cross-encoder model"""
        if self.model is None:
            try:
                self.model = CrossEncoder(self.model_name)
                logger.info(f"Cross-encoder model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading cross-encoder model: {e}")
                raise

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 20
    ) -> List[RankedDocument]:
        """
        Rerank documents using cross-encoder

        Args:
            query: Search query
            documents: List of document texts to rerank
            top_k: Number of top results to return

        Returns:
            List of RankedDocument objects, sorted by reranked score
        """
        try:
            self._load_model()

            if not documents:
                return []

            # Create query-document pairs
            pairs = [[query, doc] for doc in documents]

            # Get cross-encoder scores
            scores = self.model.predict(pairs)

            # Create ranked documents
            ranked_docs = []
            for i, (doc, score) in enumerate(zip(documents, scores)):
                ranked_doc = RankedDocument(
                    document=doc,
                    score=float(score),
                    original_rank=i
                )
                ranked_docs.append(ranked_doc)

            # Sort by score (descending)
            ranked_docs.sort(key=lambda x: x.score, reverse=True)

            # Assign reranked positions
            for i, doc in enumerate(ranked_docs):
                doc.reranked_rank = i

            # Return top_k
            return ranked_docs[:top_k]

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            raise

    def rerank_search_results(
        self,
        query: str,
        search_results: List[Any],
        document_extractor: callable,
        top_k: int = 20
    ) -> List[Any]:
        """
        Rerank search results with custom document extraction

        Args:
            query: Search query
            search_results: List of search result objects
            document_extractor: Function to extract text from search result
            top_k: Number of top results to return

        Returns:
            Reranked search results with added rerank_score
        """
        try:
            if not search_results:
                return []

            # Extract documents
            documents = [document_extractor(result) for result in search_results]

            # Rerank
            reranked = self.rerank(query, documents, top_k=len(search_results))

            # Map back to original results
            reranked_results = []
            for ranked_doc in reranked[:top_k]:
                original_result = search_results[ranked_doc.original_rank]

                # Add reranking metadata
                if hasattr(original_result, 'rerank_score'):
                    original_result.rerank_score = ranked_doc.score
                    original_result.original_score = original_result.score if hasattr(original_result, 'score') else None
                    original_result.rank_change = ranked_doc.original_rank - ranked_doc.reranked_rank
                elif isinstance(original_result, dict):
                    original_result['rerank_score'] = ranked_doc.score
                    original_result['original_score'] = original_result.get('score')
                    original_result['rank_change'] = ranked_doc.original_rank - ranked_doc.reranked_rank

                reranked_results.append(original_result)

            return reranked_results

        except Exception as e:
            logger.error(f"Error in reranking search results: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranking model"""
        return {
            'model_name': self.model_name,
            'model_loaded': self.model is not None,
            'model_type': 'cross-encoder'
        }


# Singleton instance - lazy loaded
_reranking_service_instance = None


def get_reranking_service() -> RerankingService:
    """Get or create the singleton reranking service instance"""
    global _reranking_service_instance

    if _reranking_service_instance is None:
        _reranking_service_instance = RerankingService()

    return _reranking_service_instance
