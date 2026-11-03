"""
Value Physics RRP Fairness Audit & Empirical Benchmarking Engine
Deliverable ID: VPE-54 | Alethekanon Research Institute — Division 2
Author: Jarrod Lyndsay Hamilton, Australia

Empirical testing suite for the Universal Price Equation (UPE):
  P = m1 * m2 * gamma(v_rel) * [(S * U) / (R_n * (1 - R_a))] + P_e + P_b

Calculates forward biophysical pricing, reverse-engineers observed commercial RRPs,
solves for extractive drag (R_a), and establishes objective Recommended Retail Prices
based on Difficulty (RRP/D).
"""

import math
import csv
from typing import Dict, Any, List

# Official Services Australia (20 Sep 2026), Fair Work Ombudsman (1 Jul 2026) & ABS (May 2026) Income Brackets
# Services Australia Fortnightly Rates converted to Weekly (/2.0):
Y_YA_AT_HOME_WEEKLY_AUD = 241.20          # Youth Allowance (Single 18+, living at parent home: $482.40/fn)
Y_YA_INDEPENDENT_WEEKLY_AUD = 338.60      # Youth Allowance (Single, living away from home: $677.20/fn)
Y_JSP_SINGLE_WEEKLY_AUD = 412.45          # JobSeeker Payment (Single, no children: $824.90/fn)
Y_DSP_BASELINE_WEEKLY_AUD = 618.85        # Disability Support Pension (Single 21+ max total: $1,237.70/fn) -> CANONICAL STRUCTURAL FLOOR
Y_NMW_NET_WEEKLY_AUD = 888.90             # National Minimum Wage Net Disposable (Gross $1,004.90/wk @ $26.44/hr, 38h)
Y_NMW_GROSS_WEEKLY_AUD = 1004.90          # National Minimum Wage Gross Full-Time (38h @ $26.44/hr, FWO 1 Jul 2026)
Y_MEDIAN_NET_WEEKLY_AUD = 1285.00         # All-Employees Net Disposable Weekly Income (Gross $1,579.20/wk, ABS May 2026)
Y_ALL_EMP_GROSS_WEEKLY_AUD = 1579.20      # All-Employees Average Weekly Total Earnings Gross (ABS May 2026)
Y_AWOTE_NET_WEEKLY_AUD = 1635.00          # Full-Time Adult AWOTE Net Disposable Weekly (Gross $2,083.70/wk, ABS May 2026)
Y_AWOTE_GROSS_WEEKLY_AUD = 2083.70        # Full-Time Adult Average Weekly Ordinary Time Earnings Gross (ABS May 2026)

AUSTRALIAN_INCOME_BRACKETS_WEEKLY_AUD = {
    "YA_At_Home": Y_YA_AT_HOME_WEEKLY_AUD,
    "YA_Away_From_Home": Y_YA_INDEPENDENT_WEEKLY_AUD,
    "JSP_Single": Y_JSP_SINGLE_WEEKLY_AUD,
    "DSP_Structural_Baseline": Y_DSP_BASELINE_WEEKLY_AUD,
    "NMW_Net_38hr": Y_NMW_NET_WEEKLY_AUD,
    "NMW_Gross_38hr": Y_NMW_GROSS_WEEKLY_AUD,
    "All_Employees_Net": Y_MEDIAN_NET_WEEKLY_AUD,
    "All_Employees_Gross": Y_ALL_EMP_GROSS_WEEKLY_AUD,
    "FT_AWOTE_Net": Y_AWOTE_NET_WEEKLY_AUD,
    "FT_AWOTE_Gross": Y_AWOTE_GROSS_WEEKLY_AUD,
}

# Canonical defaults: DSP ($618.85/wk) is the true permanent non-working structural subsistence floor;
# All-Employees Net ($1,285.00/wk) / Median ($1,250.00/wk) and NMW ($1,004.90/wk gross, $26.44/hr) anchor wage comparisons.
DEFAULT_WEEKLY_DISPOSABLE_INCOME_AUD = 1250.00  # Regional NSW Median Weekly Disposable Income reference
DEFAULT_SUBSISTENCE_WEEKLY_INCOME_AUD = Y_DSP_BASELINE_WEEKLY_AUD  # $618.85/wk Disability Support Pension structural floor
STANDARD_WEEKLY_WORK_HOURS = 38.0               # Standard full-time Australian workweek (NES = 38.0 hours)
DEFAULT_NET_HOURLY_WAGE_AUD = DEFAULT_WEEKLY_DISPOSABLE_INCOME_AUD / STANDARD_WEEKLY_WORK_HOURS  # ~$32.8947/hr
NMW_HOURLY_WAGE_AUD = 26.44                     # Official FWO National Minimum Wage ($26.44/hr from 1 July 2026)

def calculate_gamma(v_rel: float, eps: float = 1e-16) -> float:
    """Calculates the relativistic urgency/coercion factor gamma(v_rel)."""
    v_capped = min(max(v_rel, 0.0), 1.0 - eps)
    return 1.0 / math.sqrt(1.0 - v_capped**2)

def calculate_forward_upe(
    P_e: float,
    P_b: float,
    U: float,
    S: float = 1.0,
    R_n: float = 1.0,
    R_a: float = 0.0,
    m1: float = 1.0,
    m2: float = 1.0,
    v_rel: float = 0.0,
    eps: float = 1e-16
) -> float:
    """Computes forward price from biophysical, energetic, and metabolic difficulty inputs."""
    gamma = calculate_gamma(v_rel, eps)
    denom = max(R_n * (1.0 - min(R_a, 1.0 - eps)), eps)
    metabolic_tier = m1 * m2 * gamma * ((S * U) / denom)
    return metabolic_tier + P_e + P_b

# Stock-Flow Consistent (SFC) Destination Decomposition of Extractive Drag (Ra)
# Grounded in VPE-38 (sfc_model.py) Godley-Lavoie Flow-of-Funds Matrix & ABS/ACCC Sectoral Margin Audits:
SFC_EXTRACTIVE_SINK_SHARES = {
    "Sink_1_Compound_Debt_Interest_Service": 0.38,       # 38%: Corporate, infrastructure (RAB) & working-capital interest/debt service
    "Sink_2_Commercial_Property_REIT_Land_Rent": 0.27,   # 27%: Retail/industrial leases & port/terminal tolls (pledged to commercial mortgages)
    "Sink_3_Oligopoly_Dividends_Buybacks_EBIT": 0.22,    # 22%: Net oligopoly equity payouts & executive rent extraction
    "Sink_4_Speculative_Brokerage_AntiWork_Admin": 0.13, # 13%: Futures hedging desks, multi-tier middleman brokerage & non-productive admin
}

def decompose_extractive_drag_sinks(extractive_premium_aud: float) -> Dict[str, float]:
    """
    Decomposes the Extractive Premium (P_retail - RRP/D) into its four macroeconomic
    Stock-Flow Consistent (SFC) destination sinks, quantifying how much of the unfair
    price markup goes to servicing compound debt & bad/inflated asset valuations.
    """
    prem = max(0.0, extractive_premium_aud)
    s1 = prem * SFC_EXTRACTIVE_SINK_SHARES["Sink_1_Compound_Debt_Interest_Service"]
    s2 = prem * SFC_EXTRACTIVE_SINK_SHARES["Sink_2_Commercial_Property_REIT_Land_Rent"]
    s3 = prem * SFC_EXTRACTIVE_SINK_SHARES["Sink_3_Oligopoly_Dividends_Buybacks_EBIT"]
    s4 = prem * SFC_EXTRACTIVE_SINK_SHARES["Sink_4_Speculative_Brokerage_AntiWork_Admin"]
    return {
        "Sink_1_Compound_Debt_Interest_AUD": round(s1, 4),
        "Sink_2_Commercial_Land_Rent_Mortgages_AUD": round(s2, 4),
        "Sink_3_Oligopoly_Dividends_EBIT_AUD": round(s3, 4),
        "Sink_4_Brokerage_AntiWork_Admin_AUD": round(s4, 4),
        "Combined_Debt_And_Mortgage_Service_Share_AUD": round(s1 + s2, 4),
        "Combined_Debt_And_Mortgage_Service_Pct_Of_Drag": 65.0,
    }

