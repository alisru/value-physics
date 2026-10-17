"""
Closed-Loop Fleet & Deadheading Logistics Solver
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation
Institutional Reference: ARI-VPE-LOG-2026-01

Solves optimal closed-loop multi-commodity transportation and vehicle repositioning
across the 10-node regional NSW network.
Enforces:
1. Exact commodity supply and demand satisfaction across Grain, Water, and Mobile BESS.
2. Vehicle class conservation at every depot node: sum_j v_{m, j, i} == sum_j v_{m, i, j}.
3. Loaded vs empty tare fuel exergy friction accounting (deadheading penalty).
4. Highway link gross freight capacity constraints.
"""

import numpy as np
import scipy.optimize as opt
from typing import Dict, List, Tuple, Any

class ClosedLoopLogisticsSolver:
    def __init__(self):
        self.nodes = [
            "Generic Regional Hub", "Gilgandra", "Gunnedah", "Narrabri", 
            "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
        ]
        self.n_nodes = len(self.nodes)
        
        # Vehicle Classes:
        # 0: B-Double Grain Tipper (Payload: 40 t, Tare GVM: 22 t, Loaded GVM: 62.5 t)
        # 1: Liquid Potable Water Tanker (Payload: 0.030 ML = 30 t, Tare GVM: 18 t, Loaded GVM: 48 t)
        # 2: Low-Loader BESS Flatbed (Payload: 1.0 MWh = 25 t, Tare GVM: 20 t, Loaded GVM: 45 t)
        self.vehicle_classes = ["Grain_BDouble", "Water_Tanker", "BESS_LowLoader"]
        self.n_classes = len(self.vehicle_classes)
        
        # Payload capacity per vehicle trip
        self.payload_capacities = np.array([40.0, 0.030, 1.0])
        
        # Loaded and Tare fuel exergy burn rates (WEST tokens per vehicle-km)
        # 1 L diesel ~ 0.10 WEST difficulty equivalent
        self.loaded_exergy_per_km = np.array([0.055, 0.058, 0.060])
        self.tare_exergy_per_km   = np.array([0.032, 0.034, 0.035])
        
        # Gross Vehicle Mass (tonnes)
        self.loaded_gvm = np.array([62.5, 48.0, 45.0])
        self.tare_gvm   = np.array([22.0, 18.0, 20.0])
        
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
        
        # Directed corridor weekly gross freight capacity limit (tonnes)
        self.link_capacity = 2500.0

    def solve_closed_loop(self, net_supplies: np.ndarray) -> Dict[str, Any]:
        """
        net_supplies: shape (10 nodes, 3 commodities)
          Positive: Surplus commodity at node
          Negative: Deficit commodity at node
        """
        # Variables:
        # For each class m in [0..2], origin i in [0..9], dest j in [0..9] (i != j):
        # f_{m, i, j} : Loaded trips
        # e_{m, i, j} : Empty deadhead repositioning trips
        # Total links per class: 90. Total variables = 3 * 90 * 2 = 540 variables.
        f_map = {}
        e_map = {}
        rev_map = {}
        idx = 0
        
        for m in range(self.n_classes):
            for i in range(self.n_nodes):
                for j in range(self.n_nodes):
                    if i != j:
                        f_map[(m, i, j)] = idx
                        rev_map[idx] = ("loaded", m, i, j)
                        idx += 1
                        e_map[(m, i, j)] = idx
                        rev_map[idx] = ("empty", m, i, j)
                        idx += 1
                        
        n_vars = idx
        c = np.zeros(n_vars)
        for (m, i, j), var_idx in f_map.items():
            c[var_idx] = self.distance_matrix[i, j] * self.loaded_exergy_per_km[m]
        for (m, i, j), var_idx in e_map.items():
            c[var_idx] = self.distance_matrix[i, j] * self.tare_exergy_per_km[m]
            
        A_ub_list = []
        b_ub_list = []
        A_eq_list = []
        b_eq_list = []
        
        # 1. Supply limits: sum_j f_{m, i, j} * payload_m <= max(0, Surplus_{i, m})
        for m in range(self.n_classes):
            for i in range(self.n_nodes):
                row = np.zeros(n_vars)
                for j in range(self.n_nodes):
                    if i != j:
                        row[f_map[(m, i, j)]] = self.payload_capacities[m]
                A_ub_list.append(row)
                b_ub_list.append(max(0.0, net_supplies[i, m]))
                
        # 2. Demand satisfaction: sum_i f_{m, i, j} * payload_m >= max(0, -Deficit_{j, m})
        # In <= form: -sum_i f_{m, i, j} * payload_m <= Deficit_{j, m} (negative)
        for m in range(self.n_classes):
            for j in range(self.n_nodes):
                if net_supplies[j, m] < 0:
                    row = np.zeros(n_vars)
                    for i in range(self.n_nodes):
                        if i != j:
                            row[f_map[(m, i, j)]] = -self.payload_capacities[m]
                    A_ub_list.append(row)
                    b_ub_list.append(net_supplies[j, m])
                    
        # 3. Closed-Loop Vehicle Fleet Balance at each node:
        # sum_{j != i} (f_{m, j, i} + e_{m, j, i}) - sum_{j != i} (f_{m, i, j} + e_{m, i, j}) == 0
        for m in range(self.n_classes):
            for i in range(self.n_nodes):
                row = np.zeros(n_vars)
                for j in range(self.n_nodes):
                    if i != j:
                        # Inflow
                        row[f_map[(m, j, i)]] += 1.0
                        row[e_map[(m, j, i)]] += 1.0
                        # Outflow
                        row[f_map[(m, i, j)]] -= 1.0
                        row[e_map[(m, i, j)]] -= 1.0
                A_eq_list.append(row)
                b_eq_list.append(0.0)
                
        # 4. Highway corridor capacity constraints:
        # sum_m (loaded_gvm_m * f_{m, i, j} + tare_gvm_m * e_{m, i, j}) <= link_capacity
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                if i != j:
                    row = np.zeros(n_vars)
                    for m in range(self.n_classes):
                        row[f_map[(m, i, j)]] = self.loaded_gvm[m]
                        row[e_map[(m, i, j)]] = self.tare_gvm[m]
                    A_ub_list.append(row)
                    b_ub_list.append(self.link_capacity)
                    
        A_ub = np.array(A_ub_list)
        b_ub = np.array(b_ub_list)
        A_eq = np.array(A_eq_list)
        b_eq = np.array(b_eq_list)
        bounds = [(0, None) for _ in range(n_vars)]
        
        res = opt.linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        loaded_trips = np.zeros((self.n_classes, self.n_nodes, self.n_nodes))
        empty_trips  = np.zeros((self.n_classes, self.n_nodes, self.n_nodes))
        delivered_payload = np.zeros((self.n_classes, self.n_nodes, self.n_nodes))
        link_tonnage = np.zeros((self.n_nodes, self.n_nodes))
        
        total_loaded_exergy = 0.0
        total_empty_exergy = 0.0
        
        if res.success:
            for idx_v, val in enumerate(res.x):
                if val > 1e-5:
                    v_type, m, i, j = rev_map[idx_v]
                    if v_type == "loaded":
                        loaded_trips[m, i, j] = val
                        delivered_payload[m, i, j] = val * self.payload_capacities[m]
                        link_tonnage[i, j] += val * self.loaded_gvm[m]
                        total_loaded_exergy += val * self.distance_matrix[i, j] * self.loaded_exergy_per_km[m]
                    else:
                        empty_trips[m, i, j] = val
                        link_tonnage[i, j] += val * self.tare_gvm[m]
                        total_empty_exergy += val * self.distance_matrix[i, j] * self.tare_exergy_per_km[m]
                        
        # Check node balance conservation
        balance_errors = []
        for m in range(self.n_classes):
            for i in range(self.n_nodes):
                inflow = np.sum(loaded_trips[m, :, i]) + np.sum(empty_trips[m, :, i])
                outflow = np.sum(loaded_trips[m, i, :]) + np.sum(empty_trips[m, i, :])
                balance_errors.append(abs(inflow - outflow))
                
        balance_verified = (max(balance_errors) < 1e-4) if balance_errors else True
        
        return {
            "status": "Optimal" if res.success else "Failed",
            "total_system_exergy_west": float(res.fun) if res.success else 0.0,
            "loaded_exergy_west": total_loaded_exergy,
            "deadhead_exergy_west": total_empty_exergy,
            "deadhead_overhead_percentage": (total_empty_exergy / max(1e-6, total_loaded_exergy)) * 100.0,
            "fleet_balance_conserved": balance_verified,
            "loaded_trips": loaded_trips,
            "empty_trips": empty_trips,
            "delivered_payload": delivered_payload,
            "peak_link_utilization": float(np.max(link_tonnage) / self.link_capacity)
        }

