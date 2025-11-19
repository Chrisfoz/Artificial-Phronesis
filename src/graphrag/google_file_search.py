"""
Google File Search integration for document indexing and retrieval.

Uses Google's Gemini API with File Search capability for powerful RAG.
"""

import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import logging

try:
    import google.generativeai as genai
    HAS_GOOGLE_AI = True
except ImportError:
    HAS_GOOGLE_AI = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleFileSearch:
    """Google File Search integration for document RAG."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google File Search.

        Args:
            api_key: Google API key (defaults to env variable)
        """
        load_dotenv()

        if not HAS_GOOGLE_AI:
            raise ImportError(
                "google-generativeai not installed. Install with: pip install google-generativeai"
            )

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        genai.configure(api_key=self.api_key)
        self.model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro-latest")

        logger.info(f"Initialized Google File Search with model: {self.model_name}")

    def upload_file(self, file_path: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to Google File API.

        Args:
            file_path: Path to file
            display_name: Optional display name for the file

        Returns:
            File metadata including URI
        """
        logger.info(f"Uploading file: {file_path}")

        if not display_name:
            display_name = Path(file_path).name

        try:
            uploaded_file = genai.upload_file(path=file_path, display_name=display_name)

            # Wait for file to be processed
            logger.info(f"Waiting for file {display_name} to be processed...")
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)

            if uploaded_file.state.name == "FAILED":
                raise Exception(f"File processing failed: {uploaded_file.state.name}")

            logger.info(f"File uploaded successfully: {uploaded_file.uri}")

            return {
                "name": uploaded_file.name,
                "display_name": uploaded_file.display_name,
                "uri": uploaded_file.uri,
                "mime_type": uploaded_file.mime_type,
                "size_bytes": uploaded_file.size_bytes,
                "state": uploaded_file.state.name
            }

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise

    def upload_directory(self, directory: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Upload all files matching pattern in a directory.

        Args:
            directory: Directory path
            pattern: File pattern (default: *.pdf)

        Returns:
            List of uploaded file metadata
        """
        files_path = Path(directory)
        matching_files = list(files_path.glob(pattern))

        logger.info(f"Found {len(matching_files)} files matching {pattern} in {directory}")

        uploaded_files = []
        for file_path in matching_files:
            try:
                file_metadata = self.upload_file(str(file_path))
                uploaded_files.append(file_metadata)
            except Exception as e:
                logger.error(f"Failed to upload {file_path}: {e}")
                continue

        return uploaded_files

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all uploaded files.

        Returns:
            List of file metadata
        """
        try:
            files = genai.list_files()
            return [
                {
                    "name": f.name,
                    "display_name": f.display_name,
                    "uri": f.uri,
                    "mime_type": f.mime_type,
                    "state": f.state.name
                }
                for f in files
            ]
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def delete_file(self, file_name: str):
        """
        Delete an uploaded file.

        Args:
            file_name: Name of the file to delete
        """
        try:
            genai.delete_file(file_name)
            logger.info(f"Deleted file: {file_name}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_name}: {e}")
            raise

    def query(
        self,
        question: str,
        file_uris: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Query documents using Google File Search.

        Args:
            question: Question to ask
            file_uris: List of file URIs to search (None = all files)
            temperature: Generation temperature
            max_tokens: Maximum response tokens

        Returns:
            Answer from the model
        """
        logger.info(f"Querying: {question}")

        try:
            # Build context from files
            if file_uris:
                files = [genai.get_file(uri) for uri in file_uris]
            else:
                # Use all uploaded files
                files = list(genai.list_files())

            if not files:
                return "No documents found to search. Please upload documents first."

            logger.info(f"Searching across {len(files)} document(s)")

            # Create model instance
            model = genai.GenerativeModel(self.model_name)

            # Generate response
            response = model.generate_content(
                [question] + files,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )

            return response.text

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def search_documents(
        self,
        query: str,
        file_uris: Optional[List[str]] = None,
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Search documents with detailed response.

        Args:
            query: Search query
            file_uris: Optional list of specific file URIs to search
            include_citations: Whether to request citations

        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Searching documents for: {query}")

        try:
            # Get files
            if file_uris:
                files = [genai.get_file(uri) for uri in file_uris]
            else:
                files = list(genai.list_files())

            if not files:
                return {
                    "answer": "No documents available for search.",
                    "sources": [],
                    "file_count": 0
                }

            # Build prompt with citation request
            prompt = query
            if include_citations:
                prompt += "\n\nPlease cite specific papers, authors, or page numbers when relevant."

            # Create model and generate
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content([prompt] + files)

            return {
                "answer": response.text,
                "sources": [f.display_name for f in files],
                "file_count": len(files),
                "model": self.model_name
            }

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return {
                "answer": f"Error searching documents: {str(e)}",
                "sources": [],
                "file_count": 0
            }

    def compare_concepts(
        self,
        concept1: str,
        concept2: str,
        file_uris: Optional[List[str]] = None
    ) -> str:
        """
        Compare two concepts using the document corpus.

        Args:
            concept1: First concept
            concept2: Second concept
            file_uris: Optional specific files to search

        Returns:
            Comparison analysis
        """
        prompt = f"""Compare and contrast {concept1} and {concept2} based on the academic papers provided.

Focus on:
1. How each concept is defined across different papers
2. Key differences and similarities
3. Disciplinary perspectives (psychology, philosophy, AI)
4. Which traits or capabilities are associated with each
5. Cite specific papers and authors

Provide a structured comparison."""

        return self.query(prompt, file_uris)

    def find_gaps(self, concept: str, file_uris: Optional[List[str]] = None) -> str:
        """
        Identify research gaps related to a concept.

        Args:
            concept: Concept to analyze
            file_uris: Optional specific files to search

        Returns:
            Gap analysis
        """
        prompt = f"""Analyze the research landscape around {concept} based on the provided papers.

Identify:
1. What aspects are well-covered in the literature
2. What aspects are mentioned but under-theorized
3. What connections to other concepts are missing or weak
4. What implementation details are lacking
5. Potential future research directions

Cite specific papers to support your analysis."""

        return self.query(prompt, file_uris)


if __name__ == "__main__":
    # Example usage
    gfs = GoogleFileSearch()

    # Upload papers
    # uploaded = gfs.upload_directory("data/papers", "*.pdf")
    # print(f"Uploaded {len(uploaded)} papers")

    # List files
    files = gfs.list_files()
    print(f"Total files: {len(files)}")

    # Query
    # answer = gfs.query("What is artificial wisdom?")
    # print(answer)

    # Compare concepts
    # comparison = gfs.compare_concepts("Wisdom", "Intelligence")
    # print(comparison)
