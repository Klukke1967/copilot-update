#!/usr/bin/env python3
"""
Skill Harvester & Indexer for AI Intelligence Hub.
Gathers, validates, and indexes SKILL.md files from:
1. Microsoft PnP Community (pnp/copilot-prompts/samples/skills)
2. Curated Enterprise & M365 Agent Skills (local ~/.hermes/skills)

Generates:
- copilot-dashboard/skills.json (and dist/skills.json) for the web UI
- Installs community skills locally into ~/.hermes/skills/community/ for active agent use
"""

import json
import os
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "skills.json"
DIST_OUTPUT_FILE = ROOT / "dist" / "skills.json"
LOCAL_COMMUNITY_SKILLS_DIR = Path.home() / ".hermes" / "skills" / "community"

def parse_frontmatter(content):
    m = re.match(r'^---\n(.*?)\n---\n*(.*)$', content, re.DOTALL)
    if not m:
        return {}, content
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            if v.startswith('[') and v.endswith(']'):
                v = [x.strip().strip('"\'') for x in v[1:-1].split(',') if x.strip()]
            fm[k] = v
    return fm, body

def clean(text):
    if not text:
        return ""
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

PNP_SKILLS = [
    ("prompt-context-engineer", "Prompt Engineering", "Prompt Context Engineer (Andrej Karpathy Principper)"),
    ("copilot-studio-documenter", "Copilot Studio & Agenter", "Copilot Studio Agent Documenter"),
    ("copilot-studio-eval-test-set", "Copilot Studio & Agenter", "Copilot Studio Evaluation & Benchmark Test Set"),
    ("mcp-server-review", "Udvikling & MCP", "Model Context Protocol (MCP) Server Reviewer"),
    ("weekly-pacing", "Ledelse & Planlægning", "Weekly Pacing & Capacity Orchestration"),
    ("prompt-of-the-week", "Prompt Engineering", "Prompt of the Week Organization Curator"),
    ("api-docs-generator", "Udvikling & MCP", "Enterprise API Docs Generator for AI Integration"),
    ("dataverse-fetchxml-builder", "Power Platform", "Dataverse FetchXML Builder & Query Optimizer"),
    ("powerapps-canvas-yaml-generator", "Power Platform", "Power Apps Canvas YAML Generator"),
    ("self-awareness-review", "Agent Governance", "Agent Self-Awareness & Periodic Reflection"),
    ("code-review-csharp", "Udvikling & MCP", "C# & .NET Senior Code Reviewer"),
    ("photo-booth", "Kreativ AI", "AI Photo Booth & Image Prompt Generator")
]

LOCAL_CURATED_SKILLS = [
    ("excel-copilot-financials", "📊 Excel & Finans", "Excel Copilot Financial Statements Builder (Balance Sheet & P&L)", ROOT / "skills/excel-copilot-financials/SKILL.md"),
    ("excel-copilot-rules-architect", "📊 Excel & Finans", "Excel Copilot .Rules Sheet Architecture & Behavior", ROOT / "skills/excel-copilot-rules-architect/SKILL.md"),
    ("excel-gl-variance-analyzer", "📊 Excel & Finans", "Excel General Ledger & Budget Variance Analyzer", ROOT / "skills/excel-gl-variance-analyzer/SKILL.md"),
    ("excel-copilot-clean-and-transform", "📊 Excel & Finans", "Excel Data Cleaner, Table Staging & Transformation", ROOT / "skills/excel-copilot-clean-and-transform/SKILL.md"),
    ("copilot-excel-skills", "📊 Excel & Finans", "Copilot in Excel Custom Skills Authoring", Path.home() / ".hermes/skills/.archive/copilot-excel-skills/SKILL.md"),
    ("teams-meeting-pipeline", "M365 & Samarbejde", "Teams Meeting Pipeline & Graph Summarizer", Path.home() / ".hermes/skills/.archive/teams-meeting-pipeline/SKILL.md"),
    ("email-inbox-triage", "M365 & Samarbejde", "Executive Email Inbox Triage & Action Sorter", Path.home() / ".hermes/skills/.archive/email-inbox-triage/SKILL.md"),
    ("document-to-action-items", "Ledelse & Planlægning", "Document & Report to Action Items Converter", Path.home() / ".hermes/skills/.archive/document-to-action-items/SKILL.md"),
    ("meeting-action-items", "Ledelse & Planlægning", "Meeting Minutes to Actionable Owner Checklist", Path.home() / ".hermes/skills/.archive/meeting-action-items/SKILL.md"),
    ("weekly-review-planning", "Ledelse & Planlægning", "GTD Weekly Review & Strategic Planning", Path.home() / ".hermes/skills/.archive/weekly-review-planning/SKILL.md"),
    ("powerpoint", "M365 & Samarbejde", "PowerPoint Presentation Deck Builder", Path.home() / ".hermes/skills/.archive/powerpoint/SKILL.md"),
    ("notion", "Produktivitet", "Notion Workspace & Command Center Automation", Path.home() / ".hermes/skills/.archive/notion/SKILL.md"),
    ("hermes-agent-skill-authoring", "Agent Governance", "SKILL.md Authoring Standards & Architecture", Path.home() / ".hermes/skills/.archive/hermes-agent-skill-authoring/SKILL.md"),
    ("one-three-one-rule", "Ledelse & Planlægning", "1-3-1 Decision Briefs: 1 Problem, 3 Options, 1 Pick", Path.home() / ".hermes/skills/communication/one-three-one-rule/SKILL.md")
]

