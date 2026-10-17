#!/usr/bin/env python3
"""
Value Physics Research Repository — Static Site & HTML Presentation Generator
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation

Dual-Mode Architecture:
1. Primary Source: If `./downloads/` contains raw exported CSVs (deliverables_registry.csv,
   empirical_calibration_data_22_commodities.csv, CHANGELOG.md, pm_master_log.txt),
   it re-parses them and updates `./data/*.json`.
2. Fallback Source: If `./downloads/` is absent (such as in GitHub Actions or a clean clone),
   it seamlessly loads existing `./data/*.json` files to generate all HTML pages.
Zero hardcoded container paths. 100% portable.
"""

import os
import sys
import csv
import json
import re
from reader_generator import generate_all_reader_pages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
raw_dir = os.path.join(BASE_DIR, "raw_downloads")
DOWNLOADS_DIR = raw_dir if os.path.exists(raw_dir) else os.path.join(BASE_DIR, "downloads")

os.makedirs(DATA_DIR, exist_ok=True)

def parse_from_downloads():
    reg_path = os.path.join(DOWNLOADS_DIR, "deliverables_registry.csv")
    comm_files = [f for f in os.listdir(DOWNLOADS_DIR) if f.startswith("empirical_calibration_data_") and f.endswith(".csv")]
    if comm_files:
        comm_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 0, reverse=True)
        comm_path = os.path.join(DOWNLOADS_DIR, comm_files[0])
    else:
        comm_path = os.path.join(DOWNLOADS_DIR, "empirical_calibration_data_22_commodities.csv")
    cl_path = os.path.join(DOWNLOADS_DIR, "CHANGELOG.md")
    pm_log_path = os.path.join(DOWNLOADS_DIR, "pm_master_log.txt")

    if not os.path.exists(reg_path):
        return None

    print(f"Parsing raw CSV and log data from {DOWNLOADS_DIR}...")
    
    # 1. Parse Papers
    papers = []
    with open(reg_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    ws1 = text.split('===== WORKSHEET 2:')[0]
    lines = [l for l in ws1.split('\n') if l.strip()]
    header_idx = -1
    for i, l in enumerate(lines):
        if 'Doc ID' in l and 'Document Title' in l:
            header_idx = i
            break

    reader = csv.reader(lines[header_idx:])
    headers = next(reader)
    for row in reader:
        if row and row[0].startswith('VPE-'):
            doc_id = row[0].strip()
            title = row[1].strip() if len(row) > 1 else ''
            category = row[2].strip() if len(row) > 2 else ''
            scope = row[3].strip() if len(row) > 3 else ''
            status = row[4].strip() if len(row) > 4 else ''
            notebooklm = row[5].strip() if len(row) > 5 else ''
            
            # Resolve actual local repository deliverable file
            deliv_dir = os.path.join(BASE_DIR, "deliverables")
            file_path = ""
            file_ext = ""
            file_size_str = ""
            if os.path.exists(deliv_dir):
                for fname in os.listdir(deliv_dir):
                    if fname.startswith(f"{doc_id}_"):
                        file_path = f"deliverables/{fname}"
                        ext = os.path.splitext(fname)[1].lstrip('.').upper()
                        file_ext = ext if ext else "FILE"
                        fsize = os.path.getsize(os.path.join(deliv_dir, fname))
                        if fsize > 1024 * 1024:
                            file_size_str = f"{fsize / (1024*1024):.1f} MB"
                        else:
                            file_size_str = f"{max(1, fsize // 1024)} KB"
                        break
            
            cat_lower = category.lower()
            if any(k in cat_lower for k in ['treatise', 'foundational', 'foundations', 'theory', 'architecture', 'operating system', 'charter']):
                group = 'Theoretical Treatises'
            elif any(k in cat_lower for k in ['journal', 'preprint', 'manuscript']):
                group = 'Journal Manuscripts'
            elif any(k in cat_lower for k in ['simulation', 'sfc', 'agent-based', 'regional network']):
                group = 'Simulations & SFC Models'
            elif any(k in cat_lower for k in ['empirical', 'case study', 'policy', 'pricing']):
                group = 'Empirical Case Studies'
            elif any(k in cat_lower for k in ['crypto', 'ledger', 'protocol', 'bylaws']):
                group = 'Cryptographic Protocols'
            elif any(k in cat_lower for k in ['code', 'engine', 'script', 'test', 'manifest']):
                group = 'Computational Engines & Code'
            elif any(k in cat_lower for k in ['zenodo', 'distribution']):
                group = 'Zenodo Packages'
            else:
                group = 'Governance & Management'
                
            associated_data = []
            if 'UPE' in scope or 'Universal Price' in title: associated_data.append('Universal Price Equation (UPE) forward pricing formulation')
            if 'Pe' in scope or 'Pb' in scope or '3-layer' in scope: associated_data.append('3-layer biophysical cost breakdown (Pe + Pb + Pm)')
            if 'SFC' in scope or 'Stock-Flow' in title: associated_data.append('156-week SFC matrix calibrated to ABARES/ABS/RBA/ACCC/AEMO')
            if '56-cell' in scope: associated_data.append('56-cell multi-sector input-output supply chain matrix')
            if 'Monte Carlo' in scope: associated_data.append('1,000-run Monte Carlo stress verification')
            if 'Theorem 5' in scope or 'usury' in scope: associated_data.append('Theorem 5 (Non-usurious debt bifurcation & mutual credit)')
            if 'UKF' in scope or 'Kalman' in scope: associated_data.append('High-Order Unscented Kalman Filter (UKF) state observer (Theorem 2.9)')
            if 'LaTeX' in scope or 'pdf' in scope: associated_data.append('Publication-grade LaTeX source tree & camera-ready PDF proof')
            if 'unit tests' in scope or 'tests' in scope: associated_data.append('Automated test suite (24-29 unit tests, 100% pass rate)')
            if '22' in scope or '20' in scope or '14' in scope or 'commodity' in scope: associated_data.append('Real-world commodity calibration microdata (CSV/XLSX)')
                
            papers.append({
                'id': doc_id, 'title': title, 'category': category, 'group': group,
                'scope': scope, 'status': status, 'notebooklm': notebooklm,
                'file_path': file_path, 'file_ext': file_ext, 'file_size': file_size_str,
                'associated_data': associated_data
            })

    # 2. Parse Commodities
    commodities = []
    if os.path.exists(comm_path):
        with open(comm_path, 'r', encoding='utf-8') as f:
            r_dict = csv.DictReader(f)
            for r in r_dict:
                commodities.append({
                    'commodity': r['commodity'].strip(),
                    'unit': r['unit'].strip(),
                    'sector': r['sector'].strip(),
                    'P_obs': float(r['P_retail_observed']),
                    'Pe': float(r['P_energy_Pe']),
                    'Pb': float(r['P_base_Pb']),
                    'U': float(r['Metabolic_U']),
                    'S': float(r['Scarcity_S']),
                    'Rn': float(r['Regen_Capacity_Rn']),
                    'vrel': float(r['Relativistic_Urgency_vrel']),
                    'gamma': float(r['Lorentz_Gamma']),
                    'RRP_D': float(r['RRP_D_recommended']),
                    'Ra': float(r['Implied_Extractive_Drag_Ra']),
                    'premium': float(r['Extractive_Premium_AUD']),
                    'fairness': float(r['Fairness_Index_Percent'])
                })

    # 3. Parse Changelog
    changelog = []
    if os.path.exists(cl_path):
        with open(cl_path, 'r', encoding='utf-8') as f:
            cl_text = f.read()

        sprint_blocks = re.split(r'\n(?=\[[0-9]{4}-[0-9]{2}-[0-9]{2}\])', cl_text)
        for block in sprint_blocks:
            m = re.match(r'\[([0-9]{4}-[0-9]{2}-[0-9]{2})\]\s*-\s*([^\n]+)', block)
            if m:
                date = m.group(1)
                sprint_title = m.group(2).strip()
                body = block[m.end():].strip()
                items = []
                for line in body.split('\n'):
                    line_str = line.strip()
                    if line_str.startswith('* ') or line_str.startswith('- ') or line_str.startswith('• '):
                        items.append(line_str[2:].strip())
                changelog.append({
                    'date': date, 'title': sprint_title, 'raw_content': body, 'summary_items': items[:10]
                })

    # Formal logs from WS2
    ws2_text = text.split('===== WORKSHEET 2: Formal Change Log =====')[1].split('===== WORKSHEET 4:')[0] if '===== WORKSHEET 2:' in text else ''
    ws2_lines = [l for l in ws2_text.split('\n') if l.strip()]
    ws2_reader = csv.reader(ws2_lines)
    ws2_entries = []
    for r in ws2_reader:
        if r and (r[0].startswith('LOG-VPE-') or r[0].startswith('Sprint ')):
            ws2_entries.append({
                'id': r[0].strip(),
                'date': r[1].strip() if len(r) > 1 else '',
                'category': r[3].strip() if len(r) > 3 else '',
                'target': r[4].strip() if len(r) > 4 else '',
                'role': r[5].strip() if len(r) > 5 else '',
                'summary': r[6].strip() if len(r) > 6 else ''
            })

    full_changelog = {
        'sprints': changelog,
        'formal_logs': ws2_entries
    }

    # 4. Parse Daily Updates from PM Master Log
    daily_logs = []
    if os.path.exists(pm_log_path):
        with open(pm_log_path, 'r', encoding='utf-8', errors='ignore') as f:
            pm_text = f.read()

        pattern = r"(?:^|\n)([0-9]+\.\s+(?:Researcher Execution Log|Epistemic Auditor & Checker Verification Log|Project Manager Execution Log|Commercial & Orthodox Linker Review Log|Orthodox Linker Review Log)[^\n]+)"
        matches = list(re.finditer(pattern, pm_text))

        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(pm_text)
            header = m.group(1).strip()
            content = pm_text[start:end].strip()
            
            role = 'Research Triad'
            if 'Researcher' in header: role = 'Lead Researcher'
            elif 'Epistemic Auditor' in header or 'Checker' in header: role = 'Epistemic Auditor & Checker'
            elif 'Project Manager' in header: role = 'Project Manager'
            elif 'Linker' in header: role = 'Commercial & Orthodox Linker'
                
            sprint_match = re.search(r"Sprint\s+([0-9]+(?:\.[0-9]+)*)", header)
            sprint = sprint_match.group(0) if sprint_match else "Sprint"
            
            date_match = re.search(r"(2026-10-[0-9]{2}|2026-09-[0-9]{2}|2026-08-[0-9]{2})", content[:1500])
            date = date_match.group(1) if date_match else ""
            if not date:
                if "18.5" in sprint: date = "2026-10-11"
                elif "18.4" in sprint: date = "2026-10-10"
                elif "18.3" in sprint: date = "2026-10-09"
                elif "18.2" in sprint: date = "2026-10-08"
                elif "17.8" in sprint: date = "2026-10-08"
                elif "17.6" in sprint: date = "2026-10-07"
                elif "17.5" in sprint: date = "2026-10-06"
                elif "17.4" in sprint: date = "2026-10-06"
                elif "17.3" in sprint: date = "2026-10-05"
                elif "17.2" in sprint: date = "2026-10-04"
                elif "17.1" in sprint: date = "2026-10-03"
                elif "17.0" in sprint: date = "2026-10-03"
                elif "16." in sprint: date = "2026-09-28"
                elif "15." in sprint: date = "2026-09-21"
                elif "13." in sprint: date = "2026-09-14"
                elif "11." in sprint: date = "2026-09-07"
                else: date = "2026-08-28"
                
            points = []
            lines = content.split('\n')
            for line in lines[1:40]:
                l_str = line.strip()
                if (l_str.startswith('*') or l_str.startswith('-') or l_str.startswith('•') or re.match(r'^[0-9]+\.', l_str)) and len(l_str) > 10:
                    clean_l = re.sub(r'^[*•\-\s0-9.]+', '', l_str).strip()
                    if clean_l and not clean_l.startswith('http'):
                        points.append(clean_l)
                        if len(points) >= 6: break
                            
            daily_logs.append({
                'id': f"LOG-{i+1:03d}",
                'header': header,
                'role': role,
                'sprint': sprint,
                'date': date,
                'key_takeaways': points[:5],
                'full_text_preview': content[:1200]
            })

        daily_logs.sort(key=lambda x: (x['date'], x['sprint']), reverse=True)

    # 5. Weekly Summaries
    weekly_summaries = [
        {
            "week_number": "Week 7 (Current)",
            "date_range": "2026-10-05 to 2026-10-11",
            "title": "The Great 22-Commodity Empirical Expansion & Governance Treatise Lockdown",
            "sprints": ["Sprint 17.3", "Sprint 17.4", "Sprint 17.5", "Sprint 17.6", "Sprint 17.8", "Sprint 18.2", "Sprint 18.3", "Sprint 18.4", "Sprint 18.5"],
            "milestones": [
                "Expanded real-world empirical pricing matrix from 10 to 22 commodities, adding Broiler Chicken, Extruded Clay Bricks, Solar Sea Salt, and Raw Cane Sugar.",
                "Commissioned, authored, and deployed Master Treatise VPE-60: The Architecture of Autonomous Econophysics.",
                "Locked down dedicated Zenodo publication release folders for VPE-55, VPE-21, and VPE-49 with camera-ready PDF proofs, LaTeX source trees, and manifests.",
                "Maintained 100% automated test suite pass rate: 24/24 unit tests in test_value_physics.py and 9/9 tests in test_rrp_fairness_audit.py.",
                "Verified 156/156 weekly Stock-Flow Consistent balance sheet closures and 1,000/1,000 Monte Carlo boundary iterations."
            ],
            "system_health": "A+ Institutional Grade. Zero floating-point truncation, strict file extension hygiene, 60 registered deliverables verified."
        },
        {
            "week_number": "Week 6",
            "date_range": "2026-09-28 to 2026-10-04",
            "title": "Strategic Pivot to Real-World Pricing & RRP/D Fairness Engine Genesis",
            "sprints": ["Sprint 16.5", "Sprint 17.0", "Sprint 17.1", "Sprint 17.2"],
            "milestones": [
                "Executed strategic schedule prompt pivot: re-aligned all autonomous Spark schedules from abstract paper expansion to direct empirical testing of the Universal Price Equation (UPE).",
                "Built and deployed standalone executable forward pricing engine upe_pricing_engine.py (VPE-53).",
                "Deployed standalone RRP fairness audit solver rrp_fairness_audit.py (VPE-54) and calibrated initial 6 Australian commodities.",
                "Authored and published initial draft of Empirical Case Study Treatise (VPE-55), establishing the Biophysical Fairness Index metric."
            ],
            "system_health": "Transition complete. Standalone Python solvers decoupled from document bodies."
        },
        {
            "week_number": "Week 5",
            "date_range": "2026-09-21 to 2026-09-27",
            "title": "Multi-Village Regional Network Simulation & Inter-Sovereign Trade Tensor Clearing",
            "sprints": ["Sprint 15.1", "Sprint 15.2", "Sprint 16.0", "Sprint 16.4"],
            "milestones": [
                "Completed 156-week dynamic simulation across 10 Warrumbungle-Orana local government areas (ARI-VPE-SIM-2026-02, VPE-22).",
                "Simulated 6,500 citizens and 70 enterprises under a 30-week severe compound drought (50% yield collapse, $2.40/L diesel spike).",
                "Demonstrated stability of decentralized mutual credit clearing and non-usurious zero-interest reserve mechanics (WEST reserves +42.0M).",
                "Verified regional bread price invariance at $1.15 baseline under local currency clearing."
            ],
            "system_health": "Simulation closed and validated. 156-week balance sheets verified with zero discrepancy."
        },
        {
            "week_number": "Week 4",
            "date_range": "2026-09-14 to 2026-09-20",
            "title": "Academic Journal Manuscript Package Lockdown & High-Order UKF Observer",
            "sprints": ["Sprint 13.5", "Sprint 14.0", "Sprint 14.5", "Sprint 15.0"],
            "milestones": [
                "Completed consolidated journal submission manuscript VPE-21 (The Physics of Economic Value) targeted at Ecological Economics.",
                "Formulated and proved Theorem 2.9 (High-Order Unscented Kalman Filter State Observer) for non-linear latent state estimation.",
                "Compiled 15-page camera-ready PDF proof under Elsevier elsarticle.cls with 0 errors.",
                "Assembled complete open-science replication package (vpe21_latex_package.zip) with test_value_physics.py test harness."
            ],
            "system_health": "Verified zero-error LaTeX compilation pass. Unconditional publication clearance."
        },
        {
            "week_number": "Week 3",
            "date_range": "2026-09-07 to 2026-09-13",
            "title": "Thermodynamic Work-Antiwork State-Space Dynamics & Heterodox Synthesis",
            "sprints": ["Sprint 11.2", "Sprint 12.0", "Sprint 13.0", "Sprint 13.4"],
            "milestones": [
                "Authored and formalized master theoretical treatise VPE-49: Thermodynamic Work-Antiwork State-Space Dynamics.",
                "Proved Norm Isometry Theorem (Theorem 1) establishing distance preservation in 45-degree Diamond Phase Space (P, A).",
                "Proved Passivity Asymmetry Theorem (Theorem 2) and Autonomous Sclerosis Blowup Theorem.",
                "Formally dissolved the Cambridge Capital Controversy by establishing dimensional separation between physical capital (W_p) and financial debt claims (A_p)."
            ],
            "system_health": "Mathematical proofs verified. Lyapunov invariant stability envelope V(x, y) <= 1 established."
        },
        {
            "week_number": "Week 2",
            "date_range": "2026-08-31 to 2026-09-06",
            "title": "Cohesive Village Simulation & The Economics and Value Physics of Bread",
            "sprints": ["Sprint 8.1", "Sprint 9.0", "Sprint 10.0", "Sprint 11.1"],
            "milestones": [
                "Calibrated 600-citizen village micro-economy across 7 occupational guilds (VPE-11).",
                "Published empirical price audit on commercial sliced bread (VPE-10), uncovering the 5 transmission channels of interest rate cost-push inflation.",
                "Formulated 56-cell multi-sector supply chain matrix across 5 vital human provisioning sectors."
            ],
            "system_health": "Stock-flow consistent accounting balance achieved across all 7 guilds."
        },
        {
            "week_number": "Week 1",
            "date_range": "2026-08-24 to 2026-08-30",
            "title": "Foundational Axioms, Cardinal Token Geometry & Tri-Fold Cryptographic Ledger",
            "sprints": ["Sprint 1.0", "Sprint 2.0", "Sprint 5.0", "Sprint 7.4"],
            "milestones": [
                "Formalized the Cardinal Value Matrix: WEST, EAST, BEST, WORST token geometry (VPE-05).",
                "Developed the 7-Plane Token Spectrum Architecture (VPE-06) and Reciprocal Closure Law.",
                "Engineered the Tri-Fold Cryptographic Ledger whitepaper (VPE-02) featuring Proof-of-Difficulty (PoD) consensus.",
                "Established Master Deliverables Registry and canonical Excel ledger (VPE-15)."
            ],
            "system_health": "Foundational repository established. Alethekanon Research Institute charter ratified."
        }
    ]

    # Save to data directory
    with open(os.path.join(DATA_DIR, "papers.json"), "w") as f: json.dump(papers, f, indent=2)
    with open(os.path.join(DATA_DIR, "commodities.json"), "w") as f: json.dump(commodities, f, indent=2)
    with open(os.path.join(DATA_DIR, "changelog.json"), "w") as f: json.dump(full_changelog, f, indent=2)
    with open(os.path.join(DATA_DIR, "daily_updates.json"), "w") as f: json.dump(daily_logs, f, indent=2)
    with open(os.path.join(DATA_DIR, "weekly_summaries.json"), "w") as f: json.dump(weekly_summaries, f, indent=2)

    return papers, commodities, full_changelog, daily_logs, weekly_summaries

def load_from_json():
    print(f"Loading existing structured JSON datasets from {DATA_DIR}...")
    papers_path = os.path.join(DATA_DIR, "papers.json")
    comm_path = os.path.join(DATA_DIR, "commodities.json")
    cl_path = os.path.join(DATA_DIR, "changelog.json")
    daily_path = os.path.join(DATA_DIR, "daily_updates.json")
    weekly_path = os.path.join(DATA_DIR, "weekly_summaries.json")

    if not os.path.exists(papers_path):
        raise FileNotFoundError(f"Missing required data file: {papers_path}")

    with open(papers_path) as f: papers = json.load(f)
    with open(comm_path) as f: commodities = json.load(f) if os.path.exists(comm_path) else []
    with open(cl_path) as f: full_changelog = json.load(f) if os.path.exists(cl_path) else {'sprints': [], 'formal_logs': []}
    with open(daily_path) as f: daily_logs = json.load(f) if os.path.exists(daily_path) else []
    with open(weekly_path) as f: weekly_summaries = json.load(f) if os.path.exists(weekly_path) else []

    return papers, commodities, full_changelog, daily_logs, weekly_summaries

def generate_html_files(papers, commodities, full_changelog, daily_logs, weekly_summaries):
    print("Compiling responsive HTML presentation suite...")

    papers_js = json.dumps(papers)
    commodities_js = json.dumps(commodities)
    changelog_js = json.dumps(full_changelog)
    daily_updates_js = json.dumps(daily_logs)
    weekly_summaries_js = json.dumps(weekly_summaries)

    SHARED_CSS = """
:root {
  --bg-primary: #0a0e17;
  --bg-secondary: #121824;
  --bg-tertiary: #1a2234;
  --bg-card: rgba(26, 34, 52, 0.75);
  --border-color: rgba(255, 255, 255, 0.08);
  --border-active: rgba(0, 212, 255, 0.4);
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  --accent-cyan: #00d4ff;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-gold: #f59e0b;
  --accent-emerald: #10b981;
  --accent-rose: #f43f5e;
  --glow-cyan: 0 0 20px rgba(0, 212, 255, 0.2);
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  --font-serif: 'Newsreader', 'Georgia', serif;
}

[data-theme="light"] {
  --bg-primary: #f8fafc;
  --bg-secondary: #ffffff;
  --bg-tertiary: #f1f5f9;
  --bg-card: rgba(255, 255, 255, 0.85);
  --border-color: rgba(0, 0, 0, 0.08);
  --border-active: rgba(0, 150, 255, 0.4);
  --text-main: #0f172a;
  --text-muted: #475569;
  --text-dim: #94a3b8;
  --accent-cyan: #0284c7;
  --accent-blue: #2563eb;
  --accent-purple: #7c3aed;
  --accent-gold: #d97706;
  --accent-emerald: #059669;
  --accent-rose: #e11d48;
  --glow-cyan: 0 0 20px rgba(2, 132, 199, 0.15);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background-color: var(--bg-primary);
  color: var(--text-main);
  font-family: var(--font-sans);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  min-height: 100vh;
}

a { color: var(--accent-cyan); text-decoration: none; transition: all 0.2s; }
a:hover { text-decoration: underline; color: #38bdf8; }

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
  background: rgba(10, 14, 23, 0.85);
  border-bottom: 1px solid var(--border-color);
  padding: 0.75rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
[data-theme="light"] .navbar { background: rgba(255, 255, 255, 0.85); }

.brand { display: flex; align-items: center; gap: 1rem; }
.brand-logo {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 1.1rem; color: #000;
  box-shadow: var(--glow-cyan);
}
.brand-text h1 {
  font-size: 1.15rem; font-weight: 700;
  letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.5rem;
}
.brand-text p {
  font-size: 0.75rem; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.05em;
}

.nav-links { display: flex; align-items: center; gap: 0.5rem; list-style: none; }
.nav-link {
  padding: 0.5rem 0.9rem; border-radius: 6px;
  font-size: 0.85rem; font-weight: 500; color: var(--text-muted);
  transition: all 0.2s; cursor: pointer; border: 1px solid transparent;
}
.nav-link:hover, .nav-link.active {
  color: var(--text-main); background: var(--bg-tertiary); border-color: var(--border-color);
}
.nav-link.active { border-color: var(--accent-cyan); color: var(--accent-cyan); }

.nav-actions { display: flex; align-items: center; gap: 0.75rem; }
.badge-status {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.3rem 0.75rem; border-radius: 9999px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: var(--accent-emerald);
  font-size: 0.75rem; font-weight: 600; font-family: var(--font-mono);
}
.pulse-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background-color: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.theme-toggle-btn {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 0.4rem 0.75rem; border-radius: 6px;
  cursor: pointer; font-size: 0.85rem;
}
.theme-toggle-btn:hover { color: var(--text-main); }

.container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
.hero { margin-bottom: 2.5rem; }
.hero-title {
  font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #ffffff 40%, var(--accent-cyan) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
[data-theme="light"] .hero-title {
  background: linear-gradient(135deg, #0f172a 40%, var(--accent-cyan) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-subtitle { font-size: 1.05rem; color: var(--text-muted); max-width: 900px; line-height: 1.6; }

.stats-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem; margin-top: 1.5rem; margin-bottom: 2rem;
}
.stat-card {
  background: var(--bg-card); backdrop-filter: blur(8px);
  border: 1px solid var(--border-color); border-radius: 10px;
  padding: 1.25rem; transition: transform 0.2s, border-color 0.2s;
}
.stat-card:hover { transform: translateY(-2px); border-color: var(--border-active); }
.stat-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 0.35rem; }
.stat-val { font-size: 1.75rem; font-weight: 800; font-family: var(--font-mono); color: var(--text-main); }
.stat-val.cyan { color: var(--accent-cyan); }
.stat-val.gold { color: var(--accent-gold); }
.stat-val.emerald { color: var(--accent-emerald); }
.stat-val.purple { color: var(--accent-purple); }
.stat-sub { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; }

.tab-content { display: none; }
.tab-content.active { display: block; animation: fadeIn 0.25s ease-in; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

.section-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem;
}
.section-title { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; }

.filter-bar {
  background: var(--bg-card); border: 1px solid var(--border-color);
  border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem;
  display: flex; flex-direction: column; gap: 0.85rem;
}
.filter-row { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }
.search-input {
  flex: 1; min-width: 250px; background: var(--bg-tertiary);
  border: 1px solid var(--border-color); border-radius: 6px;
  padding: 0.6rem 1rem; color: var(--text-main); font-size: 0.9rem; outline: none;
}
.search-input:focus { border-color: var(--accent-cyan); }
.filter-pills { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.pill {
  padding: 0.3rem 0.75rem; border-radius: 9999px;
  font-size: 0.75rem; font-weight: 600; cursor: pointer;
  background: var(--bg-tertiary); border: 1px solid var(--border-color);
  color: var(--text-muted); transition: all 0.15s;
}
.pill:hover, .pill.active {
  background: rgba(0, 212, 255, 0.15); border-color: var(--accent-cyan); color: var(--accent-cyan);
}

.papers-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 1.25rem; }
.paper-card {
  background: var(--bg-card); backdrop-filter: blur(8px);
  border: 1px solid var(--border-color); border-radius: 10px;
  padding: 1.4rem; display: flex; flex-direction: column; justify-content: space-between;
  transition: all 0.2s; cursor: pointer; position: relative;
}
.paper-card:hover {
  border-color: var(--accent-cyan); transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}
.paper-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.75rem; }
.paper-id {
  font-family: var(--font-mono); font-weight: 700; font-size: 0.85rem;
  color: var(--accent-cyan); background: rgba(0, 212, 255, 0.1);
  padding: 0.2rem 0.5rem; border-radius: 4px;
}
.paper-status {
  font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 4px;
  background: rgba(16, 185, 129, 0.1); color: var(--accent-emerald);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.paper-title { font-size: 1.05rem; font-weight: 700; line-height: 1.4; margin-bottom: 0.5rem; color: var(--text-main); }
.paper-cat { font-size: 0.75rem; color: var(--accent-gold); margin-bottom: 0.75rem; font-weight: 600; }
.paper-scope {
  font-size: 0.825rem; color: var(--text-muted); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 1rem;
}
.paper-footer {
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid var(--border-color); padding-top: 0.75rem; font-size: 0.75rem;
}

.table-container { overflow-x: auto; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; }
table.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem; }
table.data-table th, table.data-table td { padding: 0.85rem 1rem; border-bottom: 1px solid var(--border-color); }
table.data-table th {
  background: var(--bg-tertiary); font-weight: 600; color: var(--text-muted);
  text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.05em;
  position: sticky; top: 0; cursor: pointer; user-select: none;
}
table.data-table th:hover { color: var(--accent-cyan); }
table.data-table tr:hover { background: rgba(255, 255, 255, 0.02); }

.modal-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(6px); z-index: 1000;
  align-items: center; justify-content: center; padding: 1.5rem;
}
.modal-overlay.active { display: flex; }
.modal-window {
  background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px;
  max-width: 800px; width: 100%; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5); display: flex; flex-direction: column;
}
.modal-header {
  padding: 1.5rem; border-bottom: 1px solid var(--border-color);
  display: flex; justify-content: space-between; align-items: flex-start;
  position: sticky; top: 0; background: var(--bg-secondary); z-index: 10;
}
.modal-close-btn { background: none; border: none; font-size: 1.5rem; color: var(--text-muted); cursor: pointer; padding: 0 0.5rem; }
.modal-close-btn:hover { color: var(--text-main); }
.modal-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.timeline { position: relative; padding-left: 2rem; margin-top: 1rem; }
.timeline::before { content: ''; position: absolute; left: 7px; top: 5px; bottom: 5px; width: 2px; background: var(--border-color); }
.timeline-item { position: relative; margin-bottom: 2rem; }
.timeline-dot {
  position: absolute; left: -2rem; top: 4px; width: 16px; height: 16px;
  border-radius: 50%; background: var(--bg-primary); border: 2px solid var(--accent-cyan);
}
.timeline-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 1.25rem; }
.timeline-date { font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan); margin-bottom: 0.35rem; }
.timeline-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.75rem; }

.update-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; }
.update-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.update-role {
  font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;
  background: rgba(59, 130, 246, 0.15); color: var(--accent-blue);
}

.calc-box { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; }
.calc-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }
.calc-field label { display: block; font-size: 0.75rem; font-weight: 600; color: var(--text-muted); margin-bottom: 0.35rem; }
.calc-field input, .calc-field select {
  width: 100%; background: var(--bg-tertiary); border: 1px solid var(--border-color);
  border-radius: 6px; padding: 0.5rem 0.75rem; color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;
}
.calc-res-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem; margin-top: 1.5rem; background: var(--bg-tertiary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border-color);
}

.code-block {
  background: #050811; border: 1px solid var(--border-color); border-radius: 8px;
  padding: 1rem; font-family: var(--font-mono); font-size: 0.8rem; color: #38bdf8;
  overflow-x: auto; line-height: 1.5;
}
[data-theme="light"] .code-block { background: #f1f5f9; color: #0369a1; }

@media (max-width: 900px) {
  .nav-links { display: none; }
  .container { padding: 1rem; }
  .hero-title { font-size: 1.8rem; }
}
"""

    comm_count = len(commodities)
    paper_count = len(papers)
    latest_sprint = "Sprint 19.1 Active"
    if full_changelog.get('sprints') and len(full_changelog['sprints']) > 0:
        s0 = full_changelog['sprints'][0]
        stitle = s0.get('title', '')
        if 'Sprint' in stitle:
            m = re.search(r'(Sprint\s+[0-9\.]+)', stitle)
            latest_sprint = f"{m.group(1)} Active" if m else f"{stitle[:20]} Active"

    SHARED_HEADER = f"""
<header class="navbar">
  <div class="brand">
    <div class="brand-logo">&Phi;</div>
    <div class="brand-text">
      <h1>Value Physics</h1>
      <p>Alethekanon Research Institute &bull; Division 2</p>
    </div>
  </div>
  <ul class="nav-links">
    <li><a class="nav-link" href="index.html#dashboard" onclick="switchTab('dashboard')">Dashboard</a></li>
    <li><a class="nav-link" href="index.html#papers" onclick="switchTab('papers')">Papers & Registry ({paper_count})</a></li>
    <li><a class="nav-link" href="index.html#data" onclick="switchTab('data')">Empirical Data ({comm_count})</a></li>
    <li><a class="nav-link" href="index.html#changelog" onclick="switchTab('changelog')">Changelog</a></li>
    <li><a class="nav-link" href="index.html#updates" onclick="switchTab('updates')">Daily & Weekly Updates</a></li>
    <li><a class="nav-link" href="index.html#workflow" onclick="switchTab('workflow')">Workflow Pipeline</a></li>
  </ul>
  <div class="nav-actions">
    <div class="badge-status">
      <span class="pulse-dot"></span>
      <span>{latest_sprint}</span>
    </div>
    <button class="theme-toggle-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">&#9788;</button>
  </div>
</header>
"""

    INDEX_HTML = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Value Physics — Master Research Repository & Portal</title>
  <style>
{SHARED_CSS}
  </style>
</head>
<body>
{SHARED_HEADER}

<main class="container">
  <section class="hero">
    <h1 class="hero-title">Econophysics Grounded in Thermodynamic Invariants</h1>
    <p class="hero-subtitle">
      A comprehensive macroeconomic replacement architecture unifying thermodynamic exergy destruction ($P_e$), human metabolic difficulty ($P_b, U$), relativistic urgency ($\\gamma$), and non-usurious credit clearing.
      Governed by an autonomous multi-agent research triad operating under asynchronous Gemini Spark scheduled actions.
    </p>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Registered Deliverables</div>
        <div class="stat-val cyan">{paper_count}</div>
        <div class="stat-sub">VPE-01 to VPE-{paper_count} Cataloged</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Calibrated Commodities</div>
        <div class="stat-val emerald">{comm_count}</div>
        <div class="stat-sub">6 Essential Human Sectors</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Test Suite Pass Rate</div>
        <div class="stat-val gold">100%</div>
        <div class="stat-sub">24/24 Core &bull; 15/15 RRP Audit</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">SFC Balance Closures</div>
        <div class="stat-val purple">156/156</div>
        <div class="stat-sub">Zero Divergence Over 3 Years</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Zenodo Package Folders</div>
        <div class="stat-val cyan">3</div>
        <div class="stat-sub">VPE-55 &bull; VPE-21 &bull; VPE-49</div>
      </div>
    </div>
  </section>

  <!-- TAB 1: DASHBOARD -->
  <div id="tab-dashboard" class="tab-content active">
    <div class="section-header">
      <h2 class="section-title">Foundational Theoretical Pillars</h2>
      <div class="badge-status">A+ Epistemic Integrity</div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; margin-bottom: 2.5rem;">
      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-cyan); margin-bottom: 0.5rem;">1. Universal Price Equation (UPE)</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          Decomposes market prices into embodied thermodynamic exergy ($P_e$), material substrate ($P_b$), and human metabolic exertion ($U$), modified by supply scarcity ($S$), regenerative capacity ($R_n$), and relativistic survival urgency ($\\gamma(v_{{rel}})$).
        </p>
        <div class="code-block">P = m1 &bull; m2 &bull; &gamma;(v_rel) &bull; [(S &bull; U) / (Rn &bull; (1 - Ra))] + Pe + Pb</div>
      </div>

      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-emerald); margin-bottom: 0.5rem;">2. Work-Antiwork State-Space (VPE-49)</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          Orthogonal separation of active kinetic fluxes ($W_a, A_a$) from passive structural carrying floors ($W_p, A_p$). Rotation into $45^\\circ$ Diamond Phase Space ($P, A$) resolves the Cambridge Capital Controversy and proves the Autonomous Sclerosis Blowup Theorem.
        </p>
        <div class="code-block">&Phi;_drag = &delta;_p &bull; W_p + &mu; &bull; A_p^&nu;  (&nu; &gt; 1, T_blowup &lt; &infin;)</div>
      </div>

      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-gold); margin-bottom: 0.5rem;">3. Tri-Fold Cryptographic Ledger (VPE-02)</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          Proof-of-Difficulty (PoD) consensus state machine enforcing Theorem 5 (0% usury). Separates productive working capital (Book 1) from non-circulating reserves (Book 2) and communal safety nets (Book 3).
        </p>
        <div class="code-block">Theorem 5: &part;(A_p)/&part;t = 0 &rArr; Clean Slate Jubilee Invariant</div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
      <div class="stat-card">
        <div class="section-header" style="margin-bottom: 0.75rem;">
          <h3 style="font-size: 1.05rem;">Current Sprint Highlight (Sprint 18.5)</h3>
          <span class="badge-status">Verified Pass</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
          <strong>22-Commodity Empirical Expansion Parity:</strong> Grounded Solar Sea Salt (Case 21) and Raw Cane Sugar (Case 22). Confirms that mineral packaging introduces a 57.2% extractive toll in Tier III, while primary carbohydrate milling imposes a uniform ~43-44% intermediate toll.
        </p>
        <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.5;">
          <li>Automated unit tests: 24/24 core tests pass in 0.065s; 9/9 RRP tests pass in 0.003s.</li>
          <li>Treatise VPE-55 updated with full 22-commodity econometric analysis.</li>
          <li>Dedicated Zenodo release folder synchronized.</li>
        </ul>
        <div style="margin-top: 1rem;">
          <a href="#data" onclick="switchTab('data')" style="font-weight: 600; font-size: 0.85rem;">Explore 22-Commodity Data &rarr;</a>
        </div>
      </div>

      <div class="stat-card">
        <div class="section-header" style="margin-bottom: 0.75rem;">
          <h3 style="font-size: 1.05rem;">Multi-Agent Research Triad Status</h3>
          <span class="paper-id">SPARK SCHEDULES</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          Autonomous governance operating via 4 daily scheduled agents:
        </p>
        <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.8rem;">
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">
            <span>Project Manager (VPE-60 Governance)</span>
            <span style="color: var(--accent-emerald);">Daily 7:30 AM &bull; Active</span>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">
            <span>Lead Researcher (UPE Pricing Calibrations)</span>
            <span style="color: var(--accent-emerald);">Daily 7:30 AM &bull; Active</span>
          </div>
          <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 0.25rem;">
            <span>Epistemic Auditor / Checker (Data Audits)</span>
            <span style="color: var(--accent-emerald);">Daily 9:30 AM &bull; Active</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>Commercial &amp; Orthodox Linker (Market Data)</span>
            <span style="color: var(--accent-emerald);">Daily 6:30 AM &bull; Active</span>
          </div>
        </div>
        <div style="margin-top: 1rem;">
          <a href="#updates" onclick="switchTab('updates')" style="font-weight: 600; font-size: 0.85rem;">View Daily Execution Logs &rarr;</a>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 2: PAPERS & DELIVERABLES REGISTRY -->
  <div id="tab-papers" class="tab-content">
    <div class="section-header">
      <div>
        <h2 class="section-title">Master Deliverables &amp; Research Treatises (60)</h2>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Comprehensive catalog of all formal papers, manuscripts, econometric simulations, mathematical proofs, and Zenodo packages.
        </p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <button class="pill active" id="btn-view-cards" onclick="setPaperView('cards')">Card View</button>
        <button class="pill" id="btn-view-table" onclick="setPaperView('table')">Table View</button>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-row">
        <input type="text" id="paper-search-input" class="search-input" placeholder="Search by paper ID (e.g. VPE-21), title, theoretical concept, or theorem..." oninput="filterPapers()">
        <select id="paper-status-filter" class="search-input" style="flex: 0 0 220px;" onchange="filterPapers()">
          <option value="ALL">All Lifecycle Statuses</option>
          <option value="Complete">Complete / Verified</option>
          <option value="Active">Active Canonical</option>
          <option value="Remediated">Master Draft</option>
          <option value="Preprint">Preprints</option>
          <option value="Archived">Archived / Historical</option>
        </select>
      </div>
      <div class="filter-pills" id="paper-category-pills">
        <span class="pill active" onclick="setPaperCategory('ALL', this)">All Categories (60)</span>
        <span class="pill" onclick="setPaperCategory('Theoretical Treatises', this)">Theoretical Treatises</span>
        <span class="pill" onclick="setPaperCategory('Journal Manuscripts', this)">Journal Manuscripts</span>
        <span class="pill" onclick="setPaperCategory('Empirical Case Studies', this)">Empirical Pricing</span>
        <span class="pill" onclick="setPaperCategory('Simulations & SFC Models', this)">Simulations &amp; SFC</span>
        <span class="pill" onclick="setPaperCategory('Cryptographic Protocols', this)">Cryptographic Protocols</span>
        <span class="pill" onclick="setPaperCategory('Computational Engines & Code', this)">Engines &amp; Tests</span>
        <span class="pill" onclick="setPaperCategory('Zenodo Packages', this)">Zenodo Packages</span>
        <span class="pill" onclick="setPaperCategory('Governance & Management', this)">Governance &amp; Master Logs</span>
      </div>
    </div>

    <div id="papers-grid-view" class="papers-grid"></div>

    <div id="papers-table-view" class="table-container" style="display: none;">
      <table class="data-table">
        <thead>
          <tr>
            <th onclick="sortPapers('id')">Doc ID &uarr;&darr;</th>
            <th onclick="sortPapers('title')">Document Title &uarr;&darr;</th>
            <th onclick="sortPapers('category')">Category / Role &uarr;&darr;</th>
            <th>Theoretical &amp; Empirical Scope</th>
            <th onclick="sortPapers('status')">Status &uarr;&darr;</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="papers-table-body"></tbody>
      </table>
    </div>
  </div>

  <!-- TAB 3: EMPIRICAL DATA EXPLORER -->
  <div id="tab-data" class="tab-content">
    <div class="section-header">
      <div>
        <h2 class="section-title">{comm_count}-Commodity Empirical Pricing &amp; RRP/D Fairness Matrix</h2>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Grounded real-world Australian price audits comparing observed commercial retail prices ($P_{{obs}}$) against the biophysical Recommended Retail Price based on Difficulty (RRP/D).
        </p>
      </div>
      <button class="pill" onclick="exportCommoditiesCSV()">Export CSV</button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Average Extractive Drag (Ra)</div>
        <div class="stat-val gold">44.8%</div>
        <div class="stat-sub">Across {comm_count} Australian Staples</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Most Exploitative Sector</div>
        <div class="stat-val cyan">Digital / NBN</div>
        <div class="stat-sub">Ra = 79.2% &bull; Fairness 39.1%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Most Biophysically Fair</div>
        <div class="stat-val emerald">Water Cartage</div>
        <div class="stat-sub">Fairness 91.1% &bull; Ra = 20.8%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Latest Commodities Added</div>
        <div class="stat-val purple">Case {comm_count-1} &bull; {comm_count}</div>
        <div class="stat-sub">Expanded Staples Benchmark</div>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-row">
        <input type="text" id="comm-search-input" class="search-input" placeholder="Search commodity (e.g. Diesel, Sugar, Bread, Concrete)..." oninput="filterCommodities()">
        <select id="comm-sort-select" class="search-input" style="flex: 0 0 250px;" onchange="filterCommodities()">
          <option value="default">Default Order (Case 1 - {comm_count})</option>
          <option value="drag_desc">Highest Extractive Drag (Ra &darr;)</option>
          <option value="fairness_asc">Lowest Biophysical Fairness (&Phi; &uarr;)</option>
          <option value="premium_desc">Highest Dollar Premium ($AUD &darr;)</option>
          <option value="price_desc">Highest Market Price ($AUD &darr;)</option>
        </select>
      </div>
      <div class="filter-pills" id="comm-sector-pills">
        <span class="pill active" onclick="setCommSector('ALL', this)">All Sectors ({comm_count})</span>
        <span class="pill" onclick="setCommSector('Food', this)">Sector 1: Food &amp; Staples</span>
        <span class="pill" onclick="setCommSector('Energy', this)">Sector 2: Energy &amp; Fuels</span>
        <span class="pill" onclick="setCommSector('Water', this)">Sector 3: Water &amp; Sanitation</span>
        <span class="pill" onclick="setCommSector('Shelter', this)">Sector 4: Shelter Materials</span>
        <span class="pill" onclick="setCommSector('Care', this)">Sector 5: Healthcare &amp; Care</span>
        <span class="pill" onclick="setCommSector('Logistics', this)">Logistics &amp; Digital</span>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Commodity &amp; Packaging</th>
            <th>Sector Classification</th>
            <th>Observed Retail ($AUD)</th>
            <th>Fair RRP/D ($AUD)</th>
            <th>Extractive Drag (Ra)</th>
            <th>Unearned Toll</th>
            <th>Fairness Index</th>
            <th>Pe (Energy)</th>
            <th>Pb (Base)</th>
            <th>Labor (U)</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="commodities-table-body"></tbody>
      </table>
    </div>

    <div class="calc-box">
      <div class="section-header" style="margin-bottom: 0.5rem;">
        <h3 style="font-size: 1.15rem; color: var(--accent-cyan);">Live Universal Price Equation (UPE) Simulator &amp; Fairness Auditor</h3>
        <select id="calc-preset-select" class="search-input" style="flex: 0 0 280px;" onchange="loadCommodityPreset(this.value)">
          <option value="">Load Real Commodity Preset...</option>
        </select>
      </div>
      <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem;">
        Test and simulate price formation under varying physical energy input ($P_e$), material base ($P_b$), metabolic labor difficulty ($U$), scarcity ($S$), regenerative capacity ($R_n$), and speculative extractive drag ($R_a$).
      </p>

      <div class="calc-grid">
        <div class="calc-field">
          <label>Observed Retail Price ($AUD):</label>
          <input type="number" id="calc-P-obs" value="4.10" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Energy Exergy Pe ($AUD):</label>
          <input type="number" id="calc-Pe" value="0.38" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Physical Material Base Pb ($AUD):</label>
          <input type="number" id="calc-Pb" value="0.45" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Metabolic Labor Difficulty U ($AUD):</label>
          <input type="number" id="calc-U" value="2.15" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Scarcity Multiplier S:</label>
          <input type="number" id="calc-S" value="1.00" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Renewal Capacity Rn:</label>
          <input type="number" id="calc-Rn" value="1.00" step="0.01" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Extractive Drag Fraction Ra (0.0 to 0.95):</label>
          <input type="number" id="calc-Ra" value="0.3417" step="0.01" min="0" max="0.95" oninput="runCalculator()">
        </div>
        <div class="calc-field">
          <label>Relativistic Urgency v_rel (0.0 to 0.9):</label>
          <input type="number" id="calc-vrel" value="0.05" step="0.01" min="0" max="0.9" oninput="runCalculator()">
        </div>
      </div>

      <div class="calc-res-grid">
        <div>
          <div class="stat-label">Calculated Forward Price</div>
          <div class="stat-val cyan" id="calc-res-forward">$4.10</div>
          <div class="stat-sub">Including Extractive Drag</div>
        </div>
        <div>
          <div class="stat-label">Fair RRP/D Benchmark</div>
          <div class="stat-val emerald" id="calc-res-rrpd">$3.03</div>
          <div class="stat-sub">Zero Parasitic Friction (Ra=0)</div>
        </div>
        <div>
          <div class="stat-label">Extractive Premium</div>
          <div class="stat-val gold" id="calc-res-premium">+$1.07</div>
          <div class="stat-sub">Unearned Intermediary Rent</div>
        </div>
        <div>
          <div class="stat-label">Biophysical Fairness</div>
          <div class="stat-val purple" id="calc-res-fairness">73.8%</div>
          <div class="stat-sub">&Phi; = RRP_D / P_obs</div>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 4: CHANGELOG -->
  <div id="tab-changelog" class="tab-content">
    <div class="section-header">
      <div>
        <h2 class="section-title">Master Repository Changelog &amp; Sprints</h2>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Audited historical record of formal revisions, adversarial audits, test suite benchmarks, and milestone completions.
        </p>
      </div>
      <input type="text" id="cl-search-input" class="search-input" placeholder="Search changelog entries..." style="max-width: 300px;" oninput="filterChangelog()">
    </div>

    <div class="timeline" id="changelog-timeline"></div>
  </div>

  <!-- TAB 5: DAILY UPDATES & WEEKLY SUMMARIES -->
  <div id="tab-updates" class="tab-content">
    <div class="section-header">
      <div>
        <h2 class="section-title">Daily Execution Logs &amp; Weekly Executive Summaries</h2>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Asynchronous operational logs from the Lead Researcher, Epistemic Checker, and Project Manager, synthesized into weekly milestones.
        </p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <button class="pill active" id="btn-view-weekly" onclick="setUpdatesSubTab('weekly')">Weekly Summaries (7 Weeks)</button>
        <button class="pill" id="btn-view-daily" onclick="setUpdatesSubTab('daily')">Daily Multi-Agent Logs (79)</button>
      </div>
    </div>

    <div id="updates-weekly-view"></div>

    <div id="updates-daily-view" style="display: none;">
      <div class="filter-bar" style="margin-bottom: 1.25rem;">
        <div class="filter-row">
          <input type="text" id="daily-search-input" class="search-input" placeholder="Search daily logs..." oninput="filterDailyLogs()">
          <select id="daily-role-filter" class="search-input" style="flex: 0 0 250px;" onchange="filterDailyLogs()">
            <option value="ALL">All Roles</option>
            <option value="Lead Researcher">Lead Researcher</option>
            <option value="Epistemic Auditor & Checker">Epistemic Auditor &amp; Checker</option>
            <option value="Project Manager">Project Manager</option>
            <option value="Commercial & Orthodox Linker">Commercial &amp; Orthodox Linker</option>
          </select>
        </div>
      </div>
      <div id="daily-logs-stream"></div>
    </div>
  </div>

  <!-- TAB 6: WORKFLOW & PIPELINE -->
  <div id="tab-workflow" class="tab-content">
    <div class="section-header">
      <div>
        <h2 class="section-title">Autonomous Workflow &amp; Publishing Pipeline</h2>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Architectural documentation of the autonomous research triad, automated build scripts, and continuous HTML deployment.
        </p>
      </div>
      <span class="badge-status">Continuous Synchronization</span>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-cyan); margin-bottom: 0.75rem;">1. Autonomous Spark Schedules</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.75rem;">
          The research corpus evolves daily through asynchronous Gemini Spark scheduled actions:
        </p>
        <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.6;">
          <li><strong>6:30 AM AEST:</strong> Commercial Linker surveys ABS/ACCC/ABARES regulatory benchmarks.</li>
          <li><strong>7:30 AM AEST:</strong> Lead Researcher runs Python forward pricing solvers and updates treatises.</li>
          <li><strong>7:30 AM AEST:</strong> Project Manager audits repository health, logs sprints, and ensures Zenodo packaging.</li>
          <li><strong>9:30 AM AEST:</strong> Epistemic Auditor stress-tests mathematical proofs, code solvers, and test suites.</li>
        </ul>
      </div>

      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-emerald); margin-bottom: 0.75rem;">2. Local &amp; CI/CD Static Generator</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.75rem;">
          The static HTML website is generated deterministically by <code>build_value_physics_site.py</code>:
        </p>
        <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.6;">
          <li>Ingests <code>deliverables_registry.csv</code> and extracts 60 deliverables.</li>
          <li>Ingests <code>empirical_calibration_data_22_commodities.csv</code>.</li>
          <li>Parses <code>CHANGELOG.md</code> and <code>pm_master_log.txt</code>.</li>
          <li>Gracefully falls back to bundled <code>./data/*.json</code> in clean environments without downloads.</li>
          <li>Generates 100% standalone, dependency-free HTML pages ready for local browsing or web hosting.</li>
        </ul>
      </div>

      <div class="stat-card">
        <h3 style="font-size: 1.1rem; color: var(--accent-gold); margin-bottom: 0.75rem;">3. Zero-Maintenance Hosting</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.75rem;">
          Deploy anywhere with zero configuration:
        </p>
        <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.6;">
          <li><strong>GitHub Pages:</strong> Push to <code>gh-pages</code> branch via included GitHub Actions workflow.</li>
          <li><strong>Cloudflare Pages / Netlify:</strong> Connect Git repo; build command: <code>python3 build_value_physics_site.py</code>.</li>
          <li><strong>Local Browser:</strong> Open <code>index.html</code> directly in Chrome/Firefox/Safari (all JSON data is embedded for <code>file://</code> protocol compatibility).</li>
        </ul>
      </div>
    </div>

    <div class="stat-card" style="margin-bottom: 2rem;">
      <h3 style="font-size: 1.05rem; margin-bottom: 0.75rem;">Executable Pipeline Commands</h3>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
        Run the following commands to sync latest changes and re-build the complete site:
      </p>
      <div class="code-block">
# 1. Run sync and build script
bash sync_and_build.sh

# 2. Or run Python generator directly (works with raw CSVs or existing JSONs)
python3 build_value_physics_site.py

# 3. Serve locally for testing
python3 -m http.server 8000
# &gt; Open http://localhost:8000 in your browser
      </div>
    </div>
  </div>
</main>

<div id="paper-modal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
  <div class="modal-window">
    <div class="modal-header">
      <div>
        <span class="paper-id" id="modal-paper-id">VPE-01</span>
        <span class="paper-status" id="modal-paper-status" style="margin-left: 0.5rem;">Verified</span>
        <h3 id="modal-paper-title" style="margin-top: 0.5rem; font-size: 1.25rem;">Paper Title</h3>
        <div id="modal-paper-cat" style="font-size: 0.8rem; color: var(--accent-gold); margin-top: 0.25rem;">Category</div>
      </div>
      <button class="modal-close-btn" onclick="closePaperModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div>
        <h4 style="font-size: 0.85rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 0.35rem;">Theoretical &amp; Empirical Scope</h4>
        <p id="modal-paper-scope" style="font-size: 0.9rem; line-height: 1.6; color: var(--text-main);"></p>
      </div>

      <div id="modal-associated-box">
        <h4 style="font-size: 0.85rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 0.5rem;">Associated Computational &amp; Empirical Data</h4>
        <ul id="modal-paper-associated" style="font-size: 0.85rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.6;"></ul>
      </div>

      <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 8px; padding: 1.25rem; margin-top: 1rem;">
        <h4 style="font-size: 0.85rem; text-transform: uppercase; color: var(--accent-cyan); margin-bottom: 0.35rem;">Document Access &amp; In-Browser Reading</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.85rem;">Read the complete full-text document directly in your browser without downloading, or access the raw repository deliverable.</p>
        <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
          <a id="modal-paper-read-btn" href="#" style="display: inline-flex; align-items: center; gap: 0.6rem; text-decoration: none; padding: 0.75rem 1.5rem; font-size: 0.95rem; font-weight: 700; background: linear-gradient(135deg, #f59e0b, #d97706); color: #0a0e17; border-radius: 6px; box-shadow: 0 4px 14px rgba(245, 158, 11, 0.4);">
            <span>Read Full Document in Browser &rarr;</span>
          </a>
          <a id="modal-paper-file" href="#" target="_blank" style="display: inline-flex; align-items: center; gap: 0.6rem; text-decoration: none; padding: 0.75rem 1.25rem; font-size: 0.88rem; font-weight: 600; background: rgba(255, 255, 255, 0.08); border: 1px solid var(--border-color); color: var(--text-main); border-radius: 6px;">
            <span>Download Raw File</span>
            <span id="modal-paper-ext-badge" style="background: rgba(255,255,255,0.15); padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.75rem; font-family: var(--font-mono);">PDF</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
const PAPERS = {papers_js};
const COMMODITIES = {commodities_js};
const CHANGELOG = {changelog_js};
const DAILY_UPDATES = {daily_updates_js};
const WEEKLY_SUMMARIES = {weekly_summaries_js};

let currentTab = 'dashboard';
let currentPaperCategory = 'ALL';
let currentPaperStatus = 'ALL';
let currentPaperSearch = '';
let paperViewMode = 'cards';
let currentCommSector = 'ALL';
let currentCommSearch = '';
let currentCommSort = 'default';
let currentUpdatesSubTab = 'weekly';

function switchTab(tabId) {{
  currentTab = tabId;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');
  
  document.querySelectorAll('.nav-link').forEach(el => {{
    if (el.getAttribute('href').includes(tabId)) el.classList.add('active');
  }});
  window.scrollTo({{ top: 0, behavior: 'smooth' }});
}}

function toggleTheme() {{
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
}}

function renderPapers() {{
  const filtered = PAPERS.filter(p => {{
    const matchCat = currentPaperCategory === 'ALL' || p.group === currentPaperCategory;
    const matchStat = currentPaperStatus === 'ALL' || p.status.toLowerCase().includes(currentPaperStatus.toLowerCase());
    const query = currentPaperSearch.toLowerCase();
    const matchQuery = !query || 
      p.id.toLowerCase().includes(query) || 
      p.title.toLowerCase().includes(query) || 
      p.scope.toLowerCase().includes(query) || 
      p.category.toLowerCase().includes(query);
    return matchCat && matchStat && matchQuery;
  }});

  const grid = document.getElementById('papers-grid-view');
  grid.innerHTML = filtered.map(p => `
    <div class="paper-card" onclick="openPaperModal('${{p.id}}')">
      <div>
        <div class="paper-header">
          <span class="paper-id">${{p.id}}</span>
          <span class="paper-status">${{p.status.split('/')[0].trim()}}</span>
        </div>
        <h3 class="paper-title">${{p.title}}</h3>
        <div class="paper-cat">${{p.category}}</div>
        <p class="paper-scope">${{p.scope}}</p>
      </div>
      <div class="paper-footer" style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-top: 1rem;">
        <a href="read/${{p.id}}.html" onclick="event.stopPropagation()" class="enter-btn" style="padding: 0.45rem 0.9rem; font-size: 0.8rem; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-flex; align-items: center; gap: 0.35rem;">
          <span>Read Document</span> &rarr;
        </a>
        <div style="display: flex; align-items: center; gap: 0.4rem;">
          <a href="${{p.file_path}}" target="_blank" onclick="event.stopPropagation()" class="pill" style="font-size: 0.72rem; text-decoration: none; padding: 0.2rem 0.5rem;">${{p.file_ext}} (${{p.file_size}})</a>
        </div>
      </div>
    </div>
  `).join('');

  const tbody = document.getElementById('papers-table-body');
  tbody.innerHTML = filtered.map(p => `
    <tr>
      <td><span class="paper-id">${{p.id}}</span></td>
      <td><strong>${{p.title}}</strong></td>
      <td style="color: var(--accent-gold); font-size: 0.8rem;">${{p.category}}</td>
      <td style="max-width: 450px; font-size: 0.8rem; color: var(--text-muted);">${{p.scope}}</td>
      <td><span class="paper-status">${{p.status.split('/')[0].trim()}}</span></td>
      <td style="white-space: nowrap;">
        <a href="read/${{p.id}}.html" class="pill active" style="font-size: 0.8rem; text-decoration: none; font-weight: 600; margin-right: 0.35rem;">Read Text &rarr;</a>
        <a href="${{p.file_path}}" target="_blank" class="pill" style="font-size: 0.75rem; text-decoration: none; margin-right: 0.35rem;">${{p.file_ext}}</a>
        <button class="pill" onclick="openPaperModal('${{p.id}}'); event.stopPropagation();">Inspect</button>
      </td>
    </tr>
  `).join('');
}}

function setPaperCategory(cat, el) {{
  currentPaperCategory = cat;
  document.querySelectorAll('#paper-category-pills .pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  renderPapers();
}}

function filterPapers() {{
  currentPaperSearch = document.getElementById('paper-search-input').value;
  currentPaperStatus = document.getElementById('paper-status-filter').value;
  renderPapers();
}}

function setPaperView(mode) {{
  paperViewMode = mode;
  document.getElementById('btn-view-cards').classList.toggle('active', mode === 'cards');
  document.getElementById('btn-view-table').classList.toggle('active', mode === 'table');
  document.getElementById('papers-grid-view').style.display = mode === 'cards' ? 'grid' : 'none';
  document.getElementById('papers-table-view').style.display = mode === 'table' ? 'block' : 'none';
}}

function openPaperModal(id) {{
  const p = PAPERS.find(item => item.id === id);
  if (!p) return;
  document.getElementById('modal-paper-id').innerText = p.id;
  document.getElementById('modal-paper-status').innerText = p.status;
  document.getElementById('modal-paper-title').innerText = p.title;
  document.getElementById('modal-paper-cat').innerText = p.category + ' (' + p.group + ')';
  document.getElementById('modal-paper-scope').innerText = p.scope;
  
  const assocUl = document.getElementById('modal-paper-associated');
  if (p.associated_data && p.associated_data.length > 0) {{
    assocUl.innerHTML = p.associated_data.map(item => `<li>${{item}}</li>`).join('');
    document.getElementById('modal-associated-box').style.display = 'block';
  }} else {{
    assocUl.innerHTML = '<li>Universal Price Equation (UPE) mathematical parameters</li><li>Standalone test suite verification pass</li>';
    document.getElementById('modal-associated-box').style.display = 'block';
  }}
  
  const readBtn = document.getElementById('modal-paper-read-btn');
  if (readBtn) {{
    readBtn.href = 'read/' + p.id + '.html';
  }}

  const fileEl = document.getElementById('modal-paper-file');
  const badgeEl = document.getElementById('modal-paper-ext-badge');
  if (p.file_path) {{
    fileEl.href = p.file_path;
    badgeEl.textContent = `${{p.file_ext}} (${{p.file_size}})`;
    fileEl.style.display = 'inline-flex';
  }} else {{
    fileEl.style.display = 'none';
  }}
  
  document.getElementById('paper-modal').classList.add('active');
}}

function closePaperModal() {{
  document.getElementById('paper-modal').classList.remove('active');
}}

function closeModalOnOverlay(e) {{
  if (e.target.id === 'paper-modal') closePaperModal();
}}

function renderCommodities() {{
  let list = [...COMMODITIES];
  if (currentCommSector !== 'ALL') {{
    list = list.filter(c => c.sector.toLowerCase().includes(currentCommSector.toLowerCase()));
  }}
  if (currentCommSearch) {{
    const q = currentCommSearch.toLowerCase();
    list = list.filter(c => c.commodity.toLowerCase().includes(q) || c.sector.toLowerCase().includes(q));
  }}
  
  if (currentCommSort === 'drag_desc') list.sort((a,b) => b.Ra - a.Ra);
  else if (currentCommSort === 'fairness_asc') list.sort((a,b) => a.fairness - b.fairness);
  else if (currentCommSort === 'premium_desc') list.sort((a,b) => b.premium - a.premium);
  else if (currentCommSort === 'price_desc') list.sort((a,b) => b.P_obs - a.P_obs);

  const tbody = document.getElementById('commodities-table-body');
  tbody.innerHTML = list.map(c => `
    <tr>
      <td><strong>${{c.commodity}}</strong><br><span style="font-size: 0.75rem; color: var(--text-dim);">${{c.unit}}</span></td>
      <td style="font-size: 0.75rem; color: var(--accent-gold);">${{c.sector}}</td>
      <td style="font-family: var(--font-mono); font-weight: 700;">$${{c.P_obs.toFixed(2)}}</td>
      <td style="font-family: var(--font-mono); color: var(--accent-emerald); font-weight: 700;">$${{c.RRP_D.toFixed(2)}}</td>
      <td>
        <span style="font-family: var(--font-mono); font-weight: 600; color: ${{c.Ra > 0.5 ? 'var(--accent-rose)' : 'var(--accent-gold)'}};">
          ${{(c.Ra * 100).toFixed(1)}}%
        </span>
      </td>
      <td style="font-family: var(--font-mono); color: var(--accent-rose);">+$${{c.premium.toFixed(2)}}</td>
      <td>
        <span style="font-family: var(--font-mono); font-weight: 700; color: ${{c.fairness >= 75 ? 'var(--accent-emerald)' : c.fairness >= 55 ? 'var(--accent-gold)' : 'var(--accent-rose)'}};">
          ${{c.fairness.toFixed(1)}}%
        </span>
      </td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">$${{c.Pe.toFixed(2)}}</td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">$${{c.Pb.toFixed(2)}}</td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-muted);">$${{c.U.toFixed(2)}}</td>
      <td>
        <button class="pill" onclick="loadCommodityPreset('${{c.commodity.replace(/'/g, "\\'")}}')">Simulate</button>
      </td>
    </tr>
  `).join('');
}}

function setCommSector(sec, el) {{
  currentCommSector = sec;
  document.querySelectorAll('#comm-sector-pills .pill').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  renderCommodities();
}}

function filterCommodities() {{
  currentCommSearch = document.getElementById('comm-search-input').value;
  currentCommSort = document.getElementById('comm-sort-select').value;
  renderCommodities();
}}

function runCalculator() {{
  const P_obs = parseFloat(document.getElementById('calc-P-obs').value) || 0;
  const Pe = parseFloat(document.getElementById('calc-Pe').value) || 0;
  const Pb = parseFloat(document.getElementById('calc-Pb').value) || 0;
  const U = parseFloat(document.getElementById('calc-U').value) || 0;
  const S = parseFloat(document.getElementById('calc-S').value) || 1;
  const Rn = parseFloat(document.getElementById('calc-Rn').value) || 1;
  const Ra = parseFloat(document.getElementById('calc-Ra').value) || 0;
  const vrel = parseFloat(document.getElementById('calc-vrel').value) || 0;

  const gamma = 1.0 / Math.sqrt(Math.max(0.001, 1.0 - (vrel * vrel)));
  const denominator = Math.max(0.01, Rn * (1.0 - Ra));
  const forwardPrice = (gamma * ((S * U) / denominator)) + Pe + Pb;
  const fairRRPD = (gamma * ((S * U) / Rn)) + Pe + Pb;
  
  const premium = Math.max(0, P_obs - fairRRPD);
  const fairness = P_obs > 0 ? (fairRRPD / P_obs) * 100 : 100;

  document.getElementById('calc-res-forward').innerText = '$' + forwardPrice.toFixed(2);
  document.getElementById('calc-res-rrpd').innerText = '$' + fairRRPD.toFixed(2);
  document.getElementById('calc-res-premium').innerText = (premium > 0 ? '+$' : '$') + premium.toFixed(2);
  document.getElementById('calc-res-fairness').innerText = fairness.toFixed(1) + '%';
}}

function loadCommodityPreset(name) {{
  const c = COMMODITIES.find(item => item.commodity === name);
  if (!c) return;
  document.getElementById('calc-P-obs').value = c.P_obs;
  document.getElementById('calc-Pe').value = c.Pe;
  document.getElementById('calc-Pb').value = c.Pb;
  document.getElementById('calc-U').value = c.U;
  document.getElementById('calc-S').value = c.S;
  document.getElementById('calc-Rn').value = c.Rn;
  document.getElementById('calc-Ra').value = c.Ra;
  document.getElementById('calc-vrel').value = c.vrel;
  runCalculator();
  document.querySelector('.calc-box').scrollIntoView({{ behavior: 'smooth' }});
}}

function renderChangelog() {{
  const container = document.getElementById('changelog-timeline');
  const q = (document.getElementById('cl-search-input')?.value || '').toLowerCase();
  
  const sprints = CHANGELOG.sprints || [];
  const filtered = sprints.filter(s => !q || s.title.toLowerCase().includes(q) || s.date.includes(q) || s.raw_content.toLowerCase().includes(q));

  container.innerHTML = filtered.map(s => `
    <div class="timeline-item">
      <div class="timeline-dot"></div>
      <div class="timeline-card">
        <div class="timeline-date">${{s.date}}</div>
        <h3 class="timeline-title">${{s.title}}</h3>
        <ul style="font-size: 0.85rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.6;">
          ${{s.summary_items.map(item => `<li>${{item}}</li>`).join('')}}
        </ul>
      </div>
    </div>
  `).join('');
}}

function filterChangelog() {{
  renderChangelog();
}}

function renderUpdates() {{
  const weeklyContainer = document.getElementById('updates-weekly-view');
  weeklyContainer.innerHTML = WEEKLY_SUMMARIES.map(w => `
    <div class="update-card" style="margin-bottom: 1.5rem;">
      <div class="update-header">
        <div>
          <span style="font-family: var(--font-mono); font-weight: 700; color: var(--accent-cyan); font-size: 0.9rem;">${{w.week_number}}</span>
          <span style="color: var(--text-dim); font-size: 0.8rem; margin-left: 0.5rem;">${{w.date_range}}</span>
        </div>
        <span class="badge-status">System Health Pass</span>
      </div>
      <h3 style="font-size: 1.2rem; margin-bottom: 0.75rem; color: var(--text-main);">${{w.title}}</h3>
      <p style="font-size: 0.8rem; color: var(--accent-gold); margin-bottom: 0.75rem; font-weight: 600;">
        Active Sprints: ${{w.sprints.join(', ')}}
      </p>
      <div style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 0.75rem;">
        <strong>Key Milestones &amp; Accomplishments:</strong>
        <ul style="padding-left: 1.2rem; margin-top: 0.35rem;">
          ${{w.milestones.map(m => `<li>${{m}}</li>`).join('')}}
        </ul>
      </div>
      <div style="font-size: 0.75rem; color: var(--accent-emerald); font-family: var(--font-mono); border-top: 1px solid var(--border-color); padding-top: 0.5rem;">
        &bull; ${{w.system_health}}
      </div>
    </div>
  `).join('');

  renderDailyLogs();
}}

function renderDailyLogs() {{
  const stream = document.getElementById('daily-logs-stream');
  const roleFilter = document.getElementById('daily-role-filter')?.value || 'ALL';
  const query = (document.getElementById('daily-search-input')?.value || '').toLowerCase();

  const filtered = DAILY_UPDATES.filter(d => {{
    const matchRole = roleFilter === 'ALL' || d.role === roleFilter;
    const matchQuery = !query || d.header.toLowerCase().includes(query) || d.full_text_preview.toLowerCase().includes(query) || d.date.includes(query);
    return matchRole && matchQuery;
  }});

  stream.innerHTML = filtered.slice(0, 30).map(d => `
    <div class="update-card">
      <div class="update-header">
        <span class="update-role">${{d.role}}</span>
        <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-dim);">${{d.date}} (${{d.sprint}})</span>
      </div>
      <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem; color: var(--text-main);">${{d.header}}</h4>
      <ul style="font-size: 0.8rem; color: var(--text-muted); padding-left: 1.2rem; line-height: 1.5; margin-bottom: 0.5rem;">
        ${{d.key_takeaways.map(t => `<li>${{t}}</li>`).join('')}}
      </ul>
      <details style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.5rem;">
        <summary style="cursor: pointer; color: var(--accent-cyan);">Inspect Raw Log Excerpt &darr;</summary>
        <div class="code-block" style="margin-top: 0.5rem; font-size: 0.75rem; max-height: 250px;">
          ${{d.full_text_preview}}...
        </div>
      </details>
    </div>
  `).join('');
}}

function setUpdatesSubTab(sub) {{
  currentUpdatesSubTab = sub;
  document.getElementById('btn-view-weekly').classList.toggle('active', sub === 'weekly');
  document.getElementById('btn-view-daily').classList.toggle('active', sub === 'daily');
  document.getElementById('updates-weekly-view').style.display = sub === 'weekly' ? 'block' : 'none';
  document.getElementById('updates-daily-view').style.display = sub === 'daily' ? 'block' : 'none';
}}

function filterDailyLogs() {{
  renderDailyLogs();
}}

function exportCommoditiesCSV() {{
  window.open('data/commodities.json', '_blank');
}}

window.addEventListener('DOMContentLoaded', () => {{
  const presetSelect = document.getElementById('calc-preset-select');
  COMMODITIES.forEach(c => {{
    const opt = document.createElement('option');
    opt.value = c.commodity;
    opt.innerText = c.commodity;
    presetSelect.appendChild(opt);
  }});

  const hash = window.location.hash.replace('#', '');
  if (['dashboard', 'papers', 'data', 'changelog', 'updates', 'workflow'].includes(hash)) {{
    switchTab(hash);
  }} else {{
    switchTab('dashboard');
  }}

  renderPapers();
  renderCommodities();
  renderChangelog();
  renderUpdates();
  runCalculator();
}});
</script>
</body>
</html>
"""

    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_HTML)

    def generate_subpage(page_name, page_title, active_tab_id):
        content = INDEX_HTML.replace("switchTab('dashboard')", f"switchTab('{active_tab_id}')")
        content = content.replace("<title>Value Physics — Master Research Repository & Portal</title>", f"<title>{page_title} — Value Physics</title>")
        content = content.replace("window.location.hash.replace('#', '')", f"'{active_tab_id}'")
        with open(os.path.join(BASE_DIR, page_name), "w", encoding="utf-8") as f:
            f.write(content)

    generate_subpage("papers.html", "Papers & Deliverables Registry", "papers")
    generate_subpage("data.html", f"{len(commodities)}-Commodity Empirical Pricing Matrix", "data")
    generate_subpage("changelog.html", "Repository Sprints Changelog", "changelog")
    generate_subpage("updates.html", "Daily Updates & Weekly Summaries", "updates")
    generate_subpage("workflow.html", "Autonomous Research Pipeline & Workflow", "workflow")
    print("All HTML files compiled successfully.")

def main():
    print("=== Value Physics Site Generator & Pipeline ===")
    
    # Try parsing from raw downloads first
    data = parse_from_downloads()
    if data:
        papers, commodities, full_changelog, daily_logs, weekly_summaries = data
        print(f"Successfully re-parsed raw files: {len(papers)} papers, {len(commodities)} commodities.")
    else:
        # Fall back to existing JSON files
        print("Notice: downloads/ directory or raw CSVs not present. Falling back to ./data/*.json...")
        papers, commodities, full_changelog, daily_logs, weekly_summaries = load_from_json()
        print(f"Successfully loaded JSON datasets: {len(papers)} papers, {len(commodities)} commodities.")

    generate_html_files(papers, commodities, full_changelog, daily_logs, weekly_summaries)
    generate_all_reader_pages(papers, BASE_DIR)
    print("=== Build Completed Successfully ===")

if __name__ == '__main__':
    main()
