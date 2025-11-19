#!/usr/bin/env python3
"""
Upload PDF papers to Google File Search for RAG.

This script uploads all PDFs from data/papers/ to Google's File API
for use with the Gemini RAG system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graphrag.google_file_search import GoogleFileSearch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Upload papers to Google File Search."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload PDF papers to Google File Search"
    )
    parser.add_argument(
        "--papers-dir",
        default="data/papers",
        help="Directory containing PDF files (default: data/papers)"
    )
    parser.add_argument(
        "--pattern",
        default="*.pdf",
        help="File pattern to match (default: *.pdf)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List currently uploaded files"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all uploaded files (use with caution!)"
    )

    args = parser.parse_args()

    # Initialize Google File Search
    logger.info("Initializing Google File Search...")
    gfs = GoogleFileSearch()

    # List files if requested
    if args.list:
        files = gfs.list_files()
        logger.info(f"\n{'='*60}")
        logger.info(f"Currently uploaded files: {len(files)}")
        logger.info(f"{'='*60}")
        for i, file in enumerate(files, 1):
            logger.info(f"{i}. {file['display_name']}")
            logger.info(f"   URI: {file['uri']}")
            logger.info(f"   State: {file['state']}")
            logger.info("")
        return

    # Clear files if requested
    if args.clear:
        files = gfs.list_files()
        if not files:
            logger.info("No files to delete.")
            return

        response = input(f"Delete {len(files)} file(s)? This cannot be undone. (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Cancelled.")
            return

        logger.info("Deleting files...")
        for file in files:
            try:
                gfs.delete_file(file['name'])
                logger.info(f"Deleted: {file['display_name']}")
            except Exception as e:
                logger.error(f"Failed to delete {file['display_name']}: {e}")

        logger.info("Done.")
        return

    # Upload files
    papers_path = Path(args.papers_dir)
    if not papers_path.exists():
        logger.error(f"Directory not found: {args.papers_dir}")
        logger.info(f"Please create {args.papers_dir} and add PDF papers.")
        return

    matching_files = list(papers_path.glob(args.pattern))

    if not matching_files:
        logger.warning(f"No files matching '{args.pattern}' found in {args.papers_dir}")
        logger.info(f"Please add PDF papers to {args.papers_dir}")
        return

    logger.info(f"\n{'='*60}")
    logger.info(f"Uploading papers to Google File Search")
    logger.info(f"{'='*60}")
    logger.info(f"Directory: {args.papers_dir}")
    logger.info(f"Pattern: {args.pattern}")
    logger.info(f"Found {len(matching_files)} file(s)")
    logger.info("")

    # Check for existing files
    existing_files = gfs.list_files()
    existing_names = {f['display_name'] for f in existing_files}

    # Upload each file
    uploaded_count = 0
    skipped_count = 0
    failed_count = 0

    for i, file_path in enumerate(matching_files, 1):
        file_name = file_path.name

        # Skip if already uploaded
        if file_name in existing_names:
            logger.info(f"[{i}/{len(matching_files)}] Skipping {file_name} (already uploaded)")
            skipped_count += 1
            continue

        logger.info(f"[{i}/{len(matching_files)}] Uploading: {file_name}")

        try:
            result = gfs.upload_file(str(file_path))
            logger.info(f"  ✓ Success - URI: {result['uri']}")
            uploaded_count += 1

        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            failed_count += 1

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("Upload Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Uploaded: {uploaded_count}")
    logger.info(f"Skipped (already exists): {skipped_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info(f"Total files in Google: {len(gfs.list_files())}")
    logger.info("")

    if uploaded_count > 0:
        logger.info("✓ Papers uploaded successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Run: make web")
        logger.info("  2. Visit http://localhost:8000")
        logger.info("  3. Ask questions using the Google File Search RAG system")


if __name__ == "__main__":
    main()
