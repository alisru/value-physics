# Value Physics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1755001.svg)](https://zenodo.org)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Computational replication archives, empirical pricing solvers, non-linear state-space ODE models, and publication LaTeX manuscripts for **Value Physics** — developed at the **Alethekanon Research Institute**, Division 2: Societal Economics & Macro-Micro Simulation.

---

## Repository Structure

```text
value-physics/
├── 01_Empirical_Pricing_Audit_VPE55/       # VPE-55: Empirical RRP/D Fairness Audit (Ecological Economics)
│   ├── manuscript_vpe55.tex                # Elsevier elsarticle camera-ready LaTeX manuscript
│   ├── manuscript_vpe55.pdf                # Pre-compiled publication proof (11 pages)
│   ├── rrp_fairness_audit.py               # Standalone UPE forward & reverse pricing solver
│   ├── empirical_calibration_data_14_...   # 14-commodity empirical Australian parameter dataset
│   ├── figure1_biophysical_breakdown.png   # 300 DPI cost decomposition figure
│   ├── figure2_sclerosis_spectrum.png      # 300 DPI Extractive Drag vs. Fairness index figure
│   ├── vpe55_latex_package.zip             # Self-contained submission archive
│   └── zenodo_vpe55_manifest.json          # Zenodo deposit manifest
│
├── 02_Physics_of_Economic_Value_VPE21/     # VPE-21: Foundational Theory & SFC Modeling
│   ├── manuscript_vpe21.tex                # 15-page publication LaTeX manuscript
│   ├── sfc_model.py                        # 156-week Stock-Flow Consistent dynamic simulation
│   ├── test_value_physics.py               # Master automated verification test suite
│   ├── finite_boundary_stress_test.py      # Monte Carlo finite boundary exhaustion solver
│   ├── vpe21_latex_package.zip             # Self-contained LaTeX submission archive
│   └── zenodo_vpe21_manifest.json          # Zenodo deposit manifest
│
├── 03_Thermodynamic_State_Space_VPE49/     # VPE-49: Non-Linear State-Space Mechanics (JEDC)
│   ├── manuscript_vpe49.tex                # 37-page comprehensive theoretical treatise
│   ├── work_antiwork_dynamics.py           # Core ODE simulation and Lyapunov stability solver
│   ├── phase_portrait.png                  # Diamond Phase Space (P, A) vector field
│   ├── bifurcation_diagram.png             # Transcritical bifurcation and leverage boundary
│   ├── vpe49_latex_package.zip             # Self-contained LaTeX submission bundle
│   └── zenodo_v2.7.0_manifest.json         # Zenodo deposit manifest
│
├── tools/zenodo/                           # Zenodo REST API Upload & Automation Engine
│   ├── zenodo_uploader.py                  # CLI tool for automated depositions (Sandbox/Prod)
│   ├── README.md                           # Tool usage documentation
│   └── .env.example                        # API token configuration template
│
├── .zenodo.json                            # Zenodo automated GitHub Release metadata
├── CITATION.cff                            # Citation File Format (CFF)
└── README.md                               # This file
```

---

## Research Packages Overview

### 1. VPE-55: Empirical Pricing & RRP/D Fairness Audit
* **Target Journal:** *Ecological Economics* (Elsevier)
* **Deliverable ID:** `VPE-55` / `ARI-VPE-EMP-2026-03`
* **What it does:** Operationalizes the Universal Price Equation (UPE) against official Australian datasets (ABARES, ABS, AEMO, ACCC, NHVR) across 14 essential commodities (bread, wheat, milk, beef cattle, diesel, electricity, LPG, water cartage, waste collection, antibiotics, timber, concrete, steel mesh, and road freight). It calculates forward biophysical baseline prices (Recommended Retail Price based on Difficulty, RRP/D), reverse-engineers observed commercial prices to quantify institutional extractive drag ($R_a$), and establishes an ungameable fairness metric ($\Phi_{\text{fairness}}$).

**Run the empirical audit:**
```bash
python 01_Empirical_Pricing_Audit_VPE55/rrp_fairness_audit.py
```

---

