"""
Value Physics Engine (vpe) - Core Mathematical & Computational Framework
Alethekanon Research Institute | Division 2: Societal Economics & Value Physics
Institutional Identifier: ARI-VPE-ENG-2026-01
"""

import math
import hashlib
import numpy as np

# Constant for Cost of Being baseline non-zero floor
INF_U = 1e-9

def calculate_urgency_velocity(u_a: float, u_b: float) -> float:
    """Computes regularized relative urgency velocity v_rel in [0, 1)."""
    max_u = max(u_a, u_b)
    diff_u = abs(u_a - u_b)
    return diff_u / (max_u + INF_U)

def calculate_lorentz_coercion(v_rel: float) -> float:
    """Computes relativistic Lorentz Coercion Factor gamma(v_rel)."""
    if v_rel >= 1.0:
        v_rel = 0.999999999
    return 1.0 / math.sqrt(1.0 - v_rel**2)

def calculate_difficulty(skill_years: float, met_exertion: float, danger: float, attention: float) -> float:
    """Computes instantaneous human metabolic and cognitive difficulty D in WEST tokens."""
    s = 1.0 + math.log(1.0 + max(0.0, skill_years))
    e = max(1.0, met_exertion)
    d = max(0.0, danger)
    c = max(0.0, attention)
    return s * e * (1.0 + d) * (1.0 + c)

def universal_price_equation(s: float, u: float, r_n: float, r_a: float, 
                             p_e: float, p_b: float, v_rel: float = 0.0, 
                             m1: float = 1.0, m2: float = 1.0) -> float:
    """Master Universal Price Equation (UPE): P(x, t) = m1*m2*gamma*( (S*U)/(Rn*(1-Ra)) ) + Pe + Pb"""
    gamma = calculate_lorentz_coercion(v_rel)
    r_a_clamped = min(0.999999, max(0.0, r_a))
    r_n_clamped = max(1e-6, r_n)
    scarcity_strain = (s * u) / (r_n_clamped * (1.0 - r_a_clamped))
    return m1 * m2 * gamma * scarcity_strain + p_e + p_b

def compute_distortion_quotient(nominal_price_share: float, west_difficulty_share: float) -> float:
    """Calculates Distortion Quotient DQ = (% Nominal Price Share) / (% WEST Share)."""
    if west_difficulty_share <= 0:
        return 0.0
    return nominal_price_share / west_difficulty_share

def solve_leontief_embodied_difficulty(a_matrix: np.ndarray, d_direct: np.ndarray) -> np.ndarray:
    """Computes total integrated embodied difficulty: d_integrated = d_direct * (I - A)^(-1)."""
    i_matrix = np.eye(a_matrix.shape[0])
    leontief_inv = np.linalg.inv(i_matrix - a_matrix)
    return np.dot(d_direct, leontief_inv)

def generate_pod_block_header(parent_hash: str, timestamp: int, plane_id: int, guild_id: int,
                              skill_s: float, exertion_e: float, danger_d: float, attention_c: float,
                              exergy_pe_mj: float, state_root_book2: str) -> str:
    """Generates SHA-256 Proof-of-Difficulty (PoD) block hash for Book 3 Reality Ledger."""
    payload = f"{parent_hash}|{timestamp}|{plane_id}|{guild_id}|{skill_s:.4f}|{exertion_e:.4f}|{danger_d:.4f}|{attention_c:.4f}|{exergy_pe_mj:.4f}|{state_root_book2}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    # Self-test validation
    v_rel = calculate_urgency_velocity(100.0, 0.0)
    gamma = calculate_lorentz_coercion(v_rel)
    p_total = universal_price_equation(s=1.0, u=1.0, r_n=1.0, r_a=0.0, p_e=0.5, p_b=0.5, v_rel=0.0)
    print(f"Self-Test PASS: v_rel={v_rel:.4f}, gamma={gamma:.4f}, p_total={p_total:.4f}")
