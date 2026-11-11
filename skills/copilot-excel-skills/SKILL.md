---
name: copilot-excel-skills
description: Use when authoring or managing Copilot in Excel skills.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    category: productivity
    tags: [excel, copilot, skills, onedrive, skill-md, microsoft-365]
---

# Copilot in Excel Skills

Use this skill when the task is to author, store, validate, enable, or debug custom SKILL.md files for Copilot in Excel.

## What this skill covers

- Building repeatable Excel workflows as skills.
- Storing skills in the OneDrive skills folder Copilot manages.
- Keeping the skill name, folder name, and frontmatter aligned.
- Writing skills that are short, explicit, and easy for Copilot to follow.
- Troubleshooting why a skill is not showing up in Excel.

## Core rules

1. Each skill lives in its own folder.
2. The folder must contain a file named exactly `SKILL.md`.
3. The `name` field in frontmatter must match the folder name.
4. The frontmatter must include at least `name` and `description`.
5. Skills for Excel are currently English-only; the Office display language must be English.
6. After adding or renaming a custom skill, refresh skills in Excel so Copilot recognizes the change.

## Recommended workflow

1. Open Excel and go to Copilot settings.
2. Manage skills -> Custom skills.
3. Create the OneDrive skills folder if it does not exist.
4. Open the skills folder.
5. Create one folder per skill, using a lowercase hyphenated name.
6. Add `SKILL.md` to that folder.
7. Keep the body instructions concise and procedural.
8. Return to Excel and refresh the custom skills list.

## How to write a good skill

Prefer:

- one recurring task per skill
- explicit trigger language in the description
- numbered steps for the procedure
- concrete output requirements
- format rules for headers, tables, formulas, rounding, naming, and sheet layout

Avoid:

- vague prose
- too many unrelated tasks in one skill
- assuming Copilot will infer local conventions
- burying the trigger condition inside the body instead of frontmatter

## Good Excel skill shape

A strong skill usually answers these questions:

- When should Copilot use this skill?
- What exact workbook input does it expect?
- What steps should it follow?
- What must it never change?
- What should the final output look like?

## Pitfalls

- Folder name mismatch: Copilot ignores a folder whose name does not match `name` in `SKILL.md`.
- Missing refresh: newly added or renamed skills may not appear until the list is refreshed.
- Wrong language: English display language is required.
- Overloaded skill: if the file tries to cover too many workflows, it becomes harder for Copilot to follow.

## Support files

- See `references/copilot-excel-skills.md` for the Microsoft-supported structure, examples, and notes.

## Verification

Before considering a skill done, confirm:

- the folder name matches the `name` field
- the file is exactly `SKILL.md`
- the frontmatter is valid YAML
- the description clearly says when to use the skill
- the body contains clear steps and output rules
- the skill is visible in Excel after refresh
