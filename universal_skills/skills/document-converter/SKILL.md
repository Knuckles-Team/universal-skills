---
name: document-converter
domain: docs
skill_type: skill
description: >-
  Bulk convert office documents (.doc, .docx, .pdf) to Markdown format with high-
  fidelity formatting preservation. Use when preparing documents for LLM
  processing, building knowledge bases, or converting legacy document archives. Do
  NOT use for creating new documents — use document-tools instead.
license: MIT
tags: [pdf, docx, markdown, conversion, document-processing]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
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

## Steps

1. Locate the inputs by running `ls -R ./my_docs | grep -Ei '\.(doc|docx|pdf)$'`. Verify that the listing shows at least one `.doc`, `.docx` or `.pdf` file.
2. Convert a single file first with `python scripts/convert.py --path my_doc.docx --output-dir ./markdown_docs`. Verify that `ls ./markdown_docs/my_doc.md` exists and `head -20 ./markdown_docs/my_doc.md` shows headings rendered as `#` lines.
3. Run the bulk conversion with `python scripts/convert.py --path ./my_docs --output-dir ./markdown_docs --recursive`. Verify that `find ./markdown_docs -name '*.md' | wc -l` matches the number of source documents found in step 1.
4. Spot-check formatting fidelity with `grep -c '^|' ./markdown_docs/<converted>.md` on a source that contained a table. Verify that the count is above zero and that bold or list markers survived.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `ModuleNotFoundError` when running `scripts/convert.py` | A conversion dependency is not installed in the active interpreter | Read the missing module name from the traceback, install it with `pip install <module>`, and rerun the single-file command from step 2. |
| Output `.md` is empty or has garbled text for a PDF | The PDF is a scanned image with no text layer | Skip the file for this skill, OCR it with `document-tools` (`pytesseract` path), and convert the OCR output. |
| Subdirectory documents are missing from the output | `--recursive` was not passed | Rerun the step 3 command with `--recursive` added and recount with `find ./markdown_docs -name '*.md'`. |
| Legacy `.doc` file fails to convert | The binary format needs LibreOffice to be upgraded to `.docx` first | Run `soffice --headless --convert-to docx <file>.doc` and point `--path` at the resulting `.docx`. |
