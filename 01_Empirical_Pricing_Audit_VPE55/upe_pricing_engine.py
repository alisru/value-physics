"""
Universal Price Equation (UPE) Real-World Pricing & RRP/D Engine
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation

This module provides standalone tools to:
1. Compute forward prices from direct physical, energy, and labor difficulty inputs.
2. Reverse engineer commercial Recommended Retail Prices (RRP) to isolate extractive drag (Ra).
3. Derive the Recommended Retail Price based on Difficulty (RRP/D) and compute fairness metrics.
"""

import math
from typing import Dict, Any, List

def calculate_gamma(v_rel: float, eps: float = 1e-16) -> float:
    """Calculates relativistic urgency factor gamma(v_rel)."""
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
    """
    Computes forward price:
    P = m1 * m2 * gamma(v_rel) * [(S * U) / (R_n * (1 - R_a))] + P_e + P_b
    """
    gamma = calculate_gamma(v_rel, eps)
    denom = max(R_n * (1.0 - min(R_a, 1.0 - eps)), eps)
    metabolic_tier = m1 * m2 * gamma * ((S * U) / denom)
    return metabolic_tier + P_e + P_b

def reverse_engineer_rrp(
    P_retail: float,
    P_e: float,
    P_b: float,
    U: float,
    S: float = 1.0,
    R_n: float = 1.0,
    m1: float = 1.0,
    m2: float = 1.0,
    v_rel: float = 0.0,
    eps: float = 1e-16
) -> Dict[str, Any]:
    """
    Reverse engineers observed retail price (RRP) to solve for:
    1. Implied extractive drag (R_a)
    2. Recommended Retail Price / Difficulty (RRP/D) where R_a = 0 (or fair baseline)
    3. Fairness metrics: Extractive spread and Fairness Index
    """
    gamma = calculate_gamma(v_rel, eps)
    spread = P_retail - (P_e + P_b)
    
    if spread <= eps:
        implied_Ra = 0.0
    else:
        numerator = m1 * m2 * gamma * S * U
        ratio = numerator / (R_n * spread)
        implied_Ra = max(0.0, min(1.0 - ratio, 1.0))
        
    # Baseline RRP/D with fair operational reserve Ra = 0.02 (2% non-extractive contingency)
    rrp_d = calculate_forward_upe(
        P_e=P_e,
        P_b=P_b,
        U=U,
        S=S,
        R_n=R_n,
        R_a=0.02,
        m1=1.0,
        m2=1.0,
        v_rel=v_rel,
        eps=eps
    )
    
    extractive_premium = max(0.0, P_retail - rrp_d)
    fairness_index = min(1.0, rrp_d / max(P_retail, eps))
    
    return {
        "P_retail_observed": round(P_retail, 2),
        "P_energy_Pe": round(P_e, 2),
        "P_base_Pb": round(P_b, 2),
        "Metabolic_U": round(U, 2),
        "RRP_D_recommended": round(rrp_d, 2),
        "Implied_Extractive_Drag_Ra": round(implied_Ra, 4),
        "Extractive_Premium_AUD": round(extractive_premium, 2),
        "Fairness_Index_Percent": round(fairness_index * 100.0, 1)
    }

def run_benchmark_case_studies() -> List[Dict[str, Any]]:
    """Runs empirical calibration benchmarks across essential goods."""
    cases = [
        {
            "commodity": "Commercial Sliced White Bread (680g)",
            "unit": "loaf",
            "P_retail": 4.10,
            "P_e": 0.38,   # Bakery electricity, oven gas, delivery diesel
            "P_b": 0.45,   # Farm-gate flour, yeast, salt, packaging film
            "U": 2.15,     # Direct metabolic labor (farm + milling + bakery + retail shelf)
            "S": 1.00,
            "R_n": 1.00,
            "v_rel": 0.05
        },
        {
            "commodity": "Milling Wheat (APW1 / ASW1)",
            "unit": "tonne",
            "P_retail": 365.00,
            "P_e": 104.40, # Tractor diesel, crop drying, fuel
            "P_b": 82.00,  # Certified seed, crop protection, soil minerals
            "U": 95.00,   # Operational labor hours across broadacre cycle
            "S": 1.05,
            "R_n": 0.98,
            "v_rel": 0.02
        },
        {
            "commodity": "Automotive Diesel Fuel (Ultra-Low Sulphur)",
            "unit": "litre",
            "P_retail": 2.15,
            "P_e": 0.32,   # Refining electricity & process thermal energy
            "P_b": 0.92,   # Crude oil feedstock at terminal import parity
            "U": 0.35,     # Terminal operations, tanker driver, service station attendant
            "S": 1.08,
            "R_n": 0.90,
            "v_rel": 0.12
        },
        {
            "commodity": "Residential Grid Electricity (Single-Rate Flat)",
            "unit": "kWh",
            "P_retail": 0.36,
            "P_e": 0.08,   # Wholesale generation fuel & thermal loss
            "P_b": 0.07,   # Poles, wires, network maintenance capital base
            "U": 0.09,     # Lineworkers, grid engineering, customer service
            "S": 1.15,
            "R_n": 0.92,
            "v_rel": 0.08
        }
    ]
    
    results = []
    for c in cases:
        audit = reverse_engineer_rrp(
            P_retail=c["P_retail"],
            P_e=c["P_e"],
            P_b=c["P_b"],
            U=c["U"],
            S=c["S"],
            R_n=c["R_n"],
            v_rel=c["v_rel"]
        )
        audit["commodity"] = c["commodity"]
        audit["unit"] = c["unit"]
        results.append(audit)
    return results

if __name__ == "__main__":
    print("=== Universal Price Equation (UPE) Real-World Pricing & RRP/D Benchmark ===")
    results = run_benchmark_case_studies()
    for r in results:
        print(f"\nGood: {r['commodity']} (per {r['unit']})")
        print(f"  Observed Retail RRP:  ${r['P_retail_observed']:.2f}")
        print(f"  Energy Base (Pe):     ${r['P_energy_Pe']:.2f}")
        print(f"  Physical Base (Pb):   ${r['P_base_Pb']:.2f}")
        print(f"  Metabolic Labor (U):  ${r['Metabolic_U']:.2f}")
        print(f"  Fair RRP/D Benchmark: ${r['RRP_D_recommended']:.2f}")
        print(f"  Extractive Drag (Ra): {r['Implied_Extractive_Drag_Ra'] * 100:.1f}%")
        print(f"  Extractive Premium:   ${r['Extractive_Premium_AUD']:.2f}")
        print(f"  Fairness Index:       {r['Fairness_Index_Percent']:.1f}%")
