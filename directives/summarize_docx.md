# Directive: Summarize Docx Document

## Goal
Extract text from a `.docx` file and provide a structured summary of its contents.

## Inputs
- `.docx` file path (e.g., `PulseSense1.docx`)

## Tools
- `execution/docx_to_txt.ps1` (for text extraction)

## Output
- Structured summary of the document's content.
- Temporary `.txt` file in `.tmp/` for processing.

## Instructions
1. Run `execution/docx_to_txt.ps1` with the target file as input.
2. Read the resulting `.txt` file from `.tmp/`.
3. Analyze the content and generate a summary covering:
   - Document Type
   - Main Topics
   - Key Requirements/Specifications
   - Action Items (if any)
4. Cleanup temporary files if necessary.
