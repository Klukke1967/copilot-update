---
name: excel-copilot-rules-architect
description: Use when creating, auditing, or standardizing workbook-scoped .Rules worksheets to control Excel Copilot behavior, formatting, and formulas.
version: 1.0.0
author: Excel University & Nous Research
license: MIT
platforms: [excel, m365, windows, macos]
metadata:
  category: "Excel & Finans"
  tags: [excel, copilot, rules, standards, tables, formulas, formatting, style-guide]
---

# Excel Copilot .Rules Architect
Standardized Workbook Governance & Behavior Control for Microsoft 365 Copilot in Excel.

Use this skill when you want to establish firm, predictable guidelines for how Excel Copilot formats numbers, builds formulas, structures tables, and presents financial data.

## Why Use a .Rules Sheet?
Without explicit instructions, Excel Copilot improvises. A dedicated `.Rules` worksheet provides workbook-scoped guardrails that override generic AI defaults and guarantee that every generated column, summary, or report conforms to your corporate reporting standards.

## Mandatory Technical Requirements for Excel Copilot
1. **Sheet Name:** The sheet must be named exactly `.Rules` (with the leading period).
2. **Column A Placement:** All rules must be written in Column A. Sections can be defined using bold category headers (e.g., `Formatting`, `Formulas`, `Reports`, `Style Guide`).
3. **Visibility:** The `.Rules` worksheet MUST remain visible. If hidden, Copilot ignores it and falls back to global generic defaults.
4. **Natural Language Syntax:** Write rules as imperative statements ("Prefer X over Y", "Never merge cells", "Format currency as...").

## Recommended Core Rule Template (Column A)

```text
Rules for this workbook
[Company Name / Department Standard]

Formatting
- Format currency as #,##0 (no symbol, no decimals unless specifically requested).
- Format negative numbers with parentheses: (#,##0).
- Format percentage columns as 0.0% or 0%.
- Store table-like ranges in official Ctrl+T tables prefixed with tbl_.
- Never merge cells; if centering text over multiple cells is required, use Center Across Selection instead of Merge & Center.
- Avoid full cell fills and heavy dark borders; prefer subtle zebra striping (#F8FAFC) and light horizontal dividers (#E2E8F0).
- Align text columns to the left, numeric data to the right, and dates/codes to the center.

Formulas
- Prefer XLOOKUP over VLOOKUP or INDEX/MATCH.
- Prefer SUMIFS over SUMIF or nested IF statements when building aggregated summaries.
- Always use structured table references (e.g., =[@Actual]-[@Budget]) instead of hard-coded cell coordinates when calculating within tables.
- Prefer modern dynamic array functions (FILTER, UNIQUE, SORT, XLOOKUP, LET) over legacy array formulas (CSE).
- When writing complex calculations, break steps down or use LET() for clarity.

Reports
- Prefer PivotTables for multidimensional summaries and cross-tabulations.
- When generating formula-based financial reports, place summaries on dedicated reporting worksheets separate from raw data tables.
- Always include a data validation or reconciliation row (e.g., Out of Balance check) on financial reports.

Style Guide
- Cell A1 is always the worksheet title (18-point bold, Primary Dark #0F172A).
- Cell B2 is company/organization name (12-point plain, #64748B).
- Primary accent color: #0284C7 (Blue) or #006633 (Corporate Green).
- Subtotal rows use a single top thin border; Grand Total rows use a single top thin border and double bottom accounting border.
```

## How to Prompt Copilot with Rules Active
Once the `.Rules` sheet is in place, prompts can remain concise because the rules handle formatting and structure:
- `"Clean and format the GL sample"`
- `"Add a Variance column comparing Actual to Budget and verify math"`
- `"Build a monthly department expense summary"`
