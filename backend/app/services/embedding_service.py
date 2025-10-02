"""
Embedding Service using Sentence Transformers for text embeddings
"""
import logging
import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Sentence Transformers"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_dir: str = None):
        """
        Initialize the embedding service

        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
            cache_dir: Directory to cache the model
        """
        self.model_name = model_name
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.cache_dir = cache_dir or str(Path.home() / '.cache' / 'sentence_transformers')

        logger.info(f"Initializing Embedding Service with model: {model_name}")
        logger.info(f"Using device: {self.device}")

        try:
            # Load the model
            self.model = SentenceTransformer(
                model_name,
                cache_folder=self.cache_dir,
                device=self.device
            )

            # Get embedding dimension
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dim}")

        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            numpy array of embedding vector
        """
        try:
            if not text or not text.strip():
                # Return zero vector for empty text
                return np.zeros(self.embedding_dim, dtype=np.float32)

            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # L2 normalization for better similarity
            )

            return embedding.astype(np.float32)

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        try:
            if not texts:
                return np.array([], dtype=np.float32)

            # Filter out empty texts and keep track of indices
            valid_texts = []
            valid_indices = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text)
                    valid_indices.append(i)

            if not valid_texts:
                # Return zero vectors for all texts
                return np.zeros((len(texts), self.embedding_dim), dtype=np.float32)

            # Generate embeddings for valid texts
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=show_progress,
                normalize_embeddings=True
            )

            # Create result array with zero vectors for invalid texts
            result = np.zeros((len(texts), self.embedding_dim), dtype=np.float32)
            for i, idx in enumerate(valid_indices):
                result[idx] = embeddings[i]

            return result

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'device': self.device,
            'max_seq_length': self.model.max_seq_length,
            'cache_dir': self.cache_dir
        }

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (-1 to 1)
        """
        try:
            # Cosine similarity with normalized vectors is just dot product
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            raise


# Singleton instance - lazy loaded
_embedding_service_instance = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton embedding service instance"""
    global _embedding_service_instance

    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()

    return _embedding_service_instance
