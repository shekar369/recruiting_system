"""
Semantic Chunking Service for resumes using LangChain
"""
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


class ChunkingService:
    """Service for semantically chunking resume text"""

    def __init__(self):
        # Initialize the text splitter with resume-appropriate settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reasonable size for resume sections
            chunk_overlap=50,  # Overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Hierarchical splitting
        )

    def chunk_by_sections(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create chunks based on resume sections (skills, experience, education)

        Args:
            parsed_data: Dict with parsed resume data

        Returns:
            List of chunk dictionaries with text, metadata, and order
        """
        chunks = []
        chunk_order = 0

        # Chunk 1: Contact and Skills
        if parsed_data.get('skills'):
            skills_text = "Skills: " + ", ".join(parsed_data['skills'])
            chunks.append({
                'chunk_text': skills_text,
                'chunk_type': 'skills',
                'chunk_order': chunk_order,
                'metadata': {
                    'email': parsed_data.get('email'),
                    'phone': parsed_data.get('phone'),
                    'linkedin_url': parsed_data.get('linkedin_url'),
                    'github_url': parsed_data.get('github_url'),
                }
            })
            chunk_order += 1

        # Chunk 2+: Experience (may create multiple chunks)
        if parsed_data.get('experience_section'):
            exp_chunks = self._chunk_section(
                parsed_data['experience_section'],
                'experience',
                chunk_order
            )
            chunks.extend(exp_chunks)
            chunk_order += len(exp_chunks)

        # Chunk N: Education (may create multiple chunks)
        if parsed_data.get('education_section'):
            edu_chunks = self._chunk_section(
                parsed_data['education_section'],
                'education',
                chunk_order
            )
            chunks.extend(edu_chunks)
            chunk_order += len(edu_chunks)

        # If no structured sections found, chunk the full text
        if not chunks and parsed_data.get('full_text'):
            full_text_chunks = self._chunk_section(
                parsed_data['full_text'],
                'full_text',
                0
            )
            chunks.extend(full_text_chunks)

        return chunks

    def _chunk_section(
        self,
        text: str,
        section_type: str,
        starting_order: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk a section of text using RecursiveCharacterTextSplitter

        Args:
            text: Text to chunk
            section_type: Type of section (experience, education, etc.)
            starting_order: Starting order number for chunks

        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            return []

        # Create LangChain documents
        documents = [Document(page_content=text)]

        # Split into chunks
        split_docs = self.text_splitter.split_documents(documents)

        # Convert to our chunk format
        chunks = []
        for i, doc in enumerate(split_docs):
            chunks.append({
                'chunk_text': doc.page_content,
                'chunk_type': section_type,
                'chunk_order': starting_order + i,
                'metadata': {}
            })

        return chunks

    def chunk_with_metadata(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk text with custom metadata

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks

        Returns:
            List of chunk dictionaries
        """
        if not text or not text.strip():
            return []

        documents = [Document(page_content=text, metadata=metadata or {})]
        split_docs = self.text_splitter.split_documents(documents)

        chunks = []
        for i, doc in enumerate(split_docs):
            chunks.append({
                'chunk_text': doc.page_content,
                'chunk_type': 'general',
                'chunk_order': i,
                'metadata': doc.metadata
            })

        return chunks

    def semantic_chunk_resume(
        self,
        parsed_data: Dict[str, Any],
        preserve_sections: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Main method to semantically chunk a resume

        Args:
            parsed_data: Parsed resume data from DocumentProcessorService
            preserve_sections: If True, chunks by sections; else chunks full text

        Returns:
            List of chunk dictionaries ready for database storage
        """
        try:
            if preserve_sections:
                return self.chunk_by_sections(parsed_data)
            else:
                full_text = parsed_data.get('full_text', '')
                return self.chunk_with_metadata(full_text, {
                    'email': parsed_data.get('email'),
                    'skills': parsed_data.get('skills', [])
                })

        except Exception as e:
            logger.error(f"Error during semantic chunking: {e}")
            raise


# Singleton instance
chunking_service = ChunkingService()
