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
    "Excel & Finans": "Excel & Finans",
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

EXCEL_COPILOT_PROMPTS = [
    {
        "title": "Rens og formatér rå finansdata til officiel tabel (tbl_GL)",
        "task_type": "Create",
        "description": "Konverterer ustrukturerede kontoposter til en officiel Ctrl+T tabel (tbl_GL), standardiserer kontonavne til Proper Case og formaterer valuta efter .Rules standarden.",
        "prompt": "Gennemgå det markerede rå kontoudtræk på dette ark. Konverter området til en officiel Excel-tabel navngivet 'tbl_GL'. Standardiser alle kontonavne i kolonnen 'Account Name', så de følger Proper Case uden unødige mellemrum. Formatér kolonnerne 'Actual' og 'Budget' som valuta med formatet '#,##0' (uden valutasymbol og uden decimaler). Tjek om der er en aktiv '.Rules'-fane i projektmappen og efterlev dens formateringsregler. Kør en matematisk verificering på rækkeniveau og bekræft overensstemmelsen."
    },
    {
        "title": "Månedlig variansanalyse mellem Realiseret (Actual) og Budget",
        "task_type": "Analyze",
        "description": "Opretter beregnet varianskolonne og procentvis afvigelse med dynamiske tabelreferencer og betinget formatering af kritiske afvigelser.",
        "prompt": "Tilføj en ny beregnet kolonne 'Variance' til tabellen tbl_GL med den strukturerede formel '=[@Actual]-[@Budget]' samt en kolonne 'Variance %' med formlen '=IFERROR([@Variance]/[@Budget], 0)'. Formatér 'Variance' som '#,##0;(#,##0);\"-\"' og 'Variance %' som '0.0%'. Påfør en blød rød betinget formatering på alle omkostningskonti, hvor den negative afvigelse overstiger 5.000 kr eller 10%. Afslut med en opsummerende Total Row i tabellen, der viser den samlede nettoafvigelse."
    },
    {
        "title": "Automatisk Balance og Resultatopgørelse fra Råbalance (Trial Balance)",
        "task_type": "Create",
        "description": "Opbygger en fuldt forbundet resultatopgørelse og balance fra en kontotabel (tbl_GL) med dynamiske SUMIFS og automatisk balance-check.",
        "prompt": "Opret et nyt faneblad 'Financial Statements' baseret på dataene i tabellen tbl_GL. Opbyg en to-delt finansiel rapport: Øverst en struktureret Balance Sheet (Aktiver opdelt i Cash, A/R, Inventory, Fixed Assets; Passiver opdelt i Forpligtelser og Egenkapital) og nederst en Profit and Loss (Omsætning, Vareforbrug, Bruttoavance, Driftsposter og Nettoresultat). Brug udelukkende strukturerede formler med SUMIFS mod kolonnerne [Bsheet], [PL] og [Amount] frem for statiske celler. Forbind årets resultat direkte fra P&L ind i egenkapitalen på balancen, og indsæt en 'Balance Check' formel der bekræfter at Aktiver = Passiver + Egenkapital (Afvigelse = 0)."
    },
    {
        "title": "Dynamisk kontoplan-opslag med XLOOKUP og fejlsikring",
        "task_type": "Find",
        "description": "Beriger transaktionslinjer med afdelingsnavn, omkostningstype og budgetansvarlig fra en central stamdatatabel uden skrøbelige VLOOKUP-formler.",
        "prompt": "Tilføj en ny kolonne 'Department Lead' til transaktionstabellen tbl_Expenses. Brug en moderne XLOOKUP-formel, der slår kontonummeret [@AcctNum] op i stamdatatabellen tbl_ChartOfAccounts[AcctNum] og returnerer tbl_ChartOfAccounts[Owner]. Hvis et kontonummer ikke findes i kontoplanen, skal formlen returnere '[UKENDT KONTO - TJEK]' i stedet for #N/A fejl. Gennemfør en kontrol og list eventuelle konti, der mangler i stamdata."
    },
    {
        "title": "Multi-kriterie udgiftsdashboard med SUMIFS og dynamiske arrays",
        "task_type": "Analyze",
        "description": "Genererer en matrix-opgørelse over afdelingers udgifter fordelt på kvartaler med dynamiske arrays og SUMIFS aggregering.",
        "prompt": "Byg et separat rapporteringsark 'Dept_Summary', der opsummerer udgifter fra tbl_Expenses. Opret en dynamisk matrix med Afdelinger i rækkerne (hentet unikt via =SORT(UNIQUE(tbl_Expenses[Dept]))) og Kvartaler i kolonnerne (Q1, Q2, Q3, Q4). Fyld cellerne med dynamiske SUMIFS formler, der filtrerer på både afdeling og kvartal: '=SUMIFS(tbl_Expenses[Amount], tbl_Expenses[Dept], $A5, tbl_Expenses[Quarter], B$4)'. Tilføj en række med 'Samlet Udgift' og en kolonne med '% af Total'. Undgå at låse faste rækkenumre; anvend fuld dynamisk tabelreferering."
    },
    {
        "title": "PivotTable og interaktive Slicere til ledelsesrapportering",
        "task_type": "Create",
        "description": "Instruerer Copilot til at oprette en optimeret PivotTable med tidslinje, afdelings-slicere og automatisk top-5 udgiftsanalyse.",
        "prompt": "Generer en PivotTable på et nyt ark med udgangspunkt i tabellen tbl_SalesData. Placer 'Region' og 'Customer Segment' i Rows, 'Product Category' i Columns, og indsæt summen af 'Revenue' og gennemsnittet af 'Margin %' i Values. Formatér tallene som valuta og procent. Tilføj to interaktive Slicere: én for 'Year/Quarter' og én for 'Sales Rep'. Konfigurer PivotTabellen til klassisk tabelvisning uden gentagne overskrifter og skjul tomme celler."
    },
    {
        "title": "Rengøring af sammenkædede kontostrenge og datoer",
        "task_type": "Create",
        "description": "Splitter sammensatte koder (fx '5100-ADMIN-DK'), konverterer tekstformaterede tal og opretter ISO-validerede datokolonner.",
        "prompt": "Inspicér kolonnen 'Raw_String' i tabellen tbl_Import. Kolonnen indeholder data på formatet 'Kontonummer-Afdeling-Landekode' (f.eks. '5200-OPS-DK'). Opret tre nye strukturerede kolonner: 'Account_Code' (de første 4 cifre), 'Department' (teksten mellem bindestregerne) og 'Country' (de sidste to bogstaver). Kontroller desuden kolonnen 'Transaction_Date', og ret eventuelle amerikanske datoer (MM/DD/YYYY) til standard dansk datoformat (DD-MM-YYYY). Verificer at der ikke opstår cirkulære referencer eller fejlbehæftede formler."
    },
    {
        "title": "Finansiel sensitivitetsanalyse og What-If scenariemodel",
        "task_type": "Analyze",
        "description": "Etablerer en 2-vejs sensitivitetsmatrix i Excel, der beregner EBIT ved varierende salgspriser og volumen-vækst.",
        "prompt": "Byg en What-If følsomhedsanalyse for vores budgetmodel på arket 'Scenario_Planning'. Tag udgangspunkt i basismodellen for EBIT. Opret en to-vejs datatabel (Sensitivity Matrix), hvor række-inputtet er ændring i Salgspris (-10%, -5%, 0%, +5%, +10%) og kolonne-inputtet er Volumen-vækst (-15%, -10%, 0%, +10%, +15%). Forbind cellerne til resultatcellen for Årets Resultat. Formatér matricen med en 3-farvet betinget formatering (rød for fald, gul for uændret, grøn for vækst), så ledelsen straks kan aflæse de mest robuste og sårbare udfald."
    },
    {
        "title": "Identifikation af finansielle anomalier, dubletter og usædvanlige posteringer",
        "task_type": "Find",
        "description": "Finder automatisk usædvanlige transaktioner, weekend-posteringer, dublerede bilagsnumre eller beløb over 2,5 standardafvigelser fra middelværdien.",
        "prompt": "Analyser alle transaktionslinjer i tabellen tbl_GeneralLedger for regnskabsåret. Etabler tre automatiske revisions-tjek: 1) Find potentielle dubletter hvor dato, leverandør og beløb er identiske. 2) Marker transaktioner bogført i weekender (=IF(WEEKDAY([@Date], 2)>5, 'Weekend Booking', 'Normal')). 3) Beregn Z-score for transaktionsstørrelser pr. afdeling og marker beløb, der ligger mere end 2,5 standardafvigelser over afdelingens gennemsnit. Saml alle mistænkelige linjer i en overskuelig 'Audit Review' tabel."
    },
    {
        "title": "Beregning af nøgletalskort (Likviditet, Soliditet, ROIC & EBITDA)",
        "task_type": "Analyze",
        "description": "Opbygger en executive nøgletalsoversigt direkte fra balancen og resultatopgørelsen med Benchmark-sammenligning og pæne KPI-kort.",
        "prompt": "Opret et executive KPI-dashboard 'Executive_Ratios' baseret på regnskabstallene i 'Financial Statements'. Beregn følgende nøgletal med eksplicitte formler: 1) Likviditetsgrad (Omsætningsaktiver / Kortfristet gæld), 2) Soliditetsgrad (Egenkapital / Samlede aktiver * 100), 3) EBITDA-margin (EBITDA / Omsætning * 100), og 4) Dækningsgrad. Præsenter hvert nøgletal som et overskueligt KPI-kort med: Nøgletalsnavn, aktuel værdi formateret med rette enhed, målsætning (Benchmark), og en statusindikator ('🟢 På mål', '🟡 Opmærksomhed', '🔴 Kritisk')."
    },
    {
        "title": "Indirekte pengestrømsopgørelse fra Resultatopgørelse og Balanceforskydninger",
        "task_type": "Create",
        "description": "Automatiserer beregningen af drifts-, investerings- og finansieringspengestrømme baseret på to perioders balancer.",
        "prompt": "Udarbejd en indirekte pengestrømsopgørelse på arket 'Cash_Flow' for regnskabsåret. Tag udgangspunkt i Årets Resultat fra tbl_IncomeStatement. Tilbagefør ikke-likvide poster (afskrivninger og hensættelser). Beregn ændringer i arbejdskapital (forskydning i debitorer, varelager og kreditorer mellem 'Balance Sheet 2025' og 'Balance Sheet 2026'). Saml opgørelsen i: 1) Pengestrømme fra driftsaktivitet, 2) Pengestrømme fra investeringsaktivitet, og 3) Pengestrømme fra finansieringsaktivitet. Afslut med en kontrolcelle, der bekræfter at den beregnede nettoændring i likvider svarer præcist til forskydningen på bankkontiene."
    },
    {
        "title": "Opret en autoritativ .Rules fane til styring af Excel Copilot",
        "task_type": "Prepare",
        "description": "Etablerer en fuldstændig .Rules-fane i kolonne A med virksomhedens formaterings-, formel- og rapportkrav til Copilot.",
        "prompt": "Opret en ny fane i denne projektmappe navngivet præcist '.Rules' og sørg for at fanen forbliver synlig. Udfyld kolonne A med vores standarder for Excel Copilot opdelt i sektioner: 'Formatting' (Valuta #,##0 uden symbol/decimaler, tabeller med Ctrl+T og tbl_ præfiks, forbud mod merged cells, brug 'Center Across Selection' ved centrering), 'Formulas' (Foretræk altid XLOOKUP over VLOOKUP, foretræk SUMIFS over SUMIF, brug strukturerede tabelreferencer som [@Felt] frem for cellereferencer), 'Reports' (Foretræk PivotTables til multivariat analyse, placer rapporter på egne ark, medtag altid balance-check), og 'Style Guide' (A1 overskrift 18pt bold, B2 firmanavn 12pt plain, primærfarve #0284C7). Bekræft når fanen er aktiv og klar til brug."
    }
]

