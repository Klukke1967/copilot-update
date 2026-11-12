---
name: excel-copilot-clean-and-transform
description: Use when cleaning messy Excel data, removing duplicate records, splitting text columns, standardizing formats, and establishing official Excel tables.
version: 1.0.0
author: Excel University & Nous Research
license: MIT
platforms: [excel, m365, windows, macos]
metadata:
  category: "Excel & Finans"
  tags: [excel, copilot, data-cleaning, text-to-columns, deduplication, xlookup, data-types]
---

# Excel Data Cleaner & Transformer
Robust Pre-Processing & Data Cleansing Framework for Microsoft 365 Copilot in Excel.

Use this skill when preparing raw, messy, or externally exported datasets (from ERPs, CRMs, or accounting systems) before running financial analysis or generating reports.

## What this skill covers
- Identifying and eliminating blank rows, phantom spaces, and duplicate records.
- Standardizing casing, date formats (ISO `YYYY-MM-DD` or Danish `DD-MM-YYYY`), and numeric types.
- Parsing concatenated fields (e.g., `5100 - Office Supplies` -> `AcctNum` = `5100`, `AcctName` = `Office Supplies`).
- Converting unstructured ranges into official Excel Tables (`Ctrl+T`) with validated column types.
- Applying modern dynamic lookup formulas (`XLOOKUP`, `FILTER`, `UNIQUE`) to cross-reference master data.

## Standard Cleansing Checklist
1. **Single Header Row Verification:**
   Ensure exactly one header row exists. Remove repeated headers, title blocks, and blank header cells.
2. **Text Sanitation:**
   Trim non-breaking spaces (`=TRIM(CLEAN(SUBSTITUTE(A2, CHAR(160), " ")))`) and convert text-stored numbers to true numeric values (`=VALUE()` or multiplying by 1).
3. **Table Conversion:**
   Assign meaningful names: `tbl_Sales`, `tbl_Employees`, `tbl_Inventory`. Never leave default `Table1`.
4. **Structured Formula Column Additions:**
   When extracting dates, use `=YEAR([@Date])`, `=MONTH([@Date])`, or `=TEXT([@Date], "yyyy-mm")` for reliable grouping in PivotTables.
5. **No Merged Cells:**
   Unmerge any merged cells across the data range; fill down header values if needed for flat tabular integrity.
