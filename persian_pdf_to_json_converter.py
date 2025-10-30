#!/usr/bin/env python3
"""
Persian Law PDF to JSON Converter for ParsBERT Training
Converts over 3000 Persian law-related PDF documents to clean, structured JSON files
Handles both text-based and image-based PDFs automatically
"""

import os
import sys
import json
import hashlib
import logging
import time
import re
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

# PDF Processing Libraries
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import io

# OCR Libraries
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Language Detection
from langdetect import detect_langs, LangDetectException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PDFMetadata:
    """Metadata for each processed PDF"""
    id: str
    source_path: str
    title: str
    page_count: int
    type: str  # 'text' or 'ocr'
    created_at: str
    extraction_time: float
    language: str
    encoder_ready: bool
    file_hash: str
    status: str  # 'success', 'failed', 'partial'
    error_message: Optional[str] = None


@dataclass
class ProcessedDocument:
    """Structured document for JSON output"""
    id: str
    source_path: str
    title: str
    text_chunks: List[str]
    metadata: PDFMetadata


class PersianTextNormalizer:
    """Normalizes Persian text for consistency"""

    # Persian character mappings for normalization
    PERSIAN_CHAR_MAP = {
        'ك': 'ک',  # Arabic Kaf to Persian Kaf
        'ي': 'ی',  # Arabic Yeh to Persian Yeh
        'ى': 'ی',  # Alef Maksura to Persian Yeh
        'ة': 'ه',  # Teh Marbuta to Heh
        '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
        '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹',
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """Normalize Persian text"""
        if not text:
            return ""

        # Apply character mappings
        for arabic, persian in cls.PERSIAN_CHAR_MAP.items():
            text = text.replace(arabic, persian)

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters
        text = ''.join(char for char in text if not unicodedata.category(char).startswith('C'))

        # Normalize Unicode
        text = unicodedata.normalize('NFC', text)

        return text.strip()


class PDFClassifier:
    """Classifies PDFs as text-based or image-based"""

    MIN_TEXT_DENSITY = 0.3  # Minimum ratio of text to file size
    MIN_CHARS_PER_PAGE = 50  # Minimum characters per page for text PDF

    @classmethod
    def classify(cls, pdf_path: str) -> Tuple[str, float]:
        """
        Classify PDF as 'text' or 'image' based on extractable text density
        Returns: (type, confidence)
        """
        try:
            # Try to extract text using pdfminer
            text = cls._extract_text_pdfminer(pdf_path)

            # Get PDF info
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            file_size = os.path.getsize(pdf_path)
            doc.close()

            # Calculate metrics
            text_length = len(text.strip())
            chars_per_page = text_length / page_count if page_count > 0 else 0
            text_density = text_length / file_size if file_size > 0 else 0

            # Classification logic
            if chars_per_page >= cls.MIN_CHARS_PER_PAGE and text_density >= cls.MIN_TEXT_DENSITY:
                confidence = min(1.0, chars_per_page / 1000)  # Higher chars/page = higher confidence
                return 'text', confidence
            else:
                confidence = 1.0 - text_density  # Lower text density = higher confidence it's an image
                return 'image', confidence

        except Exception as e:
            logger.warning(f"Error classifying PDF {pdf_path}: {str(e)}")
            return 'image', 0.5  # Default to image with low confidence

    @staticmethod
    def _extract_text_pdfminer(pdf_path: str) -> str:
        """Extract text using pdfminer for classification"""
        try:
            output = io.StringIO()
            with open(pdf_path, 'rb') as pdf_file:
                extract_text_to_fp(pdf_file, output, laparams=LAParams())
            return output.getvalue()
        except:
            return ""


class PDFTextExtractor:
    """Extracts text from PDFs using multiple methods"""

    @staticmethod
    def extract_text_pymupdf(pdf_path: str) -> Tuple[str, int]:
        """Extract text using PyMuPDF (fitz)"""
        try:
            doc = fitz.open(pdf_path)
            text_chunks = []

            for page_num, page in enumerate(doc):
                try:
                    text = page.get_text()
                    if text.strip():
                        text_chunks.append(f"--- صفحه {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num + 1} from {pdf_path}: {str(e)}")

            page_count = len(doc)
            doc.close()

            return '\n\n'.join(text_chunks), page_count

        except Exception as e:
            logger.error(f"PyMuPDF extraction failed for {pdf_path}: {str(e)}")
            raise

    @staticmethod
    def extract_text_pdfminer_advanced(pdf_path: str) -> str:
        """Advanced text extraction using pdfminer with better layout analysis"""
        try:
            output = io.StringIO()
            with open(pdf_path, 'rb') as pdf_file:
                # Use more aggressive LAParams for better text extraction
                laparams = LAParams(
                    line_overlap=0.5,
                    char_margin=2.0,
                    word_margin=0.1,
                    boxes_flow=0.5
                )
                extract_text_to_fp(pdf_file, output, laparams=laparams)

            return output.getvalue()

        except Exception as e:
            logger.error(f"PDFMiner extraction failed for {pdf_path}: {str(e)}")
            return ""

    @staticmethod
    def extract_text_hybrid(pdf_path: str) -> Tuple[str, int]:
        """Hybrid extraction using both PyMuPDF and pdfminer"""
        # Try PyMuPDF first
        pymupdf_text, page_count = PDFTextExtractor.extract_text_pymupdf(pdf_path)

        # If PyMuPDF gets good results, use it
        if len(pymupdf_text.strip()) > 100:
            return pymupdf_text, page_count

        # Otherwise, try pdfminer
        pdfminer_text = PDFTextExtractor.extract_text_pdfminer_advanced(pdf_path)

        # Use whichever got more text
        if len(pdfminer_text) > len(pymupdf_text):
            return pdfminer_text, page_count

        return pymupdf_text, page_count


class PDFOCRExtractor:
    """Extracts text from image-based PDFs using OCR"""

    # OCR settings
    DPI = 300  # Resolution for PDF to image conversion
    TESSERACT_CONFIG = '--oem 3 --psm 6'  # OCR Engine Mode and Page Segmentation Mode
    MAX_RETRIES = 3

    @classmethod
    def extract_text_ocr(cls, pdf_path: str, retry_count: int = 0) -> Tuple[str, int]:
        """Extract text using OCR (Tesseract with Persian language)"""
        try:
            # Convert PDF pages to images
            logger.info(f"Converting PDF to images for OCR: {pdf_path}")
            images = convert_from_path(pdf_path, dpi=cls.DPI)

            text_chunks = []
            page_count = len(images)

            for i, image in enumerate(images):
                try:
                    # Perform OCR with Persian language
                    text = pytesseract.image_to_string(
                        image,
                        lang='fas',  # Persian language
                        config=cls.TESSERACT_CONFIG
                    )

                    if text.strip():
                        text_chunks.append(f"--- صفحه {i + 1} ---\n{text}")

                    # Log progress for large documents
                    if (i + 1) % 10 == 0:
                        logger.info(f"OCR progress: {i + 1}/{page_count} pages processed")

                except Exception as e:
                    logger.warning(f"OCR failed for page {i + 1} of {pdf_path}: {str(e)}")

                finally:
                    # Clean up image to save memory
                    image.close()

            combined_text = '\n\n'.join(text_chunks)

            # Retry if OCR failed and we haven't exceeded retry limit
            if not combined_text.strip() and retry_count < cls.MAX_RETRIES:
                logger.warning(f"OCR produced no text, retrying... (attempt {retry_count + 1})")
                return cls.extract_text_ocr(pdf_path, retry_count + 1)

            return combined_text, page_count

        except Exception as e:
            logger.error(f"OCR extraction failed for {pdf_path}: {str(e)}")
            if retry_count < cls.MAX_RETRIES:
                logger.info(f"Retrying OCR... (attempt {retry_count + 1})")
                return cls.extract_text_ocr(pdf_path, retry_count + 1)
            raise


class PersianTextValidator:
    """Validates Persian text quality"""

    # Persian Unicode ranges
    PERSIAN_CHARS = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    MIN_PERSIAN_RATIO = 0.3  # Minimum ratio of Persian characters
    MIN_TEXT_LENGTH = 50  # Minimum text length for validation

    @classmethod
    def validate(cls, text: str) -> Tuple[bool, float, str]:
        """
        Validate Persian text quality
        Returns: (is_valid, persian_ratio, validation_message)
        """
        if not text or len(text.strip()) < cls.MIN_TEXT_LENGTH:
            return False, 0.0, "Text too short or empty"

        # Count Persian characters
        persian_chars = len(cls.PERSIAN_CHARS.findall(text))
        total_chars = len(re.findall(r'\w', text))

        if total_chars == 0:
            return False, 0.0, "No word characters found"

        persian_ratio = persian_chars / total_chars

        # Check language detection
        try:
            langs = detect_langs(text[:1000])  # Check first 1000 chars
            lang_dict = {lang.lang: lang.prob for lang in langs}

            # Check if Persian/Farsi is detected
            if 'fa' not in lang_dict and 'ar' not in lang_dict:
                return False, persian_ratio, f"Language detection failed: {lang_dict}"

        except LangDetectException:
            # If language detection fails, rely on character ratio
            pass

        # Validate based on Persian character ratio
        if persian_ratio >= cls.MIN_PERSIAN_RATIO:
            return True, persian_ratio, "Valid Persian text"
        else:
            return False, persian_ratio, f"Low Persian character ratio: {persian_ratio:.2f}"

    @classmethod
    def calculate_quality_score(cls, text: str) -> float:
        """Calculate a quality score for the extracted text (0-1)"""
        if not text:
            return 0.0

        scores = []

        # 1. Persian character ratio
        persian_chars = len(cls.PERSIAN_CHARS.findall(text))
        total_chars = len(text)
        persian_ratio = persian_chars / total_chars if total_chars > 0 else 0
        scores.append(persian_ratio)

        # 2. Text coherence (presence of Persian punctuation)
        persian_punctuation = len(re.findall(r'[،؛؟]', text))
        punctuation_score = min(1.0, persian_punctuation / 100)  # Normalize to 0-1
        scores.append(punctuation_score)

        # 3. Word diversity (unique words / total words)
        words = re.findall(r'\b\w+\b', text)
        if words:
            word_diversity = len(set(words)) / len(words)
            scores.append(word_diversity)

        # 4. Reasonable line lengths (not too many single characters per line)
        lines = text.split('\n')
        reasonable_lines = sum(1 for line in lines if len(line) > 10)
        line_score = reasonable_lines / len(lines) if lines else 0
        scores.append(line_score)

        # Calculate weighted average
        return sum(scores) / len(scores) if scores else 0.0


class PDFToJSONConverter:
    """Main converter class orchestrating the conversion pipeline"""

    def __init__(self, source_dir: str, output_dir: str, max_workers: int = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers or multiprocessing.cpu_count()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'text_pdfs': 0,
            'ocr_pdfs': 0,
            'total_time': 0,
            'failed_files': []
        }

        # Failed files log
        self.failed_log_path = self.source_dir / 'failed_files.log'

    def discover_pdfs(self) -> List[Path]:
        """Discover all PDF files in the source directory"""
        logger.info(f"Scanning directory: {self.source_dir}")
        pdf_files = list(self.source_dir.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_title_from_pdf(self, pdf_path: Path, extracted_text: str) -> str:
        """Extract title from PDF metadata or first page"""
        try:
            # Try to get title from PDF metadata
            doc = fitz.open(str(pdf_path))
            metadata = doc.metadata
            doc.close()

            if metadata and metadata.get('title'):
                return metadata['title']

            # Extract from first lines of text
            lines = extracted_text.split('\n')
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if len(line) > 10 and len(line) < 200:  # Reasonable title length
                    return line

            # Fallback to filename
            return pdf_path.stem

        except:
            return pdf_path.stem

    def process_single_pdf(self, pdf_path: Path) -> Optional[ProcessedDocument]:
        """Process a single PDF file"""
        start_time = time.time()
        pdf_id = pdf_path.stem

        try:
            logger.info(f"Processing: {pdf_path.name}")

            # Calculate file hash
            file_hash = self.calculate_file_hash(pdf_path)

            # Classify PDF
            pdf_type, confidence = PDFClassifier.classify(str(pdf_path))
            logger.info(f"Classified as {pdf_type} PDF (confidence: {confidence:.2f})")

            # Extract text based on type
            if pdf_type == 'text':
                text, page_count = PDFTextExtractor.extract_text_hybrid(str(pdf_path))
                self.stats['text_pdfs'] += 1
            else:
                text, page_count = PDFOCRExtractor.extract_text_ocr(str(pdf_path))
                self.stats['ocr_pdfs'] += 1

            # Normalize text
            normalized_text = PersianTextNormalizer.normalize(text)

            # Validate text
            is_valid, persian_ratio, validation_msg = PersianTextValidator.validate(normalized_text)

            if not is_valid:
                logger.warning(f"Validation failed for {pdf_path.name}: {validation_msg}")
                # Continue processing even if validation fails, but mark status

            # Calculate quality score
            quality_score = PersianTextValidator.calculate_quality_score(normalized_text)

            # Extract title
            title = self.extract_title_from_pdf(pdf_path, normalized_text)

            # Split into chunks (by pages or paragraphs)
            text_chunks = self._create_text_chunks(normalized_text)

            # Create metadata
            metadata = PDFMetadata(
                id=pdf_id,
                source_path=str(pdf_path),
                title=title,
                page_count=page_count,
                type=pdf_type,
                created_at=datetime.now().isoformat(),
                extraction_time=time.time() - start_time,
                language='fa',
                encoder_ready=is_valid and quality_score > 0.5,
                file_hash=file_hash,
                status='success' if is_valid else 'partial',
                error_message=None if is_valid else validation_msg
            )

            # Create processed document
            document = ProcessedDocument(
                id=pdf_id,
                source_path=str(pdf_path),
                title=title,
                text_chunks=text_chunks,
                metadata=metadata
            )

            return document

        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {str(e)}")

            # Create failed metadata
            metadata = PDFMetadata(
                id=pdf_id,
                source_path=str(pdf_path),
                title=pdf_path.stem,
                page_count=0,
                type='unknown',
                created_at=datetime.now().isoformat(),
                extraction_time=time.time() - start_time,
                language='fa',
                encoder_ready=False,
                file_hash=self.calculate_file_hash(pdf_path),
                status='failed',
                error_message=str(e)
            )

            # Record failed file
            self.stats['failed_files'].append({
                'path': str(pdf_path),
                'error': str(e)
            })

            return None

    def _create_text_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        # Split by pages if page markers exist
        if "--- صفحه" in text:
            chunks = re.split(r'--- صفحه \d+ ---', text)
            return [chunk.strip() for chunk in chunks if chunk.strip()]

        # Otherwise, split by paragraphs or size
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def save_document(self, document: ProcessedDocument) -> bool:
        """Save processed document to JSON file"""
        try:
            output_path = self.output_dir / f"{document.id}.json"

            # Convert to dictionary
            doc_dict = {
                'id': document.id,
                'source_path': document.source_path,
                'title': document.title,
                'text_chunks': document.text_chunks,
                'metadata': asdict(document.metadata)
            }

            # Save with proper UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"Failed to save document {document.id}: {str(e)}")
            return False

    def process_batch(self, pdf_files: List[Path]) -> None:
        """Process a batch of PDF files using parallel processing"""
        logger.info(f"Processing {len(pdf_files)} files with {self.max_workers} workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_single_pdf, pdf_path): pdf_path
                for pdf_path in pdf_files
            }

            # Process completed tasks
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                self.stats['processed'] += 1

                try:
                    document = future.result()

                    if document:
                        # Save document
                        if self.save_document(document):
                            self.stats['success'] += 1
                            logger.info(f"Successfully processed: {pdf_path.name}")
                        else:
                            self.stats['failed'] += 1
                    else:
                        self.stats['failed'] += 1

                except Exception as e:
                    logger.error(f"Unexpected error processing {pdf_path.name}: {str(e)}")
                    self.stats['failed'] += 1

                # Log progress
                if self.stats['processed'] % 10 == 0:
                    self._log_progress()

    def _log_progress(self):
        """Log processing progress"""
        success_rate = (self.stats['success'] / self.stats['processed'] * 100) if self.stats['processed'] > 0 else 0
        logger.info(
            f"Progress: {self.stats['processed']}/{self.stats['total_files']} files | "
            f"Success rate: {success_rate:.1f}% | "
            f"Text PDFs: {self.stats['text_pdfs']} | "
            f"OCR PDFs: {self.stats['ocr_pdfs']}"
        )

    def generate_manifest(self) -> None:
        """Generate dataset manifest file"""
        logger.info("Generating dataset manifest...")

        # Collect all processed JSON files
        json_files = list(self.output_dir.glob("*.json"))

        manifest = {
            'dataset_info': {
                'name': 'Persian Law Documents for ParsBERT',
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'source_directory': str(self.source_dir),
                'total_documents': len(json_files),
                'language': 'fa',
                'description': 'Persian law-related documents converted from PDF to JSON for ParsBERT training'
            },
            'statistics': {
                'total_files_scanned': self.stats['total_files'],
                'successfully_processed': self.stats['success'],
                'failed': self.stats['failed'],
                'text_based_pdfs': self.stats['text_pdfs'],
                'ocr_processed_pdfs': self.stats['ocr_pdfs'],
                'success_rate': f"{(self.stats['success'] / self.stats['total_files'] * 100):.1f}%" if self.stats['total_files'] > 0 else "0%"
            },
            'files': []
        }

        # Add file information
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc = json.load(f)

                manifest['files'].append({
                    'filename': json_file.name,
                    'id': doc['id'],
                    'title': doc['title'],
                    'source_pdf': doc['source_path'],
                    'page_count': doc['metadata']['page_count'],
                    'type': doc['metadata']['type'],
                    'encoder_ready': doc['metadata']['encoder_ready']
                })
            except Exception as e:
                logger.warning(f"Error reading {json_file}: {str(e)}")

        # Save manifest
        manifest_path = self.output_dir / 'dataset_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        logger.info(f"Manifest saved to: {manifest_path}")

    def generate_report(self) -> None:
        """Generate final processing report"""
        logger.info("Generating final report...")

        report_lines = [
            "=" * 70,
            "Persian PDF to JSON Conversion Report",
            "=" * 70,
            f"Start Time: {datetime.now().isoformat()}",
            f"Source Directory: {self.source_dir}",
            f"Output Directory: {self.output_dir}",
            "",
            "STATISTICS:",
            f"Total PDFs Found: {self.stats['total_files']}",
            f"Successfully Processed: {self.stats['success']}",
            f"Failed: {self.stats['failed']}",
            f"Success Rate: {(self.stats['success'] / self.stats['total_files'] * 100):.1f}%" if self.stats['total_files'] > 0 else "0%",
            "",
            "PROCESSING BREAKDOWN:",
            f"Text-based PDFs: {self.stats['text_pdfs']}",
            f"OCR-processed PDFs: {self.stats['ocr_pdfs']}",
            f"Average Processing Time: {(self.stats['total_time'] / self.stats['processed']):.2f} seconds" if self.stats['processed'] > 0 else "N/A",
            "",
            "=" * 70
        ]

        # Add failed files section if any
        if self.stats['failed_files']:
            report_lines.extend([
                "",
                "FAILED FILES:",
                "-" * 50
            ])
            for failed in self.stats['failed_files'][:20]:  # Show first 20 failed files
                report_lines.append(f"- {failed['path']}")
                report_lines.append(f"  Error: {failed['error']}")

            if len(self.stats['failed_files']) > 20:
                report_lines.append(f"... and {len(self.stats['failed_files']) - 20} more")

        # Save report
        report_path = self.output_dir / 'training-summary.log'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        # Also save failed files log
        if self.stats['failed_files']:
            with open(self.failed_log_path, 'w', encoding='utf-8') as f:
                json.dump(self.stats['failed_files'], f, ensure_ascii=False, indent=2)

        # Print report to console
        print('\n'.join(report_lines))

        logger.info(f"Report saved to: {report_path}")

    def run(self) -> None:
        """Run the complete conversion pipeline"""
        logger.info("Starting Persian PDF to JSON conversion pipeline...")
        start_time = time.time()

        try:
            # 1. Discover PDFs
            pdf_files = self.discover_pdfs()
            self.stats['total_files'] = len(pdf_files)

            if not pdf_files:
                logger.error("No PDF files found in source directory!")
                return

            # 2. Process PDFs in batches
            self.process_batch(pdf_files)

            # 3. Calculate total time
            self.stats['total_time'] = time.time() - start_time

            # 4. Generate manifest
            self.generate_manifest()

            # 5. Generate report
            self.generate_report()

            # 6. Completion signal
            logger.info("Conversion pipeline completed successfully!")

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    # Configuration
    SOURCE_DIR = "/home/amirxo/Desktop/New Folder 2"
    OUTPUT_DIR = "/home/amirxo/Desktop/ParsBERT_training_dataset"
    MAX_WORKERS = 4  # Number of parallel workers

    # Create and run converter
    converter = PDFToJSONConverter(SOURCE_DIR, OUTPUT_DIR, MAX_WORKERS)
    converter.run()


if __name__ == "__main__":
    main()
