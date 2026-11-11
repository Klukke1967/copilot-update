#!/usr/bin/env python3
"""
Build Prompts Dataset for AI Intelligence Hub.
Extracts prompts from:
1. organizational-prompts-starter.csv (44 prompts)
2. power-users/README.md (26 prompts)
3. inbox-management-action-mode.md (12 prompts)
4. role-specific/project-leadership.md (18 prompts)
5. Microsoft PnP Community (pnp/copilot-prompts) (Top 50 M365 & Copilot samples)

Total: ~150 curated production-grade prompts structured around the 5-Pillar framework:
1. Vær specifik og præcis
2. Giv kontekst (Baggrund)
3. Tildel en rolle (Persona)
4. Definer ønsket output (Format)
5. Brug eksempler & guardrails
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
    "Outlook Action": "Outlook & Mail-styring",
    "M365 & Samarbejde": "M365 & Samarbejde",
    "PnP Community": "Microsoft PnP Community"
}

TASK_TYPE_DA = {
    "Catch up": "Opsummer (Catch-up)",
    "Create": "Forfat / Opret (Create)",
    "Prepare": "Forberedelse (Prepare)",
    "Analyze": "Analyse (Analyze)",
    "Find": "Søg & Find (Find)"
}

PNP_TOP_SAMPLES = [
    ("m365-actionable-meeting-summary", "M365 & Samarbejde", "Prepare", "Draft Planner Tasks from Meeting Summary"),
    ("m365-7-day-inbox-review-action-framework", "Outlook Action", "Catch up", "7-Day Inbox Review & Action Framework"),
    ("m365-7-day-sent-review-and-remind-action", "Outlook Action", "Find", "7-Day Sent Emails Review & Follow-up"),
    ("m365-analyze-my-week", "Ledelse & Projektledelse", "Analyze", "Analyze My Week: Time & Meeting Audit"),
    ("m365-blocker-finder", "Ledelse & Projektledelse", "Find", "Blocker Finder across Teams & Chats"),
    ("m365-calendar-upcoming-week", "Outlook Action", "Prepare", "Upcoming Week Calendar Preparation"),
    ("m365-change-impacts", "Ledelse & Projektledelse", "Analyze", "Organizational Change Impact Assessment"),
    ("m365-communication-balance-analyzer-prompt", "Ledelse & Projektledelse", "Analyze", "Communication Balance & Responsiveness Analyzer"),
    ("m365-competitor-analysis-report", "Salg & Forretningsudvikling", "Analyze", "Competitor Analysis & Market Intelligence Report"),
    ("m365-compliance-checklist", "IT & Drift", "Prepare", "Governance & Compliance Audit Checklist"),
    ("m365-copilot-as-a-professional-executive-assistant", "Power Users", "Prepare", "Copilot as Executive Assistant: Daily Briefing"),
    ("m365-copilot-as-an-excel-tutor", "Power Users", "Create", "Excel Expert Tutor: Formulas & Pivot Analysis"),
    ("m365-copilot-compare-proposals-on-defined-criteria", "Indkøb & Kontrakter", "Analyze", "Vendor Proposal Comparison on Weighted Criteria"),
    ("m365-decision-log-generator-prompt", "Ledelse & Projektledelse", "Find", "Decision Log Generator from Teams & Meetings"),
    ("m365-define-todays-actions", "Outlook Action", "Catch up", "Define Today's Priority Action Items"),
    ("m365-detailed-agenda-for-upcoming-meeting-prompt", "Ledelse & Projektledelse", "Prepare", "Detailed Agenda Builder for Upcoming Meeting"),
    ("m365-detect-hidden-automation-business", "IT & Drift", "Analyze", "Detect Hidden Workflow Automation Opportunities"),
    ("m365-email-ranking", "Outlook Action", "Analyze", "Urgent & High-Value Email Ranking"),
    ("m365-email-sorting", "Outlook Action", "Catch up", "Inbox Sorting by Action Required vs Info"),
    ("m365-external-stakeholder-meeting-minutes-prompt", "Ledelse & Projektledelse", "Prepare", "External Stakeholder Meeting Minutes & Actions"),
    ("m365-extract-unresolved-issues", "Ledelse & Projektledelse", "Find", "Extract Unresolved Questions from Long Threads"),
    ("m365-find-emails-from-leaders-prompt", "Outlook Action", "Find", "Find & Prioritize Leadership Communications"),
    ("m365-last-7-days-recap", "M365 & Samarbejde", "Catch up", "Last 7 Days Cross-App Activity Recap"),
    ("m365-manage-pending-emails-conversations-prompt", "Outlook Action", "Catch up", "Pending Email Conversations Tracker"),
    ("m365-meeting-action-items-prompt", "M365 & Samarbejde", "Create", "Meeting Action Items Table with Owners"),
    ("m365-meeting-minutes-generator", "M365 & Samarbejde", "Create", "Executive Meeting Minutes Generator"),
    ("m365-meeting-summary-transcript", "M365 & Samarbejde", "Analyze", "Synthesize Teams Meeting Transcript"),
    ("m365-my-name-mentioned-prompt", "M365 & Samarbejde", "Find", "Catch All @Mentions and Action Requests"),
    ("m365-optimize-my-work-schedule", "Power Users", "Prepare", "Optimize Work Schedule for Focus & Deep Work"),
    ("m365-outlook-calendar-analytics", "Outlook Action", "Analyze", "Outlook Calendar Analytics: Meeting Load vs Solo Time"),
    ("m365-outlook-thread-summary", "Outlook Action", "Catch up", "Summarize Massive Email Thread in 3 Bullets"),
    ("m365-planning-kickoff-meeting-minutes-prompt", "Ledelse & Projektledelse", "Prepare", "Project Kickoff Meeting Minutes & Deliverables"),
    ("m365-post-meeting-summary-prompt", "M365 & Samarbejde", "Create", "Post-Meeting Executive Summary Email Draft"),
    ("m365-risk-analysis-meeting-minutes-prompt", "Ledelse & Projektledelse", "Analyze", "Risk & Dependency Analysis from Meeting Notes"),
    ("m365-risk-analysis", "Ledelse & Projektledelse", "Analyze", "Cross-Project Strategic Risk Assessment"),
    ("m365-sharepoint-content-search", "IT & Drift", "Find", "Deep Search Across SharePoint Document Libraries"),
    ("m365-summarise-chat-group-prompt", "M365 & Samarbejde", "Catch up", "Teams Group Chat Discussion Summary"),
    ("m365-task-recovery-assistant", "Power Users", "Find", "Forgotten Task Recovery from Past 14 Days"),
    ("m365-team-retrospective-minutes-prompt", "Ledelse & Projektledelse", "Prepare", "Team Retrospective: What Went Well & Improvements"),
    ("m365-teams-meeting-action-items", "M365 & Samarbejde", "Create", "Teams Meeting Action Items & Deadlines"),
    ("m365-tenant-compliance-and-security-summary-report", "IT & Drift", "Analyze", "Tenant Compliance & Security Executive Report"),
    ("m365-top-5-tasks-of-the-day", "Power Users", "Catch up", "Top 5 High-Impact Tasks of the Day"),
    ("m365-top10_bullet_points_in_document", "Power Users", "Analyze", "Top 10 Executive Key Points in Dense Document"),
    ("m365-upcoming-meeting-prompt", "M365 & Samarbejde", "Prepare", "Upcoming Meeting Preparation & Context Pre-read"),
    ("m365-weekly-highlights-summary", "Ledelse & Projektledelse", "Create", "Weekly Management Highlights & Friday Status"),
    ("m365-work-productivity-and-distractions-check", "Power Users", "Analyze", "Productivity Audit: Meeting Fatigue vs Value"),
    ("m365-wrapup-day-tomo-planner", "Power Users", "Prepare", "End-of-Day Wrapup & Tomorrow's Action Plan"),
    ("m365-yearly-performance-review-prompt", "HR", "Prepare", "Yearly Performance Appraisal & Accomplishment Recap"),
    ("ppt-sales-report-prompt", "Marketing", "Create", "PowerPoint Sales & Performance Deck Generator"),
    ("word-sales-proposal-with-file-reference-prompt", "Sales", "Create", "Word Business Proposal Grounded in Client Files")
]

def clean(text):
    if not text:
        return ""
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def build_pillars(ptext, task_type, dept):
    persona = "AI & M365 Faglig Assistent"
    m_role = re.search(r'(?:Act as my|Act as an?|You are a|You are my)\s+([^.]+)', ptext, re.I)
    if m_role:
        persona = clean(m_role.group(1).split(',')[0])
    elif dept in ["Finance", "Økonomi & Finans"]:
        persona = "FP&A Controller / Finansiel Analytiker"
    elif dept in ["Project Management", "Project Leadership", "Ledelse & Projektledelse"]:
        persona = "Senior Projektleder / PMO Director"
    elif dept in ["IT", "IT & Drift"]:
        persona = "IT Service & Governance Manager"
    elif dept in ["HR", "HR & Personale"]:
        persona = "HR Partner / Organisationskonsulent"
    elif dept in ["Sales", "Salg & Forretningsudvikling"]:
        persona = "B2B Sales Account Strateg"
    elif dept in ["Marketing", "Marketing & Kommunikation"]:
        persona = "Kommunikations- & Content Strateg"
    elif dept in ["Procurement", "Indkøb & Kontrakter"]:
        persona = "Indkøbs- & Kontraktforhandler"
    elif dept in ["Outlook Action", "Outlook & Mail-styring"]:
        persona = "Executive Mail & Triage Assistent"
    elif dept in ["M365 & Samarbejde", "Power Users"]:
        persona = "Microsoft 365 Copilot Power User"

    context = "Søg i seneste e-mails, Teams-chats og SharePoint-filer i organisationen."
    if "teams" in ptext.lower() or "chat" in ptext.lower():
        context = "Teams-kanaler, chat-beskeder og mødereferater i de seneste 7-30 dage."
    elif "planner" in ptext.lower() or "task" in ptext.lower():
        context = "Planner-tavler, Microsoft To Do og tildelte handlingspunkter i workspace."
    elif "excel" in ptext.lower() or "spreadsheet" in ptext.lower():
        context = "Aktive Excel-dataark, pivottabeller og tilknyttede forretningsrapporter."
    elif "calendar" in ptext.lower() or "meeting" in ptext.lower():
        context = "Outlook-kalender, mødeindkaldelser og dagsordener for den aktuelle periode."

    format_out = "Klar punktopstilling med tydelige handlingspunkter og ejere."
    if "table" in ptext.lower():
        format_out = "Struktureret tabel med overskrifter, status og datoer."
    elif "checklist" in ptext.lower():
        format_out = "Tjekliste med afkrydsningsfelter grupperet efter prioritet."
    elif "bullet" in ptext.lower() or "3 bullets" in ptext.lower():
        format_out = "Præcise bullet points med de vigtigste pointer og beslutninger."
    elif "agenda" in ptext.lower():
        format_out = "Tidsopdelt mødedagsorden med formål og forventet output."

    guardrails = "Brug kun fakta fra virksomhedens data. Opfind aldrig aftaler eller tal. Marker usikre punkter med [VERIFICÉR]."

    return {
        "persona": persona,
        "context": context,
        "format": format_out,
        "guardrails": guardrails
    }

def fetch_pnp_prompt(sample_slug):
    url = f"https://raw.githubusercontent.com/pnp/copilot-prompts/main/samples/prompts/{sample_slug}/README.md"
    try:
        content = urllib.request.urlopen(url, timeout=8).read().decode('utf-8')
        m_prompt = re.search(r'##\s+Prompt[^\n]*\n+(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if not m_prompt:
            m_prompt = re.search(r'```(?:markdown|text)?\n(.*?)\n```', content, re.DOTALL)
        prompt_text = m_prompt.group(1).strip() if m_prompt else ""
        prompt_text = re.sub(r'^```[a-z]*\n?', '', prompt_text)
        prompt_text = re.sub(r'\n?```$', '', prompt_text).strip()

        m_desc = re.search(r'##\s+Summary[^\n]*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not m_desc:
            m_desc = re.search(r'###\s+Description[^\n]*\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
        desc = clean(m_desc.group(1).split('\n')[0]) if m_desc else ""
        return prompt_text, desc
    except Exception as e:
        return "", ""

def main():
    all_prompts = []
    p_id = 1

    print("--- 1: Henter 44 prompts fra starter CSV ---")
    try:
        url_csv = "https://raw.githubusercontent.com/kesslernity/awesome-microsoft-copilot-prompts/main/organizational-prompts-import/organizational-prompts-starter.csv"
        content = urllib.request.urlopen(url_csv, timeout=10).read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        for r in reader:
            title = clean(r.get("Title", ""))
            dept = r.get("Department", "Other").strip()
            task_type = r.get("Task Type", "Create").strip()
            desc = clean(r.get("Description", ""))
            ptext = r.get("Prompt Text", "").strip()
            if not title or not ptext:
                continue

            dept_da = DEPT_MAP_DA.get(dept, dept)
            task_da = TASK_TYPE_DA.get(task_type, task_type)
            pillars = build_pillars(ptext, task_type, dept)

            all_prompts.append({
                "id": f"prompt_{p_id:03d}",
                "title": title,
                "department": dept,
                "department_da": dept_da,
                "task_type": task_type,
                "task_type_da": task_da,
                "tool": "Microsoft 365 Copilot",
                "source": "Kesslernity Org Pack",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"Indlæst {len(all_prompts)} fra CSV.")
    except Exception as e:
        print("Fejl ved CSV:", e)

    print("--- 2: Henter Power Users (26 prompts) ---")
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
                "source": "Power User Pack",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Power Users.")
    except Exception as e:
        print("Fejl ved Power Users:", e)

    print("--- 3: Henter Outlook Action Mode (12 prompts) ---")
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
                "source": "Outlook Action Pack",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Outlook Inbox.")
    except Exception as e:
        print("Fejl ved Outlook Inbox:", e)

    print("--- 4: Henter Project Leadership (18 prompts) ---")
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
                "source": "Project Leadership Pack",
                "description": desc,
                "prompt": ptext,
                "pillars": pillars
            })
            p_id += 1
        print(f"I alt {len(all_prompts)} prompts efter Project Leadership.")
    except Exception as e:
        print("Fejl ved Project Leadership:", e)

    print(f"--- 5: Henter Top {len(PNP_TOP_SAMPLES)} prompts fra Microsoft PnP Community ---")
    pnp_success = 0
    for slug, dept, task_type, display_title in PNP_TOP_SAMPLES:
        ptext, desc = fetch_pnp_prompt(slug)
        if not ptext:
            continue
        if len(ptext) < 25:
            continue

        desc = desc or f"M365 Copilot community prompt til {display_title}"
        dept_da = DEPT_MAP_DA.get(dept, dept)
        task_da = TASK_TYPE_DA.get(task_type, task_type)
        pillars = build_pillars(ptext, task_type, dept)

        all_prompts.append({
            "id": f"prompt_{p_id:03d}",
            "title": display_title,
            "department": dept,
            "department_da": dept_da,
            "task_type": task_type,
            "task_type_da": task_da,
            "tool": "Microsoft 365 Copilot",
            "source": "Microsoft PnP Community",
            "description": desc,
            "prompt": ptext,
            "pillars": pillars
        })
        p_id += 1
        pnp_success += 1

    print(f"Indlæst {pnp_success} prompts fra Microsoft PnP.")
    print(f"Samlet antal prompts i biblioteket: {len(all_prompts)}")

    OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    if DIST_OUTPUT_FILE.parent.exists():
        DIST_OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Succes! Gemt {len(all_prompts)} prompts i {OUTPUT_FILE} og dist.")

if __name__ == "__main__":
    main()
