---
name: document-tools
domain: docs
skill_type: skill
description: >-
  Use this skill whenever the user wants to read, edit, analyze, or create document files. This includes PDFs (reading, merging, splitting, OCR, forms, watermarks), Spreadsheets (.xlsx, .csv, DataFrames, formulas with zero errors), Word Documents (.docx), PowerPoint Presentations (.pptx), and Markdown to EPUB conversion.
license: MIT
tags: [documents, pdf, excel, word, powerpoint, csv, epub, ocr, formatting, automation]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# Document Tools

Scope: Use this skill whenever the user wants to read, edit, analyze, or create document files. This includes PDFs (reading, merging, splitting, OCR, forms, watermarks), Spreadsheets (.xlsx, .csv, DataFrames, formulas with zero errors), Word Documents (.docx), PowerPoint Presentations (.pptx), and Markdown to EPUB conversion. Treat this as the primary tool for any standard office file or document formatting/extraction task.

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

## Steps

1. Identify the format of the target with `file <path>` and pick the matching `scripts/` subfolder from the sections above. Verify that the `file` output names PDF, Excel, Word, PowerPoint or Markdown content and that `ls scripts/<format>_scripts` lists the helper scripts.
2. Probe the input before changing it, for example `pdftotext <file>.pdf - | head -40` for PDFs or `python -c "import openpyxl; print(openpyxl.load_workbook('<file>.xlsx').sheetnames)"` for spreadsheets. Verify that the output is readable text or a sheet list, and treat empty PDF output as a scanned document that needs OCR.
3. Perform the edit or creation with the library named for that format (`pypdf`, `openpyxl`, `python-docx`, `python-pptx`, `pypandoc`), keeping existing templates. Verify that the output file exists with `ls -l <output>` and reopens without error in the same library.
4. For spreadsheets, recalculate with `python scripts/xlsx_scripts/recalc.py <file>.xlsx`. Verify that the script reports zero formula errors (`#REF!`, `#DIV/0!`).

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| `pdftotext` returns empty or garbled text | The PDF is a scan with no text layer | Rasterize pages with `pdfimages -png <file>.pdf out` and run `pytesseract` on them, then re-extract. |
| Recalc reports `#REF!` or `#DIV/0!` | A formula points at a deleted cell or an empty denominator | Open the named cell, fix the reference or guard the divisor with `IF`, and rerun `scripts/xlsx_scripts/recalc.py`. |
| `recalc.py` cannot start | LibreOffice is not installed or not on `PATH` | Check `which soffice`, install LibreOffice, and rerun the recalc command. |
| `ImportError` for `docx` or `pptx` | `python-docx` or `python-pptx` missing | Run `pip install python-docx python-pptx` and rerun the script. |