if __name__ == "__main__":
    solver = ClosedLoopLogisticsSolver()
    
    # Net supplies matrix: shape (10 nodes, 3 commodities)
    # Grain (t), Water (ML), BESS (MWh)
    net_supplies = np.zeros((10, 3))
    
    # Drought Deficits (Walgett, Moree, Narrabri)
    net_supplies[8] = [-40.0, -0.060, -2.0]
    net_supplies[9] = [-80.0, -0.090, -4.0]
    net_supplies[3] = [-40.0, -0.030, -2.0]
    
    # Surpluses (Regional NSW, Gunnedah, Gilgandra, Dubbo)
    net_supplies[0] = [ 40.0,  0.060,  3.0]
    net_supplies[2] = [ 80.0,  0.060,  3.0]
    net_supplies[1] = [ 40.0,  0.060,  2.0]
    
    res = solver.solve_closed_loop(net_supplies)
    print("Closed-Loop Optimization Status:", res["status"])
    print(f"Total System Exergy: {res['total_system_exergy_west']:.2f} WEST Tokens")
    print(f"  - Loaded Delivery Exergy: {res['loaded_exergy_west']:.2f} WEST Tokens")
    print(f"  - Deadhead Return Exergy: {res['deadhead_exergy_west']:.2f} WEST Tokens")
    print(f"Deadhead Tare Overhead: {res['deadhead_overhead_percentage']:.1f}%")
    print(f"Fleet Depot Balance Conserved: {res['fleet_balance_conserved']}")
    print(f"Peak Highway Corridor Utilization: {res['peak_link_utilization']*100:.1f}%")
    
    print("\nSample Vehicle Trips (Loaded vs Empty Repositioning):")
    for m, c_name in enumerate(solver.vehicle_classes):
        print(f"\n--- Vehicle Class: {c_name} ---")
        for i in range(10):
            for j in range(10):
                if res["loaded_trips"][m, i, j] > 0.01 or res["empty_trips"][m, i, j] > 0.01:
                    print(f"  {solver.nodes[i]} -> {solver.nodes[j]}: "
                          f"Loaded Trips: {res['loaded_trips'][m, i, j]:.2f}, "
                          f"Empty Deadhead: {res['empty_trips'][m, i, j]:.2f}")
