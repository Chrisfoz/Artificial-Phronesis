"""
PDF processing and text extraction for academic papers.
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Metadata extracted from academic paper."""
    title: Optional[str] = None
    authors: List[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    venue: Optional[str] = None
    file_path: str = ""

    def __post_init__(self):
        if self.authors is None:
            self.authors = []


@dataclass
class TextChunk:
    """A chunk of text from a paper."""
    text: str
    page_num: int
    section: Optional[str] = None
    chunk_id: int = 0
    metadata: Optional[Dict[str, Any]] = None


class PDFProcessor:
    """Processes PDF files and extracts structured content."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor.

        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if not HAS_PYMUPDF and not HAS_PDFPLUMBER:
            raise ImportError("Either PyMuPDF or pdfplumber must be installed")

    def extract_text(self, pdf_path: str) -> str:
        """
        Extract all text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        if HAS_PYMUPDF:
            return self._extract_text_pymupdf(pdf_path)
        elif HAS_PDFPLUMBER:
            return self._extract_text_pdfplumber(pdf_path)
        else:
            raise RuntimeError("No PDF library available")

    def _extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF."""
        doc = fitz.open(pdf_path)
        text_parts = []

        for page in doc:
            text_parts.append(page.get_text())

        doc.close()
        return "\n\n".join(text_parts)

    def _extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber."""
        text_parts = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return "\n\n".join(text_parts)

    def extract_metadata(self, pdf_path: str, text: Optional[str] = None) -> PaperMetadata:
        """
        Extract metadata from PDF.

        Args:
            pdf_path: Path to PDF file
            text: Pre-extracted text (optional)

        Returns:
            Paper metadata
        """
        metadata = PaperMetadata(file_path=pdf_path)

        # Try to get metadata from PDF properties
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(pdf_path)
                meta = doc.metadata

                if meta.get('title'):
                    metadata.title = meta['title']
                if meta.get('author'):
                    # Split multiple authors
                    authors = re.split(r',|;|\band\b', meta['author'])
                    metadata.authors = [a.strip() for a in authors if a.strip()]

                doc.close()
            except Exception as e:
                logger.warning(f"Could not extract metadata from PDF properties: {e}")

        # If no metadata from PDF properties, try to extract from text
        if not metadata.title or not metadata.authors:
            if text is None:
                text = self.extract_text(pdf_path)

            # Try to extract title from first page (usually largest or first bold text)
            lines = text.split('\n')[:50]  # First 50 lines
            for line in lines:
                line = line.strip()
                if len(line) > 20 and len(line) < 200:
                    # Heuristic: title is often a long line near the top
                    if not metadata.title and not line.startswith('http'):
                        metadata.title = line
                        break

            # Try to extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', text[:2000])
            if year_match:
                metadata.year = int(year_match.group())

            # Try to extract abstract
            abstract_match = re.search(
                r'Abstract[:\s]+(.*?)(?:\n\n|\n[A-Z][a-z]+:|\n1\.?\s+Introduction)',
                text,
                re.DOTALL | re.IGNORECASE
            )
            if abstract_match:
                metadata.abstract = abstract_match.group(1).strip()

            # Try to extract DOI
            doi_match = re.search(r'doi[:\s]*(10\.\d{4,}[^\s]+)', text, re.IGNORECASE)
            if doi_match:
                metadata.doi = doi_match.group(1)

        return metadata

    def chunk_text(self, text: str, metadata: Optional[PaperMetadata] = None) -> List[TextChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            metadata: Optional paper metadata

        Returns:
            List of text chunks
        """
        chunks = []
        chunk_id = 0

        # Simple sentence-aware chunking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(TextChunk(
                    text=chunk_text,
                    page_num=0,  # TODO: Track page numbers
                    chunk_id=chunk_id,
                    metadata={'paper_metadata': metadata} if metadata else None
                ))
                chunk_id += 1

                # Keep overlap
                overlap_text = chunk_text[-self.chunk_overlap:] if len(chunk_text) > self.chunk_overlap else chunk_text
                current_chunk = [overlap_text, sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(TextChunk(
                text=chunk_text,
                page_num=0,
                chunk_id=chunk_id,
                metadata={'paper_metadata': metadata} if metadata else None
            ))

        return chunks

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF file completely: extract text, metadata, and create chunks.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing metadata, full text, and chunks
        """
        logger.info(f"Processing PDF: {pdf_path}")

        # Extract text
        text = self.extract_text(pdf_path)

        # Extract metadata
        metadata = self.extract_metadata(pdf_path, text)

        # Create chunks
        chunks = self.chunk_text(text, metadata)

        logger.info(f"Extracted {len(chunks)} chunks from {Path(pdf_path).name}")

        return {
            'metadata': metadata,
            'full_text': text,
            'chunks': chunks,
            'file_path': pdf_path
        }

    def process_directory(self, directory: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Process all PDFs in a directory.

        Args:
            directory: Directory containing PDFs
            pattern: File pattern to match

        Returns:
            List of processed paper data
        """
        pdf_files = list(Path(directory).glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")

        results = []
        for pdf_file in pdf_files:
            try:
                result = self.process_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file}: {e}")

        return results


if __name__ == "__main__":
    # Example usage
    processor = PDFProcessor()

    # Process a single PDF
    # result = processor.process_pdf("data/papers/example.pdf")
    # print(f"Title: {result['metadata'].title}")
    # print(f"Authors: {result['metadata'].authors}")
    # print(f"Chunks: {len(result['chunks'])}")

    # Process directory
    # results = processor.process_directory("data/papers")
    # print(f"Processed {len(results)} papers")
