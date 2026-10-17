import numpy as np
from typing import Dict, List, Tuple, Any

class HVNLFatigueDispatchSolver:
    def __init__(self):
        self.nodes = [
            "Generic Regional", "Gilgandra", "Gunnedah", "Narrabri", 
            "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
        ]
        self.n_nodes = len(self.nodes)
        self.distance_matrix = np.array([
            [  0,  65, 110, 120, 140, 185, 180, 170, 180, 220],
            [ 65,   0, 155, 170,  65, 190, 225, 105, 190, 270],
            [110, 155,   0, 100, 210, 240,  75, 230, 180, 190],
            [120, 170, 100,   0, 240, 290, 170, 240, 115, 100],
            [140,  65, 210, 240,   0, 120, 290, 120, 250, 335],
            [185, 190, 240, 290, 120,   0, 240, 240, 360, 390],
            [180, 225,  75, 170, 290, 240,   0, 305, 255, 220],
            [170, 105, 230, 240, 120, 240, 305,   0, 130, 290],
            [180, 190, 180, 115, 250, 360, 255, 130,   0, 140],
            [220, 270, 190, 100, 335, 390, 220, 290, 140,   0]
        ], dtype=float)
        self.avg_speed_kmh = 80.0
        self.loading_time_hrs = 1.0
        self.unloading_time_hrs = 1.0
        self.max_continuous_driving_hrs = 5.25
        self.mandatory_short_rest_hrs = 0.25
        self.max_daily_work_hrs = 12.0
        self.min_daily_rest_hrs = 7.0

    def evaluate_route_fatigue(self, origin_idx: int, dest_idx: int) -> Dict[str, Any]:
        distance_one_way = self.distance_matrix[origin_idx, dest_idx]
        roundtrip_distance = distance_one_way * 2.0
        total_driving_time = roundtrip_distance / self.avg_speed_kmh
        total_work_time = total_driving_time + self.loading_time_hrs + self.unloading_time_hrs
        breaks_needed = int(total_driving_time // self.max_continuous_driving_hrs)
        total_rest_break_time = breaks_needed * self.mandatory_short_rest_hrs
        total_trip_elapsed_time = total_work_time + total_rest_break_time
        is_single_driver_compliant = (total_work_time <= self.max_daily_work_hrs)
        requires_staging_swap = not is_single_driver_compliant
        staging_hub = "Generic Regional" if requires_staging_swap else None

        return {
            "origin": self.nodes[origin_idx],
            "destination": self.nodes[dest_idx],
            "is_single_driver_compliant": is_single_driver_compliant,
            "requires_staging_swap": requires_staging_swap,
            "recommended_staging_hub": staging_hub
        }
