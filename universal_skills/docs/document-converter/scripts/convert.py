#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

try:
    import mammoth
    import markdownify
    import pymupdf4llm
    from agent_utilities.base_utilities import get_logger
except ImportError:
    print("Error: Missing required dependencies for the 'document-converter' skill.")
    print(
        "Please install them by running: pip install 'universal-skills[document-converter]'"
    )
    sys.exit(1)

logger = get_logger(__name__)


def convert_docx_to_md(docx_path: Path) -> str:
    """Converts a .docx file to markdown string preserving formatting."""
    with open(docx_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html = result.value
        messages = result.messages
        for message in messages:
            logger.debug(f"Mammoth message: {message}")

        md = markdownify.markdownify(html, heading_style="ATX")
        return md


def convert_pdf_to_md(pdf_path: Path) -> str:
    """Converts a .pdf file to markdown string preserving formatting."""
    return pymupdf4llm.to_markdown(str(pdf_path))


def convert_file(file_path: Path, output_dir: Path) -> bool:
    """Converts a single file to markdown."""
    suffix = file_path.suffix.lower()
    if suffix not in [".docx", ".doc", ".pdf"]:
        return False

    logger.info(f"Converting {file_path}...")
    try:
        if suffix in [".docx", ".doc"]:
            # Note: .doc usually needs something like antiword or pandoc,
            # but python-docx only supports .docx natively.
            # For simplicity, we treat .doc as .docx and let python-docx error if it's actually old .doc
            try:
                content = convert_docx_to_md(file_path)
            except Exception as e:
                logger.error(
                    f"Failed to convert {file_path} (maybe it's an old .doc format?): {e}"
                )
                return False
        elif suffix == ".pdf":
            content = convert_pdf_to_md(file_path)

        output_file = output_dir / f"{file_path.stem}.md"
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"Saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error converting {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Bulk convert documents to Markdown")
    parser.add_argument("--path", required=True, help="Path to file or directory")
    parser.add_argument("--output-dir", "--output_dir", help="Output directory")
    parser.add_argument(
        "--recursive", action="store_true", help="Convert subdirectories"
    )

    args = parser.parse_args()

    source_path = Path(args.path)
    if not source_path.exists():
        logger.error(f"Path not found: {source_path}")
        sys.exit(1)

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else source_path if source_path.is_dir() else source_path.parent
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    if source_path.is_file():
        convert_file(source_path, output_dir)
    else:
        pattern = "**/*" if args.recursive else "*"
        files = [
            f
            for f in source_path.glob(pattern)
            if f.is_file() and f.suffix.lower() in [".docx", ".pdf"]
        ]

        if not files:
            logger.info("No supported documents found.")
            return

        success_count = 0
        for f in files:
            if convert_file(f, output_dir):
                success_count += 1

        logger.info(
            f"Successfully converted {success_count} out of {len(files)} files."
        )


if __name__ == "__main__":
    main()