def calculate_index_metrics(
    P_retail: float,
    rrp_d: float,
    weekly_income_Y: float = DEFAULT_WEEKLY_DISPOSABLE_INCOME_AUD,
    subsistence_income_Y: float = DEFAULT_SUBSISTENCE_WEEKLY_INCOME_AUD,
    weekly_hours: float = STANDARD_WEEKLY_WORK_HOURS,
    eps: float = 1e-16
) -> Dict[str, float]:
    """
    Computes the Income Normalised Difficulty Examination (INDEX) metrics:
    Expresses commercial RRP, fair biophysical RRP/D, and extractive rentier drag
    as relative shares (%) of disposable weekly income and working life minutes.
    """
    y_med = max(weekly_income_Y, eps)
    y_sub = max(subsistence_income_Y, eps)
    w_net = y_med / max(weekly_hours, eps)
    extractive_premium = max(0.0, P_retail - rrp_d)

    # Percentage of Weekly Disposable Income (Median Regional Earner)
    index_obs_med_pct = (P_retail / y_med) * 100.0
    index_rrpd_med_pct = (rrp_d / y_med) * 100.0
    index_toll_med_pct = (extractive_premium / y_med) * 100.0

    # Percentage of Weekly Subsistence / Minimum Income (Low-Income Earner)
    index_obs_sub_pct = (P_retail / y_sub) * 100.0
    index_rrpd_sub_pct = (rrp_d / y_sub) * 100.0
    index_toll_sub_pct = (extractive_premium / y_sub) * 100.0

    # Working Life Equivalent in Minutes (at Median Net Hourly Wage w_net)
    labor_min_obs = (P_retail / w_net) * 60.0
    labor_min_rrpd = (rrp_d / w_net) * 60.0
    labor_min_confiscated = (extractive_premium / w_net) * 60.0

    # Multi-Bracket Statutory Welfare & Wage Normalisations (% of Weekly Income)
    bracket_shares = {}
    for b_name, b_inc in AUSTRALIAN_INCOME_BRACKETS_WEEKLY_AUD.items():
        bracket_shares[f"INDEX_Obs_Pct_{b_name}"] = round((P_retail / b_inc) * 100.0, 4)
        bracket_shares[f"INDEX_RRPD_Pct_{b_name}"] = round((rrp_d / b_inc) * 100.0, 4)
        bracket_shares[f"INDEX_Toll_Pct_{b_name}"] = round((extractive_premium / b_inc) * 100.0, 4)

    # Minimum Wage Labor Minutes (at FWO National Minimum Wage $26.44/hr gross)
    nmw_min_obs = (P_retail / NMW_HOURLY_WAGE_AUD) * 60.0
    nmw_min_rrpd = (rrp_d / NMW_HOURLY_WAGE_AUD) * 60.0
    nmw_min_confiscated = (extractive_premium / NMW_HOURLY_WAGE_AUD) * 60.0

    out = {
        "INDEX_Observed_Pct_DSP_Baseline": round((P_retail / Y_DSP_BASELINE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_RRPD_Pct_DSP_Baseline": round((rrp_d / Y_DSP_BASELINE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Extractive_Toll_Pct_DSP_Baseline": round((extractive_premium / Y_DSP_BASELINE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Observed_Pct_JSP_Single": round((P_retail / Y_JSP_SINGLE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_RRPD_Pct_JSP_Single": round((rrp_d / Y_JSP_SINGLE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Extractive_Toll_Pct_JSP_Single": round((extractive_premium / Y_JSP_SINGLE_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Observed_Pct_YA_Away": round((P_retail / Y_YA_INDEPENDENT_WEEKLY_AUD) * 100.0, 4),
        "INDEX_RRPD_Pct_YA_Away": round((rrp_d / Y_YA_INDEPENDENT_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Extractive_Toll_Pct_YA_Away": round((extractive_premium / Y_YA_INDEPENDENT_WEEKLY_AUD) * 100.0, 4),
        "INDEX_Observed_Pct_Median_Income": round(index_obs_med_pct, 4),
        "INDEX_RRPD_Pct_Median_Income": round(index_rrpd_med_pct, 4),
        "INDEX_Extractive_Toll_Pct_Median_Income": round(index_toll_med_pct, 4),
        "INDEX_Observed_Pct_Subsistence_Income": round(index_obs_sub_pct, 4),
        "INDEX_RRPD_Pct_Subsistence_Income": round(index_rrpd_sub_pct, 4),
        "INDEX_Extractive_Toll_Pct_Subsistence_Income": round(index_toll_sub_pct, 4),
        "Labor_Minutes_Observed": round(labor_min_obs, 2),
        "Labor_Minutes_Fair_RRPD": round(labor_min_rrpd, 2),
        "Labor_Minutes_Confiscated": round(labor_min_confiscated, 2),
        "NMW_Labor_Minutes_Observed": round(nmw_min_obs, 2),
        "NMW_Labor_Minutes_Fair_RRPD": round(nmw_min_rrpd, 2),
        "NMW_Labor_Minutes_Confiscated": round(nmw_min_confiscated, 2),
    }
    out.update(bracket_shares)
    return out

def audit_commercial_rrp(
    commodity: str,
    unit: str,
    sector: str,
    P_retail: float,
    P_e: float,
    P_b: float,
    U: float,
    S: float = 1.0,
    R_n: float = 1.0,
    v_rel: float = 0.0,
    m1: float = 1.0,
    m2: float = 1.0,
    fair_reserve_Ra: float = 0.02,
    weekly_income_Y: float = DEFAULT_WEEKLY_DISPOSABLE_INCOME_AUD,
    subsistence_income_Y: float = DEFAULT_SUBSISTENCE_WEEKLY_INCOME_AUD,
    weekly_hours: float = STANDARD_WEEKLY_WORK_HOURS,
    eps: float = 1e-16
) -> Dict[str, Any]:
    gamma = calculate_gamma(v_rel, eps)
    p_phys = P_e + P_b
    spread = P_retail - p_phys
    w_num = m1 * m2 * gamma * S * U
    m_pure = w_num / max(R_n, eps)
    m_fair = (gamma * S * U) / max(R_n * (1.0 - fair_reserve_Ra), eps)
    
    if spread <= eps:
        implied_Ra = 0.0
    else:
        ratio = m_pure / spread
        implied_Ra = max(0.0, min(1.0 - ratio, 1.0))
        
    rrp_d = calculate_forward_upe(
        P_e=P_e,
        P_b=P_b,
        U=U,
        S=S,
        R_n=R_n,
        R_a=fair_reserve_Ra,
        m1=1.0,
        m2=1.0,
        v_rel=v_rel,
        eps=eps
    )
    
    extractive_premium = max(0.0, P_retail - rrp_d)
    fairness_index = min(1.0, rrp_d / max(P_retail, eps))
    index_metrics = calculate_index_metrics(
        P_retail=P_retail,
        rrp_d=rrp_d,
        weekly_income_Y=weekly_income_Y,
        subsistence_income_Y=subsistence_income_Y,
        weekly_hours=weekly_hours,
        eps=eps
    )
    
    prec = 4 if "nt-km" in unit else 2
    fmt = f".{prec}f"
    working_out_str = (
        f"[Step 1: Biophysical Base] P_phys = P_e (${P_e:{fmt}}) + P_b (${P_b:{fmt}}) = ${p_phys:{fmt}}; "
        f"[Step 2: Observed Spread] Delta_spread = P_retail (${P_retail:{fmt}}) - P_phys (${p_phys:{fmt}}) = ${spread:{fmt}}; "
        f"[Step 3: Lorentz Coercion] gamma({v_rel:.2f}) = 1/sqrt(1 - {v_rel:.2f}^2) = {gamma:.4f}; "
        f"[Step 4: Metabolic Numerator] W_num = gamma ({gamma:.4f}) * S ({S:.2f}) * U ({U:{fmt}}) = {w_num:.4f}; "
        f"[Step 5: Pure Metabolic Cost] M_pure = W_num ({w_num:.4f}) / R_n ({R_n:.2f}) = ${m_pure:.4f}; "
        f"[Step 6: Fair Metabolic Tier (Ra=0.02)] M_fair = M_pure (${m_pure:.4f}) / 0.98 = ${m_fair:.4f}; "
        f"[Step 7: Fair RRP/D] RRP/D = P_phys (${p_phys:{fmt}}) + M_fair (${m_fair:.4f}) = ${rrp_d:{fmt}}; "
        f"[Step 8: Implied Drag Ra] Ra = 1 - (M_pure ${m_pure:.4f} / Delta_spread ${spread:{fmt}}) = {implied_Ra*100.0:.1f}%; "
        f"[Step 9: Premium & Fairness] Delta_P = ${P_retail:{fmt}} - ${rrp_d:{fmt}} = ${extractive_premium:{fmt}}, "
        f"Fairness = (${rrp_d:{fmt}} / ${P_retail:{fmt}}) * 100 = {fairness_index*100.0:.1f}%; "
        f"[Step 10: DSP INDEX ($618.85/wk) & NMW ($26.44/hr)] "
        f"INDEX_Obs = {index_metrics['INDEX_Observed_Pct_DSP_Baseline']:.2f}%, "
        f"INDEX_RRPD = {index_metrics['INDEX_RRPD_Pct_DSP_Baseline']:.2f}%, "
        f"INDEX_Toll = {index_metrics['INDEX_Extractive_Toll_Pct_DSP_Baseline']:.2f}%, "
        f"Confiscated_NMW = {index_metrics['NMW_Labor_Minutes_Confiscated']:.2f} min"
    )
    
    res = {
        "commodity": commodity,
        "unit": unit,
        "sector": sector,
        "P_retail_observed": round(P_retail, prec),
        "P_energy_Pe": round(P_e, prec),
        "P_base_Pb": round(P_b, prec),
        "P_phys_Pe_plus_Pb": round(p_phys, prec),
        "Observed_Metabolic_Spread_Delta": round(spread, prec),
        "Metabolic_U": round(U, prec),
        "Scarcity_S": round(S, 2),
        "Regen_Capacity_Rn": round(R_n, 2),
        "Relativistic_Urgency_vrel": round(v_rel, 2),
        "Lorentz_Gamma": round(gamma, 4),
        "Unextracted_Metabolic_Numerator_W": round(w_num, 4),
        "Pure_Metabolic_Cost_M_pure": round(m_pure, 4),
        "Fair_Metabolic_Tier_M_fair": round(m_fair, 4),
        "RRP_D_recommended": round(rrp_d, prec),
        "Implied_Extractive_Drag_Ra": round(implied_Ra, 4),
        "Extractive_Premium_AUD": round(extractive_premium, prec),
        "Fairness_Index_Percent": round(fairness_index * 100.0, 1),
        "Step_By_Step_Working_Out": working_out_str,
    }
    res.update(index_metrics)
    return res

def get_australian_benchmark_dataset() -> List[Dict[str, Any]]:
    return [
        {
            "commodity": "Commercial Sliced White Bread (680g)",
            "unit": "loaf",
            "sector": "Sector 1 (Food / Subsistence)",
            "P_retail": 4.10,
            "P_e": 0.38,  # Bakery gas/electricity, delivery logistics fuel
            "P_b": 0.45,  # Milling flour, yeast, salt, packaging film
            "U": 2.15,    # Broadacre farm labor, milling, industrial baking, retail shelf stocking
            "S": 1.00,    # Normal seasonal grain availability
            "R_n": 1.00,   # Fully renewable annual cropping cycle
            "v_rel": 0.05  # Moderate daily consumption urgency
        },
        {
            "commodity": "Milling Wheat (APW1 / ASW1)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Feedstock)",
            "P_retail": 365.00,
            "P_e": 104.40,  # Tractor diesel, harvest fuel, grain drying thermal exergy
            "P_b": 82.00,   # Certified seed stock, soil mineral replenishment, ag-chemicals
            "U": 95.00,     # Agronomic labor hours across 4,000 ha broadacre rotation
            "S": 1.05,      # Post-harvest storage scarcity buffer
            "R_n": 0.98,    # Soil organic carbon regeneration index
            "v_rel": 0.02   # Grain storage temporal buffer
        },
        {
            "commodity": "Fresh Full Cream Milk (Full Fat)",
            "unit": "litre",
            "sector": "Sector 1 (Food / Dairy Subsistence)",
            "P_retail": 2.10,
            "P_e": 0.31,  # Farm milk vat chilling, tanker refrigeration, HTST pasteurisation, store fridge
            "P_b": 0.48,  # Pasture feed, silage, grain concentrates, veterinary, HDPE bottle & cap
            "U": 0.75,    # Twice-daily herd milking labor, processing plant techs, tanker driver, dairy stocking
            "S": 1.05,    # Seasonal regional milk production buffer
            "R_n": 0.95,   # Dairy herd lactation and pasture regrowth capacity
            "v_rel": 0.10  # Highly perishable 14-day cold-chain product; captive dairy farmer supply
        },
        {
            "commodity": "Farmgate Beef Cattle Weaners (British Breed)",
            "unit": "kg liveweight",
            "sector": "Sector 1 (Food / Pastoral Livestock)",
            "P_retail": 3.85,  # $1,155 per 300kg steer at regional saleyard auction
            "P_e": 0.42,  # Paddock stock water solar/diesel pumping exergy, farm ute & cattle truck transport fuel
            "P_b": 1.15,  # Breeding cow maintenance depreciation, pasture superphosphate, mineral lick, vaccines, NLIS tags
            "U": 1.25,    # Extensive pastoral grazing labor (calving watch, muster, yard drafting, cattle handling)
            "S": 1.15,    # Post-drought maternal breeding herd rebuilding demand
            "R_n": 0.85,   # Perennial pasture seasonal regrowth & 9-month bovine gestation recovery cycle
            "v_rel": 0.15  # Summer pasture biomass drying coercion (graziers cannot hold stock without costly supplementary feed)
        },
        {
            "commodity": "Automotive Diesel Fuel (Ultra-Low Sulphur)",
            "unit": "litre",
            "sector": "Sector 2 (Energy / Liquid Fuels)",
            "P_retail": 2.15,
            "P_e": 0.32,  # Refinery thermal cracking, electricity, pipeline pressure
            "P_b": 0.92,  # Crude oil feedstock at terminal import parity price (TIPP)
            "U": 0.35,    # Terminal logistics, road tanker transport driver, service station operator
            "S": 1.08,    # Regional NSW freight corridor supply buffer
            "R_n": 0.90,   # Non-renewable fossil depletion replenishment drag
            "v_rel": 0.12  # Regional transport operational dependency
        },
        {
            "commodity": "Residential Grid Electricity (Single-Rate Flat)",
            "unit": "kWh",
            "sector": "Sector 2 (Energy / Power Utility)",
            "P_retail": 0.36,
            "P_e": 0.08,  # NEM wholesale generation thermal energy & line transmission losses
            "P_b": 0.07,  # Physical poles, wires, transformer capital depreciation base
            "U": 0.09,    # Lineworker maintenance shifts, dispatch engineering, billing admin
            "S": 1.15,    # Peak demand grid stress multiplier
            "R_n": 0.92,   # Renewable generation firmness and battery storage renewal
            "v_rel": 0.08  # Essential domestic heating/cooling baseline
        },
        {
            "commodity": "LPG Bottled Gas (45kg Domestic Cylinder)",
            "unit": "45kg cylinder",
            "sector": "Sector 2 (Energy / Liquid Petroleum Gas)",
            "P_retail": 165.00,  # Regional delivered exchange cylinder price
            "P_e": 29.40,  # Propane distillation, compression exergy, tanker haulage, local delivery truck diesel
            "P_b": 58.36,  # Liquid propane feedstock (88L @ import parity), 10-year cylinder testing amortisation, brass valves
            "U": 28.50,    # Hazardous goods driver exertion, manual 90kg cylinder trolley handling, safety coupling
            "S": 1.15,    # Regional distance from coastal import terminals & winter heating peak
            "R_n": 0.88,   # Associated petroleum/natural gas depleting fossil reserves
            "v_rel": 0.16  # Winter domestic heating/cooking dependence in unreticulated regional towns
        },
        {
            "commodity": "Bulk Potable Water Cartage (Regional NSW)",
            "unit": "kL (1,000L)",
            "sector": "Sector 3 (Water / Municipal Subsistence)",
            "P_retail": 15.50, # $155.00 per 10,000L heavy vehicle delivery load
            "P_e": 4.32,  # Class 4 heavy rigid tanker diesel transport (40 km roundtrip) + booster pumping
            "P_b": 3.95,  # Council treated potable standpipe tariff ($3.20/kL) + food-grade hose/tanker maintenance
            "U": 3.20,    # Heavy tanker operator driving hours, standpipe loading, rural tank discharge
            "S": 1.30,    # Regional drought rainfall deficit in Warrumbungle Shire
            "R_n": 0.75,   # Castlereagh river basin and groundwater aquifer recharge capacity
            "v_rel": 0.25  # High existential urgency (empty domestic rainwater tanks in unserviced rural zone)
        },
        {
            "commodity": "Domestic Waste Collection (Regional NSW)",
            "unit": "weekly bin lift",
            "sector": "Sector 3/5 (Municipal Sanitation & Care)",
            "P_retail": 9.33,  # $485.00 annual domestic waste service charge / 52 weeks
            "P_e": 2.45,  # Heavy dual-control side-loader compactor truck diesel & hydraulic PTO exergy
            "P_b": 1.85,  # Mobile 240L HDPE bin depreciation, compactor chassis maintenance, transfer station upkeep
            "U": 2.15,    # Driver operational vigilance, repetitive route control, early shift labor
            "S": 1.20,    # Local landfill airspace capacity & EPA buffer zoning regulations
            "R_n": 0.72,   # Landfill environmental assimilation & leachate treatment capacity
            "v_rel": 0.22  # Statutory non-discretionary municipal public health monopoly
        },
        {
            "commodity": "Prescription Antibiotic (Amoxicillin 500mg, 20 Caps)",
            "unit": "dispensing course",
            "sector": "Sector 5 (Care / Essential Healthcare)",
            "P_retail": 16.50,  # Benchmark private retail pharmacy price (non-PBS subsidized)
            "P_e": 2.10,  # Sterile fermentation bioprocessing exergy, cleanroom HVAC, spray-drying, blister thermoforming heat
            "P_b": 3.20,  # 10g pure amoxicillin trihydrate API powder, excipients, gelatin capsule shells, PVC blister foil, carton
            "U": 5.80,    # Certified community pharmacist clinical checking, drug interaction screening, labeling, patient counseling
            "S": 1.20,    # Global API manufacturing concentration & offshore supply chain bottleneck buffer
            "R_n": 0.94,   # Biochemical fermentation enzymatic synthesis replenishment capacity
            "v_rel": 0.35  # Severe biological bacterial infection urgency (delaying treatment risks systemic complications)
        },
        {
            "commodity": "Residential Structural Softwood Timber (MGP10 90x45mm Pine)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Building Construction)",
            "P_retail": 7.20,
            "P_e": 0.85,  # Forestry harvesting diesel, kiln drying thermal gas, sawmill electricity
            "P_b": 1.20,  # Plantation stumpage royalty, seedling renewal, land management
            "U": 2.10,    # Mechanical harvester operators, sawmill processing, timber yard logistics
            "S": 1.25,    # Post-Black Summer bushfire plantation resource deficit
            "R_n": 0.88,   # 28-year radiata pine rotation cycle renewal capacity
            "v_rel": 0.15  # Fixed-price builder contract milestone completion urgency
        },
        {
            "commodity": "Pre-Mixed Ready-Mix Concrete (N20 20 MPa Structural)",
            "unit": "cubic metre",
            "sector": "Sector 4 (Shelter / Building Construction)",
            "P_retail": 295.00,
            "P_e": 62.00,  # Cement kiln clinker calcination exergy, quarry crushing, agitator fuel
            "P_b": 78.00,  # Portland cement, washed coarse basalt aggregate, river sand, admixtures
            "U": 58.00,    # Quarry operators, batch plant batcher, agitator transit driver, QC testing
            "S": 1.15,    # Metro infrastructure pouring demand pressure
            "R_n": 0.85,   # Virgin aggregate non-renewable mineral depletion index
            "v_rel": 0.20  # 90-minute initial setting window / slump loss transit coercion
        },
        {
            "commodity": "Structural Steel Reinforcing Mesh (SL82, 6.0m x 2.4m Sheet)",
            "unit": "sheet (14.4 m2)",
            "sector": "Sector 4 (Shelter / Building Construction)",
            "P_retail": 128.00,
            "P_e": 28.50,  # Blast furnace coke exergy, EAF electric scrap melting, rod rolling & cross-welding
            "P_b": 36.80,  # 41 kg iron ore / scrap billet base, chemical pickling, anti-corrosive scale coating
            "U": 22.50,    # Heavy metallurgical steelworkers, continuous caster operators, automated grid welders
            "S": 1.12,    # Regional construction delivery buffer & NSW residential slab demand
            "R_n": 0.82,   # Steel closed-loop recyclability modulated by non-renewable virgin ore/coke depletion
            "v_rel": 0.18  # Concrete slab pour critical path inspection sequencing urgency
        },
        {
            "commodity": "Bulk Road Freight Transport (Newell Highway B-Double Corridor)",
            "unit": "net tonne-km",
            "sector": "Sector 2/4 (Logistics / Spatial Freight)",
            "P_retail": 0.1250, # $5.00/km loaded B-Double rate for a 40-tonne payload
            "P_e": 0.0345,  # 55 L/100km loaded B-Double diesel exergy across Newell Highway freight corridor
            "P_b": 0.0285,  # Prime mover/trailer chassis capital depreciation, 34 radial tyres, scheduled servicing, tolls
            "U": 0.0210,    # Long-haul HVNL driving shift vigilance, physical hitching/tarping, loading dock detention
            "S": 1.10,      # Regional directional freight imbalance (headhaul vs. backhaul)
            "R_n": 0.92,    # Highway pavement infrastructure renewal capacity
            "v_rel": 0.14   # Supermarket JIT supply chain penalty windows & perishable produce transit urgency
        },
        {
            "commodity": "Australian Merino Greasy Wool (19-Micron Fleece)",
            "unit": "kg clean",
            "sector": "Sector 1/4 (Agri-Fiber / Thermal Shelter)",
            "P_retail": 15.50,
            "P_e": 1.45,  # Shearing shed diesel generator, hydraulic wool press, farm vehicle mustering, regional road haulage
            "P_b": 2.20,  # Veterinary drench, flystrike prevention, pasture trace mineral licks, nylon woolpacks
            "U": 5.60,    # Contract shearing labor, wool classing, year-round flock husbandry, crutching, drafting
            "S": 1.10,    # Seasonal shearing flush & auction cataloguing buffer
            "R_n": 0.88,  # Rangeland perennial pasture regeneration rate
            "v_rel": 0.08 # Annual shearing operating cashflow constraint
        },
        {
            "commodity": "Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)",
            "unit": "monthly service",
            "sector": "Sector 5/6 (Digital Infrastructure / Utilities)",
            "P_retail": 85.00,
            "P_e": 4.80,  # Fiber line termination laser power, street node active power, POI routing exergy, data center cooling
            "P_b": 14.50, # Subterranean duct amortization, optical line terminal depreciation, NTD hardware, cable pit maintenance
            "U": 12.20,   # Network operations center (NOC) engineering, field fiber splicing, customer service fault resolution
            "S": 1.05,    # Peak evening hour CVC bandwidth contention buffer
            "R_n": 0.95,  # Optical component lifecycle renewal & battery backup maintenance
            "v_rel": 0.15 # Non-discretionary telework, educational access, and telehealth dependence
        },
        {
            "commodity": "Prescription Salbutamol Inhaler (100mcg CFC-Free MDI, 200 Doses)",
            "unit": "inhaler unit",
            "sector": "Sector 5 (Care / Essential Healthcare)",
            "P_retail": 12.50,
            "P_e": 0.65,  # Cleanroom HVAC filtration, cryogenic propellant liquefaction, sterile processing
            "P_b": 1.35,  # Micronized salbutamol sulfate, HFA-134a propellant, aluminum canister, metering valve, actuator
            "U": 3.40,    # GMP cleanroom technicians, batch release testing, pharmacist clinical consultation
            "S": 1.10,    # TGA batch certification regulatory buffer
            "R_n": 0.92,  # Chemical synthesis active precursor availability & propellant supply
            "v_rel": 0.40 # Acute asthma/bronchospasm life-safety urgency
        },
        {
            "commodity": "Urban Reticulated Potable Water (Municipal Pipeline Tariff)",
            "unit": "kL (1,000L)",
            "sector": "Sector 3 (Water / Municipal Utility)",
            "P_retail": 3.60,
            "P_e": 0.48,  # Intake river/dam pump electricity, water treatment filtration, elevated reservoir booster pumping
            "P_b": 0.62,  # Alum coagulant, chlorine disinfection, pH adjustment lime, pipeline capital maintenance depreciation
            "U": 1.15,    # Certified treatment plant operators, mains burst maintenance crew, microbiological water quality testing
            "S": 1.15,    # Regional inland catchment storage level & seasonal restriction buffer
            "R_n": 0.80,  # River basin inflow replenishment & environmental flow allocation
            "v_rel": 0.20 # Essential daily residential hydration and municipal sanitation
        },
        {
            "commodity": "Commercial Broiler Chicken (Whole Fresh Dressed Bird)",
            "unit": "kg dressed",
            "sector": "Sector 1 (Food / Poultry Subsistence)",
            "P_retail": 4.50,
            "P_e": 0.46,  # Broiler shed climate control ventilation/heating, feed milling, abattoir spin chilling
            "P_b": 1.68,  # Formulated grain feed (FCR 1.65), day-old chick cost, bedding litter, barrier packaging
            "U": 1.15,    # Shed management labor, bird catching, abattoir processing line, supermarket display
            "S": 1.05,    # Short biological growing cycle elasticity vs cold-chain buffer
            "R_n": 0.95,  # Rapid flock cycle turnover & high grain-to-protein conversion efficiency
            "v_rel": 0.12 # Perishable fresh meat cold-chain urgency
        },
        {
            "commodity": "Standard Extruded Clay Facing Bricks (Common Structural Masonry)",
            "unit": "1,000 bricks",
            "sector": "Sector 4 (Shelter / Building Construction)",
            "P_retail": 1150.00,
            "P_e": 278.00, # Tunnel kiln gas firing at 1050-1150 C, pugmill/extrusion electricity, flatbed transport
            "P_b": 182.00, # Natural clay/shale royalty, sand, barium efflorescence additive, kiln furniture wear, pallets
            "U": 185.00,   # Quarry extraction, extrusion line setup, kiln surveillance, robotic setting, crane offloading
            "S": 1.12,     # Regional construction demand buffer & kiln batch firing schedules
            "R_n": 0.82,   # Non-renewable clay pit depletion and refractory degradation
            "v_rel": 0.18  # Critical-path bricklaying sequencing in residential construction
        },
        {
            "commodity": "Coarse Solar Sea Salt (Unrefined Food & Livestock Grade)",
            "unit": "25kg bag",
            "sector": "Sector 1/3 (Food / Mineral Subsistence)",
            "P_retail": 14.50,
            "P_e": 1.65,  # Seawater intake pumping, pan harvesting, mechanical washing, bagging electricity, road freight
            "P_b": 2.10,  # Seawater brine royalty, pan levee maintenance, multi-wall woven PP bag, pallets, stretch wrap
            "U": 4.20,    # Pan brine density monitoring, harvester operation, wash screening, bagging QC, warehouse handling
            "S": 1.05,    # Abundant oceanic supply modulated by seasonal rainfall in evaporation pans
            "R_n": 0.96,  # Inexhaustible tidal seawater recharge and high solar insolation renewal
            "v_rel": 0.06 # Non-perishable essential biological mineral nutrient with stable shelf buffer
        },
        {
            "commodity": "Raw Centrifugal Cane Sugar (Bulk Crystal Milling Feedstock)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Carbohydrate)",
            "P_retail": 620.00,
            "P_e": 142.00, # Cane harvesting diesel, bin locomotive haulage, mill crushing tandems, vacuum pan boiling, centrifuge
            "P_b": 168.00, # Cane stool planting sets amortization, fertilizer, herbicides, mill roller re-shelling, bulk storage
            "U": 145.00,   # Sugarcane agronomic management, laser leveling, harvester haul-out driving, boiler/pan operators, QC lab
            "S": 1.08,     # Seasonal tropical crushing window buffer against weather delays
            "R_n": 0.90,   # Annual ratoon crop vegetative regrowth capacity modulated by soil nutrient depletion
            "v_rel": 0.05  # Non-perishable dry bulk carbohydrate crystal storage stability
        },
        {
            "commodity": "HDPE Rural Water Reticulation Pipe (32mm PN12.5, 100m Coil)",
            "unit": "100m coil",
            "sector": "Sector 3/4 (Water & Agricultural Infrastructure)",
            "P_retail": 245.00,
            "P_e": 48.50,  # Virgin polymer extrusion motor, barrel heating to 200 C, vacuum bath cooling, transport
            "P_b": 68.00,  # PE100 resin pellets (28kg), carbon black UV stabilizer, die tooling wear, wooden strapping
            "U": 38.00,    # Extruder line setup, ultrasonic wall-thickness QC testing, coiler operation, merchant loading
            "S": 1.10,     # Regional agricultural drought infrastructure buffer & pipe demand spikes
            "R_n": 0.88,   # Petrochemical polymer fossil reliance and extrusion machinery renewal
            "v_rel": 0.16  # Critical stock watering emergency repair urgency on rural grazing properties
        },
        {
            "commodity": "Farmgate Canola Grain (Bulk Non-GM Oilseed)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Vegetable Oil & Protein Meal)",
            "P_retail": 685.00,
            "P_e": 118.50, # Broadacre tractor diesel for direct drilling, spraying, swathing, combine harvesting, haulage
            "P_b": 215.00, # Hybrid seed sets, high-rate nitrogen/sulfur fertilizers, fungicides, harvester capital depreciation
            "U": 112.00,   # Agronomic surveillance, precision spraying, swathing, combine operation, oil sampling
            "S": 1.08,     # Frost risk, seasonal winter rain dependency, and oilseed crush capacity buffer
            "R_n": 0.92,   # Annual cropping cycle with rotational soil disease break benefits for wheat
            "v_rel": 0.04  # Stable dry bulk oilseed on-farm aerated silo storage buffer
        },
        {
            "commodity": "Commercial FIBC Polypropylene Bulk Bags (1-Tonne Woven Container)",
            "unit": "bag",
            "sector": "Sector 1/4 (Agri-Logistics & Storage Infrastructure)",
            "P_retail": 24.50,
            "P_e": 4.20,  # Propylene polymerization/extrusion, circular loom weaving, cutting/sewing power, transport
            "P_b": 5.90,  # Virgin PP resin (1.85kg), UV masterbatch, heavy lifting webbing loops (0.45kg), thread, bundle packaging
            "U": 4.80,    # Loom setup technicians, industrial seamstress fabrication, SWL pull-testing, baling press, forklift handling
            "S": 1.08,    # Harvest seasonal grain/fertilizer bagging demand spikes and overseas container supply lead-times
            "R_n": 0.90,  # Petrochemical polymer fossil reliance, reusable for 2-4 cycles if unweathered, recyclable PP
            "v_rel": 0.12 # Seed grain bagging or fertilizer loading urgency during tight seasonal agricultural windows
        },
        {
            "commodity": "Bulk Portland Cement (General Purpose GP Clinker)",
            "unit": "tonne",
            "sector": "Sector 4 (Shelter / Building Construction)",
            "P_retail": 345.00,
            "P_e": 112.00, # Quarry blasting/haulage diesel, raw grinding, rotary kiln 1450 C pyroprocessing (3.4 GJ/t), finish grinding, tanker haulage
            "P_b": 84.00,  # Limestone/shale/sand/iron royalties (1.55t raw meal/t clinker), gypsum setting regulator (5%), kiln refractory brick wear
            "U": 56.00,   # Heavy quarry operators, raw mill chemical/XRF testing, kiln lead burner, millwrights, pneumatic tanker drivers
            "S": 1.12,     # Continuous kiln thermal inertia, clinker import shipping lead-times, and regional concrete pouring schedules
            "R_n": 0.78,   # Non-renewable limestone/shale geological deposit extraction, refractory wear, carbon calcination degradation
            "v_rel": 0.15  # Continuous construction concrete pour sequencing; batching plants cannot pause structural slab pours
        },
        {
            "commodity": "Corrugated Galvanized Steel Roofing Sheets (Custom Orb 0.42mm BMT)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Building Envelope Roofing)",
            "P_retail": 21.50,
            "P_e": 4.85,  # Blast furnace coke smelting, hot/cold rolling electric motors, continuous zinc pot heating, roll-forming, freight
            "P_b": 6.20,  # Iron ore lump, coking coal, limestone flux, SHG zinc coating (Z275 = 275g/m2), roll-forming tooling wear, pallets
            "U": 3.80,    # Steel mill operators, galvanizing line chemical technicians, roll-forming machine setup, crane loading, yard handling
            "S": 1.10,    # Regional roofing construction contractor delivery buffer and roll-forming custom cut-to-length lead-time
            "R_n": 0.82,  # Non-renewable iron ore/coal geological extraction, zinc mineral depletion, high recyclability modulated by smelting
            "v_rel": 0.18 # Weather-tight lockup urgency; timber wall framing is vulnerable to rain damage until roofing iron is installed
        },
        {
            "commodity": "Bulk Granular Agricultural Urea Fertilizer (46% Nitrogen)",
            "unit": "tonne",
            "sector": "Sector 1/2 (Agricultural Biochemical Energy Feedstock)",
            "P_retail": 740.00,
            "P_e": 315.00, # Haber-Bosch steam methane reforming (SMR) natural gas thermal/feedstock (~20 GJ/t), prilling/granulation electricity, freight
            "P_b": 165.00, # Natural gas chemical feedstock, process water, formaldehyde anti-caking conditioning, synthesis reactor depreciation, storage
            "U": 78.00,   # Chemical synthesis plant operators, gas reforming compressor mechanics, laboratory purity QC chemists, bulk delivery drivers
            "S": 1.14,     # Tight seasonal broadacre top-dressing planting window demand spikes, import vessel shipping lead-times, gas reservation
            "R_n": 0.84,   # Non-renewable fossil methane depletion, energy-intensive Haber-Bosch synthesis, reactive nitrogen volatilization losses
            "v_rel": 0.15  # Seasonal soil moisture crop uptake window; nitrogen must be applied immediately prior to forecast rain events
        },
        {
            "commodity": "Agricultural Glyphosate Herbicide (450g/L SL Systemic Formulation)",
            "unit": "20L drum",
            "sector": "Sector 1/2 (Agricultural Chemical Inputs)",
            "P_retail": 135.00,
            "P_e": 22.50,  # Catalytic synthesis exergy, neutralization, surfactant high-shear mixing, HDPE blow-molding, DG compliance freight
            "P_b": 54.00,  # Technical glyphosate AI (9kg), tallow amine surfactant (2.4kg), fluorinated HDPE drum, tamper closure, drumMUSTER
            "U": 21.50,    # Batch reactor operators, HPLC active assay chemists, automated packaging technicians, APVMA compliance, rural handling
            "S": 1.12,     # Pre-seeding autumn knockdown demand spikes, APVMA regulatory batch certification buffer
            "R_n": 0.86,   # Non-renewable petrochemical/phosphorus precursor extraction, chemical synthesis waste, weed resistance duty
            "v_rel": 0.18  # Critical 48-72h broadacre autumn post-rain knockdown moisture window prior to direct-drill seeding
        },
        {
            "commodity": "Standard Gypsum Plasterboard Wall Lining (10mm Recessed Edge)",
            "unit": "1.2m x 2.4m sheet",
            "sector": "Sector 4 (Shelter / Building Interior Linings)",
            "P_retail": 24.80,
            "P_e": 4.90,   # Natural gypsum calcining kiln (160 C), boardline slurry pumping, multi-deck board drying kiln (130 C), transport
            "P_b": 6.40,   # Raw gypsum rock royalty, multi-ply 100% recycled paper linerboard (380g/m2), core starch additives, edge tape, gluts
            "U": 4.10,     # Quarry operators, calciner surveillance, boardline wet-end chemistry technicians, cutter operators, crane offloading
            "S": 1.10,     # Residential interior lining trade scheduling buffer, regional plastering contractor stock lead-times
            "R_n": 0.85,   # Non-renewable mineral gypsum deposit extraction, natural gas combustion degradation, high paper liner recyclability
            "v_rel": 0.14  # Interior construction critical path; walls must be hung, stopped, and sanded before painting and electrical fit-out
        },
        {
            "commodity": "Commercial Structural Hardwood Timber (F17 Kiln-Dried Hardwood, 90x45mm)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Framing & Heavy Construction)",
            "P_retail": 14.80,
            "P_e": 2.15,   # Heavy native harvester felling/snigging diesel, high-torque breakdown saw electric power, 4-6 week kiln dehumidification, transport
            "P_b": 2.85,   # Native forest sustainable yield forestry royalty, carbide sawblade tip wear, wax emulsion end-grain sealer, high-tensile strapping
            "U": 3.20,     # Steep terrain faller vigilance, heavy log carriage sawyer operations, visual stress-grading (AS 2082/AS 2796 F17), timber sorting
            "S": 1.25,     # Severe hardwood supply constraints across eastern Australia following native forest harvesting policy transitions in Victoria/WA/NSW
            "R_n": 0.72,   # Long 60-80 year native eucalypt biological growth rotation cycles, selective sawlog harvest regimes, ecological forest buffers
            "v_rel": 0.14  # Structural framing critical milestone; roof trusses and lintels depend on bearer/joist installation before weather enclosure
        },
        {
            "commodity": "Agricultural Feed Barley (F1 Broadacre Feed Grain)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Feedstock & Livestock Energy)",
            "P_retail": 325.00,
            "P_e": 92.50,  # Tractor diesel for pre-sowing fallow prep, air-seeder planting fuel, selective in-crop spraying, harvester/header fuel, grain aeration
            "P_b": 74.00,  # Certified F1 seed grain, MAP basal starter fertilizer, selective in-crop herbicide/fungicide, broadacre machinery capital wear
            "U": 84.00,    # Broadacre tractor operator hours, chaser bin logistics, header operational vigilance, road train transport, receival sampling
            "S": 1.06,     # Domestic feedlot beef and dairy ration demand buffer, regional export shipping allocation
            "R_n": 0.98,   # Annual winter crop replenishment, soil organic carbon recharge, rotational legume nitrogen fixation recovery
            "v_rel": 0.04  # Continuous livestock feedlot ration requirements and pastoral drought supplementary feeding buffer
        },
        {
            "commodity": "Commercial Copper Electrical Building Wire (2.5mm2 Twin & Earth Flat TPS Cable)",
            "unit": "100m drum",
            "sector": "Sector 2/4 (Energy Reticulation & Building Infrastructure)",
            "P_retail": 225.00,
            "P_e": 24.50,  # Copper rod continuous upcasting, tandem wire-drawing through diamond dies, electric resistance annealing, PVC extrusion heating, spooling, freight
            "P_b": 118.50, # High-conductivity electrolytic tough pitch (ETP) copper (6.72kg Cu-ETP), electrical grade V-90 flame-retardant PVC compound (5.5kg), spool packaging
            "U": 22.00,    # Continuous wire casting operators, diamond die drawing bench technicians, high-voltage spark testing QA, automated spool coiling, warehouse storemen
            "S": 1.15,     # Global refined copper cathode inventory buffer, domestic electrical wholesale trade stocking lead-times
            "R_n": 0.82,   # Non-renewable primary copper geological ore grade depletion, offset by high secondary copper recycling and scrap reclamation value
            "v_rel": 0.18  # Mandatory first-fix electrical rough-in milestone; cables must be clipped through wall framing studs prior to insulation and plasterboard lockup
        },
        {
            "commodity": "Solvent-Extracted Canola Meal / Protein Cake (Bulk Pelletized, 36%-38% Crude Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Livestock Protein Feedstock & Nutrition)",
            "P_retail": 580.00,
            "P_e": 84.50,  # Expeller crushing friction, steam conditioning, hexane extraction solvent recovery re-boiler, desolventizer-toaster, hammer-mill, pellet die extrusion, bulk transport
            "P_b": 212.00, # Allocated raw canola seed feedstock mass fraction (crushing yields ~42% oil and ~58% meal), hexane solvent make-up, boiler water chemicals, pelleting binders
            "U": 82.00,    # Solvent plant DCS board operators, extraction pump maintenance mechanics, analytical NIR laboratory protein assay chemists, pellet mill operators, gantry dispatch
            "S": 1.10,     # Domestic intensive beef feedlot and dairy ration demand buffer, regional export meal container allocation
            "R_n": 0.94,   # Annual oilseed crop replenishment, rotational soil nutrient recovery, high soil organic nitrogen requirement
            "v_rel": 0.10  # Continuous livestock rumen microbial protein maintenance; feedlots cannot interrupt protein ration without severe digestive acidosis and daily weight gain collapse
        },
        {
            "commodity": "Commercial Hot-Rolled Structural Steel Universal Beams (150UB14.0)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Construction)",
            "P_retail": 52.00,
            "P_e": 11.20,  # EAF scrap melting electricity, structural beam reheat furnace thermal gas exergy, universal rolling mill drives, roller straightener, freight
            "P_b": 14.50,  # Certified structural steel scrap/billet (14.2kg steel), Grade 300PLUS micro-alloying (Si-Mn), roll redressing wear, anti-corrosive primer
            "U": 8.20,     # Rolling mill automation engineers, roughing/edging pulpit operators, metallurgical test technicians, crane riggers, merchant yard sawyers
            "S": 1.12,     # Regional structural steel merchant trade inventory buffer, project custom-cut scheduling lead times
            "R_n": 0.82,   # Non-renewable metallurgical coking coal and high-grade ore reserves, modulated by 100% closed-loop steel recyclability
            "v_rel": 0.16  # Mandatory structural load-bearing lintel/bearer installation milestone prior to upper floor construction and roof truss erection
        },
        {
            "commodity": "Whole Ginned Cottonseed (Fuzzy White Cattle Feedstock)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Protein Feedstock & Nutrition)",
            "P_retail": 520.00,
            "P_e": 86.50,  # Broadacre cotton picker diesel exergy, saw-ginning mechanical power, gin drying tower gas heat, aeration, bulk transport to feedlot
            "P_b": 178.50, # Allocated crop seed mass production fraction after lint crediting, seed water allocations, basal fertilizer, gin shed depreciation
            "U": 68.00,    # Irrigation agronomists, picker operators, gin superintendents, press technicians, front-end loader drivers, road train tipper drivers
            "S": 1.14,     # Intensive feedlot inclusion demand, Murray-Darling seasonal water availability variations, export container competition
            "R_n": 0.90,   # Annual intensive irrigated/dryland cropping cycle, soil moisture and nutrient replenishment
            "v_rel": 0.10  # Continuous livestock feedlot finishing rations and supplementary pastoral drought feeding buffer
        },
        {
            "commodity": "Commercial Cold-Formed Steel Galvanized Framing / C-Purlin (C15015, 1.5mm BMT)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Framing & Industrial Roofing)",
            "P_retail": 16.50,
            "P_e": 3.40,   # Continuous zinc pot galvanizing thermal exergy (450 C), cold-roll coil slitting, multi-stand roll-forming drives, automated punching, freight
            "P_b": 5.10,   # High-tensile structural strip coil (2.95kg G450 steel), Z350/Z275 zinc coating, chemical passivation, steel strapping, timber gluts
            "U": 2.60,     # Slitter line setup operators, roll-forming mill technicians, automated uncoiler attendants, crane bundle riggers, truck drivers
            "S": 1.10,     # Trade distributor inventory lead times, custom cut-to-length scheduling buffer
            "R_n": 0.82,   # Non-renewable zinc and primary iron ore extraction, balanced by 100% closed-loop scrap circularity
            "v_rel": 0.16  # Roof structural purlin fixing critical path before roof sheeting can be fastened
        },
        {
            "commodity": "Australian Prime Hard Breadmaking Wheat (APH2 High-Protein Milling Grain, min 13% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Feedstock)",
            "P_retail": 410.00,
            "P_e": 118.50, # Broadacre tillage and air-seeder planting fuel, multiple in-crop liquid UAN / granular urea top-dressing passes, combine harvesting, aeration, freight
            "P_b": 96.50,  # High-nitrogen fertilization regime (120-150 kg N/ha), certified APH varietal seed, selective flag-leaf fungicides, testing equipment depreciation
            "U": 108.00,   # Intensive broadacre agronomic management, multiple spreader/sprayer operating hours, harvest timing vigilance (falling number >350s), protein NIR assay testing
            "S": 1.08,     # Domestic premium bread flour milling contracts, export container packing demand buffer
            "R_n": 0.98,   # Annual winter cereal rotation, soil organic matter and nitrogen balance replenishment
            "v_rel": 0.04  # Continuous domestic flour mill grist blending and baker flour milling requirements
        },
        {
            "commodity": "Commercial Aluminum Window Glazing Frames (Double-Glazed Residential Sliding Window, 1200mm x 1800mm Standard Unit)",
            "unit": "unit (2.16 m2)",
            "sector": "Sector 4 (Shelter / Fenestration & Building Envelope)",
            "P_retail": 540.00,
            "P_e": 52.00,   # Aluminum bauxite Hall-Héroult smelting exergy, billet extrusion heating, float glass furnace melting at 1,550 C, automated argon gas filling, flatbed freight
            "P_b": 168.00,  # Extruded architectural aluminum alloy (6063-T5 powder-coated, 11.5 kg Al), float glass lites (4mm/12mm Argon/4mm, 43.2 kg glass), warm-edge desiccant spacer, structural secondary silicone sealant, stainless rollers, cam locks, weather-pile mohair seals
            "U": 64.80,    # Billet extrusion press operators, IGU automated assembly line technicians, CNC mitre sawyers, frame assembly fabricators, glazing QA inspectors
            "S": 1.14,     # NCC 2022 7-star energy compliance demand surge, lead-time manufacturing buffer
            "R_n": 0.84,   # Non-renewable bauxite/silica mineral depletion, modulated by high secondary aluminum and glass cullet recyclability
            "v_rel": 0.18  # Building lockup stage critical path; internal plasterboard and joinery cannot proceed until fenestration is weatherproofed
        },
        {
            "commodity": "Commercial Feed Sorghum (SGM1 Summer Grain Sorghum, min 9% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Feedstock & Livestock Nutrition)",
            "P_retail": 360.00,
            "P_e": 104.50, # Tractor diesel for summer fallow tillage, precision air-seeder planting, selective in-crop atrazine/dual spraying, combine harvesting, grain aeration, bulk tipper freight
            "P_b": 82.00,  # Certified hybrid seed, starter MAP and pre-plant urea nitrogen fertilization, targeted pest control, header machinery depreciation
            "U": 92.00,    # Broadacre summer planter operators, spray rig operators, harvest logistics, receival stand grading
            "S": 1.08,     # Summer cattle feedlot and intensive poultry/swine ration demand buffer, export container allocation
            "R_n": 0.98,   # Annual summer grain rotation, soil moisture and organic carbon replenishment
            "v_rel": 0.05  # Continuous domestic livestock ration energy continuity and feedlot bunk management
        },
        {
            "commodity": "Commercial Structural Steel Hollow Sections (100x100x4.0mm RHS/SHS, Grade C350LO)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Framing & Post Columns)",
            "P_retail": 42.20,
            "P_e": 9.40,   # Continuous high-frequency induction ERW tube welding electricity, multi-stand roll-forming drives, automated flying saw sizing, flatbed freight
            "P_b": 12.60,  # Hot-rolled structural strip coil feedstock (11.6 kg Grade C350 steel/m), in-line anti-corrosive primer coating or light pre-passivation, timber gluts
            "U": 6.80,     # ERW tube mill operators, slit-coil handling crane riggers, welding NDT ultrasonic technicians, bundle staging sawyers, yard dispatch logistics
            "S": 1.12,     # Trade distributor inventory lead times, custom cut-to-length scheduling buffer
            "R_n": 0.82,   # Non-renewable virgin iron ore and coking coal extraction, tempered by high circular scrap recycling in electric arc furnaces
            "v_rel": 0.16  # Loadbearing structural post and portal column critical path; portal frames cannot be erected without primary columns
        },
        {
            "commodity": "Australian Desi Chickpeas (CHKP1 Premium Bulk Pulse Grain)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Legume Protein & Crop Rotation)",
            "P_retail": 710.00,
            "P_e": 135.00, # Broadacre tractor diesel for deep tillage and precision inoculation seeding, multiple fungicide spray passes, axial-flow combine harvesting, bulk road freight
            "P_b": 145.00, # Certified Desi seed, rhizobia peat inoculant (Group N), basal MAP fertilizer, targeted Ascochyta blight fungicides, machinery wear and depreciation
            "U": 114.00,   # Intensive broadacre pulse agronomic management, rigorous Ascochyta fungal scouting, harvest timing vigilance to prevent pod shatter, seed grading assays
            "S": 1.15,     # Global pulse export demand surges (India tariff exemption window), domestic planting area moisture constraints
            "R_n": 1.04,   # Symbiotic biological nitrogen fixation enhances soil nitrogen capital, regenerating biophysical fertility for subsequent cereal crops
            "v_rel": 0.05  # Continuous global and domestic plant-based legume protein dietary requirement
        },
        {
            "commodity": "Commercial Heavy Structural Steel Plate (Grade 250, 12mm Medium Plate, AS/NZS 3678)",
            "unit": "m2 (94.2 kg)",
            "sector": "Sector 4 (Shelter / Heavy Engineering & Civil Construction)",
            "P_retail": 220.70,
            "P_e": 52.50,   # Blast furnace coke smelting exergy, continuous slab casting, heavy reversing plate mill rolling at 1200 C, plasma edge shearing, linehaul flatbed freight
            "P_b": 64.50,   # 94.2 kg carbon-manganese structural steel slab feedstock (AS/NZS 3678 Grade 250), deoxidation alloys, surface scale conditioning, lifting dunnage
            "U": 34.00,     # Caster operators, heavy plate rolling pulpit technicians, ultrasonic internal lamination QA inspectors, plasma plate cutting sawyers, yard crane riggers
            "S": 1.10,     # Heavy engineering distributor inventory lead times, custom plate profiling and plate scheduling buffer
            "R_n": 0.82,   # Non-renewable virgin iron ore and metallurgical coking coal extraction, mitigated by closed-loop secondary scrap recyclability
            "v_rel": 0.14  # Structural column baseplates, portal knee joints, and bridge girder fabrication critical path
        },
        {
            "commodity": "Commercial Faba Beans (F1 Broadacre Pulse Grain, min 24% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human/Livestock Nutrition)",
            "P_retail": 455.00,
            "P_e": 118.00, # Broadacre tractor diesel for deep winter sowing, multiple chocolate spot [Botrytis fabae] fungicide passes, axial-flow harvesting, aeration, road freight
            "P_b": 98.00,  # Certified F1 seed, rhizobium peat inoculant (Group F), starter single superphosphate/MAP, targeted fungicides and aphidicides, header machinery wear
            "U": 98.00,    # Agronomic scouting for fungal chocolate spot, harvest timing vigilance to prevent pod shatter and seed staining, receival protein and moisture assay testing
            "S": 1.08,     # Domestic intensive feedlot/swine ration swap-in floor demand, Middle East human consumption export container competition
            "R_n": 1.05,   # Vigorous biological nitrogen fixation (70-120 kg N/ha into soil profile) regenerating biological soil carrying capacity for subsequent wheat rotations
            "v_rel": 0.05  # Continuous human and livestock staple vegetable protein and amino acid requirement
        },
        {
            "commodity": "Commercial Structural Steel Equal Angle (100x100x8.0mm EA, Grade 300PLUS / AS/NZS 3679.1)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Framing & Bracing)",
            "P_retail": 43.50,
            "P_e": 9.80,    # Reheating furnace thermal gas exergy at 1200 C, angle mill roughing and finishing roll drives, automated cold sawing, flatbed freight
            "P_b": 12.90,   # 11.8 kg structural steel billet feedstock (AS/NZS 3679.1 Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 6.90,      # Rolling pulpit operators, angle straightening roll technicians, QA dimensional inspectors, crane bundle riggers, yard dispatch logistics
            "S": 1.10,      # Merchant trade inventory buffer, regional steel fabrication cut-to-length and portal bracing staging lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by high EAF secondary scrap circularity
            "v_rel": 0.16   # Portal knee bracing, roof truss diagonal lacing, and lintel fabrication critical path
        },
        {
            "commodity": "Australian Field Peas (Kaspa Type Bulk Grain / Livestock Protein Feed, min 22% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human/Livestock Nutrition)",
            "P_retail": 440.00,
            "P_e": 112.50,  # Tractor diesel for precision no-till winter seeding, selective post-emergent grass/broadleaf spraying, axial-flow harvesting with pulse crop lifters, aeration drying, bulk road freight
            "P_b": 94.50,   # Certified Kaspa seed, Group E rhizobia peat inoculant, single superphosphate starter fertilizer, targeted insect/weed chemistries, header wear
            "U": 94.00,     # Agronomic monitoring, precise harvest ground-speed vigilance to prevent pod shatter and split peas, receival protein and split assays
            "S": 1.08,      # Domestic stockfeed ration swap-in floor demand, split pea export packaging allocation
            "R_n": 1.05,    # Biological nitrogen fixation (60-100 kg N/ha into soil profile) regenerating biological soil carrying capacity for subsequent cereal rotations
            "v_rel": 0.05   # Staple human and livestock dietary vegetable protein and amino acid continuity
        },
        {
            "commodity": "Commercial Structural Steel Parallel Flange Channel (150x75mm PFC, Grade 300PLUS / AS/NZS 3679.1)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Framing & Floor Joists)",
            "P_retail": 65.50,
            "P_e": 14.50,   # Reheating furnace thermal gas exergy at 1200 C, heavy structural breakdown and channel finishing roll drives, automated cold sawing, flatbed transport
            "P_b": 19.80,   # 17.7 kg continuous-cast structural steel billet feedstock (AS/NZS 3679.1 Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 10.20,     # Rolling mill pulpit operators, web-flange caliper alignment, 7-roll cold straightener technicians, crane rigging, yard staging logistics
            "S": 1.10,      # Merchant floor stock inventory buffer, residential/commercial bearer and lintel lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16   # Floor joist, structural lintel, and bearer framing critical path
        },
        {
            "commodity": "Australian Narrow-Leaf Lupins (Angustifolius Bulk Feed Lupins, min 32% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & High-Protein Feed)",
            "P_retail": 520.00,
            "P_e": 131.00,  # Tractor diesel for deep-ripping sandplains and precision no-till winter seeding, selective spraying, axial-flow harvesting with pulse concaves, aeration, road freight
            "P_b": 121.00,  # Certified Mandelup/Jurien seed, Group G peat inoculant, single superphosphate and potash fertilizer, crop chemistries, machinery wear
            "U": 112.00,    # Agronomic monitoring, native budworm pest scouting, harvest vigilance at 12-14% moisture to prevent pod shatter and split seeds, protein assays
            "S": 1.10,      # High export demand from aquaculture/ruminant markets, domestic intensive dairy/feedlot protein buffer
            "R_n": 1.08,    # Exceptional biological nitrogen fixation (80-120 kg N/ha into soil profile) and root carboxylate exudation mobilizing fixed soil phosphorus
            "v_rel": 0.05   # Staple livestock dietary vegetable protein and essential amino acid continuity
        },
        {
            "commodity": "Commercial Galvanized Steel Built-In Lintel / T-Bar (200x10mm Lintel, AS/NZS 2699.3 / AS 4100)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Masonry & Roof-Load Lintels)",
            "P_retail": 105.00,
            "P_e": 22.80,   # Billet reheating gas exergy at 1200 C, hot-dip galvanizing zinc kettle heating at 450 C, continuous submerged-arc welding / rolling, automated saw cutting, flatbed delivery
            "P_b": 33.60,   # 25.1 kg structural steel Grade 300PLUS feedstock, 600 g/m2 hot-dip zinc coating (AS/NZS 4680), anti-corrosion passivation, timber bundling dunnage
            "U": 16.50,     # Automated welding/rolling line technicians, galvanizing kettle dipping riggers, zinc dross skimming, ultrasonic weld testing, yard logistics
            "S": 1.10,      # Structural lintel stock buffer, masonry cavity wall opening framing staging lead times
            "R_n": 0.82,    # Virgin iron ore and zinc mineral depletion, offset by high steel and zinc scrap recyclability
            "v_rel": 0.18   # Masonry cavity wall opening framing critical path; builder milestone sign-off prior to bricklaying continuation
        },
        {
            "commodity": "Australian Mungbeans (Berken / Crystal Type Pulse Grain, min 24% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Summer Legume)",
            "P_retail": 1150.00,
            "P_e": 175.00,  # Summer crop tractor diesel for precision planting into stubble, multi-pass selective insect spraying for mirids/helicoverpa, desiccation pass, specialized draper front harvesting, aeration, road freight
            "P_b": 185.00,  # Certified Berken/Crystal seed, Group I Bradyrhizobium peat inoculant, starter phosphorus fertilizer, high-potency selective chemistries, harvesting wear, bulk bag packaging
            "U": 165.00,    # Intensive summer agronomic scouting, daily mirid pest monitoring, harvest timing vigilance within 48 hours of maturity to avoid weather staining, optical sorting and gravity grading
            "S": 1.15,      # Volatile summer rainfall acreage, high export container shipping competition to China, India, and Southeast Asia
            "R_n": 1.04,    # Biological nitrogen fixation (40-80 kg N/ha into soil profile) across a rapid 70-90 day summer crop rotation
            "v_rel": 0.08   # Staple high-protein Asian cuisine, sprouting, and domestic plant-based protein continuity
        },
        {
            "commodity": "Commercial Structural Steel Parallel Flange Channel (200x75mm PFC, Grade 300PLUS / AS/NZS 3679.1)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Framing & Floor Bearers)",
            "P_retail": 85.00,
            "P_e": 18.80,   # Reheating furnace gas exergy at 1200 C, heavy channel breakdown and finishing roll drives, cold sawing, flatbed freight
            "P_b": 25.60,   # 22.9 kg continuous-cast structural billet feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 13.20,     # Rolling mill pulpit operators, 22.9 kg/m web-flange caliper alignment, 7-roll cold straightener technicians, crane rigging, yard logistics
            "S": 1.10,      # Merchant floor stock inventory buffer, residential/commercial bearer and heavy lintel staging lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16   # Heavy floor bearer, transfer beam, and multi-storey lintel structural critical path
        },
        {
            "commodity": "Commercial De-Hulled Split Faba Beans (Machine Dressed Export & Food Grade, min 28% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human/Food Processing)",
            "P_retail": 750.00,
            "P_e": 226.00,  # 1.19t farmgate bean growing exergy ($140.40) + mechanical impact de-hulling, counter-flow aspiration, optical color sorting (Buhler Sortex), bagging, container freight ($85.60)
            "P_b": 156.00,  # 1.19t raw faba bean substrate ($116.60) + food-grade multi-wall polypropylene bags, slipsheets, rubber de-hulling roller & screen wear ($39.40)
            "U": 138.00,    # Milling plant operators, optical sorter calibration technicians, continuous purity QA sampling, forklift warehouse staging, export phytosanitary documentation
            "S": 1.12,      # Seasonal Middle Eastern food import demand peaks (Ramadan falafel/foul mudammas trade), Australian container freight availability
            "R_n": 1.05,    # Biological nitrogen fixation (70-120 kg N/ha into soil profile) from parent faba bean rotation regenerating broadacre soil carrying capacity
            "v_rel": 0.06   # Staple human dietary vegetable protein, Middle Eastern culinary subsistence, and domestic plant-based protein fractionation
        },
        {
            "commodity": "Commercial Structural Steel Parallel Flange Channel (250x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Framing & Heavy Transfer Bearers)",
            "P_retail": 132.00,
            "P_e": 29.20,   # Heavy billet reheating gas exergy at 1200 C, heavy breakdown and 250mm finishing roll drives, cold cut-off sawing, flatbed freight
            "P_b": 39.70,   # 35.5 kg continuous-cast structural billet feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 20.40,     # Rolling mill pulpit operators, 35.5 kg/m web-flange caliper alignment, 7-roll cold straightener technicians, heavy crane rigging, yard logistics
            "S": 1.10,      # Merchant floor stock inventory buffer, multi-storey residential/commercial bearer staging lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16   # Heavy floor bearer, multi-storey transfer beam, and large commercial opening critical path
        },
        {
            "commodity": "Commercial De-Hulled Split Yellow Field Peas (Machine Dressed Food Grade, min 25% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 680.00,
            "P_e": 207.00,  # 1.18t farmgate field pea growing exergy ($132.75) + mechanical abrasive de-hulling, counter-flow aspiration, optical color sorting, bagging, linehaul freight ($74.25)
            "P_b": 145.00,  # 1.18t raw field pea substrate ($111.50) + food-grade multi-wall polypropylene bags, pallet wrap, de-huller emery stone/screen maintenance ($33.50)
            "U": 132.00,    # Milling plant operators, optical sorter color calibration technicians, continuous purity QA sampling, forklift warehouse staging, export phytosanitary documentation
            "S": 1.10,      # Domestic split pea food ration buffer, soup/canning industry demand, export container shipping allocation
            "R_n": 1.05,    # Biological nitrogen fixation (60-100 kg N/ha into soil profile) from parent field pea crop regenerating broadacre soil carrying capacity
            "v_rel": 0.05   # Staple human dietary vegetable protein, split pea soup/dhal culinary subsistence, and plant protein isolate extraction
        },
        {
            "commodity": "Commercial Structural Steel Parallel Flange Channel (300x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Structural Steel Framing & Heavy Transfer Bearers)",
            "P_retail": 149.50,
            "P_e": 33.20,   # Heavy billet reheating gas exergy at 1200 C, heavy breakdown and 300mm finishing roll drives, cold cut-off sawing, flatbed freight
            "P_b": 45.20,   # 40.1 kg continuous-cast structural billet feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 23.10,     # Rolling mill pulpit operators, 40.1 kg/m web-flange caliper alignment, 7-roll cold straightener technicians, heavy crane rigging, yard logistics
            "S": 1.10,      # Merchant floor stock inventory buffer, heavy commercial floor bearer and portal frame staging lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16   # Heavy floor bearer, portal frame transfer beam, and bridge stringer structural critical path
        },
        {
            "commodity": "Commercial De-Hulled Split Red Lentils (Machine Dressed Export Grade, min 26% Protein)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 1050.00,
            "P_e": 262.00,  # 1.22t farmgate red lentil growing exergy ($152.50) + mechanical abrasive decortication, splitting rolls, aspiration, optical bichromatic color sorting, bagging, container freight ($109.50)
            "P_b": 178.00,  # 1.22t raw red lentil substrate ($134.20) + food-grade multi-wall polypropylene bags, slipsheets, emery de-hulling stone wear and mill maintenance ($43.80)
            "U": 146.00,    # Milling plant operators, optical sorter color calibration technicians, continuous purity QA sampling, forklift warehouse staging, export phytosanitary documentation
            "S": 1.15,      # High export container shipping competition to India, Sri Lanka, and Bangladesh; international subcontinental demand peaks
            "R_n": 1.05,    # Biological nitrogen fixation (50-90 kg N/ha into soil profile) from parent red lentil rotation regenerating broadacre soil carrying capacity
            "v_rel": 0.07   # Staple global dietary legume protein, dhal culinary subsistence, and international human nutritional security
        },
        {
            "commodity": "Pharmaceutical Saline IV Infusion Bag (Sodium Chloride 0.9%, 1,000 mL)",
            "unit": "1,000 mL bag",
            "sector": "Sector 5 (Essential Care & Emergency Healthcare Consumables)",
            "P_retail": 8.50,
            "P_e": 0.65,   # Autoclave steam sterilization @ 121C, cleanroom Class A/B HVAC air filtration, BFS power
            "P_b": 0.85,   # Water for injection (WFI) distillation, pharmaceutical NaCl, polyolefin film, sterile port
            "U": 2.40,     # Cleanroom technician monitoring, endotoxin testing, microbiology assays, pharmacy dispatch
            "S": 1.20,     # Acute hospital ICU and clinical emergency reserve buffer
            "R_n": 0.90,   # Non-renewable medical polymers modulated by clinical water closed-loop recycling
            "v_rel": 0.35  # Extreme clinical hydration, trauma, and surgical fluid replacement urgency
        },
        {
            "commodity": "Commercial Solar PV Module (440W Monocrystalline Residential Panel, Tier-1)",
            "unit": "440W panel",
            "sector": "Sector 2/4 (Renewable Energy Infrastructure & Building Envelope)",
            "P_retail": 165.00,
            "P_e": 38.50,  # Polysilicon reduction, Czochralski crystal pulling, cell diffusion, vacuum lamination exergy
            "P_b": 52.00,  # Hyper-pure silicon wafer, 3.2mm tempered solar glass, anodized aluminum frame, EVA/POE film
            "U": 14.50,    # Cleanroom automated stringer techs, EL defect inspection, flash tester calibration, freight
            "S": 1.08,     # Residential rooftop installation buffer, shipping container lead-time allocation
            "R_n": 0.88,   # High circular recyclability of aluminum frame and glass offset by refining energy
            "v_rel": 0.12  # Residential rooftop solar installation critical-path electrical milestone
        },
        {
            "commodity": "Commercial Structural Steel Universal Column (200UC46.2, AS/NZS 3679.1 Grade 300PLUS)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Heavy Engineering & Structural Columns)",
            "P_retail": 172.00,
            "P_e": 38.50,  # Heavy bloom reheating furnace gas exergy @ 1200 C, breakdown and 4-roll universal finishing stand electric drives, automated cold sawing, heavy flatbed transport
            "P_b": 52.00,  # 46.2 kg continuous-cast structural billet/bloom feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 26.50,    # Rolling pulpit operators, 46.2 kg/m heavy flange/web caliper alignment, heavy multi-roll cold straightener technicians, crane rigging, yard logistics
            "S": 1.10,     # Merchant floor stock inventory buffer, commercial column and heavy structural portal frame staging lead times
            "R_n": 0.82,   # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16  # Primary multi-storey building column, industrial portal frame upright, and heavy gantry support critical path
        },
        {
            "commodity": "Commercial Australian Faba Bean Protein Concentrate / Flour (min 55% Protein, per Tonne)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 1280.00,
            "P_e": 310.00, # 2.15t farmgate bean growing exergy ($253.70) + fine pin milling, air classification / turbo-fractionation electric drive power, multi-cyclone collection, packaging, linehaul freight ($56.30)
            "P_b": 245.00, # 2.15t raw faba bean substrate ($210.70) + multi-wall Kraft paper bags with PE barrier liner, food-grade pallets, air classifier ceramic rotor wear and filter media replacement ($34.30)
            "U": 162.00,   # Milling plant operators, air classifier particle size/cut-point technicians, continuous protein assay (combustion Dumas method) QA chemists, food hygiene compliance, logistics
            "S": 1.15,     # High domestic and export food-grade alternative protein / plant-based meat formulation demand, international pulse market shipping allocation
            "R_n": 1.05,   # Vigorous biological nitrogen fixation (70-120 kg N/ha into soil profile) from parent faba bean rotation regenerating broadacre soil carrying capacity
            "v_rel": 0.06  # Staple human dietary vegetable protein concentrate, bakery enrichment, and plant-based protein meat alternative manufacturing continuity
        },
        {
            "commodity": "Commercial Structural Steel Universal Column (250UC72.9, AS/NZS 3679.1 Grade 300PLUS)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Heavy Engineering & Structural Columns)",
            "P_retail": 272.00,
            "P_e": 60.50,  # Heavy bloom reheating furnace gas exergy @ 1200 C, breakdown and 4-roll universal roughing and finishing stand electric drives, automated cold sawing, heavy flatbed transport
            "P_b": 82.50,  # 72.9 kg continuous-cast structural billet/bloom feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 41.50,    # Rolling pulpit operators, 72.9 kg/m heavy flange/web caliper alignment, heavy multi-roll cold straightener technicians, crane rigging, yard logistics
            "S": 1.10,     # Merchant floor stock inventory buffer, commercial column and heavy structural portal frame staging lead times
            "R_n": 0.82,   # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16  # Primary multi-storey building column, industrial portal frame upright, and heavy gantry support critical path
        },
        {
            "commodity": "Commercial Australian Field Pea Protein Isolate (min 80% Protein, Spray-Dried, per Tonne)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 3450.00,
            "P_e": 820.00, # 4.2t field pea growing exergy ($472.50) + alkaline solubilization, isoelectric precipitation, multi-stage disc-stack centrifugation, spray drying exergy, linehaul freight ($347.50)
            "P_b": 615.00, # 4.2t raw field pea grain substrate ($396.90) + food-grade NaOH, HCl, multi-wall Kraft paper bags with PE barrier liners, sanitary CIP chemicals, membrane filter replacements ($218.10)
            "U": 385.00,   # Wet extraction plant operators, spray-dryer thermal profile technicians, continuous protein assay (Dumas) & microbiology QC chemists, sanitary compliance, logistics
            "S": 1.15,     # High domestic & export sports nutrition, plant-based dairy/meat formulation demand, specialized sanitary processing line allocation
            "R_n": 1.05,   # Biological nitrogen fixation (60-100 kg N/ha into soil profile) from parent field pea rotation regenerating broadacre soil fertility
            "v_rel": 0.06  # Dietary protein isolate formulation, clinical nutrition, and plant-based meat manufacturing continuity
        },
        {
            "commodity": "Commercial Structural Steel Universal Column (310UC96.8, AS/NZS 3679.1 Grade 300PLUS)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Heavy Engineering & Structural Columns)",
            "P_retail": 360.00,
            "P_e": 80.50,  # Heavy bloom reheating furnace gas exergy @ 1200 C, heavy breakdown and 4-roll universal stands electric drives, automated cold sawing, heavy flatbed transport
            "P_b": 109.50, # 96.8 kg continuous-cast structural billet/bloom feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 55.00,    # Rolling pulpit operators, 96.8 kg/m heavy flange/web caliper alignment, heavy multi-roll cold straightener technicians, crane rigging, yard logistics
            "S": 1.10,     # Merchant floor stock inventory buffer, commercial column and heavy structural portal frame staging lead times
            "R_n": 0.82,   # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16  # Primary multi-storey building column, industrial portal frame upright, and heavy gantry support critical path
        },
        {
            "commodity": "Commercial Australian Chickpea Protein Isolate / Functional Flour (min 75% Protein, Alkaline-Extracted, per Tonne)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 3150.00,
            "P_e": 745.00, # 3.8t desi chickpea growing exergy ($513.00) + wet alkaline solubilization, isoelectric precipitation, multi-stage disc-stack centrifugation, spray drying exergy, linehaul freight ($232.00)
            "P_b": 560.00, # 3.8t raw desi chickpea grain substrate ($513.00 allocated) + food-grade NaOH, HCl, multi-wall Kraft paper bags with PE barrier liners, sanitary CIP chemicals, membrane filter replacements ($47.00)
            "U": 350.00,   # Wet extraction plant operators, spray-dryer thermal profile technicians, continuous protein assay (Dumas) & microbiology QC chemists, sanitary compliance, logistics
            "S": 1.15,     # High domestic & export sports nutrition, plant-based dairy/meat formulation demand, specialized sanitary processing line allocation
            "R_n": 1.04,   # Biological nitrogen fixation (40-80 kg N/ha into soil profile) from parent chickpea crop regenerating broadacre soil fertility
            "v_rel": 0.06  # Dietary protein isolate formulation, clinical nutrition, and plant-based meat manufacturing continuity
        },
        {
            "commodity": "Commercial Structural Steel Universal Column (310UC118, AS/NZS 3679.1 Grade 300PLUS)",
            "unit": "lineal metre",
            "sector": "Sector 4 (Shelter / Heavy Engineering & Structural Columns)",
            "P_retail": 438.00,
            "P_e": 98.00,   # Continuous heavy bloom reheating furnace gas exergy @ 1200 C, heavy breakdown stand and 4-roll universal stands electric drives, automated cold sawing, heavy flatbed transport
            "P_b": 133.50,  # 118.0 kg continuous-cast structural billet/bloom feedstock (Grade 300PLUS), surface passivation primer, timber bundling dunnage
            "U": 67.00,     # Rolling pulpit operators, 118.0 kg/m heavy flange/web caliper alignment, heavy multi-roll cold straightener technicians, crane rigging, yard logistics
            "S": 1.10,      # Merchant floor stock inventory buffer, commercial column and heavy structural portal frame staging lead times
            "R_n": 0.82,    # Virgin iron ore and metallurgical coking coal depletion, offset by EAF secondary scrap circularity
            "v_rel": 0.16   # Primary multi-storey building column, industrial portal frame upright, and heavy gantry support critical path
        },
        {
            "commodity": "Commercial Australian Faba Bean Protein Isolate (min 85% Protein, Wet-Extracted & Spray-Dried, per Tonne)",
            "unit": "tonne",
            "sector": "Sector 1 (Food / Agricultural Pulse Protein & Human Food Processing)",
            "P_retail": 3580.00,
            "P_e": 855.00,  # 4.4t faba bean growing exergy ($519.20) + wet alkaline solubilization, isoelectric precipitation, multi-stage disc-stack centrifugation, spray drying exergy, linehaul freight ($335.80)
            "P_b": 640.00,  # 4.4t raw faba bean substrate ($431.20 allocated) + food-grade NaOH, HCl, multi-wall Kraft paper bags with PE barrier liners, sanitary CIP chemicals, membrane filter replacements ($208.80)
            "U": 398.00,    # Wet extraction plant operators, spray-dryer thermal profile technicians, continuous protein assay (Dumas) & microbiology QC chemists, sanitary compliance, logistics
            "S": 1.15,      # High domestic & export sports nutrition, plant-based dairy/meat formulation demand, specialized sanitary processing line allocation
            "R_n": 1.05,    # Biological nitrogen fixation (70-120 kg N/ha into soil profile) from parent faba bean rotation regenerating broadacre soil fertility
            "v_rel": 0.06   # Dietary protein isolate formulation, clinical nutrition, and plant-based meat manufacturing continuity
        }
    ]

def run_full_fairness_audit() -> List[Dict[str, Any]]:
    dataset = get_australian_benchmark_dataset()
    audited_results = []
    for item in dataset:
        res = audit_commercial_rrp(
            commodity=item["commodity"],
            unit=item["unit"],
            sector=item["sector"],
            P_retail=item["P_retail"],
            P_e=item["P_e"],
            P_b=item["P_b"],
            U=item["U"],
            S=item["S"],
            R_n=item["R_n"],
            v_rel=item["v_rel"]
        )
        audited_results.append(res)
    return audited_results

def audit_weekly_household_basket_index(
    weekly_income_Y: float = DEFAULT_WEEKLY_DISPOSABLE_INCOME_AUD,
    subsistence_income_Y: float = DEFAULT_SUBSISTENCE_WEEKLY_INCOME_AUD,
    weekly_hours: float = STANDARD_WEEKLY_WORK_HOURS
) -> Dict[str, Any]:
    """
    Evaluates the composite Weekly Household Subsistence Basket under the
    Income Normalised Difficulty Examination (INDEX) for a standard regional
    Australian household across Food, Fuel, Energy, Water, Sanitation, Care,
    Digital Utilities, and Amortized Shelter Maintenance.
    """
    audits_by_name = {a["commodity"]: a for a in run_full_fairness_audit()}
    basket_spec = [
        ("Commercial Sliced White Bread (680g)", 2.5, "loaves/wk"),
        ("Fresh Full Cream Milk (Full Fat)", 4.0, "litres/wk"),
        ("Commercial Broiler Chicken (Whole Fresh Dressed Bird)", 2.0, "kg/wk"),
        ("Automotive Diesel Fuel (Ultra-Low Sulphur)", 45.0, "litres/wk"),
        ("Residential Grid Electricity (Single-Rate Flat)", 115.0, "kWh/wk"),
        ("LPG Bottled Gas (45kg Domestic Cylinder)", 0.20, "cylinders/wk"),
        ("Urban Reticulated Potable Water (Municipal Pipeline Tariff)", 4.5, "kL/wk"),
        ("Domestic Waste Collection (Regional NSW)", 1.0, "lift/wk"),
        ("Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)", 0.2308, "monthly plan/wk"),
        ("Prescription Antibiotic (Amoxicillin 500mg, 20 Caps)", 0.10, "course/wk"),
        ("Prescription Salbutamol Inhaler (100mcg CFC-Free MDI, 200 Doses)", 0.15, "inhaler/wk"),
        ("Residential Structural Softwood Timber (MGP10 90x45mm Pine)", 2.0, "m/wk maint"),
        ("Corrugated Galvanized Steel Roofing Sheets (Custom Orb 0.42mm BMT)", 0.5, "m/wk maint"),
        ("Standard Gypsum Plasterboard Wall Lining (10mm Recessed Edge)", 0.5, "sheet/wk maint"),
    ]
    total_obs = 0.0
    total_rrpd = 0.0
    items_breakdown = []
    for comm_name, qty, freq_label in basket_spec:
        a = audits_by_name[comm_name]
        cost_obs = a["P_retail_observed"] * qty
        cost_rrpd = a["RRP_D_recommended"] * qty
        prem = cost_obs - cost_rrpd
        total_obs += cost_obs
        total_rrpd += cost_rrpd
        items_breakdown.append({
            "commodity": comm_name,
            "weekly_quantity": qty,
            "unit_label": freq_label,
            "weekly_observed_AUD": round(cost_obs, 2),
            "weekly_fair_RRPD_AUD": round(cost_rrpd, 2),
            "weekly_extractive_toll_AUD": round(prem, 2),
            "item_INDEX_observed_pct_median": round((cost_obs / weekly_income_Y) * 100.0, 3),
            "item_INDEX_rrpd_pct_median": round((cost_rrpd / weekly_income_Y) * 100.0, 3),
            "item_INDEX_toll_pct_median": round((prem / weekly_income_Y) * 100.0, 3)
        })
    total_toll = total_obs - total_rrpd
    w_net = weekly_income_Y / weekly_hours
    w_sub = subsistence_income_Y / weekly_hours
    return {
        "weekly_median_income_AUD": weekly_income_Y,
        "weekly_subsistence_income_AUD": subsistence_income_Y,
        "net_median_hourly_wage_AUD": round(w_net, 2),
        "net_subsistence_hourly_wage_AUD": round(w_sub, 2),
        "total_weekly_observed_AUD": round(total_obs, 2),
        "total_weekly_fair_RRPD_AUD": round(total_rrpd, 2),
        "total_weekly_extractive_toll_AUD": round(total_toll, 2),
        "SFC_Extractive_Drag_Sinks_Weekly_AUD": decompose_extractive_drag_sinks(total_toll),
        "Basket_INDEX_Observed_Pct_Median_Income": round((total_obs / weekly_income_Y) * 100.0, 2),
        "Basket_INDEX_RRPD_Pct_Median_Income": round((total_rrpd / weekly_income_Y) * 100.0, 2),
        "Basket_INDEX_Extractive_Toll_Pct_Median_Income": round((total_toll / weekly_income_Y) * 100.0, 2),
        "Basket_INDEX_Observed_Pct_Subsistence_Income": round((total_obs / subsistence_income_Y) * 100.0, 2),
        "Basket_INDEX_RRPD_Pct_Subsistence_Income": round((total_rrpd / subsistence_income_Y) * 100.0, 2),
        "Basket_INDEX_Extractive_Toll_Pct_Subsistence_Income": round((total_toll / subsistence_income_Y) * 100.0, 2),
        "Weekly_Labor_Hours_Observed_Median": round(total_obs / w_net, 2),
        "Weekly_Labor_Hours_Fair_RRPD_Median": round(total_rrpd / w_net, 2),
        "Weekly_Labor_Hours_Confiscated_Median": round(total_toll / w_net, 2),
        "Weekly_Labor_Hours_Observed_Subsistence": round(total_obs / w_sub, 2),
        "Weekly_Labor_Hours_Fair_RRPD_Subsistence": round(total_rrpd / w_sub, 2),
        "Weekly_Labor_Hours_Confiscated_Subsistence": round(total_toll / w_sub, 2),
        "Bracket_Summary": {
            b_name: {
                "weekly_income_AUD": b_inc,
                "Basket_INDEX_Observed_Pct": round((total_obs / b_inc) * 100.0, 2),
                "Basket_INDEX_Fair_RRPD_Pct": round((total_rrpd / b_inc) * 100.0, 2),
                "Basket_INDEX_Extractive_Toll_Pct": round((total_toll / b_inc) * 100.0, 2),
                "Remaining_Weekly_Income_Observed_AUD": round(b_inc - total_obs, 2),
                "Remaining_Weekly_Income_Fair_RRPD_AUD": round(b_inc - total_rrpd, 2),
            }
            for b_name, b_inc in AUSTRALIAN_INCOME_BRACKETS_WEEKLY_AUD.items()
        },
        "items": items_breakdown
    }


def get_big4_bank_loan_benchmark_dataset() -> List[Dict[str, Any]]:
    """
    Returns the 5-Scale Big 4 Australian Bank (CBA, Westpac, NAB, ANZ) Loan & Credit
    Spread Benchmark Dataset (October 2026 RBA F5/F6/F7 & APRA ADI Telemetry),
    spanning Individual Unsecured Revolving Credit Cards, Individual Unsecured Personal
    Loans, Owner-Occupier Residential Mortgages, Small Business (SME) & Regional
    Agribusiness Secured Loans, and Large Corporate Institutional Syndicate Loans.
    """
    return [
        {
            "scale": "Scale 1: Individual Revolving Credit Card",
            "commodity": "Big 4 Individual Revolving Credit Card ($5,000 Balance @ 20.99% p.a.)",
            "unit": "month ($5k balance)",
            "sector": "Sector 6 (Financial Credit & Banking Enclosures — Scale 1: Individual Unsecured Revolving)",
            "principal_AUD": 5000.0,
            "nominal_rate_pct": 20.99,
            "P_retail": 90.46,  # $87.46 monthly interest (@ 20.99% p.a.) + $3.00 base monthly card fee ($36/yr)
            "P_e": 1.20,        # Automated card switch, NPP clearing & cloud data center exergy per account-month
            "P_b": 8.20,        # $0.70 IT hardware/card + $7.50 pure non-extractive mutual default reserve (1.80% p.a. actuarial loss pool on $5k)
            "U": 3.50,          # Automated KYC/AML, fraud monitoring & dispute call-center labor allocation (WEST-equiv/mo)
            "S": 1.02,          # Endogenous digital ledger credit creation (near-zero physical scarcity)
            "R_n": 0.98,        # Digital ledger clearing & mutual credit pool renewal capacity
            "v_rel": 0.32       # Acute household emergency liquidity urgency (medical, vehicle, or utility shortfall)
        },
        {
            "scale": "Scale 2: Individual Unsecured Personal Loan",
            "commodity": "Big 4 Individual Unsecured Personal Loan ($20,000 Facility @ 14.50% p.a.)",
            "unit": "month ($20k loan)",
            "sector": "Sector 6 (Financial Credit & Banking Enclosures — Scale 2: Individual Unsecured Term)",
            "principal_AUD": 20000.0,
            "nominal_rate_pct": 14.50,
            "P_retail": 253.67, # $241.67 monthly interest (@ 14.50% p.a.) + $12.00 monthly administration fee
            "P_e": 1.85,        # Core banking ledger, credit bureau API & settlement electricity per account-month
            "P_b": 21.50,       # $1.50 IT/origination amortization + $20.00 pure mutual default reserve (1.20% p.a. actuarial loss pool on $20k)
            "U": 6.80,          # Retail credit assessment, payslip verification & account servicing labor (WEST-equiv/mo)
            "S": 1.04,          # Retail consumer credit tier allocation
            "R_n": 0.96,        # Unsecured consumer repayment renewal capacity
            "v_rel": 0.25       # High household essential transport, medical, or debt-consolidation urgency
        },
        {
            "scale": "Scale 3: Owner-Occupier Residential Mortgage",
            "commodity": "Big 4 Owner-Occupier Residential Mortgage ($100,000 Tranche @ 6.46% p.a.)",
            "unit": "month ($100k tranche)",
            "sector": "Sector 6 (Financial Credit & Banking Enclosures — Scale 3: Individual Housing Mortgage)",
            "principal_AUD": 100000.0,
            "nominal_rate_pct": 6.46,
            "P_retail": 544.92, # $538.33 monthly interest (@ 6.46% p.a.) + $6.59 pro-rata monthly package fee ($395/yr on $500k loan)
            "P_e": 2.35,        # PEXA settlement, core banking server & offset ledger electricity per $100k tranche-month
            "P_b": 12.10,       # $2.10 title/IT infrastructure + $10.00 pure collateralized mortgage default reserve (0.12% p.a. loss floor per $100k)
            "U": 9.20,          # Mortgage underwriting, APRA serviceability buffer verification & valuation review per $100k (WEST-equiv/mo)
            "S": 1.05,          # First-mortgage residential land collateral backing
            "R_n": 0.98,        # Full collateral security & double-entry ledger regeneration
            "v_rel": 0.22       # Non-discretionary household shelter security & foreclosure avoidance urgency
        },
        {
            "scale": "Scale 4: Small Business (SME) & Agribusiness Loan",
            "commodity": "Big 4 Small Business (SME) & Agribusiness Loan ($100,000 Facility @ 7.72% p.a.)",
            "unit": "month ($100k facility)",
            "sector": "Sector 6 (Financial Credit & Banking Enclosures — Scale 4: SME & Regional Agribusiness)",
            "principal_AUD": 100000.0,
            "nominal_rate_pct": 7.72,
            "P_retail": 673.33, # $643.33 monthly interest (@ 7.72% p.a.) + $30.00 monthly commercial line/service fee
            "P_e": 2.90,        # Commercial payment gateway, BAS/covenant telemetry & branch network exergy per $100k-month
            "P_b": 32.10,       # $2.93 PPSR/commercial registry IT + $29.17 pure secured SME mutual default reserve (0.35% p.a. loss floor per $100k)
            "U": 13.80,         # Commercial relationship manager review, seasonal cashflow & tax return underwriting per $100k (WEST-equiv/mo)
            "S": 1.06,          # APRA SME risk-weighted capital allocation
            "R_n": 0.95,        # Regional productive enterprise revenue regeneration
            "v_rel": 0.16       # Working capital, payroll & seasonal planting/input purchase urgency
        },
        {
            "scale": "Scale 5: Large Corporate Institutional Syndicate",
            "commodity": "Big 4 Large Corporate Institutional Syndicate Loan ($100,000 Tranche @ 5.79% p.a.)",
            "unit": "month ($100k tranche)",
            "sector": "Sector 6 (Financial Credit & Banking Enclosures — Scale 5: Large Corporate Wholesale)",
            "principal_AUD": 100000.0,
            "nominal_rate_pct": 5.79,
            "P_retail": 485.83, # $482.50 monthly interest (@ 5.79% p.a.) + $3.33 pro-rata monthly syndicate agency fee
            "P_e": 1.60,        # Wholesale RITS/Austraclear settlement & institutional desk exergy per $100k tranche-month
            "P_b": 8.00,        # $1.33 wholesale legal/IT + $6.67 institutional default reserve (0.08% p.a. loss floor per $100k)
            "U": 6.20,          # Institutional credit desk covenant audit amortized across multi-million facility per $100k (WEST-equiv/mo)
            "S": 1.02,          # Prime corporate wholesale credit access
            "R_n": 0.98,        # High corporate cashflow & pricing pass-through renewal capacity
            "v_rel": 0.04       # Low urgency; high corporate bargaining symmetry & multi-bank tender competition
        }
    ]

def audit_big4_loan_spreads(rba_cash_rate_pct: float = 4.60) -> Dict[str, Any]:
    """
    Audits the fairness and regressive spread inversion of Australia's Big 4 banks
    (CBA, Westpac, NAB, ANZ) across all 5 borrower scales from Individual Unsecured
    to Large Corporate Wholesale, normalizing both on canonical monthly facilities
    and per $10,000 AUD borrowed per year.
    """
    loan_dataset = get_big4_bank_loan_benchmark_dataset()
    scales_summary = []
    for item in loan_dataset:
        a = audit_commercial_rrp(
            commodity=item["commodity"],
            unit=item["unit"],
            sector=item["sector"],
            P_retail=item["P_retail"],
            P_e=item["P_e"],
            P_b=item["P_b"],
            U=item["U"],
            S=item["S"],
            R_n=item["R_n"],
            v_rel=item["v_rel"]
        )
        principal = item["principal_AUD"]
        nominal_rate = item["nominal_rate_pct"]
        obs_mo = a["P_retail_observed"]
        fair_mo = a["RRP_D_recommended"]
        toll_mo = a["Extractive_Premium_AUD"]
        obs_annual = obs_mo * 12.0
        fair_annual = fair_mo * 12.0
        toll_annual = toll_mo * 12.0
        eff_obs_rate_pct = (obs_annual / principal) * 100.0
        fair_rrpd_rate_pct = (fair_annual / principal) * 100.0
        extractive_spread_pct = eff_obs_rate_pct - fair_rrpd_rate_pct
        rba_spread_bps = round((nominal_rate - rba_cash_rate_pct) * 100.0, 1)
        scale_factor_10k = 10000.0 / principal
        row = dict(a)
        mo_interest = round((principal * (nominal_rate / 100.0)) / 12.0, 2)
        mo_fee = round(obs_mo - mo_interest, 2)
        loan_working_out = (
            f"{a['Step_By_Step_Working_Out']}; "
            f"[Step 11: Loan Rate & Per-$10k Working Out] "
            f"Monthly Interest = (${principal:,.2f} * {nominal_rate:.2f}% / 12) = ${mo_interest:.2f} + Monthly Fee ${mo_fee:.2f} = ${obs_mo:.2f}/mo (${obs_annual:.2f}/yr); "
            f"Effective Rate = (${obs_annual:.2f} / ${principal:,.2f}) * 100 = {eff_obs_rate_pct:.2f}% p.a.; "
            f"Fair RRP/D Annual = ${fair_mo:.2f}/mo * 12 = ${fair_annual:.2f}/yr ({fair_rrpd_rate_pct:.2f}% p.a.); "
            f"Spread vs RBA Cash Rate ({rba_cash_rate_pct:.2f}%) = ({nominal_rate:.2f}% - {rba_cash_rate_pct:.2f}%) * 100 = +{rba_spread_bps:.1f} bps; "
            f"Per $10k Borrowed (scale factor {scale_factor_10k:.4f}): Obs = ${obs_annual * scale_factor_10k:.2f}/yr, "
            f"Fair RRP/D = ${fair_annual * scale_factor_10k:.2f}/yr, Extractive Toll = ${toll_annual * scale_factor_10k:.2f}/yr"
        )
        row.update({
            "scale": item["scale"],
            "principal_AUD": principal,
            "nominal_interest_rate_pct": nominal_rate,
            "effective_observed_rate_pct": round(eff_obs_rate_pct, 2),
            "fair_RRPD_rate_pct": round(fair_rrpd_rate_pct, 2),
            "unearned_extractive_rate_spread_pct": round(extractive_spread_pct, 2),
            "spread_over_RBA_cash_rate_bps": rba_spread_bps,
            "monthly_observed_AUD": round(obs_mo, 2),
            "monthly_fair_RRPD_AUD": round(fair_mo, 2),
            "monthly_extractive_toll_AUD": round(toll_mo, 2),
            "annual_cost_per_10k_borrowed_AUD": round(obs_annual * scale_factor_10k, 2),
            "annual_fair_RRPD_per_10k_borrowed_AUD": round(fair_annual * scale_factor_10k, 2),
            "annual_extractive_toll_per_10k_borrowed_AUD": round(toll_annual * scale_factor_10k, 2),
            "Loan_Step_By_Step_Working_Out": loan_working_out,
        })
        scales_summary.append(row)
    corp = scales_summary[-1]
    cc = scales_summary[0]
    pers = scales_summary[1]
    sme = scales_summary[3]
    return {
        "rba_cash_rate_pct": rba_cash_rate_pct,
        "credit_card_vs_corporate_rate_multiplier": round(cc["effective_observed_rate_pct"] / corp["effective_observed_rate_pct"], 2),
        "credit_card_vs_corporate_toll_per_10k_ratio": round(
            cc["annual_extractive_toll_per_10k_borrowed_AUD"] / corp["annual_extractive_toll_per_10k_borrowed_AUD"], 2
        ),
        "personal_loan_vs_corporate_rate_multiplier": round(pers["effective_observed_rate_pct"] / corp["effective_observed_rate_pct"], 2),
        "sme_vs_corporate_spread_bps": round((sme["nominal_interest_rate_pct"] - corp["nominal_interest_rate_pct"]) * 100.0, 1),
        "standard_500k_mortgage_monthly_interest_AUD": round(scales_summary[2]["monthly_observed_AUD"] * 5.0, 2),
        "standard_500k_mortgage_monthly_fair_RRPD_AUD": round(scales_summary[2]["monthly_fair_RRPD_AUD"] * 5.0, 2),
        "standard_500k_mortgage_monthly_extractive_toll_AUD": round(scales_summary[2]["monthly_extractive_toll_AUD"] * 5.0, 2),
        "scales": scales_summary
    }

if __name__ == "__main__":
    print("=" * 80)
    print("VALUE PHYSICS: UNIVERSAL PRICE EQUATION (UPE) EMPIRICAL RRP/D FAIRNESS AUDIT")
    print("Alethekanon Research Institute — Division 2 | Official Calibration Dataset (56 Goods)")
    print("=" * 80)
    
    audits = run_full_fairness_audit()
    for a in audits:
        p_ret = a["P_retail_observed"]
        pe = a["P_energy_Pe"]
        pb = a["P_base_Pb"]
        u = a["Metabolic_U"]
        rrpd = a["RRP_D_recommended"]
        ra = a["Implied_Extractive_Drag_Ra"] * 100
        prem = a["Extractive_Premium_AUD"]
        fair = a["Fairness_Index_Percent"]
        comm = a["commodity"]
        sec = a["sector"]
        unit = a["unit"]
        fmt = ".4f" if "nt-km" in unit else ".2f"
        print(f"Target Good: {comm}")
        print(f"  Sector: {sec} | Unit: {unit}")
        print(f"  Observed Retail RRP:  ${p_ret:{fmt}} AUD")
        print(f"  Energy Base (Pe):     ${pe:{fmt}} AUD")
        print(f"  Physical Base (Pb):   ${pb:{fmt}} AUD")
        print(f"  Metabolic Labor (U):  {u:{fmt}} WEST-equiv")
        print(f"  Fair RRP/D:           ${rrpd:{fmt}} AUD")
        print(f"  Extractive Drag (Ra): {ra:.1f}%")
        print(f"  Extractive Premium:   ${prem:{fmt}} AUD")
        print(f"  Fairness Index:       {fair:.1f}%")
        print()
    print("=" * 80)
