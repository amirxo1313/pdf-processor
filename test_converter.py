#!/usr/bin/env python3
"""Test script for Persian PDF to JSON converter"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from persian_pdf_to_json_converter import PDFToJSONConverter, PDFClassifier

def test_small_batch():
    """Test the converter with a small batch of PDFs"""

    # Configuration
    source_dir = "/home/amirxo/Desktop/New Folder 2"

    # Create a temporary test directory
    test_output_dir = tempfile.mkdtemp(prefix="pdf_test_")
    print(f"Test output directory: {test_output_dir}")

    try:
        # Get first 5 PDF files for testing
        pdf_files = list(Path(source_dir).glob("*.pdf"))[:5]

        if not pdf_files:
            print("No PDF files found for testing!")
            return

        print(f"\nTesting with {len(pdf_files)} PDF files:")
        for pdf in pdf_files:
            print(f"- {pdf.name}")

        # Test PDF classification first
        print("\n" + "="*50)
        print("Testing PDF Classification:")
        print("="*50)

        for pdf in pdf_files:
            pdf_type, confidence = PDFClassifier.classify(str(pdf))
            print(f"{pdf.name}: {pdf_type} (confidence: {confidence:.2f})")

        # Create a temporary directory with test PDFs
        test_source_dir = tempfile.mkdtemp(prefix="pdf_source_test_")
        for pdf in pdf_files:
            shutil.copy2(pdf, test_source_dir)

        # Run converter on test batch
        print("\n" + "="*50)
        print("Running Full Conversion Pipeline:")
        print("="*50)

        converter = PDFToJSONConverter(
            source_dir=test_source_dir,
            output_dir=test_output_dir,
            max_workers=2  # Use fewer workers for testing
        )

        converter.run()

        # Check results
        print("\n" + "="*50)
        print("Test Results:")
        print("="*50)

        output_files = list(Path(test_output_dir).glob("*.json"))
        print(f"Generated JSON files: {len(output_files)}")

        # Show sample of first JSON file
        if output_files:
            import json
            with open(output_files[0], 'r', encoding='utf-8') as f:
                sample = json.load(f)
                print(f"\nSample JSON structure from {output_files[0].name}:")
                print(f"- ID: {sample['id']}")
                print(f"- Title: {sample['title']}")
                print(f"- Source: {sample['source_path']}")
                print(f"- Page count: {sample['metadata']['page_count']}")
                print(f"- Type: {sample['metadata']['type']}")
                print(f"- Text chunks: {len(sample['text_chunks'])}")
                if sample['text_chunks']:
                    preview = sample['text_chunks'][0][:200] + "..." if len(sample['text_chunks'][0]) > 200 else sample['text_chunks'][0]
                    print(f"- First chunk preview: {preview}")

        # Clean up temporary source directory
        shutil.rmtree(test_source_dir)

        print(f"\nTest completed! Check output at: {test_output_dir}")
        print("To clean up test output, run:")
        print(f"rm -rf {test_output_dir}")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_small_batch()
