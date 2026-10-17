"""
Coupled Multi-Commodity Spatial Dispatch Solver
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation
Institutional Reference: ARI-VPE-MCD-2026-01

Solves coupled multi-commodity spatial routing across the 10-node regional NSW network
(Regional NSW, Gilgandra, Gunnedah, Narrabri, Dubbo, Mudgee, Tamworth, Warren, Walgett, Moree)
for three critical physical commodities:
1. Grain / Food (tonnes)
2. Potable Water (MegaLitres = 1,000 tonnes)
3. Mobile Emergency Generation / BESS (MWh)

Subject to joint highway link freight tonnage capacities, commodity conservation of flow,
and exergy transport friction minimization (P_Q3).
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, List, Tuple, Any

class MultiCommodityDispatchSolver:
    def __init__(self):
        self.nodes = [
            "Generic Regional Hub", "Gilgandra", "Gunnedah", "Narrabri", 
            "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
        ]
        self.n_nodes = len(self.nodes)
        
        # Commodities: 0: Grain (t), 1: Potable Water (ML), 2: Mobile BESS (MWh)
        self.commodities = ["Grain_t", "Water_ML", "Mobile_BESS_MWh"]
        self.n_commodities = len(self.commodities)
        
        # Highway Distance Matrix D_ij (km)
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
        
        # Freight weight equivalence (tonnes per commodity unit)
        # Grain: 1.0 t/t, Water: 1000.0 t/ML, BESS: 25.0 t/MWh trailer
        self.weight_factors = np.array([1.0, 1000.0, 25.0])
        
        # Unit exergy transport cost (WEST tokens per unit-km)
        # Grain: 0.0012 WEST/t-km; Water: 1.20 WEST/ML-km; BESS: 0.030 WEST/MWh-km
        self.exergy_costs = np.array([0.0012, 1.2000, 0.0300])
        
        # Directed Highway link capacity (Gross tonnage capacity per week)
        self.default_link_capacity = 800.0 # tonnes/week per corridor
        
    def solve(self, net_supplies: np.ndarray) -> Dict[str, Any]:
        """
        Solves the coupled multi-commodity linear program:
        net_supplies: shape (n_nodes, n_commodities)
          Positive: Surplus at node
          Negative: Deficit at node
        """
        # Variables: x_{k, i, j} for k in [0..2], i in [0..9], j in [0..9] where i != j
        var_map = {}
        rev_var_map = {}
        idx = 0
        for k in range(self.n_commodities):
            for i in range(self.n_nodes):
                for j in range(self.n_nodes):
                    if i != j:
                        var_map[(k, i, j)] = idx
                        rev_var_map[idx] = (k, i, j)
                        idx += 1
                        
        n_vars = idx
        c = np.zeros(n_vars)
        for (k, i, j), v_idx in var_map.items():
            c[v_idx] = self.distance_matrix[i, j] * self.exergy_costs[k]
            
        A_ub_list = []
        b_ub_list = []
        
        # 1. Supply Availability Constraints for every node and commodity
        # sum_{j != i} x_{k, i, j} <= max(0, net_supplies[i, k])
        for k in range(self.n_commodities):
            for i in range(self.n_nodes):
                row = np.zeros(n_vars)
                for j in range(self.n_nodes):
                    if i != j:
                        row[var_map[(k, i, j)]] = 1.0
                A_ub_list.append(row)
                b_ub_list.append(max(0.0, net_supplies[i, k]))
                    
        # 2. Demand Satisfaction Constraints for every node and commodity
        # sum_{i != j} x_{k, i, j} >= max(0, -net_supplies[j, k])
        # In <= form: -sum_{i != j} x_{k, i, j} <= -max(0, -net_supplies[j, k])
        for k in range(self.n_commodities):
            for j in range(self.n_nodes):
                if net_supplies[j, k] < 0:
                    row = np.zeros(n_vars)
                    for i in range(self.n_nodes):
                        if i != j:
                            row[var_map[(k, i, j)]] = -1.0
                    A_ub_list.append(row)
                    b_ub_list.append(net_supplies[j, k]) # negative number
                    
        # 3. Joint Link Capacity Constraints (Coupled fleet weight)
        # sum_k w_k * x_{k, i, j} <= C_{ij} for each directed link (i, j)
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                if i != j:
                    row = np.zeros(n_vars)
                    for k in range(self.n_commodities):
                        row[var_map[(k, i, j)]] = self.weight_factors[k]
                    A_ub_list.append(row)
                    b_ub_list.append(self.default_link_capacity)
                    
        A_ub = np.array(A_ub_list)
        b_ub = np.array(b_ub_list)
        bounds = [(0, None) for _ in range(n_vars)]
        
        res = opt.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        
        # Process results
        dispatch_flows = np.zeros((self.n_commodities, self.n_nodes, self.n_nodes))
        link_tonnage = np.zeros((self.n_nodes, self.n_nodes))
        
        if res.success:
            for v_idx, val in enumerate(res.x):
                if val > 1e-5:
                    k, i, j = rev_var_map[v_idx]
                    dispatch_flows[k, i, j] = val
                    link_tonnage[i, j] += val * self.weight_factors[k]
                    
        return {
            "status": "Optimal" if res.success else "Failed",
            "total_exergy_friction_west": float(res.fun) if res.success else 0.0,
            "dispatch_flows": dispatch_flows,
            "link_tonnage": link_tonnage,
            "max_link_utilization": float(np.max(link_tonnage) / self.default_link_capacity)
        }

if __name__ == "__main__":
    solver = MultiCommodityDispatchSolver()
    net_supplies = np.zeros((10, 3))
    
    # Drought Deficits (Walgett, Moree, Narrabri)
    net_supplies[8] = [-25.0, -0.20, -5.0]
    net_supplies[9] = [-30.0, -0.30, -8.0]
    net_supplies[3] = [-15.0, -0.10, -4.0]
    
    # Surpluses (Regional NSW, Gunnedah, Gilgandra, Dubbo)
    net_supplies[0] = [ 15.0,  0.25,  6.0]
    net_supplies[2] = [ 40.0,  0.15,  8.0]
    net_supplies[1] = [ 25.0,  0.25,  5.0]
    net_supplies[4] = [ 10.0,  0.20, 10.0]
    
    res = solver.solve(net_supplies)
    print("Optimization Status:", res["status"])
    print(f"Total Logistical Exergy Friction: {res['total_exergy_friction_west']:.2f} WEST Tokens")
    print(f"Peak Link Fleet Utilization: {res['max_link_utilization']*100:.1f}%")
    
    print("\nActive Multi-Commodity Dispatch Routes:")
    for k, c_name in enumerate(solver.commodities):
        print(f"\n--- Commodity: {c_name} ---")
        for i in range(10):
            for j in range(10):
                if res["dispatch_flows"][k, i, j] > 0.001:
                    print(f"  {solver.nodes[i]} -> {solver.nodes[j]}: {res['dispatch_flows'][k, i, j]:.2f}")
