"""
Document Processing Service for extracting text and structured data from resumes
"""
import re
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)


class DocumentProcessorService:
    """Service for processing PDF and DOCX resumes"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']

    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using multiple methods for best results"""
        text = ""

        try:
            # Try pdfplumber first (better for structured documents)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # If pdfplumber fails, fallback to PyPDF2
            if not text.strip():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise

        return text.strip()

    async def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += "\n" + cell.text

            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise

    async def extract_text(self, file_path: str) -> str:
        """Extract text from supported file formats"""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == '.pdf':
            return await self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return await self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Various phone number patterns
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US/International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 123-456-7890
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        return None

    def extract_linkedin_url(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile URL"""
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None

    def extract_github_url(self, text: str) -> Optional[str]:
        """Extract GitHub profile URL"""
        pattern = r'https?://(?:www\.)?github\.com/[\w\-]+'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches[0] if matches else None

    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text"""
        # Common technical skills database
        common_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
            'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab',

            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
            'flask', 'fastapi', 'spring', 'asp.net', 'jquery', 'bootstrap',

            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'cassandra', 'dynamodb', 'sqlite',

            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
            'ansible', 'ci/cd', 'git', 'github', 'gitlab', 'bitbucket',

            # AI/ML
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv',

            # Other
            'agile', 'scrum', 'jira', 'rest api', 'graphql', 'microservices',
            'linux', 'unix', 'bash', 'powershell'
        }

        text_lower = text.lower()
        found_skills = []

        for skill in common_skills:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())

        return list(set(found_skills))  # Remove duplicates

    def extract_experience_section(self, text: str) -> Optional[str]:
        """Extract the experience section from resume"""
        # Common section headers for experience
        exp_headers = [
            'experience', 'work experience', 'professional experience',
            'employment history', 'work history', 'career history'
        ]

        lines = text.split('\n')
        exp_section = []
        in_exp_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if this line is an experience header
            if any(header in line_lower for header in exp_headers):
                in_exp_section = True
                continue

            # Check if we've hit a new section (Education, Skills, etc.)
            next_section_headers = ['education', 'skills', 'certifications', 'projects', 'awards']
            if in_exp_section and any(header in line_lower for header in next_section_headers):
                break

            if in_exp_section and line.strip():
                exp_section.append(line)

        return '\n'.join(exp_section) if exp_section else None

    def extract_education_section(self, text: str) -> Optional[str]:
        """Extract the education section from resume"""
        edu_headers = ['education', 'academic background', 'qualifications']

        lines = text.split('\n')
        edu_section = []
        in_edu_section = False

        for line in lines:
            line_lower = line.lower().strip()

            if any(header in line_lower for header in edu_headers):
                in_edu_section = True
                continue

            # Check if we've hit a new section
            next_section_headers = ['experience', 'skills', 'certifications', 'projects']
            if in_edu_section and any(header in line_lower for header in next_section_headers):
                break

            if in_edu_section and line.strip():
                edu_section.append(line)

        return '\n'.join(edu_section) if edu_section else None

    async def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured data

        Returns:
            Dict containing:
                - full_text: Complete extracted text
                - email: Extracted email
                - phone: Extracted phone
                - linkedin_url: LinkedIn profile
                - github_url: GitHub profile
                - skills: List of technical skills
                - experience_section: Raw experience text
                - education_section: Raw education text
        """
        try:
            # Extract full text
            full_text = await self.extract_text(file_path)

            # Extract structured information
            parsed_data = {
                'full_text': full_text,
                'email': self.extract_email(full_text),
                'phone': self.extract_phone(full_text),
                'linkedin_url': self.extract_linkedin_url(full_text),
                'github_url': self.extract_github_url(full_text),
                'skills': self.extract_skills(full_text),
                'experience_section': self.extract_experience_section(full_text),
                'education_section': self.extract_education_section(full_text),
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise


# Singleton instance
document_processor = DocumentProcessorService()
