# Value Physics Research Repository — Website & Autonomous Workflow Specification

**Institution:** Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation  
**Location:** New South Wales, Australia  
**System Revision:** Sprint 18.5 (October 2026) | 60 Registered Deliverables | 22 Calibrated Australian Commodities  

---

## 1. System Overview

This workflow and website presentation architecture is engineered to automatically translate the entire **Value Physics** research corpus—including 60 registered treatises and papers, real-world empirical pricing calibration datasets, formal sprint changelogs, daily multi-agent operational logs, and weekly executive summaries—into an accessible, interactive, and beautiful HTML presentation suite.

The system bridges the gap between raw research artifacts stored in Google Drive / Google Sheets and the public web by providing:
1. **Interactive Papers & Treatises Catalog:** Full search, filtering, and deep-dive modal views for all 60 deliverables (`VPE-01` to `VPE-60`).
2. **22-Commodity Empirical Pricing Explorer:** Live comparison between observed commercial retail prices ($P_{\text{obs}}$) and Recommended Retail Price based on Difficulty ($\text{RRP/D}$), with an interactive **Universal Price Equation (UPE)** simulator.
3. **Formal Sprint Changelog:** Complete historical audit trail across Sprints 17.0–18.5 and beyond.
4. **Daily Updates & Weekly Summaries Stream:** Automated aggregation of multi-agent logs (Project Manager, Lead Researcher, Epistemic Auditor, and Commercial Linker) alongside synthesized weekly milestones.
5. **Deterministic Static Generator:** Zero-dependency, offline-capable static site compiler (`build_value_physics_site.py`).

---

## 2. Autonomous Multi-Agent Research Triad & Spark Schedule Workflow

The Value Physics research corpus is autonomously advanced and audited through four daily scheduled actions in Gemini Spark:

```
+-----------------------------------------------------------------------------------+
|                           DAILY SCHEDULED AGENT WORKFLOW                          |
+-----------------------------------------------------------------------------------+
| 06:30 AM AEST  | Commercial & Orthodox Linker                                    |
|                | - Surveys ABS, ABARES, AEMO, and ACCC benchmark microdata.       |
|                | - Identifies real-world market costs and margin structures.      |
+----------------+------------------------------------------------------------------+
| 07:30 AM AEST  | Lead Researcher                                                 |
|                | - Selects target physical commodities for empirical calibration.  |
|                | - Executes forward pricing and reverse-engineers retail drag Ra. |
|                | - Updates VPE-55 treatise and generates standalone Python code.  |
+----------------+------------------------------------------------------------------+
| 07:30 AM AEST  | Project Manager                                                 |
|                | - Audits repository health across all 60 deliverables.           |
|                | - Appends sprint logs to canonical Master Ledger (VPE-15/23).    |
|                | - Verifies Zenodo upload packages and living treatise VPE-60.    |
+----------------+------------------------------------------------------------------+
| 09:30 AM AEST  | Epistemic Auditor & Checker                                      |
|                | - Adversarially stress-tests mathematical derivations & proofs.  |
|                | - Runs 24 unit tests in test_value_physics.py and RRP tests.     |
|                | - Issues Epistemic Audit Sign-Off (AUD-VPE-001 to AUD-VPE-015).  |
+----------------+------------------------------------------------------------------+
| 10:30 AM AEST  | [Automated Site Sync & Build] (This Workflow)                    |
| (Post-Audit)   | - Downloads latest CSVs, CHANGELOG.md, and pm_master_log.txt.    |
|                | - Compiles structured JSON datasets.                             |
|                | - Re-generates index.html, papers.html, data.html, updates.html. |
|                | - Deploys refreshed site to web hosting / GitHub Pages.          |
+----------------+------------------------------------------------------------------+
```

---

## 3. Directory Structure & Generated Artifacts

