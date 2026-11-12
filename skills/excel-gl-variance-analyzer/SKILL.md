---
name: excel-gl-variance-analyzer
description: Use when analyzing General Ledger data, calculating budget variances, formatting variance columns, and performing automated reconciliation checks in Excel.
version: 1.0.0
author: Excel University & Nous Research
license: MIT
platforms: [excel, m365, windows, macos]
metadata:
  category: "Excel & Finans"
  tags: [excel, copilot, general-ledger, variance-analysis, budget, actual, accounting]
---

# Excel GL Variance Analyzer
Automated General Ledger Analysis & Variance Modeling for Microsoft 365 Copilot in Excel.

Use this skill when analyzing financial datasets containing Actuals, Budgets, and Forecasts to produce standardized variance reports, conditional alert formatting, and audit verifications.

## Core Capabilities
- Converts unformatted GL ranges into structured Excel tables (`tbl_GL`).
- Standardizes account descriptions (Proper Case, trims leading/trailing spaces).
- Adds calculated Variance (`=[@Actual]-[@Budget]`) and Variance % (`=IFERROR([@Variance]/[@Budget], 0)`).
- Applies financial conditional formatting (Red for unfavorable variance, Green for favorable, Gray for neutral).
- Performs automated row-by-row and subtotal verification passes.

## Procedural Workflow
1. **Validation & Table Conversion:**
   Verify whether data is already in an official Excel Table. If not, convert via `Ctrl+T` and name it `tbl_GL` or `tbl_BudgetVariance`.
2. **Account Standardization:**
   Standardize inconsistent account name capitalization (e.g. changing `office SUPPLIES` to `Office Supplies`) using `=PROPER(TRIM([@AccountName]))`.
3. **Variance Logic:**
   - For Expense accounts: `Variance = Budget - Actual` (Positive = Under budget / Favorable).
   - For Revenue accounts: `Variance = Actual - Budget` (Positive = Over budget / Favorable).
   - Alternatively, follow standard financial reporting convention (`Variance = Actual - Budget`) with explicit column header naming: `Variance (Act - Bud)`.
4. **Formatting Standards:**
   - Format numeric columns (`Actual`, `Budget`, `Variance`) as `#,##0` with negative numbers in parentheses `(#,##0)`.
   - Format `Variance %` as `0.0%`.
   - Highlight negative variances exceeding a specified threshold (e.g. > 10% or > $5,000) using soft red fill (`#FEE2E2`) and dark red text (`#991B1B`).
5. **Reconciliation Summary:**
   Insert a total summary row (`Table Design > Total Row`) showing sum of Actuals, sum of Budgets, net Variance, and aggregate Variance %.

## Prompt Examples
- `"Add a Variance column to tbl_GL calculated as [@Actual]-[@Budget] and format as currency #,##0"`
- `"Identify the top 5 expense accounts with unfavorable variance compared to budget"`
- `"Group variance by Department and show both total dollar variance and percentage deviation"`
