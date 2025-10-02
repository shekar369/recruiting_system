"""
FAISS Vector Store Service for similarity search
"""
import logging
import json
import faiss
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from uuid import UUID

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing FAISS vector index and similarity search"""

    def __init__(self, dimension: int = 384, index_path: str = None):
        """
        Initialize the vector service

        Args:
            dimension: Embedding vector dimension (384 for all-MiniLM-L6-v2)
            index_path: Path to save/load the FAISS index
        """
        self.dimension = dimension
        self.index_path = index_path or "data/faiss_index"
        self.metadata_path = Path(self.index_path).parent / "faiss_metadata.json"

        # Create directory if it doesn't exist
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize FAISS index (using L2 distance for start)
        self.index = faiss.IndexFlatL2(dimension)

        # Metadata mapping: FAISS position -> chunk metadata
        self.id_to_metadata: Dict[int, Dict[str, Any]] = {}
        self.current_position = 0

        logger.info(f"Initialized FAISS index with dimension {dimension}")

        # Try to load existing index
        self.load_index()

    def add_vector(
        self,
        embedding: np.ndarray,
        chunk_id: UUID,
        candidate_id: UUID,
        resume_id: UUID,
        chunk_type: str,
        chunk_order: int
    ) -> int:
        """
        Add a single vector to the index

        Args:
            embedding: Embedding vector
            chunk_id: Database chunk ID
            candidate_id: Database candidate ID
            resume_id: Database resume ID
            chunk_type: Type of chunk (skills, experience, education)
            chunk_order: Order of chunk in resume

        Returns:
            Position in FAISS index
        """
        try:
            # Ensure embedding is the right shape and type
            embedding = embedding.reshape(1, -1).astype(np.float32)

            # Add to FAISS index
            self.index.add(embedding)

            # Store metadata
            position = self.current_position
            self.id_to_metadata[position] = {
                'chunk_id': str(chunk_id),
                'candidate_id': str(candidate_id),
                'resume_id': str(resume_id),
                'chunk_type': chunk_type,
                'chunk_order': chunk_order,
                'position': position
            }

            self.current_position += 1
            logger.debug(f"Added vector at position {position}")

            return position

        except Exception as e:
            logger.error(f"Error adding vector: {e}")
            raise

    def add_vectors(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add multiple vectors to the index

        Args:
            embeddings: numpy array of shape (n, dimension)
            metadata_list: List of metadata dicts for each embedding

        Returns:
            List of positions in FAISS index
        """
        try:
            if len(embeddings) != len(metadata_list):
                raise ValueError("Number of embeddings must match number of metadata entries")

            # Ensure correct shape and type
            embeddings = embeddings.astype(np.float32)

            # Add to FAISS index
            self.index.add(embeddings)

            # Store metadata
            positions = []
            for i, metadata in enumerate(metadata_list):
                position = self.current_position + i
                self.id_to_metadata[position] = {
                    **metadata,
                    'position': position
                }
                positions.append(position)

            self.current_position += len(embeddings)
            logger.info(f"Added {len(embeddings)} vectors to index")

            return positions

        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            raise

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 100,
        candidate_id_filter: Optional[List[UUID]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            candidate_id_filter: Optional list of candidate IDs to filter by

        Returns:
            List of dicts with distance, metadata
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Index is empty, returning no results")
                return []

            # Ensure query vector is the right shape and type
            query_vector = query_vector.reshape(1, -1).astype(np.float32)

            # Search
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))

            # Build results with metadata
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for missing results
                    continue

                metadata = self.id_to_metadata.get(int(idx))
                if metadata is None:
                    logger.warning(f"No metadata found for index {idx}")
                    continue

                # Apply candidate_id filter if provided
                if candidate_id_filter:
                    if UUID(metadata['candidate_id']) not in candidate_id_filter:
                        continue

                results.append({
                    'distance': float(dist),
                    'score': float(1 / (1 + dist)),  # Convert distance to similarity score
                    **metadata
                })

            return results

        except Exception as e:
            logger.error(f"Error searching index: {e}")
            raise

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dimension,
            'index_type': str(type(self.index).__name__),
            'metadata_count': len(self.id_to_metadata),
            'is_trained': self.index.is_trained,
            'index_path': self.index_path
        }

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)

            # Save metadata
            serializable_metadata = {}
            for pos, meta in self.id_to_metadata.items():
                serializable_metadata[str(pos)] = meta

            with open(self.metadata_path, 'w') as f:
                json.dump({
                    'metadata': serializable_metadata,
                    'current_position': self.current_position,
                    'dimension': self.dimension
                }, f, indent=2)

            logger.info(f"Saved index with {self.index.ntotal} vectors to {self.index_path}")

        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def load_index(self) -> bool:
        """
        Load FAISS index and metadata from disk

        Returns:
            True if loaded successfully, False if no index exists
        """
        try:
            if not Path(self.index_path).exists():
                logger.info("No existing index found, starting fresh")
                return False

            # Load FAISS index
            self.index = faiss.read_index(self.index_path)

            # Load metadata
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    data = json.load(f)

                # Convert string keys back to integers
                self.id_to_metadata = {
                    int(pos): meta
                    for pos, meta in data['metadata'].items()
                }
                self.current_position = data['current_position']
                self.dimension = data['dimension']

            logger.info(f"Loaded index with {self.index.ntotal} vectors from {self.index_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False

    def delete_by_candidate(self, candidate_id: UUID) -> int:
        """
        Delete all vectors for a specific candidate
        Note: FAISS doesn't support efficient deletion, so we rebuild the index

        Args:
            candidate_id: Candidate ID to delete

        Returns:
            Number of vectors deleted
        """
        try:
            # Find positions to keep
            positions_to_keep = []
            metadata_to_keep = []

            for pos, meta in self.id_to_metadata.items():
                if UUID(meta['candidate_id']) != candidate_id:
                    positions_to_keep.append(pos)
                    metadata_to_keep.append(meta)

            deleted_count = self.index.ntotal - len(positions_to_keep)

            if deleted_count == 0:
                return 0

            # Rebuild index
            if len(positions_to_keep) > 0:
                # Get embeddings for positions to keep
                embeddings_to_keep = []
                for pos in positions_to_keep:
                    # Reconstruct embedding from index
                    embedding = self.index.reconstruct(int(pos))
                    embeddings_to_keep.append(embedding)

                embeddings_array = np.array(embeddings_to_keep, dtype=np.float32)

                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.index.add(embeddings_array)

                # Rebuild metadata with new positions
                self.id_to_metadata = {}
                for i, meta in enumerate(metadata_to_keep):
                    meta['position'] = i
                    self.id_to_metadata[i] = meta

                self.current_position = len(positions_to_keep)
            else:
                # No vectors left, create empty index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.id_to_metadata = {}
                self.current_position = 0

            logger.info(f"Deleted {deleted_count} vectors for candidate {candidate_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise


# Singleton instance - lazy loaded
_vector_service_instance = None


def get_vector_service(dimension: int = 384) -> VectorService:
    """Get or create the singleton vector service instance"""
    global _vector_service_instance

    if _vector_service_instance is None:
        _vector_service_instance = VectorService(dimension=dimension)

    return _vector_service_instance