```
output/
├── index.html                   # Master Portal (SPA with live tabs, search, calculator)
├── papers.html                  # Dedicated Papers & Deliverables Registry Explorer
├── data.html                    # Dedicated 22-Commodity Empirical Pricing Matrix
├── changelog.html               # Dedicated Repository Sprints Changelog
├── updates.html                 # Dedicated Daily Updates & Weekly Summaries
├── workflow.html                # Dedicated Workflow & Architecture Documentation
├── build_value_physics_site.py  # Standalone Python Site Generator & Parser
├── sync_and_build.sh            # Automated Bash Pipeline Script
├── WORKFLOW.md                  # Comprehensive Architecture & Deployment Guide
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Pages CI/CD Continuous Deployment Action
├── downloads/                   # Raw Exported CSVs & Logs (Included in Release Package)
│   ├── deliverables_registry.csv
│   ├── empirical_calibration_data_22_commodities.csv
│   ├── CHANGELOG.md
│   └── pm_master_log.txt
└── data/
    ├── papers.json              # 60 Deliverables metadata & Drive links
    ├── commodities.json         # 22 Australian commodities calibration microdata
    ├── changelog.json           # Sprint releases and 75 formal logs
    ├── daily_updates.json       # 79 Multi-agent daily execution logs
    └── weekly_summaries.json    # 7 Synthesized weekly executive summaries
```

---

## 4. Dual-Mode Build Engine (`build_value_physics_site.py`)

`build_value_physics_site.py` features a **zero-dependency, dual-mode build architecture**:

1. **Full Re-Parsing Mode (Local / Ingestion Environment):**
   - If the `./downloads/` folder is present with raw exports (`deliverables_registry.csv`, `empirical_calibration_data_22_commodities.csv`, `CHANGELOG.md`, `pm_master_log.txt`), the script re-parses all papers, pricing data, sprint changelogs, and daily logs, updating `./data/*.json` and rebuilding all HTML pages.
2. **Autonomous Fallback Mode (CI/CD / GitHub Actions / Clean Clone):**
   - If the `./downloads/` folder is absent, the script automatically falls back to loading the existing structured `./data/*.json` files.
   - This ensures that `deploy.yml` on GitHub Actions runs seamlessly with zero errors even when raw downloads are not checked into Git.
3. **No Hardcoded Sandbox Paths:**
   - All directory paths are resolved relative to `__file__`, ensuring 100% portability across local machines, Docker containers, and cloud CI runners.

---

## 5. How to Run & Update the Site

### Option A: Local Build & Preview (Single Command)
To regenerate the site from downloaded spreadsheets and logs:
```bash
# Execute the automated pipeline
bash sync_and_build.sh

# Or run the Python generator directly
python3 build_value_physics_site.py

# Launch local preview server
python3 -m http.server 8000
```
Open `http://localhost:8000` in your web browser.

### Option B: Synchronizing Latest Changes from Google Drive
When the Project Manager or Lead Researcher updates the Google Drive spreadsheets:
1. Export the latest `Value Physics Project Management — Master Changelog & Deliverables Registry` (Sheet ID `1DmzdWW6Kkm4Z4B1QX3U1S48o06XOOQRg5LYooD8DzTg`) as CSV to `downloads/deliverables_registry.csv`.
2. Export `empirical_calibration_data_22_commodities` (Sheet ID `1NeNlS1-pjRmO4RY7fn47QTcb1hV9BStavMT9seKrcFg`) as CSV to `downloads/empirical_calibration_data_22_commodities.csv`.
3. Export `CHANGELOG.md` (Doc ID `10-izMWCGkYcslJ_ORhvBMp8hF-pOUHNNePWNDUVbqqs`) to `downloads/CHANGELOG.md`.
4. Run `python3 build_value_physics_site.py`.
5. The HTML website is instantaneously regenerated with the latest papers, prices, and sprint summaries.

---

## 6. Web Hosting & Production Deployment

### 1. GitHub Pages (Automated via GitHub Actions)
The included `.github/workflows/deploy.yml` automatically triggers on every commit to `main` and on a daily schedule (00:00 UTC / 11:00 AM AEST).
1. Push the generated directory to a GitHub repository.
2. In GitHub, navigate to **Settings > Pages**.
3. Under **Build and deployment > Source**, select **GitHub Actions**.
4. The site will deploy automatically to `https://<username>.github.io/<repo-name>/`.

### 2. Cloudflare Pages / Netlify / Vercel
1. Link your repository.
2. Build command: `python3 build_value_physics_site.py`
3. Publish directory: `.` (or `output/`)
4. Zero environment variables required.

### 3. Air-Gapped / Offline Local Browsing
The HTML files are compiled with embedded JSON datasets, allowing `index.html` to be opened directly via the `file://` protocol in any standard web browser without requiring a web server or internet connection.
