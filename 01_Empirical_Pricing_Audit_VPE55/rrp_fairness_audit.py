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
from typing import Dict, Any, List

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
    eps: float = 1e-16
) -> Dict[str, Any]:
    gamma = calculate_gamma(v_rel, eps)
    spread = P_retail - (P_e + P_b)
    
    if spread <= eps:
        implied_Ra = 0.0
    else:
        numerator = m1 * m2 * gamma * S * U
        ratio = numerator / (R_n * spread)
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
    
    return {
        "commodity": commodity,
        "unit": unit,
        "sector": sector,
        "P_retail_observed": round(P_retail, 4 if "nt-km" in unit else 2),
        "P_energy_Pe": round(P_e, 4 if "nt-km" in unit else 2),
        "P_base_Pb": round(P_b, 4 if "nt-km" in unit else 2),
        "Metabolic_U": round(U, 4 if "nt-km" in unit else 2),
        "Scarcity_S": round(S, 2),
        "Regen_Capacity_Rn": round(R_n, 2),
        "Relativistic_Urgency_vrel": round(v_rel, 2),
        "Lorentz_Gamma": round(gamma, 4),
        "RRP_D_recommended": round(rrp_d, 4 if "nt-km" in unit else 2),
        "Implied_Extractive_Drag_Ra": round(implied_Ra, 4),
        "Extractive_Premium_AUD": round(extractive_premium, 4 if "nt-km" in unit else 2),
        "Fairness_Index_Percent": round(fairness_index * 100.0, 1)
    }

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
            "S": 1.30,    # Regional drought rainfall deficit in regional inland shire
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

if __name__ == "__main__":
    print("=" * 80)
    print("VALUE PHYSICS: UNIVERSAL PRICE EQUATION (UPE) EMPIRICAL RRP/D FAIRNESS AUDIT")
    print("Alethekanon Research Institute — Division 2 | Official Calibration Dataset (14 Goods)")
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