### 2. VPE-21: The Physics of Economic Value
* **Target Journal:** *Ecological Economics*
* **Deliverable ID:** `VPE-21` / `ARI-VPE-JRNL-2026-01`
* **What it does:** Establishes the foundational micro-macro theory of Value Physics. Decomposes price into a three-layer substrate ($P_t = P_e + P_b + P_m$), derives the Lorentz Urgency Factor $\gamma(v_{\text{rel}})$ from Stone-Geary utility, formalizes the 56-cell supply chain matrix, and couples the equations to a 156-week Stock-Flow Consistent (SFC) dynamic simulation of an Australian regional agricultural collective under severe climate and interest-rate shocks.

**Run the verification suite:**
```bash
python 02_Physics_of_Economic_Value_VPE21/test_value_physics.py
```

---

### 3. VPE-49: Thermodynamic State-Space Dynamics
* **Target Journal:** *Journal of Economic Dynamics and Control* (Elsevier)
* **Deliverable ID:** `VPE-49` / `ARI-VPE-TH-2026-02`
* **What it does:** Develops the non-linear state-space mechanics of Value Physics. Separates instantaneous kinetic fluxes ($W_a, A_a$) from accumulated structural floors ($W_p, A_p$). Proves Theorem 1 (Norm Isometry under $45^\circ$ Diamond Phase Space Rotation), Theorem 2 (Fundamental Law of Passivity Asymmetry), and Theorem 3 (Autonomous Sclerosis Finite-Time Blowup), and formulates Unscented Kalman Filter state decouplers to separate biophysical carrying capacity ($R_n$) from monopoly toll extraction ($R_a$).

**Run the ODE simulation:**
```bash
python 03_Thermodynamic_State_Space_VPE49/work_antiwork_dynamics.py
```

---

## Zenodo Integration & Deposition

This repository supports two seamless deposition routes to [Zenodo](https://zenodo.org):

### Route A: Native GitHub Releases (Automatic Minting)
1. Link your GitHub account to Zenodo at [https://zenodo.org/account/settings/github/](https://zenodo.org/account/settings/github/).
2. Flip the switch next to the `value-physics` repository.
3. Every time you publish a release or push a tag (e.g. `git tag -a v1.0.0 -m "Release v1.0.0" && git push --tags`), Zenodo automatically takes a snapshot, archives the repository, reads `.zenodo.json`, and mints a permanent, citable DOI.

### Route B: Direct API Upload CLI (`tools/zenodo`)
To deposit individual package drafts or replication bundles directly to Zenodo via API:
```bash
# Dry-run validation:
python tools/zenodo/zenodo_uploader.py "01_Empirical_Pricing_Audit_VPE55" --dry-run

# Upload draft to Zenodo Sandbox:
python tools/zenodo/zenodo_uploader.py "01_Empirical_Pricing_Audit_VPE55" --sandbox --token <YOUR_TOKEN>

# Upload draft to Zenodo Production:
python tools/zenodo/zenodo_uploader.py "01_Empirical_Pricing_Audit_VPE55" --production --token <YOUR_TOKEN>
```

---

## Author Epistemic Disclaimer & Methodology

### 1. Conceptual Ownership & Author Positionality
The foundational equations, ontological definitions, and core theoretical principles of the **Universal Price Equation (UPE)** and **Value Physics** are the original intellectual work of **Jarrod Lyndsay Hamilton**.

The author holds **no formal background or academic credentials in economics**. The theoretical frameworks were developed independently through self-directed study, reading, and synthesizing what literature was accessible. Furthermore, due to documented cognitive memory impairment, the author may not actively retain specific textual details, academic citations, or literature specifics from the research and writing process. Readers and reviewers are explicitly encouraged to treat secondary economic literature interpretations with a grain of salt and evaluate the underlying mathematical formulations, computational simulations, and empirical derivations directly on their own intrinsic merits.

### 2. AI Assistance Disclosure
AI tooling (**Google Gemini / Gemini Spark**) was utilized as an assistive technology for computational implementation, automated unit testing, script verification, code translation, and LaTeX typesetting under the author's direct supervision and conceptual guidance.

---

## Citation

```bibtex
@software{hamilton2026valuephysics,
  author       = {Hamilton, Jarrod Lyndsay},
  title        = {Value Physics: Computational Replication Archive, Empirical Pricing Audits, and Theoretical Foundations},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.1755001},
  url          = {https://github.com/alisru/value-physics}
}
```

## License
* **Manuscripts, Figures, and Datasets:** [Creative Commons Attribution 4.0 International (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
* **Software and Simulation Code:** [MIT License](https://opensource.org/licenses/MIT)
