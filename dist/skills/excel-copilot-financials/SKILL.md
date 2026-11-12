---
name: excel-copilot-financials
description: Use when the user asks to create, build, or refresh a linked Balance Sheet and Profit and Loss (Income Statement) from a trial balance table in Excel.
version: 1.1.0
author: Excel University & Nous Research
license: MIT
platforms: [excel, m365, windows, macos]
metadata:
  category: "Excel & Finans"
  tags: [excel, copilot, finance, trial-balance, balance-sheet, pnl, structured-references]
---

# Financials Builder (Excel Copilot)
Custom Skill for Microsoft 365 Copilot in Excel: Balance Sheet + Profit and Loss Builder.

Use this skill whenever you need to transform a raw Trial Balance table into a standardized, presentation-ready Balance Sheet and Income Statement (P&L) with automated verification checks.

## When to Use This Skill
Invoke this skill in the Excel Copilot chat pane using `@financials` or standard prompting:
- `@financials create a balance sheet and income statement`
- `@financials build financial statements from this trial balance`
- `@financials refresh financial statements after trial balance update`

## Source Data Requirements
The source worksheet must contain an official Excel Table (`Ctrl+T`) prefixed with `tbl_` (e.g. `tbl_GL` or `tbl_TrialBalance`) with the following explicit columns:
- `AcctNum`: Account number (e.g., 1000, 2000, 4000, 5000)
- `AcctName`: Descriptive account name (e.g., Checking account, Accounts Payable, Revenue)
- `Type`: High-level classification (`Asset`, `Liability`, `Equity`, `Income`, `Expense`)
- `Nature`: Debit or Credit convention (`DR` or `CR`)
- `Bsheet`: Balance sheet line-item mapping tag (e.g., `Cash and Cash Equivalents`, `Accounts Receivable`, `Inventory`, `Fixed Assets`, `Accounts Payable`, `Loans`, `Retained Earnings`)
- `PL`: Profit & Loss line-item mapping tag (e.g., `Revenue`, `Cost of Goods Sold`, `Payroll`, `Office Supplies`, `Sales and Marketing`)
- `Amount`: Net balance amount (positive for Debit, negative for Credit, or standard net convention)

## Execution Rules & Guidelines
1. **Never Hard-Code Row Numbers:** All calculations MUST use structured table references (e.g., `=SUMIFS(tbl_GL[Amount], tbl_GL[PL], D5)`).
2. **Never Wrap Statements in Tables:** Output statements must be formatted as clean financial reporting ranges with standard indentation, not wrapped in Excel tables.
3. **Structured Reference Syntax:**
   - Revenue: `=-SUMIFS(tbl_GL[Amount], tbl_GL[PL], D5)`
   - Cost of Goods Sold: `=SUMIFS(tbl_GL[Amount], tbl_GL[PL], D6)`
   - Gross Profit: `=Revenue - COGS`
   - Net Income: `=Gross_Profit - Operating_Expenses`
4. **Link Net Income into Equity:** The Balance Sheet MUST link current period Net Income directly from the Income Statement (`='Income Statement'!E14`).
5. **Automated Balance Check:** A dedicated `Balance Check` row must be added at the bottom calculating `=Total_Assets - (Total_Liabilities + Total_Equity)`. The result must evaluate to `0`.

## Output Sheet Layout
Create a new worksheet named `Financial Statements` (or `Financial Statements 2` if already present):
- **Title Block:** Cell `A1` with report title in 18pt bold, cell `B2` with company name in 14pt plain.
- **Number Formatting:** Format all currency as `#,##0` (no currency symbol, no decimals). Negative numbers in parentheses `(#,##0)`.
- **Row Architecture:**
  - `Assets`: Cash, A/R, Inventory, Prepaids, Fixed Assets -> Subtotal `Total Assets` (single top border, double bottom accounting border).
  - `Liabilities`: Accounts Payable, Accrued Expenses, Short/Long-term Debt -> Subtotal `Total Liabilities`.
  - `Equity`: Retained Earnings, Current Period Net Income -> Subtotal `Total Equity`.
  - `Total Liabilities and Equity`: Single top border, double bottom accounting border.
  - `Integrity Verification`: Cell formula confirming `Balance Check == 0`.

## Installation into OneDrive for Copilot in Excel
To use this skill natively inside Microsoft 365 Excel:
1. Open your personal or corporate OneDrive.
2. Navigate to: `Documents > Copilot > Microsoft Excel > skills`
3. Create a subfolder named `financials`
4. Save this file as `SKILL.md` inside that folder.
5. In Excel, open Copilot -> **Manage Skills** -> toggle on **financials**.