def main():
    skills = []
    print("=== Starter SKILL.md Harvester ===")

    # 1. Fetch Microsoft PnP Skills online
    print("1. Henter Microsoft PnP Community Skills online...")
    LOCAL_COMMUNITY_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    for slug, category, display_title in PNP_SKILLS:
        url = f"https://raw.githubusercontent.com/pnp/copilot-prompts/main/samples/skills/{slug}/SKILL.md"
        try:
            content = urllib.request.urlopen(url, timeout=8).read().decode('utf-8')
            fm, body = parse_frontmatter(content)
            name = fm.get("name", slug)
            desc = clean(fm.get("description", ""))

            # Extract first heading
            m_h1 = re.search(r'^#\s+(.+)$', body, re.M)
            if m_h1:
                h1 = clean(m_h1.group(1))
            else:
                h1 = display_title

            # Save locally in Hermes skills for local agent use (Part C)
            local_target_dir = LOCAL_COMMUNITY_SKILLS_DIR / slug
            local_target_dir.mkdir(parents=True, exist_ok=True)
            (local_target_dir / "SKILL.md").write_text(content, encoding="utf-8")

            skills.append({
                "id": f"skill_{slug}",
                "name": name,
                "title": display_title,
                "category": category,
                "description": desc or f"M365 Copilot skill: {h1}",
                "source": "Microsoft PnP Community",
                "source_url": f"https://github.com/pnp/copilot-prompts/tree/main/samples/skills/{slug}",
                "version": fm.get("version", "1.0.0"),
                "platforms": fm.get("platforms", ["windows", "macos", "m365"]),
                "raw_content": content,
                "file_name": "SKILL.md"
            })
            print(f"  ✓ Hentet PnP skill: {slug} ({len(content)} bytes)")
        except Exception as e:
            print(f"  ✗ Fejl ved PnP skill {slug}: {e}")

    # 2. Add Local Curated Enterprise & M365 Skills
    print("\n2. Indlæser kuraterede enterprise & ledelses-skills...")
    for slug, category, display_title, file_path in LOCAL_CURATED_SKILLS:
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
                name = fm.get("name", slug)
                desc = clean(fm.get("description", ""))

                skills.append({
                    "id": f"skill_{slug}",
                    "name": name,
                    "title": display_title,
                    "category": category,
                    "description": desc or f"Enterprise agent skill: {display_title}",
                    "source": "Enterprise Agent Library",
                    "source_url": "https://copilot.vinverdenenrundt.dk",
                    "version": fm.get("version", "1.0.0"),
                    "platforms": fm.get("platforms", ["windows", "macos", "linux"]),
                    "raw_content": content,
                    "file_name": "SKILL.md"
                })
                print(f"  ✓ Indlæst lokal skill: {slug} ({len(content)} bytes)")
            except Exception as e:
                print(f"  ✗ Fejl ved lokal skill {slug}: {e}")
        else:
            print(f"  - Sprunget over (ikke fundet): {file_path}")

    # Write output to skills.json and dist/skills.json
    OUTPUT_FILE.write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
    if DIST_OUTPUT_FILE.parent.exists():
        DIST_OUTPUT_FILE.write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. Export standalone SKILL.md files and a complete ZIP archive for external use
    import zipfile
    skills_dir = ROOT / "skills"
    dist_skills_dir = ROOT / "dist" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    dist_skills_dir.mkdir(parents=True, exist_ok=True)

    zip_path = ROOT / "skills.zip"
    dist_zip_path = ROOT / "dist" / "skills.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for s in skills:
            slug = s["id"].replace("skill_", "")
            skill_folder = skills_dir / slug
            dist_skill_folder = dist_skills_dir / slug
            skill_folder.mkdir(parents=True, exist_ok=True)
            dist_skill_folder.mkdir(parents=True, exist_ok=True)

            file_content = s["raw_content"]
            (skill_folder / "SKILL.md").write_text(file_content, encoding="utf-8")
            (dist_skill_folder / "SKILL.md").write_text(file_content, encoding="utf-8")

            # Add to ZIP under skills/<slug>/SKILL.md
            zip_out.writestr(f"skills/{slug}/SKILL.md", file_content)

    # Copy ZIP to dist
    if dist_zip_path.parent.exists():
        shutil.copy2(zip_path, dist_zip_path)

    print(f"\nSucces! I alt {len(skills)} SKILL.md filer er høstet, indekseret og gemt i:")
    print(f"- Web UI: {OUTPUT_FILE} & dist/skills.json")
    print(f"- Standalone filer: {skills_dir} og dist/skills/")
    print(f"- Komplet ZIP-arkiv: {zip_path} og dist/skills.zip")
    print(f"- Lokale Hermes skills: {LOCAL_COMMUNITY_SKILLS_DIR}")

if __name__ == "__main__":
    main()
