#!/usr/bin/env python3
"""
Build Prompts Dataset for AI Intelligence Hub.
Extracts prompts from:
1. organizational-prompts-starter.csv (44 prompts)
2. power-users/README.md (26 prompts)
3. inbox-management-action-mode.md (12 prompts)
4. role-specific/project-leadership.md (18 prompts)

Structures each prompt with Danish translation, Department, Task Type, Persona,
and the 5-Pillar Prompting Framework:
1. Vær specifik og præcis (Goal / Task)
2. Giv kontekst (Background / Data sources)
3. Tildel en rolle (Persona)
4. Definer ønsket output (Format / Structure)
5. Brug eksempler & guardrails (Few-shot / Boundaries)
"""

import csv
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "prompts.json"
DIST_OUTPUT_FILE = ROOT / "dist" / "prompts.json"

DEPT_MAP_DA = {
    "Finance": "Økonomi & Finans",
    "HR": "HR & Personale",
    "Procurement": "Indkøb & Kontrakter",
    "Sales": "Salg & Forretningsudvikling",
    "Marketing": "Marketing & Kommunikation",
    "Customer Success": "Kundesucces & Support",
    "Project Management": "Ledelse & Projektledelse",
    "Project Leadership": "Ledelse & Projektledelse",
    "IT": "IT & Drift",
    "Power Users": "Power User (M365)",
    "Outlook Action": "Outlook & Mail-styring"
}

TASK_TYPE_DA = {
    "Catch up": "Opsummer (Catch-up)",
    "Create": "Forfat / Opret (Create)",
    "Prepare": "Forberedelse (Prepare)",
    "Analyze": "Analyse (Analyze)",
    "Find": "Søg & Find (Find)"
}

