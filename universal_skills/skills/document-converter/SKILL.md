---
name: document-converter
description: Bulk convert office documents (.doc, .docx, .pdf) to Markdown format with high-fidelity formatting preservation. Use when preparing documents for LLM processing, building knowledge bases, or converting legacy document archives. Do NOT use for creating new documents — use document-tools instead.
categories: [Data & Documents]
tags: [pdf, docx, markdown, conversion, document-processing]
---

# Document Converter Skill

This skill provides tools for bulk converting documents (.doc, .docx, .pdf) to Markdown (.md) format while preserving complex formatting like headers, tables, lists, bold, and italics. This is useful for building knowledge bases or preparing documents for LLM processing.

## Tools

### convert_documents
Bulk convert documents in a directory to markdown in an output directory.

#### Arguments
- `--path`: Path to a single file or a directory containing documents.
- `--output-dir`: (Optional) Directory to save the converted markdown files. Defaults to the same directory as the source.
- `--recursive`: (Optional) If set, converts documents in subdirectories as well.

#### Examples
```bash
# Convert a single docx
python scripts/convert.py --path my_doc.docx

# Convert all docs in a folder
python scripts/convert.py --path ./my_docs --output-dir ./markdown_docs

# Convert recursively
python scripts/convert.py --path ./project_docs --recursive
```
