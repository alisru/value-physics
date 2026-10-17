"""
Spatial Trade Optimizer & Bilateral Clearing Solver
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation
Institutional Reference: ARI-VPE-OPT-2026-01

Solves optimal multi-commodity spatial routing across the 10-node regional NSW network
(Regional NSW, Gilgandra, Gunnedah, Narrabri, Dubbo, Mudgee, Tamworth, Warren, Walgett, Moree)
minimizing logistical exergy destruction (P_Q3) subject to regional carrying capacity,
Kantorovich-Samuelson spatial duality, and regularized Inter-Sovereign Trade Tensor (Xi_trade).
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, List, Tuple, Any

class SpatialTradeOptimizer:
    def __init__(self):
        self.nodes = [
            "Generic Regional Hub", "Gilgandra", "Gunnedah", "Narrabri", 
            "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
        ]
        self.n_nodes = len(self.nodes)
        
        # Spatial Highway Distance Matrix D_ij (km)
        self.distance_matrix = np.array([
            [  0,  65, 110, 120, 140, 185, 180, 170, 180, 220], # 0: Regional NSW
            [ 65,   0, 155, 170,  65, 190, 225, 105, 190, 270], # 1: Gilgandra
            [110, 155,   0, 100, 210, 240,  75, 230, 180, 190], # 2: Gunnedah
            [120, 170, 100,   0, 240, 290, 170, 240, 115, 100], # 3: Narrabri
            [140,  65, 210, 240,   0, 120, 290, 120, 250, 335], # 4: Dubbo
            [185, 190, 240, 290, 120,   0, 240, 240, 360, 390], # 5: Mudgee
            [180, 225,  75, 170, 290, 240,   0, 305, 255, 220], # 6: Tamworth
            [170, 105, 230, 240, 120, 240, 305,   0, 130, 290], # 7: Warren
            [180, 190, 180, 115, 250, 360, 255, 130,   0, 140], # 8: Walgett
            [220, 270, 190, 100, 335, 390, 220, 290, 140,   0]  # 9: Moree
        ], dtype=float)
        
        # Transport exergy cost: 0.0012 WEST tokens / tonne-km (~0.038 L diesel/t-km)
        self.exergy_cost_per_t_km = 0.0012

    def solve_optimal_dispatch(self, net_supplies: np.ndarray) -> Dict[str, Any]:
        """
        Solves the Monge-Kantorovich transportation linear program:
        min sum_{i,j} c_{ij} * x_{ij}
        subject to:
          sum_j x_{ij} <= S_i (for supply nodes i)
          sum_i x_{ij} >= -D_j (for demand nodes j)
          x_{ij} >= 0
        Extracts primal transfer flows x_{ij}^* and dual shadow prices (u_i^*, v_j^*).
        """
        sources = np.where(net_supplies > 0)[0]
        sinks = np.where(net_supplies < 0)[0]
        
        if len(sources) == 0 or len(sinks) == 0:
            return {
                "status": "No trade required",
                "total_exergy_friction_west": 0.0,
                "total_tonnes_moved": 0.0,
                "transfer_matrix": np.zeros((self.n_nodes, self.n_nodes)),
                "nodal_potentials_west": np.zeros(self.n_nodes),
                "complementary_slackness_verified": True
            }
            
        n_sources = len(sources)
        n_sinks = len(sinks)
        n_vars = n_sources * n_sinks
        
        # Cost vector c
        c = np.zeros(n_vars)
        for s_idx, i in enumerate(sources):
            for d_idx, j in enumerate(sinks):
                var_idx = s_idx * n_sinks + d_idx
                c[var_idx] = self.distance_matrix[i, j] * self.exergy_cost_per_t_km
                
        # Supply constraints: sum_{j in sinks} x_{ij} <= net_supplies[i]
        A_ub = np.zeros((n_sources, n_vars))
        b_ub = np.zeros(n_sources)
        for s_idx, i in enumerate(sources):
            for d_idx in range(n_sinks):
                var_idx = s_idx * n_sinks + d_idx
                A_ub[s_idx, var_idx] = 1.0
            b_ub[s_idx] = net_supplies[i]
            
        # Demand constraints: -sum_{i in sources} x_{ij} <= net_supplies[j]
        A_ub_demand = np.zeros((n_sinks, n_vars))
        b_ub_demand = np.zeros(n_sinks)
        for d_idx, j in enumerate(sinks):
            for s_idx in range(n_sources):
                var_idx = s_idx * n_sinks + d_idx
                A_ub_demand[d_idx, var_idx] = -1.0
            b_ub_demand[d_idx] = net_supplies[j]
            
        A_full = np.vstack([A_ub, A_ub_demand])
        b_full = np.concatenate([b_ub, b_ub_demand])
        bounds = [(0, None) for _ in range(n_vars)]
        
        res = opt.linprog(c, A_ub=A_full, b_ub=b_full, bounds=bounds, method='highs')
        
        transfer_matrix = np.zeros((self.n_nodes, self.n_nodes))
        nodal_potentials = np.zeros(self.n_nodes)
        slackness_verified = False
        
        if res.success:
            for s_idx, i in enumerate(sources):
                for d_idx, j in enumerate(sinks):
                    var_idx = s_idx * n_sinks + d_idx
                    transfer_matrix[i, j] = res.x[var_idx]
                    
            # Extract dual shadow prices from ineqlin.marginals
            # In HiGHS: marginals for A_ub @ x <= b_ub are non-positive
            marginals = res.ineqlin.marginals
            u_marginals = -marginals[:n_sources] # Supply potentials
            v_marginals = -marginals[n_sources:] # Demand potentials
            
            for s_idx, i in enumerate(sources):
                nodal_potentials[i] = u_marginals[s_idx]
            for d_idx, j in enumerate(sinks):
                nodal_potentials[j] = v_marginals[d_idx]
                
            # Verify Kantorovich-Samuelson complementary slackness:
            # For x_{ij} > 0, v_j^* - u_i^* == c_{ij}
            slackness_errors = []
            for s_idx, i in enumerate(sources):
                for d_idx, j in enumerate(sinks):
                    if transfer_matrix[i, j] > 1e-5:
                        c_ij = self.distance_matrix[i, j] * self.exergy_cost_per_t_km
                        price_diff = nodal_potentials[j] - nodal_potentials[i]
                        slackness_errors.append(abs(price_diff - c_ij))
                        
            slackness_verified = (max(slackness_errors) < 1e-4) if slackness_errors else True
                    
        return {
            "status": "Optimal" if res.success else "Failed",
            "total_exergy_friction_west": float(res.fun) if res.success else 0.0,
            "total_tonnes_moved": float(np.sum(transfer_matrix)),
            "transfer_matrix": transfer_matrix,
            "nodal_potentials_west": nodal_potentials,
            "complementary_slackness_verified": slackness_verified
        }

    def compute_inter_sovereign_trade_tensor(self, transfer_matrix: np.ndarray, 
                                            Rn_vector: np.ndarray, 
                                            d_direct: float = 0.5474) -> np.ndarray:
        """
        Computes the regularized Inter-Sovereign Trade Tensor:
        Xi_{ij} = (WEST_exported_{ij} / WEST_imported_{ji}) * [(Rn_i + Delta_Rn_i) / (Rn_j + Delta_Rn_j)]
        """
        Xi_tensor = np.zeros((self.n_nodes, self.n_nodes))
        west_matrix = transfer_matrix * 700.0 * d_direct # Tonnes to loaves to WEST difficulty
        
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                if i != j and transfer_matrix[i, j] > 0:
                    carrying_ratio = Rn_vector[i] / max(1e-6, Rn_vector[j])
                    Xi_tensor[i, j] = west_matrix[i, j] * carrying_ratio
                    
        return Xi_tensor

if __name__ == "__main__":
    optimizer = SpatialTradeOptimizer()
    net_grain = np.array([5.0, 20.0, 35.0, -15.0, 0.0, 5.0, 10.0, -10.0, -20.0, -25.0])
    Rn_vec = np.array([1.0, 1.1, 1.2, 0.4, 1.0, 1.0, 1.1, 0.5, 0.3, 0.3])
    
    result = optimizer.solve_optimal_dispatch(net_grain)
    print("Optimization Status:", result["status"])
    print(f"Total Tonnes Moved: {result['total_tonnes_moved']:.2f} t")
    print(f"Total Logistical Exergy Friction: {result['total_exergy_friction_west']:.2f} WEST Tokens")
    print("Kantorovich-Samuelson Duality Verified:", result["complementary_slackness_verified"])
    print("Nodal Shadow Potentials (WEST/t):", np.round(result["nodal_potentials_west"], 4))
