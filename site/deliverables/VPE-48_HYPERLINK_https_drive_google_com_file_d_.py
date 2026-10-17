"""
Thermodynamic Work-Antiwork State-Space Dynamics Solver
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation
Institutional Reference: ARI-VPE-WAD-2026-01 | Deliverable ID: VPE-48
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Any

class WorkAntiworkDynamics:
    def __init__(
        self,
        alpha: float = 0.85,
        delta_p: float = 0.05,
        beta: float = 0.90,
        gamma: float = 0.12,
        mu: float = 0.04,
        nu: float = 1.15,
        eps: float = 1e-4
    ):
        self.alpha = alpha
        self.delta_p = delta_p
        self.beta = beta
        self.gamma = gamma
        self.mu = mu
        self.nu = nu
        self.eps = eps
        
        self.A_leontief = np.array([
            [0.000, 0.001, 0.002, 0.500, 0.100],
            [0.050, 0.000, 0.450, 15.000, 1.200],
            [0.002, 0.001, 0.000, 0.800, 0.050],
            [0.001, 0.0005, 0.0005, 0.000, 0.020],
            [0.002, 0.001, 0.001, 0.050, 0.000]
        ], dtype=float)

    def derivatives(self, t: float, state: np.ndarray, W_a_func, A_a_func, M_func) -> np.ndarray:
        W_p, A_p = state
        W_p = max(0.0, W_p)
        A_p = max(0.0, A_p)

        W_a = W_a_func(t)
        A_a = A_a_func(t)
        M = M_func(t)
        M_req = self.delta_p * W_p

        neglect = max(0.0, 1.0 - (M / (M_req + self.eps)))
        net_productive = max(0.0, W_a - A_a)
        dW_p_dt = self.alpha * net_productive - self.delta_p * W_p

        net_reductive = max(0.0, A_a - W_a)
        dA_p_dt = self.beta * net_reductive + self.gamma * W_p * neglect + self.mu * (A_p ** self.nu)

        return np.array([dW_p_dt, dA_p_dt])

    def calculate_finite_time_blowup(self, A_p_0: float) -> float:
        if self.nu <= 1.0 or A_p_0 <= 0.0:
            return float('inf')
        return 1.0 / (self.mu * (self.nu - 1.0) * (A_p_0 ** (self.nu - 1.0)))

    def integrate_multisector_floors(self, direct_W_p: np.ndarray, direct_A_p: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        I = np.eye(5)
        L_inv = np.linalg.inv(I - self.A_leontief)
        integrated_W_p = np.dot(direct_W_p, L_inv)
        integrated_A_p = np.dot(direct_A_p, L_inv)
        return integrated_W_p, integrated_A_p

    def multisector_derivatives(self, t: float, state_10: np.ndarray, 
                                W_a_vec: np.ndarray, A_a_vec: np.ndarray, 
                                M_vec: np.ndarray) -> np.ndarray:
        W_p = np.maximum(0.0, state_10[:5])
        A_p = np.maximum(0.0, state_10[5:])
        
        M_req = self.delta_p * W_p
        neglect = np.maximum(0.0, 1.0 - (M_vec / (M_req + self.eps)))
        
        net_productive = np.maximum(0.0, W_a_vec - A_a_vec)
        dW_p_dt = self.alpha * net_productive - self.delta_p * W_p
        
        net_reductive = np.maximum(0.0, A_a_vec - W_a_vec)
        drag_propagation = np.dot(self.A_leontief.T, A_p)
        
        dA_p_dt = (self.beta * net_reductive + 
                   self.gamma * W_p * neglect + 
                   self.mu * (A_p ** self.nu) + 
                   0.05 * drag_propagation)
        
        return np.concatenate([dW_p_dt, dA_p_dt])

    def compute_endogenous_leontief(self, drag_ratio: float, lambda_factor: float = 0.15) -> Dict[str, Any]:
        scale_factor = 1.0 + lambda_factor * max(0.0, drag_ratio)
        A_endogenous = self.A_leontief * scale_factor
        
        eigenvalues = np.linalg.eigvals(A_endogenous)
        spectral_radius = float(np.max(np.abs(eigenvalues)))
        
        I = np.eye(5)
        if spectral_radius < 1.0:
            L_inv = np.linalg.inv(I - A_endogenous)
            multiplier_norm = float(np.linalg.norm(L_inv, ord=np.inf))
            is_singular = False
        else:
            L_inv = None
            multiplier_norm = float('inf')
            is_singular = True
            
        rho_0 = float(np.max(np.abs(np.linalg.eigvals(self.A_leontief))))
        critical_drag_ratio = ( (1.0 / rho_0) - 1.0 ) / lambda_factor if lambda_factor > 0 else float('inf')
        
        return {
            "scale_factor": scale_factor,
            "spectral_radius": spectral_radius,
            "multiplier_norm": multiplier_norm,
            "is_singular": is_singular,
            "critical_drag_ratio": critical_drag_ratio,
            "A_endogenous": A_endogenous
        }

    def compute_kramers_escape(self, W_p: float, A_p: float, W_a: float, A_a: float,
                               sigma_W: float = 5.0, sigma_A: float = 3.0) -> Dict[str, float]:
        L_crit = A_a / max(1e-4, W_a)
        buffer_distance = W_p - L_crit * A_p
        
        D_eff = 0.5 * ((self.alpha * sigma_W)**2 + sigma_A**2)
        delta_U = max(0.0, buffer_distance * self.delta_p)
        
        omega_well = self.delta_p
        omega_barrier = self.delta_p * 1.5
        prefactor = (2.0 * np.pi) / np.sqrt(omega_well * omega_barrier)
        
        if buffer_distance <= 0:
            tau_escape = 0.0
            escape_rate = float('inf')
        else:
            tau_escape = prefactor * np.exp(delta_U / max(1e-4, D_eff))
            escape_rate = 1.0 / tau_escape if tau_escape > 0 else float('inf')
            
        return {
            "buffer_distance": float(buffer_distance),
            "delta_U_barrier": float(delta_U),
            "D_eff": float(D_eff),
            "prefactor": float(prefactor),
            "tau_escape_years": float(tau_escape),
            "escape_rate_annual": float(escape_rate)
        }

    def compute_colored_noise_kramers(self, W_p: float, A_p: float, W_a: float, A_a: float,
                                      tau_corr: float = 2.5, sigma_W: float = 5.0, 
                                      sigma_A: float = 3.0) -> Dict[str, float]:
        base_res = self.compute_kramers_escape(W_p, A_p, W_a, A_a, sigma_W, sigma_A)
        D_0 = base_res["D_eff"]
        color_factor = np.sqrt(1.0 + self.delta_p * tau_corr)
        D_eff_colored = D_0 / (1.0 + self.delta_p * max(0.0, tau_corr))
        
        if base_res["buffer_distance"] <= 0:
            tau_colored = 0.0
        else:
            tau_colored = base_res["prefactor"] * color_factor * np.exp(base_res["delta_U_barrier"] / max(1e-4, D_0))
            
        return {
            "tau_corr_years": float(tau_corr),
            "D_0_white": float(D_0),
            "D_eff_colored": float(D_eff_colored),
            "tau_colored_years": float(tau_colored),
            "color_prefactor_boost": float(color_factor)
        }

    def evaluate_state(self, W_a: float, A_a: float, W_p: float, A_p: float) -> Dict[str, Any]:
        x = W_a - A_a
        y = W_p - A_p

        P = (x + y) / np.sqrt(2.0)
        A = (x - y) / np.sqrt(2.0)

        if x >= 0 and y >= 0:
            condition = "Condition 1: Pure Productive Surplus"
        elif x < 0 and y >= 0:
            condition = "Condition 2: Living Off Capital"
        elif x < 0 and y < 0:
            condition = "Condition 3: Terminal Regressive Collapse"
        else:
            condition = "Condition 4: The Treadmill Trap"

        L_k = (W_p + self.eps) / (A_p + self.eps)
        L_crit = A_a / (W_a + self.eps)
        is_surplus_generating = (L_k > L_crit)

        x_envelope = 100.0
        y_envelope = 500.0
        lyapunov_metric = (x / x_envelope)**2 + (y / y_envelope)**2
        invariant_pass = (lyapunov_metric <= 1.0) and (y >= -0.8 * y_envelope)
        
        t_blowup = self.calculate_finite_time_blowup(A_p)

        return {
            "x_raw": x,
            "y_raw": y,
            "P_potential": P,
            "A_activity": A,
            "condition": condition,
            "kinetic_leverage": L_k,
            "critical_leverage": L_crit,
            "is_surplus_generating": is_surplus_generating,
            "lyapunov_metric": lyapunov_metric,
            "invariant_pass": invariant_pass,
            "t_blowup": t_blowup
        }

class InvertibleUPESolver:
    @staticmethod
    def gamma(v_rel: float) -> float:
        v = min(0.999999, max(0.0, v_rel))
        return 1.0 / np.sqrt(1.0 - v**2)

    @staticmethod
    def calculate_price(m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Rn=1.0, Ra=0.77, Pe=0.45, Pb=0.70) -> float:
        g = InvertibleUPESolver.gamma(v_rel)
        P_kinetic = (m1 * m2 * g * S * U) / (Rn * (1.0 - Ra))
        return float(P_kinetic + Pe + Pb)

    @staticmethod
    def solve_Ra(P: float, m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Rn=1.0, Pe=0.45, Pb=0.70) -> float:
        P_kinetic = max(1e-6, P - Pe - Pb)
        g = InvertibleUPESolver.gamma(v_rel)
        numerator = m1 * m2 * g * S * U
        return float(1.0 - (numerator / (Rn * P_kinetic)))

    @staticmethod
    def solve_Rn(P: float, m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Ra=0.77, Pe=0.45, Pb=0.70) -> float:
        P_kinetic = max(1e-6, P - Pe - Pb)
        g = InvertibleUPESolver.gamma(v_rel)
        numerator = m1 * m2 * g * S * U
        return float(numerator / (P_kinetic * (1.0 - Ra)))

    @staticmethod
    def solve_v_rel(P: float, m1=1.0, m2=1.0, S=1.0, U=1.0, Rn=1.0, Ra=0.77, Pe=0.45, Pb=0.70) -> float:
        P_kinetic = max(1e-6, P - Pe - Pb)
        g_target = (P_kinetic * Rn * (1.0 - Ra)) / (m1 * m2 * S * U)
        if g_target < 1.0:
            return 0.0
        v_sq = 1.0 - (1.0 / (g_target**2))
        return float(np.sqrt(max(0.0, v_sq)))

    @staticmethod
    def solve_Pb(P: float, m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Rn=1.0, Ra=0.77, Pe=0.45) -> float:
        g = InvertibleUPESolver.gamma(v_rel)
        P_kinetic = (m1 * m2 * g * S * U) / (Rn * (1.0 - Ra))
        return float(P - Pe - P_kinetic)

    @staticmethod
    def estimate_longitudinal_decoupling(
        P_obs: np.ndarray,
        I_n: np.ndarray,
        R_n_0: float,
        R_a_0: float,
        delta_n: float = 0.05,
        alpha_n: float = 0.80,
        m1: float = 1.0,
        m2: float = 1.0,
        v_rel: float = 0.0,
        S: float = 1.0,
        U: float = 1.0,
        Pe: float = 0.45,
        Pb: float = 0.70
    ) -> Tuple[np.ndarray, np.ndarray]:
        T = len(P_obs)
        R_n_est = np.zeros(T)
        R_a_est = np.zeros(T)
        R_n_est[0] = R_n_0
        R_a_est[0] = R_a_0

        g = InvertibleUPESolver.gamma(v_rel)
        numerator = m1 * m2 * g * S * U

        P_kinetic = np.maximum(1e-6, P_obs - Pe - Pb)
        Y_obs = np.log(P_kinetic) - np.log(numerator)

        for t in range(T - 1):
            R_n_est[t+1] = (1.0 - delta_n) * R_n_est[t] + alpha_n * I_n[t]
            delta_ln_Rn = np.log(R_n_est[t+1]) - np.log(R_n_est[t])
            delta_Y = Y_obs[t+1] - Y_obs[t]

            delta_ln_comp = - delta_Y - delta_ln_Rn
            ln_comp_next = np.log(max(1e-6, 1.0 - R_a_est[t])) + delta_ln_comp
            R_a_est[t+1] = float(1.0 - np.exp(ln_comp_next))

        return R_n_est, R_a_est

class ExtendedKalmanDecoupler:
    """
    Extended Kalman Filter state-space observer for decoupling physical carrying capacity
    R_n(t) from monopoly enclosure R_a(t) under stochastic observation noise (Theorem 2.8).
    """
    def __init__(self, delta_n=0.05, alpha_n=0.80, q_z=1e-4, q_theta=1e-3, r_meas=1e-3):
        self.delta_n = delta_n
        self.alpha_n = alpha_n
        self.Q = np.diag([q_z, q_theta])
        self.R = r_meas
        self.H = np.array([[-1.0, -1.0]])
        
    def filter_panel(self, P_obs, I_n, R_n_0, R_a_0, m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Pe=0.45, Pb=0.70):
        T = len(P_obs)
        g = 1.0 / np.sqrt(1.0 - min(0.9999, max(0.0, v_rel))**2)
        numerator = m1 * m2 * g * S * U
        
        P_kin = np.maximum(1e-6, P_obs - Pe - Pb)
        y = np.log(P_kin) - np.log(numerator)
        
        x_est = np.zeros((T, 2))
        x_est[0] = [np.log(R_n_0), np.log(1.0 - R_a_0)]
        P_cov = np.eye(2) * 0.01
        
        R_n_out = np.zeros(T)
        R_a_out = np.zeros(T)
        R_n_out[0] = R_n_0
        R_a_out[0] = R_a_0
        
        for t in range(T - 1):
            z_curr = x_est[t, 0]
            theta_curr = x_est[t, 1]
            
            arg = (1.0 - self.delta_n) + self.alpha_n * (I_n[t] / np.exp(z_curr))
            z_pred = z_curr + np.log(max(1e-6, arg))
            theta_pred = theta_curr
            x_pred = np.array([z_pred, theta_pred])
            
            d_arg = - self.alpha_n * I_n[t] * np.exp(-z_curr)
            F11 = 1.0 + (d_arg / arg)
            F = np.array([[F11, 0.0], [0.0, 1.0]])
            
            P_pred = F @ P_cov @ F.T + self.Q
            
            y_meas = y[t+1]
            y_pred = -x_pred[0] - x_pred[1]
            residual = y_meas - y_pred
            
            S_meas = (self.H @ P_pred @ self.H.T)[0, 0] + self.R
            K = (P_pred @ self.H.T) / S_meas
            
            x_next = x_pred + K.flatten() * residual
            P_cov = (np.eye(2) - K @ self.H) @ P_pred
            
            x_est[t+1] = x_next
            R_n_out[t+1] = np.exp(x_next[0])
            R_a_out[t+1] = 1.0 - np.exp(x_next[1])
            
        return R_n_out, R_a_out

from scipy.linalg import cholesky

class UnscentedKalmanDecoupler:
    """
    Unscented Kalman Filter state-space observer for high-order non-linear
    reconstruction of physical carrying capacity R_n(t) and monopoly extraction R_a(t)
    under stochastic observation noise (Theorem 5.4).
    """
    def __init__(self, delta_n=0.05, alpha_n=0.80, q_z=1e-4, q_theta=1e-3, r_meas=1e-3, alpha=1e-3, beta=2.0, kappa=0.0):
        self.delta_n = delta_n
        self.alpha_n = alpha_n
        self.Q = np.diag([q_z, q_theta])
        self.R = r_meas
        self.n = 2
        self.alpha = alpha
        self.beta = beta
        self.kappa = kappa
        self.lam = (self.alpha**2) * (self.n + self.kappa) - self.n
        
        self.Wm = np.zeros(2 * self.n + 1)
        self.Wc = np.zeros(2 * self.n + 1)
        self.Wm[0] = self.lam / (self.n + self.lam)
        self.Wc[0] = self.Wm[0] + (1.0 - self.alpha**2 + self.beta)
        for i in range(1, 2 * self.n + 1):
            self.Wm[i] = 1.0 / (2.0 * (self.n + self.lam))
            self.Wc[i] = self.Wm[i]
            
    def state_transition(self, x, I_n_val):
        z, theta = x
        arg = (1.0 - self.delta_n) + self.alpha_n * (I_n_val / np.exp(z))
        z_next = z + np.log(max(1e-6, arg))
        theta_next = theta
        return np.array([z_next, theta_next])
        
    def measurement_model(self, x):
        return -x[0] - x[1]
        
    def filter_panel(self, P_obs, I_n, R_n_0, R_a_0, m1=1.0, m2=1.0, v_rel=0.0, S=1.0, U=1.0, Pe=0.45, Pb=0.70):
        T = len(P_obs)
        g = 1.0 / np.sqrt(1.0 - min(0.9999, max(0.0, v_rel))**2)
        numerator = m1 * m2 * g * S * U
        P_kin = np.maximum(1e-6, P_obs - Pe - Pb)
        y = np.log(P_kin) - np.log(numerator)
        
        x_est = np.zeros((T, 2))
        x_est[0] = [np.log(R_n_0), np.log(1.0 - R_a_0)]
        P_cov = np.eye(2) * 0.01
        
        R_n_out = np.zeros(T)
        R_a_out = np.zeros(T)
        R_n_out[0] = R_n_0
        R_a_out[0] = R_a_0
        
        for t in range(T - 1):
            try:
                sqP = cholesky((self.n + self.lam) * P_cov)
            except np.linalg.LinAlgError:
                sqP = np.sqrt(np.maximum(1e-8, (self.n + self.lam) * np.diag(P_cov))) * np.eye(2)
                
            sigmas = np.zeros((2 * self.n + 1, self.n))
            sigmas[0] = x_est[t]
            for i in range(self.n):
                sigmas[i + 1] = x_est[t] + sqP[i]
                sigmas[i + 1 + self.n] = x_est[t] - sqP[i]
                
            sigmas_f = np.zeros_like(sigmas)
            for i in range(2 * self.n + 1):
                sigmas_f[i] = self.state_transition(sigmas[i], I_n[t])
                
            x_pred = np.sum(self.Wm[:, None] * sigmas_f, axis=0)
            P_pred = np.zeros((self.n, self.n))
            for i in range(2 * self.n + 1):
                diff = sigmas_f[i] - x_pred
                P_pred += self.Wc[i] * np.outer(diff, diff)
            P_pred += self.Q
            
            try:
                sqP_pred = cholesky((self.n + self.lam) * P_pred)
            except np.linalg.LinAlgError:
                sqP_pred = np.sqrt(np.maximum(1e-8, (self.n + self.lam) * np.diag(P_pred))) * np.eye(2)
                
            sigmas_pred = np.zeros((2 * self.n + 1, self.n))
            sigmas_pred[0] = x_pred
            for i in range(self.n):
                sigmas_pred[i + 1] = x_pred + sqP_pred[i]
                sigmas_pred[i + 1 + self.n] = x_pred - sqP_pred[i]
                
            gamma_y = np.array([self.measurement_model(sigmas_pred[i]) for i in range(2 * self.n + 1)])
            y_pred = np.sum(self.Wm * gamma_y)
            
            P_yy = np.sum(self.Wc * (gamma_y - y_pred)**2) + self.R
            P_xy = np.zeros(self.n)
            for i in range(2 * self.n + 1):
                P_xy += self.Wc[i] * (sigmas_pred[i] - x_pred) * (gamma_y[i] - y_pred)
                
            K = P_xy / P_yy
            residual = y[t+1] - y_pred
            x_next = x_pred + K * residual
            P_cov = P_pred - np.outer(K, K) * P_yy
            
            x_est[t+1] = x_next
            R_n_out[t+1] = np.exp(x_next[0])
            R_a_out[t+1] = 1.0 - np.exp(x_next[1])
            
        return R_n_out, R_a_out