def clean(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def build_pillars(ptext, task_type, dept):
    # Persona detection
    persona = "AI & M365 Faglig Assistent"
    m_role = re.search(r'(?:Act as my|Act as an?|You are a|You are my)\s+([^.]+)', ptext, re.I)
    if m_role:
        persona = m_role.group(1).split(',')[0].strip()
    elif dept in ["Finance", "Økonomi & Finans"]:
        persona = "FP&A Controller / Finansiel Analytiker"
    elif dept in ["Project Management", "Project Leadership", "Ledelse & Projektledelse"]:
        persona = "Senior Projektleder / PMO Director"
    elif dept in ["IT", "IT & Drift"]:
        persona = "IT Service Manager / Systemarkitekt"
    elif dept in ["HR", "HR & Personale"]:
        persona = "HR Partner / Organisationskonsulent"
    elif dept in ["Sales", "Salg & Forretningsudvikling"]:
        persona = "B2B Sales Account Strateg"
    elif dept in ["Marketing", "Marketing & Kommunikation"]:
        persona = "Content & Kampagne Strateg"
    elif dept in ["Procurement", "Indkøb & Kontrakter"]:
        persona = "Indkøbs- & Kontraktforhandler"

    # Context detection
    context = "Virksomhedens arbejdsdata, seneste mails, Teams-samtaler og SharePoint-dokumenter."
    if "email" in ptext.lower() or "teams" in ptext.lower():
        context = "Søg i seneste e-mails, Teams-chats og mødenoter om emnet."
    elif "excel" in ptext.lower() or "spreadsheet" in ptext.lower() or "ledger" in ptext.lower():
        context = "Tilknyttede regneark, ERP-udtræk eller GL-posteringer i organisationen."
    elif "report" in ptext.lower() or "deck" in ptext.lower() or "document" in ptext.lower():
        context = "Fremlagte rapporter, mødereferater og PowerPoint-slides i workspace."

    # Format detection
    format_out = "Struktureret overblik i punktopstilling med tydelige handlingspunkter."
    if "table" in ptext.lower():
        format_out = "Overskuelig tabel med relevante kolonner og nøgletal."
    elif "checklist" in ptext.lower():
        format_out = "Klar handlingsrettet tjekliste grupperet efter ansvarlig ejer."
    elif "1." in ptext and "2." in ptext:
        format_out = "Nummereret trin-for-trin disposition med klare overskrifter."
    elif "one-page" in ptext.lower() or "executive" in ptext.lower():
        format_out = "1-sides executive pre-read med ledelsesresumé og åbne spørgsmål."

    # Guardrails
    guardrails = "Arbejd kun ud fra faktiske oplysninger i materialet. Opfind aldrig tal eller datoer. Marker ukendte værdier med [VERIFICÉR]."

    return {
        "persona": persona,
        "context": context,
        "format": format_out,
        "guardrails": guardrails
    }

def main():
    all_prompts = []
    p_id = 1

    print("Henter 1: organizational-prompts-starter.csv...")
    try:
        url_csv = "https://raw.githubusercontent.com/kesslernity/awesome-microsoft-copilot-prompts/main/organizational-prompts-import/organizational-prompts-starter.csv"
        content = urllib.request.urlopen(url_csv, timeout=10).read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        for r in reader:
            title = r.get("Title", "").strip()
            dept = r.get("Department", "Other").strip()
            task_type = r.get("Task Type", "Create").strip()
            desc = r.get("Description", "").strip()
            prompt_text = r.get("Prompt Text", "").strip()
            if not title or not prompt_text:
                continue

            pillars = build_pillars(prompt_text, task_type, dept)
            dept_da = DEPT_MAP_DA.get(dept, dept)
            task_da = TASK_TYPE_DA.get(task_type, task_type)

            all_prompts.append({
                "id": f"prompt_{p_id:03d}",
                "title": title,
                "department": dept,
                "department_da": dept_da,
                "task_type": task_type,
                "task_type_da": task_da,
                "tool": "Microsoft 365 Copilot",
                "description": desc,
                "prompt": prompt_text,
                "pillars": pillars
            })
            p_id += 1
        print(f"Indlæst {len(all_prompts)} fra CSV.")
    except Exception as e:
        print("Fejl ved CSV:", e)

    print("Henter 2: power-users/README.md...")
    try:
        url_pu = "https://raw.githubusercontent.com/kesslernity/awesome-microsoft-copilot-prompts/main/prompts/power-users/README.md"
        txt_pu = urllib.request.urlopen(url_pu, timeout=10).read().decode('utf-8')
        matches = re.findall(r'###\s+\d+\.\s+([^\n]+)\s+\*\*Use Case:\*\*\s+([^\n]+).*?\*\*Prompt:\*\*\s+```(.*?)```', txt_pu, re.DOTALL)
        for t, uc, p in matches:
            title = clean(t)
            desc = clean(uc)
            ptext = p.strip()
            dept = "Power Users"
            task_type = "Analyze" if "predict" in ptext.lower() or "analyz" in ptext.lower() else "Create"
            pillars = build_pillars(ptext, task_type, dept)
            all_prompts.append({
                "id": f"prompt_{p_id:03d}",
                "title": title,
                "department": dept,
                "department_da": DEPT_MAP_DA.get(dept, dept),
                "task_type": task_type,
                "task_type_da": TASK_TYPE_DA.get(task_type, task_type),
                "tool": "Microsoft 365 Copilot (Power User)",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Power Users.")
    except Exception as e:
        print("Fejl ved Power Users:", e)

    print("Henter 3: inbox-management-action-mode.md...")
    try:
        url_inbox = "https://raw.githubusercontent.com/kesslernity/awesome-microsoft-copilot-prompts/main/prompts/outlook/inbox-management-action-mode.md"
        txt_inbox = urllib.request.urlopen(url_inbox, timeout=10).read().decode('utf-8')
        matches = re.findall(r'###\s+\d+\.\s+([^\n]+).*?\*\*Use Case:\*\*\s+([^\n]+).*?\*\*Prompt:\*\*\s+```(.*?)```', txt_inbox, re.DOTALL)
        for t, uc, p in matches:
            title = clean(t)
            desc = clean(uc)
            ptext = p.strip()
            dept = "Outlook Action"
            task_type = "Catch up"
            pillars = build_pillars(ptext, task_type, dept)
            all_prompts.append({
                "id": f"prompt_{p_id:03d}",
                "title": title,
                "department": dept,
                "department_da": DEPT_MAP_DA.get(dept, dept),
                "task_type": task_type,
                "task_type_da": TASK_TYPE_DA.get(task_type, task_type),
                "tool": "Copilot i Outlook",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Outlook Inbox.")
    except Exception as e:
        print("Fejl ved Outlook Inbox:", e)

    print("Henter 4: role-specific/project-leadership.md...")
    try:
        url_pl = "https://raw.githubusercontent.com/kesslernity/awesome-microsoft-copilot-prompts/main/prompts/role-specific/project-leadership.md"
        txt_pl = urllib.request.urlopen(url_pl, timeout=10).read().decode('utf-8')
        matches = re.findall(r'###\s+\d+\.\s+([^\n]+)\n\*\*Use Case:\*\*\s+([^\n]+).*?\*\*Prompt:\*\*\s+```(.*?)```', txt_pl, re.DOTALL)
        for t, uc, p in matches:
            title = clean(t)
            desc = clean(uc)
            ptext = p.strip()
            dept = "Project Leadership"
            task_type = "Prepare" if "prep" in title.lower() or "meet" in title.lower() else "Analyze"
            pillars = build_pillars(ptext, task_type, dept)
            all_prompts.append({
                "id": f"prompt_{p_id:03d}",
                "title": title,
                "department": dept,
                "department_da": DEPT_MAP_DA.get(dept, dept),
                "task_type": task_type,
                "task_type_da": TASK_TYPE_DA.get(task_type, task_type),
                "tool": "Copilot for Ledelse & PM",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Project Leadership.")
    except Exception as e:
        print("Fejl ved Project Leadership:", e)

    OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    if DIST_OUTPUT_FILE.parent.exists():
        DIST_OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Succes! Gemt {len(all_prompts)} prompts i {OUTPUT_FILE} og dist.")

if __name__ == "__main__":
    main()
