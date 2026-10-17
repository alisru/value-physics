"""
Heavy Vehicle National Law (HVNL) Fatigue & Driver Time-Window Dispatch Solver
Alethekanon Research Institute — Division 2: Societal Economics & Macro-Micro Simulation
Institutional Reference: ARI-VPE-HVNL-2026-01

Integrates Australian Heavy Vehicle National Law (HVNL) Standard Hours into regional logistics:
1. Max continuous driving: 5.25 hours (315 minutes) before mandatory minimum 15-min rest.
2. Max total work time in 24 hours: 12.0 hours (720 minutes).
3. Min continuous stationary rest in 24 hours: 7.0 continuous hours.
4. Identifies staging hub changeovers (slip-seating) at Regional crossroads
   for multi-hop trips exceeding single-driver 12-hour statutory work thresholds.
5. Calculates total driver hours, rest breaks, and compliance validation for closed-loop freight loops.
"""

import numpy as np
from typing import Dict, List, Tuple, Any

class HVNLFatigueDispatchSolver:
    def __init__(self):
        self.nodes = [
            "Generic Regional Hub", "Gilgandra", "Gunnedah", "Narrabri", 
            "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
        ]
        self.n_nodes = len(self.nodes)
        
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
        
        # Heavy vehicle operating speed (average km/h on regional highways)
        self.avg_speed_kmh = 80.0
        
        # Terminal handling time (loading/unloading per delivery) in hours
        self.loading_time_hrs = 1.0
        self.unloading_time_hrs = 1.0
        
        # HVNL Standard Hours Parameters (hours)
        self.max_continuous_driving_hrs = 5.25 # 5 hrs 15 mins
        self.mandatory_short_rest_hrs = 0.25    # 15 mins
        self.max_daily_work_hrs = 12.0          # 12 hrs max in 24 hrs
        self.min_daily_rest_hrs = 7.0           # 7 continuous hrs

    def evaluate_route_fatigue(self, origin_idx: int, dest_idx: int) -> Dict[str, Any]:
        """
        Evaluates HVNL fatigue metrics for a single round-trip (origin -> dest -> origin):
        Loaded forward leg + unload + empty return leg + load.
        Determines if single-driver compliant or requires staging changeover.
        """
        distance_one_way = self.distance_matrix[origin_idx, dest_idx]
        roundtrip_distance = distance_one_way * 2.0
        
        driving_time_one_way = distance_one_way / self.avg_speed_kmh
        total_driving_time = roundtrip_distance / self.avg_speed_kmh
        
        # Work time = driving + loading + unloading
        total_work_time = total_driving_time + self.loading_time_hrs + self.unloading_time_hrs
        
        # Check mandatory rest breaks during driving
        # A short break is triggered if continuous driving exceeds 5.25 hrs
        breaks_needed = int(total_driving_time // self.max_continuous_driving_hrs)
        total_rest_break_time = breaks_needed * self.mandatory_short_rest_hrs
        
        total_trip_elapsed_time = total_work_time + total_rest_break_time
        
        # Check HVNL 12-hour limit
        is_single_driver_compliant = (total_work_time <= self.max_daily_work_hrs)
        
        requires_staging_swap = not is_single_driver_compliant
        staging_hub = None
        
        if requires_staging_swap:
            # Check if Regional NSW (0) or Gilgandra (1) serves as midpoint
            d_via_coona = self.distance_matrix[origin_idx, 0] + self.distance_matrix[0, dest_idx]
            d_via_gil = self.distance_matrix[origin_idx, 1] + self.distance_matrix[1, dest_idx]
            
            if d_via_coona <= d_via_gil:
                staging_hub = "Generic Regional Hub"
            else:
                staging_hub = "Gilgandra"
                
        return {
            "origin": self.nodes[origin_idx],
            "destination": self.nodes[dest_idx],
            "one_way_distance_km": distance_one_way,
            "roundtrip_distance_km": roundtrip_distance,
            "driving_time_hrs": round(total_driving_time, 2),
            "terminal_handling_hrs": round(self.loading_time_hrs + self.unloading_time_hrs, 2),
            "total_work_time_hrs": round(total_work_time, 2),
            "mandatory_short_breaks_count": breaks_needed,
            "total_trip_elapsed_hrs": round(total_trip_elapsed_time, 2),
            "is_single_driver_compliant": is_single_driver_compliant,
            "requires_staging_swap": requires_staging_swap,
            "recommended_staging_hub": staging_hub
        }

    def audit_dispatch_manifest(self, active_routes: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Audits a full regional dispatch manifest of active transport routes
        against HVNL standard hours and identifies required slip-seating hubs.
        """
        route_audits = []
        compliant_routes = 0
        staging_required_routes = 0
        total_driver_work_hours = 0.0
        
        for orig, dest in active_routes:
            audit = self.evaluate_route_fatigue(orig, dest)
            route_audits.append(audit)
            total_driver_work_hours += audit["total_work_time_hrs"]
            if audit["is_single_driver_compliant"]:
                compliant_routes += 1
            else:
                staging_required_routes += 1
                
        return {
            "total_routes_audited": len(active_routes),
            "single_driver_compliant_routes": compliant_routes,
            "staging_swap_required_routes": staging_required_routes,
            "compliance_rate_percentage": (compliant_routes / max(1, len(active_routes))) * 100.0,
            "total_driver_work_hours": round(total_driver_work_hours, 2),
            "route_details": route_audits
        }

if __name__ == "__main__":
    solver = HVNLFatigueDispatchSolver()
    
    # Active routes from closed-loop logistics:
    # 0 -> 3 (Regional NSW -> Narrabri)
    # 0 -> 8 (Regional NSW -> Walgett)
    # 1 -> 8 (Gilgandra -> Walgett)
    # 2 -> 9 (Gunnedah -> Moree)
    # 4 -> 9 (Dubbo -> Moree) - long corridor!
    # 5 -> 9 (Mudgee -> Moree) - extreme corridor!
    active_routes = [
        (0, 3), # Regional NSW -> Narrabri (120 km)
        (0, 8), # Regional NSW -> Walgett (180 km)
        (1, 8), # Gilgandra -> Walgett (190 km)
        (2, 9), # Gunnedah -> Moree (190 km)
        (4, 9), # Dubbo -> Moree (335 km)
        (5, 9)  # Mudgee -> Moree (390 km)
    ]
    
    report = solver.audit_dispatch_manifest(active_routes)
    print("--- HVNL Regional Dispatch Fatigue Audit Report ---")
    print(f"Total Routes Audited: {report['total_routes_audited']}")
    print(f"Single-Driver Compliant: {report['single_driver_compliant_routes']}")
    print(f"Staging Changeover Required: {report['staging_swap_required_routes']}")
    print(f"Single-Driver Compliance Rate: {report['compliance_rate_percentage']:.1f}%")
    print(f"Total Driver Work Hours: {report['total_driver_work_hours']:.1f} hrs\n")
    
    for r in report["route_details"]:
        status = "COMPLIANT (Single Driver)" if r["is_single_driver_compliant"] else f"STAGING REQUIRED ({r['recommended_staging_hub']} Swap)"
        print(f"Route {r['origin']} <-> {r['destination']} ({r['roundtrip_distance_km']} km roundtrip):")
        print(f"  Driving: {r['driving_time_hrs']} hrs | Handling: {r['terminal_handling_hrs']} hrs | Total Work: {r['total_work_time_hrs']} hrs")
        print(f"  HVNL Status: {status}\n")
