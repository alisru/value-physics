"""
Unit Test Suite for Value Physics RRP Fairness Audit Engine
Deliverable ID: VPE-56 | Alethekanon Research Institute — Division 2
Author: Jarrod Lyndsay Hamilton, Coonabarabran, NSW 2357

Empirical test suite verifying 14 real-world benchmark commodity calibrations across
Food, Fuel, Energy, Water, Sanitation, Essential Healthcare, Shelter, and Freight Logistics.
"""

import unittest
import sys
from rrp_fairness_audit import (
    calculate_gamma,
    calculate_forward_upe,
    audit_commercial_rrp,
    get_australian_benchmark_dataset,
    run_full_fairness_audit
)

class TestRRPFairnessAudit(unittest.TestCase):
    def test_gamma_calculation(self):
        # Zero velocity -> gamma = 1.0
        self.assertAlmostEqual(calculate_gamma(0.0), 1.0, places=4)
        # v = 0.6 -> gamma = 1 / sqrt(1 - 0.36) = 1 / 0.8 = 1.25
        self.assertAlmostEqual(calculate_gamma(0.6), 1.25, places=4)

    def test_forward_upe_calculation(self):
        # Test bread forward baseline
        p_bread = calculate_forward_upe(
            P_e=0.38, P_b=0.45, U=2.15, S=1.0, R_n=1.0, R_a=0.02, v_rel=0.05
        )
        self.assertAlmostEqual(p_bread, 3.03, delta=0.02)
        # Test water cartage forward baseline
        p_water = calculate_forward_upe(
            P_e=4.32, P_b=3.95, U=3.20, S=1.30, R_n=0.75, R_a=0.02, v_rel=0.25
        )
        self.assertAlmostEqual(p_water, 14.12, delta=0.02)

    def test_fourteen_benchmark_commodities_audit(self):
        results = run_full_fairness_audit()
        self.assertEqual(len(results), 14)
        
        # Build lookup dict by commodity name
        audit_by_name = {r["commodity"]: r for r in results}

        # 1. Bread
        bread = audit_by_name["Commercial Sliced White Bread (680g)"]
        self.assertAlmostEqual(bread["RRP_D_recommended"], 3.03, delta=0.02)
        self.assertAlmostEqual(bread["Implied_Extractive_Drag_Ra"], 0.342, delta=0.01)
        self.assertAlmostEqual(bread["Fairness_Index_Percent"], 73.8, delta=0.5)

        # 2. Wheat
        wheat = audit_by_name["Milling Wheat (APW1 / ASW1)"]
        self.assertAlmostEqual(wheat["RRP_D_recommended"], 290.28, delta=0.1)
        self.assertAlmostEqual(wheat["Implied_Extractive_Drag_Ra"], 0.430, delta=0.01)
        self.assertAlmostEqual(wheat["Fairness_Index_Percent"], 79.5, delta=0.5)

        # 3. Milk
        milk = audit_by_name["Fresh Full Cream Milk (Full Fat)"]
        self.assertAlmostEqual(milk["RRP_D_recommended"], 1.64, delta=0.02)
        self.assertAlmostEqual(milk["Implied_Extractive_Drag_Ra"], 0.364, delta=0.01)
        self.assertAlmostEqual(milk["Fairness_Index_Percent"], 78.1, delta=0.5)

        # 4. Beef Cattle Weaners (Pastoral Livestock)
        beef = audit_by_name["Farmgate Beef Cattle Weaners (British Breed)"]
        self.assertAlmostEqual(beef["RRP_D_recommended"], 3.32, delta=0.02)
        self.assertAlmostEqual(beef["Implied_Extractive_Drag_Ra"], 0.250, delta=0.01)
        self.assertAlmostEqual(beef["Fairness_Index_Percent"], 86.1, delta=0.5)

        # 5. Diesel
        diesel = audit_by_name["Automotive Diesel Fuel (Ultra-Low Sulphur)"]
        self.assertAlmostEqual(diesel["RRP_D_recommended"], 1.67, delta=0.02)
        self.assertAlmostEqual(diesel["Implied_Extractive_Drag_Ra"], 0.535, delta=0.01)
        self.assertAlmostEqual(diesel["Fairness_Index_Percent"], 77.8, delta=0.5)

        # 6. Electricity
        power = audit_by_name["Residential Grid Electricity (Single-Rate Flat)"]
        self.assertAlmostEqual(power["RRP_D_recommended"], 0.27, delta=0.01)
        self.assertAlmostEqual(power["Implied_Extractive_Drag_Ra"], 0.463, delta=0.01)
        self.assertAlmostEqual(power["Fairness_Index_Percent"], 73.7, delta=0.5)

        # 7. LPG Bottled Gas
        lpg = audit_by_name["LPG Bottled Gas (45kg Domestic Cylinder)"]
        self.assertAlmostEqual(lpg["RRP_D_recommended"], 126.26, delta=0.1)
        self.assertAlmostEqual(lpg["Implied_Extractive_Drag_Ra"], 0.511, delta=0.01)
        self.assertAlmostEqual(lpg["Fairness_Index_Percent"], 76.5, delta=0.5)

        # 8. Water Cartage
        water = audit_by_name["Bulk Potable Water Cartage (Regional NSW / Coonabarabran)"]
        self.assertAlmostEqual(water["RRP_D_recommended"], 14.12, delta=0.02)
        self.assertAlmostEqual(water["Implied_Extractive_Drag_Ra"], 0.208, delta=0.01)
        self.assertAlmostEqual(water["Fairness_Index_Percent"], 91.1, delta=0.5)

        # 9. Domestic Waste Collection
        waste = audit_by_name["Domestic Waste Collection (Regional NSW / Coonabarabran)"]
        self.assertAlmostEqual(waste["RRP_D_recommended"], 8.05, delta=0.02)
        self.assertAlmostEqual(waste["Implied_Extractive_Drag_Ra"], 0.270, delta=0.01)
        self.assertAlmostEqual(waste["Fairness_Index_Percent"], 86.3, delta=0.5)

        # 10. Prescription Antibiotic
        med = audit_by_name["Prescription Antibiotic (Amoxicillin 500mg, 20 Caps)"]
        self.assertAlmostEqual(med["RRP_D_recommended"], 13.37, delta=0.02)
        self.assertAlmostEqual(med["Implied_Extractive_Drag_Ra"], 0.294, delta=0.01)
        self.assertAlmostEqual(med["Fairness_Index_Percent"], 81.0, delta=0.5)

        # 11. Timber
        timber = audit_by_name["Residential Structural Softwood Timber (MGP10 90x45mm Pine)"]
        self.assertAlmostEqual(timber["RRP_D_recommended"], 5.13, delta=0.02)
        self.assertAlmostEqual(timber["Implied_Extractive_Drag_Ra"], 0.414, delta=0.01)
        self.assertAlmostEqual(timber["Fairness_Index_Percent"], 71.2, delta=0.5)

        # 12. Concrete
        concrete = audit_by_name["Pre-Mixed Ready-Mix Concrete (N20 20 MPa Structural)"]
        self.assertAlmostEqual(concrete["RRP_D_recommended"], 221.72, delta=0.1)
        self.assertAlmostEqual(concrete["Implied_Extractive_Drag_Ra"], 0.483, delta=0.01)
        self.assertAlmostEqual(concrete["Fairness_Index_Percent"], 75.2, delta=0.5)

        # 13. Steel Reinforcing Mesh
        steel = audit_by_name["Structural Steel Reinforcing Mesh (SL82, 6.0m x 2.4m Sheet)"]
        self.assertAlmostEqual(steel["RRP_D_recommended"], 97.18, delta=0.1)
        self.assertAlmostEqual(steel["Implied_Extractive_Drag_Ra"], 0.502, delta=0.01)
        self.assertAlmostEqual(steel["Fairness_Index_Percent"], 75.9, delta=0.5)

        # 14. Road Freight Logistics
        freight = audit_by_name["Bulk Road Freight Transport (Newell Highway B-Double Corridor)"]
        self.assertAlmostEqual(freight["RRP_D_recommended"], 0.09, delta=0.01)
        self.assertAlmostEqual(freight["Implied_Extractive_Drag_Ra"], 0.591, delta=0.01)
        self.assertAlmostEqual(freight["Fairness_Index_Percent"], 71.1, delta=0.5)

    def test_fairness_metrics_bounds(self):
        results = run_full_fairness_audit()
        for r in results:
            self.assertTrue(0.0 < r["Fairness_Index_Percent"] <= 100.0)
            self.assertTrue(0.0 <= r["Implied_Extractive_Drag_Ra"] < 1.0)
            self.assertTrue(r["Extractive_Premium_AUD"] >= 0.0)

    def test_zero_drag_identity(self):
        item = get_australian_benchmark_dataset()[0]
        fair_price = calculate_forward_upe(
            P_e=item["P_e"], P_b=item["P_b"], U=item["U"],
            S=item["S"], R_n=item["R_n"], R_a=0.02, v_rel=item["v_rel"]
        )
        res = audit_commercial_rrp(
            commodity=item["commodity"], unit=item["unit"], sector=item["sector"],
            P_retail=fair_price, P_e=item["P_e"], P_b=item["P_b"], U=item["U"],
            S=item["S"], R_n=item["R_n"], v_rel=item["v_rel"], fair_reserve_Ra=0.02
        )
        self.assertAlmostEqual(res["Implied_Extractive_Drag_Ra"], 0.02, delta=0.001)
        self.assertAlmostEqual(res["Extractive_Premium_AUD"], 0.0, places=2)
        self.assertAlmostEqual(res["Fairness_Index_Percent"], 100.0, delta=0.1)

    def test_sensitivity_extractive_drag_vs_energy_shock(self):
        # Stress-test: Ra increase vs Pe increase
        base = calculate_forward_upe(P_e=0.38, P_b=0.45, U=2.15, S=1.0, R_n=1.0, R_a=0.02, v_rel=0.05)
        pe_up = calculate_forward_upe(P_e=0.38*1.5, P_b=0.45, U=2.15, S=1.0, R_n=1.0, R_a=0.02, v_rel=0.05)
        ra_up = calculate_forward_upe(P_e=0.38, P_b=0.45, U=2.15, S=1.0, R_n=1.0, R_a=0.342, v_rel=0.05)
        # Ra increase of 34.2% must create more price inflation than a 50% energy price shock
        self.assertGreater(ra_up - base, pe_up - base)

if __name__ == '__main__':
    unittest.main()