OPERATOR_FRAMEWORK_PROMPTS = [
    {
        "title": "Forberedelse til den svære medarbejdersamtale",
        "department": "Ledelse & Projektledelse",
        "task_type": "Prepare",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Giver en direkte og konstruktiv åbningsreplik, to sandsynlige reaktionsmønstre (defensiv vs. modtagelig) med svarmuligheder, samt faldgruber at undgå.",
        "prompt": "Jeg skal have en svær samtale med en kollega/medarbejder om følgende situation: [BESKRIV SITUATION, F.EKS. DEDIKATION, DEADLINES, ADFÆRD ELLER KVALITET]. Giv mig: 1) En direkte åbningsreplik, der er saglig og klar uden at virke anklagende. 2) To sandsynlige måder vedkommende kan reagere på — én defensiv og én modtagelig — samt et konkret forslag til mit opfølgende svar for hver reaktion. 3) Nævn én specifik vending eller fejl, jeg for alt i verden skal undgå at sige, baseret på hvorfor denne type samtaler typisk afspores."
    },
    {
        "title": "Konstruktiv og afbalanceret feedback (under 100 ord)",
        "department": "Ledelse & Projektledelse",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Omformulerer kritisk feedback, så den er 100% ærlig og specifik uden at virke demotiverende eller hård.",
        "prompt": "Jeg skal give følgende feedback til et teammedlem: [BESKRIV FEEDBACK/KRITIKKILDE]. Omformuler min besked, så den er ærlig og præcis, men uden at virke hård eller defensiv. Strukturer svaret stramt i tre punkter: 1) Hvad der fungerer godt pt., 2) Hvad der konkret skal ændres, og 3) Hvorfor ændringen gør en positiv forskel for teamet/projektet. Hold hele formuleringen på under 100 ord."
    },
    {
        "title": "Interviewspørgsmål til dyb adfærdstestning (Stærke vs. svage svar)",
        "department": "HR & Personale",
        "task_type": "Prepare",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "8 målrettede adfærdsspørgsmål der går bag om CV'et og tester reelle kompetencer, inkl. en facitliste over stærke vs. svage svar.",
        "prompt": "Jeg skal interviewe en kandidat til stillingen som [ROLLE/TITEL] hos [VIRKSOMHEDSTYPE]. Generer 8 skarpe interviewspørgsmål, der går dybere end standard-CV'et og tester specifikt for [NØGLEKOMPETENCE/PERSONLIG EGENSKAB, F.EKS. KRISERING, EJERSKAB, PRIORITERING ELLER KONFLIKTHÅNDTERING]. For hvert af de 8 spørgsmål: Beskriv kort hvordan et 'stærkt og troværdigt svar' lyder med konkrete signaler, kontra hvad et 'svagt eller overfladisk svar' indeholder, så jeg ved præcis hvad jeg skal lytte efter under samtalen."
    },
    {
        "title": "Første uges onboarding-guide uden forudsat viden",
        "department": "HR & Personale",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Dag-for-dag tjekliste til nyansatte, der antager 0 kendskab til interne værktøjer, inkl. nøglepersoner og typiske blindgyder.",
        "prompt": "Opret en struktureret onboarding-tjekliste for den første uge for en ny [ROLLE/FUNKTION], der starter på vores hold. Antag at vedkommende har nul kendskab til vores interne systemer, forkortelser og processer. Organiser tjeklisten dag for dag (Dag 1 til Dag 5). Angiv for hver dag: 1) Konkrete opgaver og opsætning, 2) Hvem vedkommende skal mødes med og det præcise formål med mødet, og 3) Flag 2-3 typiske faldgruber eller detaljer, der ofte overses i den første uge."
    },
    {
        "title": "Strategisk beslutningsramme: Option A vs. Option B",
        "department": "Ledelse & Projektledelse",
        "task_type": "Analyze",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Strukturerer svære ledelsesvalg med vejede fordele/ulemper ud fra kernekriterier (omkostning, tid, risiko) og identificerer afgørende manglende information.",
        "prompt": "Jeg skal træffe en strategisk beslutning mellem to spor: [MULIGHED A] og [MULIGHED B] i forbindelse med [KONTEKST/PROJEKT]. Opbyg en neutral analyse: 1) En sammenlignelig liste over fordele og ulemper for hver mulighed. 2) En vægtning af mulighederne ud fra min primære prioritet: [F.EKS. HASTIGHED / OMKOSTNING / DRIFTSSIKKERHED / SKALERBARHED]. 3) Konkluder med hvilken specifik manglende oplysning eller data, der reelt ville kunne tippe beslutningen fra den ene side til den anden."
    },
    {
        "title": "Idéudvidelse: 10 vinkler fra sikre til dristige",
        "department": "Ledelse & Projektledelse",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Genererer 10 innovative variationsvinkler på en idé, rangeret fra pragmatiske til dristige, med succeskriterier for de tre stærkeste.",
        "prompt": "Jeg har følgende grundidé / udfordring: [BESKRIV IDÉ ELLER OPGAVE]. Generer 10 forskellige variationer eller strategiske vinkler på denne idé. Ranger og mærk hver variation inden for tre niveauer: 1) 'Sikker & Pragmatisk' (let at eksekvere med lav risiko), 2) 'Moderat Nytænkende' (kræver visse tilpasninger), og 3) 'Dristig & Utraditionel' (høj risiko/høj gevinst). Udvælg de tre mest lovende vinkler og beskriv for hver, hvilke forudsætninger der absolut skal være til stede, for at den lykkes."
    },
    {
        "title": "Projekt-retrospektiv: Mønster vs. Engangshændelse",
        "department": "Ledelse & Projektledelse",
        "task_type": "Analyze",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Evaluerer et afsluttet projektforløb og adskiller enkeltstående hændelser fra underliggende procesfejl, der kræver systemiske rettelser.",
        "prompt": "Her er hvad der skete under forløbet for [PROJEKTNAVN / LEVERANCE]: [INDSÆT KORT BESKRIVELSE AF FORLØB, UDFORDRINGER OG RESULTAT]. Opbyg et professionelt retrospektiv med tre sektioner: 1) Hvad der fungerede optimalt og skal fastholdes. 2) Hvad der fejlede eller skabte friktion. 3) For hvert problempunkt i del 2: Vurder om der var tale om et 'enkeltstående uheld/engangshændelse' eller et 'systemisk procesmønster', der kræver en varig ændring i vores arbejdsgange. Afslut med 3 konkrete procesforbedringer til næste gang."
    },
    {
        "title": "Hurtig konkurrentsammenligning og differentieringsvinkel",
        "department": "Salg & Forretningsudvikling",
        "task_type": "Analyze",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Opbygger en 4-akset sammenligningsmatrix mod en navngiven konkurrent (pris, funktioner, målgruppe, positionering) og finder den stærkeste salgsvinkel.",
        "prompt": "Jeg skal sammenligne vores [PRODUKT / YDELSE] med konkurrenten [KONKURRENTENS NAVN]. Opbyg en fokuseret sammenligningsmatrix over fire områder: Prissætning, Kernefeatures, Målgruppe og Markedspositionering. Angiv for hvert område, hvor vi er 'Klart foran', 'Klart bagud' eller 'Omtrent lige'. Afslut med at anbefale én skarp differentieringsvinkel, som vores salgs- og marketingbudskaber bør læne sig tungt ind i."
    },
    {
        "title": "Executive Summary: 30-sekunders resumé til topledelsen",
        "department": "Ledelse & Projektledelse",
        "task_type": "Catch up",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Koger et langt dokument eller rapport ned til ét stramt afsnit til en travl beslutningstager med 30 sekunder.",
        "prompt": "Opsummer følgende dokument i ét enkelt, knivskarpt afsnit til en travl topleder, der højst har 30 sekunder til at læse det: [INDSÆT TEKST ELLER DOKUMENTUDDRAG]. Følg denne faste rækkefølge: 1) Start med den absolut vigtigste hovedkonklusion i første sætning. 2) Fremhæv det mest afgørende støtteargument eller datapunkt. 3) Afslut med den præcise beslutning eller handling, der forventes af vedkommende nu. Udelad al generel baggrundshistorie og fyldord."
    },
    {
        "title": "Indvendingshåndtering i 3 niveauer (Fra beroligelse til databevis)",
        "department": "Salg & Forretningsudvikling",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Forbereder 3 distinkte svarniveauer på kundens modstand uden at lyde defensiv, tilpasset kundens skepsisgrad.",
        "prompt": "Jeg pitcher vores [PRODUKT / LØSNING / IDÉ] og forventer modstand/indvendinger om: [BESKRIV TYPISK KUNDEINDVENDING, F.EKS. PRIS, IMPLEMENTERINGSTID ELLER SYSTEMSKIFTE]. Giv mig 3 forskellige måder at imødegå bekymringen direkte uden at lyde defensiv: 1) En hurtig beroligende respons (til den lettere skeptiske kunde), 2) Et relations- og procesorienteret svar (til den tøvende kunde), og 3) Et databaseret og veldokumenteret svar med bevisførelse (til den dybt skeptiske kunde). Forklar kort hvornår hvert svar passer bedst."
    },
    {
        "title": "Kold outreach-besked med lavt pres (under 100 ord)",
        "department": "Salg & Forretningsudvikling",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Ikke-sælgende outreach til LinkedIn eller e-mail med personlig krog og et uforpligtende spørgsmål, der er nemt at sige ja til.",
        "prompt": "Skriv en kort, usælgende henvendelse til en [MÅLPERSONENS ROLLE/BRANCHE] vedrørende [ÅRSAG TIL HENVENDELSE / VÆRDISKABENDE ANLEDNING]. Regler: 1) Hold beskeden på under 100 ord i alt. 2) Åbn med en specifik observation eller reference til vedkommendes arbejde i stedet for en generisk kliché. 3) Undgå aggressivt salgssprog. 4) Afslut med et lavt-pres spørgsmål (et 'low-pressure ask'), som tager under 30 sekunder at besvare og er nemt at sige ja til."
    },
    {
        "title": "Jargon-knuser og forenkling til eksterne modtagere",
        "department": "Marketing & Kommunikation",
        "task_type": "Create",
        "tool": "AI Model Agnostisk (Claude / Copilot / ChatGPT)",
        "source": "Adam Biddlecombe / Operator Framework",
        "description": "Fjerner intern jargon, akronymer og uforståeligt fagsprog fra et dokument, så det kan forstås af enhver uden for branchen.",
        "prompt": "Forenkl denne faglige tekst, så en person uden for vores branche kan forstå den i første gennemlæsning: [INDSÆT TEKST]. Regler: 1) Fjern alle interne akronymer og corporate buzzwords, og erstat dem med klart, jordnært hverdagssprog. 2) Behold samtlige fakta, tal og logiske pointer intakte. 3) Hvis der er et teknisk fagbegreb, som er absolut uundgåeligt, skal du tilføje en forklarende sætning i parentes, der definerer det på et øjeblik."
    }
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
    elif dept in ["Finance", "Økonomi & Finans", "Excel & Finans"]:
        persona = "FP&A Controller / Senior Excel Arkitekt"
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

    print("--- 6: Excel University & Curated Excel Copilot Prompts (12 prompts) ---")
    dept = "Excel & Finans"
    dept_da = "Excel & Finans"
    for item in EXCEL_COPILOT_PROMPTS:
        ptext = item["prompt"]
        task_type = item["task_type"]
        task_da = TASK_TYPE_DA.get(task_type, task_type)
        pillars = build_pillars(ptext, task_type, dept)
        
        all_prompts.append({
            "id": f"prompt_{p_id:03d}",
            "title": item["title"],
            "department": dept,
            "department_da": dept_da,
            "task_type": task_type,
            "task_type_da": task_da,
            "tool": "Microsoft 365 Copilot i Excel",
            "source": "Excel University & M365 Expert",
            "description": item["description"],
            "prompt": ptext,
            "pillars": pillars
        })
        p_id += 1
    print(f"Indlæst {len(EXCEL_COPILOT_PROMPTS)} kuraterede Excel Copilot prompts.")

    print("--- 7: Adam Biddlecombe Operator Framework Prompts (12 prompts) ---")
    for item in OPERATOR_FRAMEWORK_PROMPTS:
        ptext = item["prompt"]
        dept = item["department"]
        dept_da = DEPT_MAP_DA.get(dept, dept)
        task_type = item["task_type"]
        task_da = TASK_TYPE_DA.get(task_type, task_type)
        pillars = build_pillars(ptext, task_type, dept)
        
        all_prompts.append({
            "id": f"prompt_{p_id:03d}",
            "title": item["title"],
            "department": dept,
            "department_da": dept_da,
            "task_type": task_type,
            "task_type_da": task_da,
            "tool": item.get("tool", "AI Model Agnostisk (Claude / Copilot / ChatGPT)"),
            "source": item.get("source", "Adam Biddlecombe / Operator Framework"),
            "description": item["description"],
            "prompt": ptext,
            "pillars": pillars
        })
        p_id += 1
    print(f"Indlæst {len(OPERATOR_FRAMEWORK_PROMPTS)} kuraterede Operator Framework prompts.")
    print(f"Samlet antal prompts i biblioteket: {len(all_prompts)}")

    OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    if DIST_OUTPUT_FILE.parent.exists():
        DIST_OUTPUT_FILE.write_text(json.dumps(all_prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Succes! Gemt {len(all_prompts)} prompts i {OUTPUT_FILE} og dist.")

if __name__ == "__main__":
    main()
