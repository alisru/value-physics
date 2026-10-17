import unittest
import sys
sys.path.append('/tmp')
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
        # v = 0.25 (Water cartage urgency) -> gamma = 1 / sqrt(1 - 0.0625) = 1 / sqrt(0.9375) ~ 1.0328
        self.assertAlmostEqual(calculate_gamma(0.25), 1.0328, places=3)
        # v = 0.18 (Copper wire / Roofing urgency) -> gamma = 1 / sqrt(1 - 0.0324) ~ 1.0166
        self.assertAlmostEqual(calculate_gamma(0.18), 1.0166, places=3)

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

        # Test Copper wire forward baseline
        p_copper = calculate_forward_upe(
            P_e=24.50, P_b=118.50, U=22.00, S=1.15, R_n=0.82, R_a=0.02, v_rel=0.18
        )
        self.assertAlmostEqual(p_copper, 175.01, delta=0.05)

        # Test Canola meal forward baseline
        p_meal = calculate_forward_upe(
            P_e=84.50, P_b=212.00, U=82.00, S=1.10, R_n=0.94, R_a=0.02, v_rel=0.10
        )
        self.assertAlmostEqual(p_meal, 394.91, delta=0.1)

    def test_thirty_four_benchmark_commodities_audit(self):
        results = run_full_fairness_audit()
        self.assertEqual(len(results), 34, "Must audit all 34 official benchmark commodities")
        
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

        # 4. Beef Cattle Weaners
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
        self.assertAlmostEqual(lpg["RRP_D_recommended"], 126.26, delta=0.05)
        self.assertAlmostEqual(lpg["Implied_Extractive_Drag_Ra"], 0.511, delta=0.01)
        self.assertAlmostEqual(lpg["Fairness_Index_Percent"], 76.5, delta=0.5)

        # 8. Water Cartage
        water = audit_by_name["Bulk Potable Water Cartage (Regional NSW)"]
        self.assertAlmostEqual(water["RRP_D_recommended"], 14.12, delta=0.02)
        self.assertAlmostEqual(water["Implied_Extractive_Drag_Ra"], 0.208, delta=0.01)
        self.assertAlmostEqual(water["Fairness_Index_Percent"], 91.1, delta=0.5)

        # 9. Domestic Waste Collection
        waste = audit_by_name["Domestic Waste Collection (Regional NSW)"]
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

        # 14. Bulk Road Freight Logistics
        freight = audit_by_name["Bulk Road Freight Transport (Newell Highway B-Double Corridor)"]
        self.assertAlmostEqual(freight["RRP_D_recommended"], 0.0889, delta=0.005)
        self.assertAlmostEqual(freight["Implied_Extractive_Drag_Ra"], 0.591, delta=0.01)
        self.assertAlmostEqual(freight["Fairness_Index_Percent"], 71.1, delta=0.5)

        # 15. Merino Greasy Wool
        wool = audit_by_name["Australian Merino Greasy Wool (19-Micron Fleece)"]
        self.assertAlmostEqual(wool["RRP_D_recommended"], 10.82, delta=0.05)
        self.assertAlmostEqual(wool["Implied_Extractive_Drag_Ra"], 0.407, delta=0.01)
        self.assertAlmostEqual(wool["Fairness_Index_Percent"], 69.8, delta=0.5)

        # 16. Domestic Broadband Data Transit
        nbn = audit_by_name["Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)"]
        self.assertAlmostEqual(nbn["RRP_D_recommended"], 33.22, delta=0.05)
        self.assertAlmostEqual(nbn["Implied_Extractive_Drag_Ra"], 0.792, delta=0.01)
        self.assertAlmostEqual(nbn["Fairness_Index_Percent"], 39.1, delta=0.5)

        # 17. Salbutamol Inhaler
        inhaler = audit_by_name["Prescription Salbutamol Inhaler (100mcg CFC-Free MDI, 200 Doses)"]
        self.assertAlmostEqual(inhaler["RRP_D_recommended"], 6.53, delta=0.05)
        self.assertAlmostEqual(inhaler["Implied_Extractive_Drag_Ra"], 0.578, delta=0.01)
        self.assertAlmostEqual(inhaler["Fairness_Index_Percent"], 52.2, delta=0.5)

        # 18. Reticulated Water
        retic = audit_by_name["Urban Reticulated Potable Water (Municipal Pipeline Tariff)"]
        self.assertAlmostEqual(retic["RRP_D_recommended"], 2.82, delta=0.05)
        self.assertAlmostEqual(retic["Implied_Extractive_Drag_Ra"], 0.325, delta=0.01)
        self.assertAlmostEqual(retic["Fairness_Index_Percent"], 78.4, delta=0.5)

        # 19. Broiler Chicken
        chicken = audit_by_name["Commercial Broiler Chicken (Whole Fresh Dressed Bird)"]
        self.assertAlmostEqual(chicken["RRP_D_recommended"], 3.45, delta=0.05)
        self.assertAlmostEqual(chicken["Implied_Extractive_Drag_Ra"], 0.458, delta=0.01)
        self.assertAlmostEqual(chicken["Fairness_Index_Percent"], 76.6, delta=0.5)

        # 20. Clay Facing Bricks
        bricks = audit_by_name["Standard Extruded Clay Facing Bricks (Common Structural Masonry)"]
        self.assertAlmostEqual(bricks["RRP_D_recommended"], 722.12, delta=0.1)
        self.assertAlmostEqual(bricks["Implied_Extractive_Drag_Ra"], 0.628, delta=0.01)
        self.assertAlmostEqual(bricks["Fairness_Index_Percent"], 62.8, delta=0.5)

        # 21. Solar Sea Salt
        salt = audit_by_name["Coarse Solar Sea Salt (Unrefined Food & Livestock Grade)"]
        self.assertAlmostEqual(salt["RRP_D_recommended"], 8.45, delta=0.05)
        self.assertAlmostEqual(salt["Implied_Extractive_Drag_Ra"], 0.572, delta=0.01)
        self.assertAlmostEqual(salt["Fairness_Index_Percent"], 58.2, delta=0.5)

        # 22. Raw Cane Sugar
        sugar = audit_by_name["Raw Centrifugal Cane Sugar (Bulk Crystal Milling Feedstock)"]
        self.assertAlmostEqual(sugar["RRP_D_recommended"], 487.77, delta=0.1)
        self.assertAlmostEqual(sugar["Implied_Extractive_Drag_Ra"], 0.438, delta=0.01)
        self.assertAlmostEqual(sugar["Fairness_Index_Percent"], 78.7, delta=0.5)

        # 23. HDPE Rural Water Pipe
        hdpe = audit_by_name["HDPE Rural Water Reticulation Pipe (32mm PN12.5, 100m Coil)"]
        self.assertAlmostEqual(hdpe["RRP_D_recommended"], 165.60, delta=0.05)
        self.assertAlmostEqual(hdpe["Implied_Extractive_Drag_Ra"], 0.6255, delta=0.01)
        self.assertAlmostEqual(hdpe["Fairness_Index_Percent"], 67.6, delta=0.5)

        # 24. Canola Grain
        canola = audit_by_name["Farmgate Canola Grain (Bulk Non-GM Oilseed)"]
        self.assertAlmostEqual(canola["RRP_D_recommended"], 467.77, delta=0.1)
        self.assertAlmostEqual(canola["Implied_Extractive_Drag_Ra"], 0.6257, delta=0.01)
        self.assertAlmostEqual(canola["Fairness_Index_Percent"], 68.3, delta=0.5)

        # 25. FIBC Bulk Bags
        fibc = audit_by_name["Commercial FIBC Polypropylene Bulk Bags (1-Tonne Woven Container)"]
        self.assertAlmostEqual(fibc["RRP_D_recommended"], 16.02, delta=0.05)
        self.assertAlmostEqual(fibc["Implied_Extractive_Drag_Ra"], 0.5971, delta=0.01)
        self.assertAlmostEqual(fibc["Fairness_Index_Percent"], 65.4, delta=0.5)

        # 26. Bulk Portland Cement
        cement = audit_by_name["Bulk Portland Cement (General Purpose GP Clinker)"]
        self.assertAlmostEqual(cement["RRP_D_recommended"], 278.99, delta=0.1)
        self.assertAlmostEqual(cement["Implied_Extractive_Drag_Ra"], 0.4542, delta=0.01)
        self.assertAlmostEqual(cement["Fairness_Index_Percent"], 80.9, delta=0.5)

        # 27. Corrugated Steel Roofing Sheets
        roof = audit_by_name["Corrugated Galvanized Steel Roofing Sheets (Custom Orb 0.42mm BMT)"]
        self.assertAlmostEqual(roof["RRP_D_recommended"], 16.34, delta=0.05)
        self.assertAlmostEqual(roof["Implied_Extractive_Drag_Ra"], 0.5041, delta=0.01)
        self.assertAlmostEqual(roof["Fairness_Index_Percent"], 76.0, delta=0.5)

        # 28. Bulk Urea Fertilizer
        urea = audit_by_name["Bulk Granular Agricultural Urea Fertilizer (46% Nitrogen)"]
        self.assertAlmostEqual(urea["RRP_D_recommended"], 589.25, delta=0.1)
        self.assertAlmostEqual(urea["Implied_Extractive_Drag_Ra"], 0.5882, delta=0.01)
        self.assertAlmostEqual(urea["Fairness_Index_Percent"], 79.6, delta=0.5)

        # 29. Agricultural Glyphosate Herbicide
        gly = audit_by_name["Agricultural Glyphosate Herbicide (450g/L SL Systemic Formulation)"]
        self.assertAlmostEqual(gly["RRP_D_recommended"], 105.55, delta=0.05)
        self.assertAlmostEqual(gly["Implied_Extractive_Drag_Ra"], 0.5134, delta=0.01)
        self.assertAlmostEqual(gly["Fairness_Index_Percent"], 78.2, delta=0.5)

        # 30. Gypsum Plasterboard Wall Lining
        plaster = audit_by_name["Standard Gypsum Plasterboard Wall Lining (10mm Recessed Edge)"]
        self.assertAlmostEqual(plaster["RRP_D_recommended"], 16.77, delta=0.05)
        self.assertAlmostEqual(plaster["Implied_Extractive_Drag_Ra"], 0.6031, delta=0.01)
        self.assertAlmostEqual(plaster["Fairness_Index_Percent"], 67.6, delta=0.5)

        # 31. Structural Hardwood Timber
        hardwood = audit_by_name["Commercial Structural Hardwood Timber (F17 Kiln-Dried Hardwood, 90x45mm)"]
        self.assertAlmostEqual(hardwood["RRP_D_recommended"], 10.73, delta=0.05)
        self.assertAlmostEqual(hardwood["Implied_Extractive_Drag_Ra"], 0.4275, delta=0.01)
        self.assertAlmostEqual(hardwood["Fairness_Index_Percent"], 72.5, delta=0.5)

        # 32. Agricultural Feed Barley
        barley = audit_by_name["Agricultural Feed Barley (F1 Broadacre Feed Grain)"]
        self.assertAlmostEqual(barley["RRP_D_recommended"], 259.29, delta=0.1)
        self.assertAlmostEqual(barley["Implied_Extractive_Drag_Ra"], 0.4263, delta=0.01)
        self.assertAlmostEqual(barley["Fairness_Index_Percent"], 79.8, delta=0.5)

        # 33. Copper Electrical Building Wire (Sprint 19.1)
        copper = audit_by_name["Commercial Copper Electrical Building Wire (2.5mm2 Twin & Earth Flat TPS Cable)"]
        self.assertAlmostEqual(copper["RRP_D_recommended"], 175.01, delta=0.05)
        self.assertAlmostEqual(copper["Implied_Extractive_Drag_Ra"], 0.6175, delta=0.01)
        self.assertAlmostEqual(copper["Fairness_Index_Percent"], 77.8, delta=0.5)

        # 34. Solvent-Extracted Canola Protein Meal (Sprint 19.1)
        meal = audit_by_name["Solvent-Extracted Canola Meal / Protein Cake (Bulk Pelletized, 36%-38% Crude Protein)"]
        self.assertAlmostEqual(meal["RRP_D_recommended"], 394.91, delta=0.1)
        self.assertAlmostEqual(meal["Implied_Extractive_Drag_Ra"], 0.6598, delta=0.01)
        self.assertAlmostEqual(meal["Fairness_Index_Percent"], 68.1, delta=0.5)

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
