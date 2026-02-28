---
name: document-tools
description: "Use this skill whenever the user wants to read, edit, analyze, or create document files. This includes PDFs (reading, merging, splitting, OCR, forms, watermarks), Spreadsheets (.xlsx, .csv, DataFrames, formulas with zero errors), Word Documents (.docx), PowerPoint Presentations (.pptx), and Markdown to EPUB conversion. Treat this as the primary tool for any standard office file or document formatting/extraction task."
categories: [Data & Documents]
tags: [documents, pdf, excel, word, powerpoint, csv, epub, ocr, formatting, automation]
---

# Document Tools

## Overview

This skill consolidates capabilities for working with various document and office formats. The underlying scripts from the original individual tools have been preserved in their respective subdirectories under `scripts/`.

## Capabilities/Tools
### 1. PDF Mastery (`scripts/pdf_scripts`)
- **Capabilities**: Read, extract text/tables, merge, split, rotate, add watermarks, create PDFs, fill forms, encrypt/decrypt, and OCR scanned PDFs.
- **Workflow**:
  - For **extraction**: Prefer `pdfplumber` for tables and `pypdf` for metadata.
  - For **creation**: Use `reportlab` for high-fidelity programmatic layout.
  - For **scanned docs**: Always check for image content and trigger OCR if text extraction returns empty or garbled.
- **Libraries**: `pypdf`, `pdfplumber`, `reportlab`, `pytesseract`.
- **Command-Line**: `pdftotext`, `qpdf`, `pdftk`, `pdfimages`.

## 2. Spreadsheet Processing (`scripts/xlsx_scripts`)
- **Capabilities**: Create, read, edit, or analyze `.xlsx`, `.xlsm`, `.csv`, `.tsv`.
- **Requirements**:
  - Always use Excel formulas instead of calculating values in Python and hardcoding them.
  - Deliver zero formula errors (`#REF!`, `#DIV/0!`, etc.).
  - Recalculate formulas using `scripts/xlsx_scripts/recalc.py` which leverages LibreOffice.
- **Libraries**: `pandas`, `openpyxl`.

## 3. Word Document Processing (`scripts/docx_scripts`)
- **Capabilities**: Read, write, and format `.docx` files.
- **Libraries**: `python-docx` (primary for docx), `pypandoc` (for conversions).

## 4. PowerPoint Processing (`scripts/pptx_scripts`)
- **Capabilities**: Automate creation and modification of `.pptx` slides.
- **Libraries**: `python-pptx`.

## 5. EPUB Conversion (`scripts/epub_scripts`)
- **Capabilities**: Convert Markdown files to valid EPUB ebooks.

## General Usage Workflow
1. Identify the document format required by the user.
2. Select the appropriate Python library or CLI tool from the associated `scripts/` subdirectory.
3. Write Python scripts or execute shell commands using the appropriate tool.
4. For complex documents (like Excel with formulas or Word with templates), always respect existing templates and follow strict formatting guidelines.
