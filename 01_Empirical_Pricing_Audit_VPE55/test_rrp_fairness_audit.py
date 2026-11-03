import unittest
import math
import sys
import os
import importlib.util

module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rrp_fairness_audit.py")
spec = importlib.util.spec_from_file_location("rrp_fairness_audit", module_path)
rrp_mod = importlib.util.module_from_spec(spec)
sys.modules["rrp_fairness_audit"] = rrp_mod
spec.loader.exec_module(rrp_mod)

from rrp_fairness_audit import (
    calculate_gamma,
    calculate_forward_upe,
    calculate_index_metrics,
    audit_commercial_rrp,
    audit_weekly_household_basket_index,
    get_australian_benchmark_dataset,
    run_full_fairness_audit,
    get_big4_bank_loan_benchmark_dataset,
    audit_big4_loan_spreads
)

class TestRRPFairnessAudit(unittest.TestCase):
    def test_gamma_calculation(self):
        self.assertAlmostEqual(calculate_gamma(0.0), 1.0)
        self.assertGreater(calculate_gamma(0.5), 1.0)
        self.assertAlmostEqual(calculate_gamma(0.6), 1.25)
        self.assertTrue(math.isfinite(calculate_gamma(1.0)))

    def test_forward_upe_positivity_and_linearity(self):
        p = calculate_forward_upe(P_e=10.0, P_b=20.0, U=30.0, S=1.0, R_n=1.0, R_a=0.0)
        self.assertAlmostEqual(p, 60.0)

    def test_audit_commercial_rrp_bounds(self):
        audit = audit_commercial_rrp(
            commodity="Test Loaf",
            unit="loaf",
            sector="Food",
            P_retail=4.00,
            P_e=0.40,
            P_b=0.50,
            U=2.00,
            S=1.0,
            R_n=1.0,
            v_rel=0.0
        )
        self.assertGreater(audit["Implied_Extractive_Drag_Ra"], 0.0)
        self.assertLess(audit["Implied_Extractive_Drag_Ra"], 1.0)
        self.assertLessEqual(audit["RRP_D_recommended"], 4.00)
        self.assertGreaterEqual(audit["Fairness_Index_Percent"], 0.0)
        self.assertLessEqual(audit["Fairness_Index_Percent"], 100.0)

    def test_benchmark_dataset_completeness_66_goods(self):
        dataset = get_australian_benchmark_dataset()
        self.assertEqual(len(dataset), 66)
        commodities = [d["commodity"] for d in dataset]
        self.assertIn("Commercial Sliced White Bread (680g)", commodities)
        self.assertIn("Milling Wheat (APW1 / ASW1)", commodities)
        self.assertIn("Fresh Full Cream Milk (Full Fat)", commodities)
        self.assertIn("Farmgate Beef Cattle Weaners (British Breed)", commodities)
        self.assertIn("Automotive Diesel Fuel (Ultra-Low Sulphur)", commodities)
        self.assertIn("Residential Grid Electricity (Single-Rate Flat)", commodities)
        self.assertIn("LPG Bottled Gas (45kg Domestic Cylinder)", commodities)
        self.assertIn("Bulk Potable Water Cartage (Regional NSW)", commodities)
        self.assertIn("Domestic Waste Collection (Regional NSW)", commodities)
        self.assertIn("Prescription Antibiotic (Amoxicillin 500mg, 20 Caps)", commodities)
        self.assertIn("Residential Structural Softwood Timber (MGP10 90x45mm Pine)", commodities)
        self.assertIn("Pre-Mixed Ready-Mix Concrete (N20 20 MPa Structural)", commodities)
        self.assertIn("Structural Steel Reinforcing Mesh (SL82, 6.0m x 2.4m Sheet)", commodities)
        self.assertIn("Bulk Road Freight Transport (Newell Highway B-Double Corridor)", commodities)
        self.assertIn("Australian Merino Greasy Wool (19-Micron Fleece)", commodities)
        self.assertIn("Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)", commodities)
        self.assertIn("Prescription Salbutamol Inhaler (100mcg CFC-Free MDI, 200 Doses)", commodities)
        self.assertIn("Urban Reticulated Potable Water (Municipal Pipeline Tariff)", commodities)
        self.assertIn("Commercial Broiler Chicken (Whole Fresh Dressed Bird)", commodities)
        self.assertIn("Standard Extruded Clay Facing Bricks (Common Structural Masonry)", commodities)
        self.assertIn("Coarse Solar Sea Salt (Unrefined Food & Livestock Grade)", commodities)
        self.assertIn("Raw Centrifugal Cane Sugar (Bulk Crystal Milling Feedstock)", commodities)
        self.assertIn("HDPE Rural Water Reticulation Pipe (32mm PN12.5, 100m Coil)", commodities)
        self.assertIn("Farmgate Canola Grain (Bulk Non-GM Oilseed)", commodities)
        self.assertIn("Commercial FIBC Polypropylene Bulk Bags (1-Tonne Woven Container)", commodities)
        self.assertIn("Bulk Portland Cement (General Purpose GP Clinker)", commodities)
        self.assertIn("Corrugated Galvanized Steel Roofing Sheets (Custom Orb 0.42mm BMT)", commodities)
        self.assertIn("Bulk Granular Agricultural Urea Fertilizer (46% Nitrogen)", commodities)
        self.assertIn("Agricultural Glyphosate Herbicide (450g/L SL Systemic Formulation)", commodities)
        self.assertIn("Standard Gypsum Plasterboard Wall Lining (10mm Recessed Edge)", commodities)
        self.assertIn("Commercial Aluminum Window Glazing Frames (Double-Glazed Residential Sliding Window, 1200mm x 1800mm Standard Unit)", commodities)
        self.assertIn("Commercial Feed Sorghum (SGM1 Summer Grain Sorghum, min 9% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Hollow Sections (100x100x4.0mm RHS/SHS, Grade C350LO)", commodities)
        self.assertIn("Australian Desi Chickpeas (CHKP1 Premium Bulk Pulse Grain)", commodities)
        self.assertIn("Commercial Heavy Structural Steel Plate (Grade 250, 12mm Medium Plate, AS/NZS 3678)", commodities)
        self.assertIn("Commercial Faba Beans (F1 Broadacre Pulse Grain, min 24% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Equal Angle (100x100x8.0mm EA, Grade 300PLUS / AS/NZS 3679.1)", commodities)
        self.assertIn("Australian Field Peas (Kaspa Type Bulk Grain / Livestock Protein Feed, min 22% Protein)", commodities)
        self.assertIn("Commercial Galvanized Steel Built-In Lintel / T-Bar (200x10mm Lintel, AS/NZS 2699.3 / AS 4100)", commodities)
        self.assertIn("Australian Mungbeans (Berken / Crystal Type Pulse Grain, min 24% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Parallel Flange Channel (200x75mm PFC, Grade 300PLUS / AS/NZS 3679.1)", commodities)
        self.assertIn("Commercial De-Hulled Split Faba Beans (Machine Dressed Export & Food Grade, min 28% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Parallel Flange Channel (250x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)", commodities)
        self.assertIn("Commercial De-Hulled Split Yellow Field Peas (Machine Dressed Food Grade, min 25% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Parallel Flange Channel (300x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)", commodities)
        self.assertIn("Commercial De-Hulled Split Red Lentils (Machine Dressed Export Grade, min 26% Protein)", commodities)
        self.assertIn("Commercial Structural Steel Universal Column (200UC46.2, AS/NZS 3679.1 Grade 300PLUS)", commodities)
        self.assertIn("Commercial Australian Faba Bean Protein Concentrate / Flour (min 55% Protein, per Tonne)", commodities)
        self.assertIn("Commercial Structural Steel Universal Column (250UC72.9, AS/NZS 3679.1 Grade 300PLUS)", commodities)
        self.assertIn("Commercial Australian Field Pea Protein Isolate (min 80% Protein, Spray-Dried, per Tonne)", commodities)
        self.assertIn("Commercial Structural Steel Universal Column (310UC96.8, AS/NZS 3679.1 Grade 300PLUS)", commodities)
        self.assertIn("Commercial Australian Chickpea Protein Isolate / Functional Flour (min 75% Protein, Alkaline-Extracted, per Tonne)", commodities)
        self.assertIn("Commercial Structural Steel Universal Column (310UC118, AS/NZS 3679.1 Grade 300PLUS)", commodities)
        self.assertIn("Commercial Australian Faba Bean Protein Isolate (min 85% Protein, Wet-Extracted & Spray-Dried, per Tonne)", commodities)

    def test_full_fairness_audit_execution(self):
        audits = run_full_fairness_audit()
        self.assertEqual(len(audits), 66)
        for a in audits:
            self.assertGreater(a["P_retail_observed"], 0.0)
            self.assertGreater(a["RRP_D_recommended"], 0.0)
            self.assertGreaterEqual(a["Implied_Extractive_Drag_Ra"], 0.0)
            self.assertGreaterEqual(a["Fairness_Index_Percent"], 35.0)

    def test_wool_and_telecom_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        wool = audits["Australian Merino Greasy Wool (19-Micron Fleece)"]
        self.assertAlmostEqual(wool["P_retail_observed"], 15.50)
        self.assertAlmostEqual(wool["RRP_D_recommended"], 10.82)
        self.assertAlmostEqual(wool["Implied_Extractive_Drag_Ra"], 0.4074, places=3)
        self.assertAlmostEqual(wool["Fairness_Index_Percent"], 69.8, places=1)

        nbn = audits["Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)"]
        self.assertAlmostEqual(nbn["P_retail_observed"], 85.00)
        self.assertAlmostEqual(nbn["RRP_D_recommended"], 33.22)
        self.assertAlmostEqual(nbn["Implied_Extractive_Drag_Ra"], 0.7924, places=3)
        self.assertAlmostEqual(nbn["Fairness_Index_Percent"], 39.1, places=1)

    def test_inhaler_and_reticulated_water_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        inhaler = audits["Prescription Salbutamol Inhaler (100mcg CFC-Free MDI, 200 Doses)"]
        self.assertAlmostEqual(inhaler["P_retail_observed"], 12.50)
        self.assertAlmostEqual(inhaler["RRP_D_recommended"], 6.53)
        self.assertAlmostEqual(inhaler["Implied_Extractive_Drag_Ra"], 0.5776, places=3)
        self.assertAlmostEqual(inhaler["Fairness_Index_Percent"], 52.2, places=1)

        water = audits["Urban Reticulated Potable Water (Municipal Pipeline Tariff)"]
        self.assertAlmostEqual(water["P_retail_observed"], 3.60)
        self.assertAlmostEqual(water["RRP_D_recommended"], 2.82)
        self.assertAlmostEqual(water["Implied_Extractive_Drag_Ra"], 0.3251, places=3)
        self.assertAlmostEqual(water["Fairness_Index_Percent"], 78.4, places=1)

    def test_chicken_and_bricks_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        chicken = audits["Commercial Broiler Chicken (Whole Fresh Dressed Bird)"]
        self.assertAlmostEqual(chicken["P_retail_observed"], 4.50)
        self.assertAlmostEqual(chicken["RRP_D_recommended"], 3.45)
        self.assertAlmostEqual(chicken["Implied_Extractive_Drag_Ra"], 0.4575, places=3)
        self.assertAlmostEqual(chicken["Fairness_Index_Percent"], 76.6, places=1)

        bricks = audits["Standard Extruded Clay Facing Bricks (Common Structural Masonry)"]
        self.assertAlmostEqual(bricks["P_retail_observed"], 1150.00)
        self.assertAlmostEqual(bricks["RRP_D_recommended"], 722.12)
        self.assertAlmostEqual(bricks["Implied_Extractive_Drag_Ra"], 0.6277, places=3)
        self.assertAlmostEqual(bricks["Fairness_Index_Percent"], 62.8, places=1)

    def test_salt_and_sugar_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        salt = audits["Coarse Solar Sea Salt (Unrefined Food & Livestock Grade)"]
        self.assertAlmostEqual(salt["P_retail_observed"], 14.50)
        self.assertAlmostEqual(salt["RRP_D_recommended"], 8.45)
        self.assertAlmostEqual(salt["Implied_Extractive_Drag_Ra"], 0.5719, places=3)
        self.assertAlmostEqual(salt["Fairness_Index_Percent"], 58.2, places=1)

        sugar = audits["Raw Centrifugal Cane Sugar (Bulk Crystal Milling Feedstock)"]
        self.assertAlmostEqual(sugar["P_retail_observed"], 620.00)
        self.assertAlmostEqual(sugar["RRP_D_recommended"], 487.77)
        self.assertAlmostEqual(sugar["Implied_Extractive_Drag_Ra"], 0.4380, places=3)
        self.assertAlmostEqual(sugar["Fairness_Index_Percent"], 78.7, places=1)

    def test_pipe_and_canola_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        pipe = audits["HDPE Rural Water Reticulation Pipe (32mm PN12.5, 100m Coil)"]
        self.assertAlmostEqual(pipe["P_retail_observed"], 245.00)
        self.assertAlmostEqual(pipe["RRP_D_recommended"], 165.60)
        self.assertAlmostEqual(pipe["Implied_Extractive_Drag_Ra"], 0.6255, places=3)
        self.assertAlmostEqual(pipe["Fairness_Index_Percent"], 67.6, places=1)

        canola = audits["Farmgate Canola Grain (Bulk Non-GM Oilseed)"]
        self.assertAlmostEqual(canola["P_retail_observed"], 685.00)
        self.assertAlmostEqual(canola["RRP_D_recommended"], 467.77, places=2)
        self.assertAlmostEqual(canola["Implied_Extractive_Drag_Ra"], 0.6257, places=3)
        self.assertAlmostEqual(canola["Fairness_Index_Percent"], 68.3, places=1)

    def test_bulk_bags_and_cement_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        bag = audits["Commercial FIBC Polypropylene Bulk Bags (1-Tonne Woven Container)"]
        self.assertAlmostEqual(bag["P_retail_observed"], 24.50)
        self.assertAlmostEqual(bag["RRP_D_recommended"], 16.02)
        self.assertAlmostEqual(bag["Implied_Extractive_Drag_Ra"], 0.5971, places=3)
        self.assertAlmostEqual(bag["Fairness_Index_Percent"], 65.4, places=1)

        cement = audits["Bulk Portland Cement (General Purpose GP Clinker)"]
        self.assertAlmostEqual(cement["P_retail_observed"], 345.00)
        self.assertAlmostEqual(cement["RRP_D_recommended"], 278.99, places=2)
        self.assertAlmostEqual(cement["Implied_Extractive_Drag_Ra"], 0.4542, places=3)
        self.assertAlmostEqual(cement["Fairness_Index_Percent"], 80.9, places=1)

    def test_roofing_and_fertilizer_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        roof = audits["Corrugated Galvanized Steel Roofing Sheets (Custom Orb 0.42mm BMT)"]
        self.assertAlmostEqual(roof["P_retail_observed"], 21.50)
        self.assertAlmostEqual(roof["RRP_D_recommended"], 16.34)
        self.assertAlmostEqual(roof["Implied_Extractive_Drag_Ra"], 0.5041, places=3)
        self.assertAlmostEqual(roof["Fairness_Index_Percent"], 76.0, places=1)

        urea = audits["Bulk Granular Agricultural Urea Fertilizer (46% Nitrogen)"]
        self.assertAlmostEqual(urea["P_retail_observed"], 740.00)
        self.assertAlmostEqual(urea["RRP_D_recommended"], 589.25, places=2)
        self.assertAlmostEqual(urea["Implied_Extractive_Drag_Ra"], 0.5882, places=3)
        self.assertAlmostEqual(urea["Fairness_Index_Percent"], 79.6, places=1)

    def test_herbicide_and_plasterboard_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        gly = audits["Agricultural Glyphosate Herbicide (450g/L SL Systemic Formulation)"]
        self.assertAlmostEqual(gly["P_retail_observed"], 135.00)
        self.assertAlmostEqual(gly["RRP_D_recommended"], 105.55, places=2)
        self.assertAlmostEqual(gly["Implied_Extractive_Drag_Ra"], 0.5134, places=3)
        self.assertAlmostEqual(gly["Fairness_Index_Percent"], 78.2, places=1)

        plaster = audits["Standard Gypsum Plasterboard Wall Lining (10mm Recessed Edge)"]
        self.assertAlmostEqual(plaster["P_retail_observed"], 24.80)
        self.assertAlmostEqual(plaster["RRP_D_recommended"], 16.77, places=2)
        self.assertAlmostEqual(plaster["Implied_Extractive_Drag_Ra"], 0.6031, places=3)
        self.assertAlmostEqual(plaster["Fairness_Index_Percent"], 67.6, places=1)

    def test_hardwood_and_barley_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        hw = audits["Commercial Structural Hardwood Timber (F17 Kiln-Dried Hardwood, 90x45mm)"]
        self.assertAlmostEqual(hw["P_retail_observed"], 14.80)
        self.assertAlmostEqual(hw["RRP_D_recommended"], 10.73, places=2)
        self.assertAlmostEqual(hw["Implied_Extractive_Drag_Ra"], 0.4275, places=3)
        self.assertAlmostEqual(hw["Fairness_Index_Percent"], 72.5, places=1)

        bar = audits["Agricultural Feed Barley (F1 Broadacre Feed Grain)"]
        self.assertAlmostEqual(bar["P_retail_observed"], 325.00)
        self.assertAlmostEqual(bar["RRP_D_recommended"], 259.29, places=2)
        self.assertAlmostEqual(bar["Implied_Extractive_Drag_Ra"], 0.4263, places=3)
        self.assertAlmostEqual(bar["Fairness_Index_Percent"], 79.8, places=1)

    def test_copper_wire_and_canola_meal_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        cw = audits["Commercial Copper Electrical Building Wire (2.5mm2 Twin & Earth Flat TPS Cable)"]
        self.assertAlmostEqual(cw["P_retail_observed"], 225.00)
        self.assertAlmostEqual(cw["RRP_D_recommended"], 175.01, places=2)
        self.assertAlmostEqual(cw["Implied_Extractive_Drag_Ra"], 0.6175, places=3)
        self.assertAlmostEqual(cw["Fairness_Index_Percent"], 77.8, places=1)

        cm = audits["Solvent-Extracted Canola Meal / Protein Cake (Bulk Pelletized, 36%-38% Crude Protein)"]
        self.assertAlmostEqual(cm["P_retail_observed"], 580.00)
        self.assertAlmostEqual(cm["RRP_D_recommended"], 394.91, places=2)
        self.assertAlmostEqual(cm["Implied_Extractive_Drag_Ra"], 0.6598, places=3)
        self.assertAlmostEqual(cm["Fairness_Index_Percent"], 68.1, places=1)

    def test_universal_beam_and_cottonseed_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        ub = audits["Commercial Hot-Rolled Structural Steel Universal Beams (150UB14.0)"]
        self.assertAlmostEqual(ub["P_retail_observed"], 52.00)
        self.assertAlmostEqual(ub["RRP_D_recommended"], 37.28, places=2)
        self.assertAlmostEqual(ub["Implied_Extractive_Drag_Ra"], 0.5686, places=3)
        self.assertAlmostEqual(ub["Fairness_Index_Percent"], 71.7, places=1)

        cs = audits["Whole Ginned Cottonseed (Fuzzy White Cattle Feedstock)"]
        self.assertAlmostEqual(cs["P_retail_observed"], 520.00)
        self.assertAlmostEqual(cs["RRP_D_recommended"], 353.33, places=2)
        self.assertAlmostEqual(cs["Implied_Extractive_Drag_Ra"], 0.6605, places=3)
        self.assertAlmostEqual(cs["Fairness_Index_Percent"], 67.9, places=1)

    def test_purlin_and_aph2_wheat_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        purlin = audits["Commercial Cold-Formed Steel Galvanized Framing / C-Purlin (C15015, 1.5mm BMT)"]
        self.assertAlmostEqual(purlin["P_retail_observed"], 16.50)
        self.assertAlmostEqual(purlin["RRP_D_recommended"], 12.11, places=2)
        self.assertAlmostEqual(purlin["Implied_Extractive_Drag_Ra"], 0.5583, places=3)
        self.assertAlmostEqual(purlin["Fairness_Index_Percent"], 73.4, places=1)
        self.assertAlmostEqual(purlin["INDEX_Observed_Pct_DSP_Baseline"], 2.6662, places=2)

        aph2 = audits["Australian Prime Hard Breadmaking Wheat (APH2 High-Protein Milling Grain, min 13% Protein)"]
        self.assertAlmostEqual(aph2["P_retail_observed"], 410.00)
        self.assertAlmostEqual(aph2["RRP_D_recommended"], 336.55, places=2)
        self.assertAlmostEqual(aph2["Implied_Extractive_Drag_Ra"], 0.3892, places=3)
        self.assertAlmostEqual(aph2["Fairness_Index_Percent"], 82.1, places=1)
        self.assertAlmostEqual(aph2["INDEX_Observed_Pct_DSP_Baseline"], 66.2519, places=2)

    def test_window_and_sorghum_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        window = audits["Commercial Aluminum Window Glazing Frames (Double-Glazed Residential Sliding Window, 1200mm x 1800mm Standard Unit)"]
        self.assertAlmostEqual(window["P_retail_observed"], 540.00)
        self.assertAlmostEqual(window["RRP_D_recommended"], 311.23, places=2)
        self.assertAlmostEqual(window["Implied_Extractive_Drag_Ra"], 0.7206, places=3)
        self.assertAlmostEqual(window["Fairness_Index_Percent"], 57.6, places=1)
        self.assertAlmostEqual(window["INDEX_Observed_Pct_DSP_Baseline"], 87.2586, places=2)
        self.assertAlmostEqual(window["INDEX_RRPD_Pct_DSP_Baseline"], 50.2913, places=2)
        self.assertAlmostEqual(window["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 36.9673, places=2)
        self.assertAlmostEqual(window["NMW_Labor_Minutes_Confiscated"], 519.15, places=1)

        sorghum = audits["Commercial Feed Sorghum (SGM1 Summer Grain Sorghum, min 9% Protein)"]
        self.assertAlmostEqual(sorghum["P_retail_observed"], 360.00)
        self.assertAlmostEqual(sorghum["RRP_D_recommended"], 290.09, places=2)
        self.assertAlmostEqual(sorghum["Implied_Extractive_Drag_Ra"], 0.4149, places=3)
        self.assertAlmostEqual(sorghum["Fairness_Index_Percent"], 80.6, places=1)
        self.assertAlmostEqual(sorghum["INDEX_Observed_Pct_DSP_Baseline"], 58.1724, places=2)
        self.assertAlmostEqual(sorghum["INDEX_RRPD_Pct_DSP_Baseline"], 46.8751, places=2)
        self.assertAlmostEqual(sorghum["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 11.2973, places=2)
        self.assertAlmostEqual(sorghum["NMW_Labor_Minutes_Confiscated"], 158.65, places=1)

    def test_rhs_and_chickpea_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        rhs = audits["Commercial Structural Steel Hollow Sections (100x100x4.0mm RHS/SHS, Grade C350LO)"]
        self.assertAlmostEqual(rhs["P_retail_observed"], 42.20)
        self.assertAlmostEqual(rhs["RRP_D_recommended"], 31.60, places=2)
        self.assertAlmostEqual(rhs["Implied_Extractive_Drag_Ra"], 0.5342, places=3)
        self.assertAlmostEqual(rhs["Fairness_Index_Percent"], 74.9, places=1)
        self.assertAlmostEqual(rhs["INDEX_Observed_Pct_DSP_Baseline"], 6.8191, places=2)
        self.assertAlmostEqual(rhs["INDEX_RRPD_Pct_DSP_Baseline"], 5.1064, places=2)
        self.assertAlmostEqual(rhs["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 1.7127, places=2)
        self.assertAlmostEqual(rhs["NMW_Labor_Minutes_Confiscated"], 24.05, places=1)

        chkp = audits["Australian Desi Chickpeas (CHKP1 Premium Bulk Pulse Grain)"]
        self.assertAlmostEqual(chkp["P_retail_observed"], 710.00)
        self.assertAlmostEqual(chkp["RRP_D_recommended"], 408.79, places=2)
        self.assertAlmostEqual(chkp["Implied_Extractive_Drag_Ra"], 0.7065, places=3)
        self.assertAlmostEqual(chkp["Fairness_Index_Percent"], 57.6, places=1)
        self.assertAlmostEqual(chkp["INDEX_Observed_Pct_DSP_Baseline"], 114.7289, places=2)
        self.assertAlmostEqual(chkp["INDEX_RRPD_Pct_DSP_Baseline"], 66.0566, places=2)
        self.assertAlmostEqual(chkp["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 48.6723, places=2)
        self.assertAlmostEqual(chkp["NMW_Labor_Minutes_Confiscated"], 683.53, places=1)

    def test_plate_and_faba_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        plate = audits["Commercial Heavy Structural Steel Plate (Grade 250, 12mm Medium Plate, AS/NZS 3678)"]
        self.assertAlmostEqual(plate["P_retail_observed"], 220.70)
        self.assertAlmostEqual(plate["RRP_D_recommended"], 164.00, places=2)
        self.assertAlmostEqual(plate["Implied_Extractive_Drag_Ra"], 0.5558, places=3)
        self.assertAlmostEqual(plate["Fairness_Index_Percent"], 74.3, places=1)
        self.assertAlmostEqual(plate["INDEX_Observed_Pct_DSP_Baseline"], 35.6629, places=2)
        self.assertAlmostEqual(plate["INDEX_RRPD_Pct_DSP_Baseline"], 26.5013, places=2)
        self.assertAlmostEqual(plate["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 9.1616, places=2)
        self.assertAlmostEqual(plate["NMW_Labor_Minutes_Confiscated"], 128.66, places=1)

        faba = audits["Commercial Faba Beans (F1 Broadacre Pulse Grain, min 24% Protein)"]
        self.assertAlmostEqual(faba["P_retail_observed"], 455.00)
        self.assertAlmostEqual(faba["RRP_D_recommended"], 318.99, places=2)
        self.assertAlmostEqual(faba["Implied_Extractive_Drag_Ra"], 0.5777, places=3)
        self.assertAlmostEqual(faba["Fairness_Index_Percent"], 70.1, places=1)
        self.assertAlmostEqual(faba["INDEX_Observed_Pct_DSP_Baseline"], 73.5235, places=2)
        self.assertAlmostEqual(faba["INDEX_RRPD_Pct_DSP_Baseline"], 51.5450, places=2)
        self.assertAlmostEqual(faba["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 21.9785, places=2)
        self.assertAlmostEqual(faba["NMW_Labor_Minutes_Confiscated"], 308.66, places=1)

    def test_angle_and_peas_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        angle = audits["Commercial Structural Steel Equal Angle (100x100x8.0mm EA, Grade 300PLUS / AS/NZS 3679.1)"]
        self.assertAlmostEqual(angle["P_retail_observed"], 43.50)
        self.assertAlmostEqual(angle["RRP_D_recommended"], 32.27, places=2)
        self.assertAlmostEqual(angle["Implied_Extractive_Drag_Ra"], 0.5492, places=3)
        self.assertAlmostEqual(angle["Fairness_Index_Percent"], 74.2, places=1)
        self.assertAlmostEqual(angle["INDEX_Observed_Pct_DSP_Baseline"], 7.0292, places=2)
        self.assertAlmostEqual(angle["INDEX_RRPD_Pct_DSP_Baseline"], 5.2142, places=2)
        self.assertAlmostEqual(angle["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 1.8149, places=2)
        self.assertAlmostEqual(angle["NMW_Labor_Minutes_Confiscated"], 25.49, places=1)

        peas = audits["Australian Field Peas (Kaspa Type Bulk Grain / Livestock Protein Feed, min 22% Protein)"]
        self.assertAlmostEqual(peas["P_retail_observed"], 440.00)
        self.assertAlmostEqual(peas["RRP_D_recommended"], 305.78, places=2)
        self.assertAlmostEqual(peas["Implied_Extractive_Drag_Ra"], 0.5845, places=3)
        self.assertAlmostEqual(peas["Fairness_Index_Percent"], 69.5, places=1)
        self.assertAlmostEqual(peas["INDEX_Observed_Pct_DSP_Baseline"], 71.0996, places=2)
        self.assertAlmostEqual(peas["INDEX_RRPD_Pct_DSP_Baseline"], 49.4114, places=2)
        self.assertAlmostEqual(peas["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 21.6882, places=2)
        self.assertAlmostEqual(peas["NMW_Labor_Minutes_Confiscated"], 304.58, places=1)

    def test_pfc_and_lupins_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        pfc = audits["Commercial Structural Steel Parallel Flange Channel (150x75mm PFC, Grade 300PLUS / AS/NZS 3679.1)"]
        self.assertAlmostEqual(pfc["P_retail_observed"], 65.50)
        self.assertAlmostEqual(pfc["RRP_D_recommended"], 48.44, places=2)
        self.assertAlmostEqual(pfc["Implied_Extractive_Drag_Ra"], 0.5557, places=3)
        self.assertAlmostEqual(pfc["Fairness_Index_Percent"], 74.0, places=1)
        self.assertAlmostEqual(pfc["INDEX_Observed_Pct_DSP_Baseline"], 10.5841, places=2)
        self.assertAlmostEqual(pfc["INDEX_RRPD_Pct_DSP_Baseline"], 7.8281, places=2)
        self.assertAlmostEqual(pfc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 2.7560, places=2)
        self.assertAlmostEqual(pfc["NMW_Labor_Minutes_Confiscated"], 38.70, places=1)

        lupins = audits["Australian Narrow-Leaf Lupins (Angustifolius Bulk Feed Lupins, min 32% Protein)"]
        self.assertAlmostEqual(lupins["P_retail_observed"], 520.00)
        self.assertAlmostEqual(lupins["RRP_D_recommended"], 368.55, places=2)
        self.assertAlmostEqual(lupins["Implied_Extractive_Drag_Ra"], 0.5738, places=3)
        self.assertAlmostEqual(lupins["Fairness_Index_Percent"], 70.9, places=1)
        self.assertAlmostEqual(lupins["INDEX_Observed_Pct_DSP_Baseline"], 84.0268, places=2)
        self.assertAlmostEqual(lupins["INDEX_RRPD_Pct_DSP_Baseline"], 59.5537, places=2)
        self.assertAlmostEqual(lupins["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 24.4732, places=2)
        self.assertAlmostEqual(lupins["NMW_Labor_Minutes_Confiscated"], 343.69, places=1)

    def test_lintel_and_mungbean_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        lintel = audits["Commercial Galvanized Steel Built-In Lintel / T-Bar (200x10mm Lintel, AS/NZS 2699.3 / AS 4100)"]
        self.assertAlmostEqual(lintel["P_retail_observed"], 105.00)
        self.assertAlmostEqual(lintel["RRP_D_recommended"], 79.36, places=2)
        self.assertAlmostEqual(lintel["Implied_Extractive_Drag_Ra"], 0.5370, places=3)
        self.assertAlmostEqual(lintel["Fairness_Index_Percent"], 75.6, places=1)
        self.assertAlmostEqual(lintel["INDEX_Observed_Pct_DSP_Baseline"], 16.9670, places=2)
        self.assertAlmostEqual(lintel["INDEX_RRPD_Pct_DSP_Baseline"], 12.8238, places=2)
        self.assertAlmostEqual(lintel["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 4.1432, places=2)
        self.assertAlmostEqual(lintel["NMW_Labor_Minutes_Confiscated"], 58.18, places=1)

        mung = audits["Australian Mungbeans (Berken / Crystal Type Pulse Grain, min 24% Protein)"]
        self.assertAlmostEqual(mung["P_retail_observed"], 1150.00)
        self.assertAlmostEqual(mung["RRP_D_recommended"], 546.77, places=2)
        self.assertAlmostEqual(mung["Implied_Extractive_Drag_Ra"], 0.7683, places=3)
        self.assertAlmostEqual(mung["Fairness_Index_Percent"], 47.5, places=1)
        self.assertAlmostEqual(mung["INDEX_Observed_Pct_DSP_Baseline"], 185.8286, places=2)
        self.assertAlmostEqual(mung["INDEX_RRPD_Pct_DSP_Baseline"], 88.3526, places=2)
        self.assertAlmostEqual(mung["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 97.4760, places=2)
        self.assertAlmostEqual(mung["NMW_Labor_Minutes_Confiscated"], 1368.89, places=1)

    def test_pfc200_and_split_beans_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        pfc = audits["Commercial Structural Steel Parallel Flange Channel (200x75mm PFC, Grade 300PLUS / AS/NZS 3679.1)"]
        self.assertAlmostEqual(pfc["P_retail_observed"], 85.00)
        self.assertAlmostEqual(pfc["RRP_D_recommended"], 62.70, places=2)
        self.assertAlmostEqual(pfc["Implied_Extractive_Drag_Ra"], 0.5582, places=3)
        self.assertAlmostEqual(pfc["Fairness_Index_Percent"], 73.8, places=1)
        self.assertAlmostEqual(pfc["INDEX_Observed_Pct_DSP_Baseline"], 13.7352, places=2)
        self.assertAlmostEqual(pfc["INDEX_RRPD_Pct_DSP_Baseline"], 10.1324, places=2)
        self.assertAlmostEqual(pfc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 3.6028, places=2)
        self.assertAlmostEqual(pfc["NMW_Labor_Minutes_Confiscated"], 50.59, places=1)

        split = audits["Commercial De-Hulled Split Faba Beans (Machine Dressed Export & Food Grade, min 28% Protein)"]
        self.assertAlmostEqual(split["P_retail_observed"], 750.00)
        self.assertAlmostEqual(split["RRP_D_recommended"], 532.48, places=2)
        self.assertAlmostEqual(split["Implied_Extractive_Drag_Ra"], 0.5993, places=3)
        self.assertAlmostEqual(split["Fairness_Index_Percent"], 71.0, places=1)
        self.assertAlmostEqual(split["INDEX_Observed_Pct_DSP_Baseline"], 121.1925, places=2)
        self.assertAlmostEqual(split["INDEX_RRPD_Pct_DSP_Baseline"], 86.0431, places=2)
        self.assertAlmostEqual(split["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 35.1494, places=2)
        self.assertAlmostEqual(split["NMW_Labor_Minutes_Confiscated"], 493.63, places=1)

    def test_pfc250_and_split_peas_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        pfc = audits["Commercial Structural Steel Parallel Flange Channel (250x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)"]
        self.assertAlmostEqual(pfc["P_retail_observed"], 132.00)
        self.assertAlmostEqual(pfc["RRP_D_recommended"], 97.19, places=2)
        self.assertAlmostEqual(pfc["Implied_Extractive_Drag_Ra"], 0.5606, places=3)
        self.assertAlmostEqual(pfc["Fairness_Index_Percent"], 73.6, places=1)
        self.assertAlmostEqual(pfc["INDEX_Observed_Pct_DSP_Baseline"], 21.3299, places=2)
        self.assertAlmostEqual(pfc["INDEX_RRPD_Pct_DSP_Baseline"], 15.7047, places=2)
        self.assertAlmostEqual(pfc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 5.6252, places=2)
        self.assertAlmostEqual(pfc["NMW_Labor_Minutes_Confiscated"], 79.00, places=1)

        peas = audits["Commercial De-Hulled Split Yellow Field Peas (Machine Dressed Food Grade, min 25% Protein)"]
        self.assertAlmostEqual(peas["P_retail_observed"], 680.00)
        self.assertAlmostEqual(peas["RRP_D_recommended"], 493.28, places=2)
        self.assertAlmostEqual(peas["Implied_Extractive_Drag_Ra"], 0.5779, places=3)
        self.assertAlmostEqual(peas["Fairness_Index_Percent"], 72.5, places=1)
        self.assertAlmostEqual(peas["INDEX_Observed_Pct_DSP_Baseline"], 109.8812, places=2)
        self.assertAlmostEqual(peas["INDEX_RRPD_Pct_DSP_Baseline"], 79.7098, places=2)
        self.assertAlmostEqual(peas["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 30.1714, places=2)
        self.assertAlmostEqual(peas["NMW_Labor_Minutes_Confiscated"], 423.71, places=1)

    def test_saline_and_solar_pv_calibrations(self):
        """Audits calibration for Case 57 (Saline IV Infusion Bag) and Case 58 (Solar PV Module 440W)."""
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        sal = audits["Pharmaceutical Saline IV Infusion Bag (Sodium Chloride 0.9%, 1,000 mL)"]
        self.assertAlmostEqual(sal["P_retail_observed"], 8.50)
        self.assertAlmostEqual(sal["RRP_D_recommended"], 4.99, places=2)
        self.assertAlmostEqual(sal["Implied_Extractive_Drag_Ra"], 0.5120, places=3)
        self.assertAlmostEqual(sal["Fairness_Index_Percent"], 58.7, places=1)
        self.assertAlmostEqual(sal["INDEX_Observed_Pct_DSP_Baseline"], 1.3735, places=2)
        self.assertAlmostEqual(sal["INDEX_RRPD_Pct_DSP_Baseline"], 0.8057, places=2)
        self.assertAlmostEqual(sal["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 0.5678, places=2)
        self.assertAlmostEqual(sal["NMW_Labor_Minutes_Confiscated"], 7.97, places=2)

        pv = audits["Commercial Solar PV Module (440W Monocrystalline Residential Panel, Tier-1)"]
        self.assertAlmostEqual(pv["P_retail_observed"], 165.00)
        self.assertAlmostEqual(pv["RRP_D_recommended"], 108.79, places=2)
        self.assertAlmostEqual(pv["Implied_Extractive_Drag_Ra"], 0.7594, places=3)
        self.assertAlmostEqual(pv["Fairness_Index_Percent"], 65.9, places=1)
        self.assertAlmostEqual(pv["INDEX_Observed_Pct_DSP_Baseline"], 26.6624, places=2)
        self.assertAlmostEqual(pv["INDEX_RRPD_Pct_DSP_Baseline"], 17.5795, places=2)
        self.assertAlmostEqual(pv["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 9.0829, places=2)
        self.assertAlmostEqual(pv["NMW_Labor_Minutes_Confiscated"], 127.55, places=2)

    def test_uc200_and_faba_concentrate_calibrations(self):
        """Audits calibration for Case 59 (Universal Column 200UC46.2) and Case 60 (Faba Bean Protein Concentrate 55%)."""
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        uc = audits["Commercial Structural Steel Universal Column (200UC46.2, AS/NZS 3679.1 Grade 300PLUS)"]
        self.assertAlmostEqual(uc["P_retail_observed"], 172.00)
        self.assertAlmostEqual(uc["RRP_D_recommended"], 127.25, places=2)
        self.assertAlmostEqual(uc["Implied_Extractive_Drag_Ra"], 0.5581, places=3)
        self.assertAlmostEqual(uc["Fairness_Index_Percent"], 74.0, places=1)
        self.assertAlmostEqual(uc["INDEX_Observed_Pct_DSP_Baseline"], 27.7935, places=2)
        self.assertAlmostEqual(uc["INDEX_RRPD_Pct_DSP_Baseline"], 20.5620, places=2)
        self.assertAlmostEqual(uc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 7.2315, places=2)
        self.assertAlmostEqual(uc["NMW_Labor_Minutes_Confiscated"], 101.56, places=1)

        faba = audits["Commercial Australian Faba Bean Protein Concentrate / Flour (min 55% Protein, per Tonne)"]
        self.assertAlmostEqual(faba["P_retail_observed"], 1280.00)
        self.assertAlmostEqual(faba["RRP_D_recommended"], 736.38, places=2)
        self.assertAlmostEqual(faba["Implied_Extractive_Drag_Ra"], 0.7548, places=3)
        self.assertAlmostEqual(faba["Fairness_Index_Percent"], 57.5, places=1)
        self.assertAlmostEqual(faba["INDEX_Observed_Pct_DSP_Baseline"], 206.8353, places=2)
        self.assertAlmostEqual(faba["INDEX_RRPD_Pct_DSP_Baseline"], 118.9911, places=2)
        self.assertAlmostEqual(faba["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 87.8442, places=2)
        self.assertAlmostEqual(faba["NMW_Labor_Minutes_Confiscated"], 1233.64, places=1)

    def test_uc250_and_pea_isolate_calibrations(self):
        """Audits calibration for Case 61 (Universal Column 250UC72.9) and Case 62 (Field Pea Protein Isolate 80%)."""
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        uc = audits["Commercial Structural Steel Universal Column (250UC72.9, AS/NZS 3679.1 Grade 300PLUS)"]
        self.assertAlmostEqual(uc["P_retail_observed"], 272.00)
        self.assertAlmostEqual(uc["RRP_D_recommended"], 200.55, places=2)
        self.assertAlmostEqual(uc["Implied_Extractive_Drag_Ra"], 0.5628, places=3)
        self.assertAlmostEqual(uc["Fairness_Index_Percent"], 73.7, places=1)
        self.assertAlmostEqual(uc["INDEX_Observed_Pct_DSP_Baseline"], 43.9525, places=2)
        self.assertAlmostEqual(uc["INDEX_RRPD_Pct_DSP_Baseline"], 32.4069, places=2)
        self.assertAlmostEqual(uc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 11.5456, places=2)
        self.assertAlmostEqual(uc["NMW_Labor_Minutes_Confiscated"], 162.14, places=1)

        isolate = audits["Commercial Australian Field Pea Protein Isolate (min 80% Protein, Spray-Dried, per Tonne)"]
        self.assertAlmostEqual(isolate["P_retail_observed"], 3450.00)
        self.assertAlmostEqual(isolate["RRP_D_recommended"], 1866.05, places=2)
        self.assertAlmostEqual(isolate["Implied_Extractive_Drag_Ra"], 0.7904, places=3)
        self.assertAlmostEqual(isolate["Fairness_Index_Percent"], 54.1, places=1)
        self.assertAlmostEqual(isolate["INDEX_Observed_Pct_DSP_Baseline"], 557.4857, places=2)
        self.assertAlmostEqual(isolate["INDEX_RRPD_Pct_DSP_Baseline"], 301.5351, places=2)
        self.assertAlmostEqual(isolate["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 255.9506, places=2)
        self.assertAlmostEqual(isolate["NMW_Labor_Minutes_Confiscated"], 3594.44, places=1)

    def test_uc310_and_chickpea_isolate_calibrations(self):
        """Audits calibration for Case 63 (Universal Column 310UC96.8) and Case 64 (Chickpea Protein Isolate 75%)."""
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        uc = audits["Commercial Structural Steel Universal Column (310UC96.8, AS/NZS 3679.1 Grade 300PLUS)"]
        self.assertAlmostEqual(uc["P_retail_observed"], 360.00)
        self.assertAlmostEqual(uc["RRP_D_recommended"], 266.27, places=2)
        self.assertAlmostEqual(uc["Implied_Extractive_Drag_Ra"], 0.5603, places=3)
        self.assertAlmostEqual(uc["Fairness_Index_Percent"], 74.0, places=1)
        self.assertAlmostEqual(uc["INDEX_Observed_Pct_DSP_Baseline"], 58.1724, places=2)
        self.assertAlmostEqual(uc["INDEX_RRPD_Pct_DSP_Baseline"], 43.0263, places=2)
        self.assertAlmostEqual(uc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 15.1462, places=2)
        self.assertAlmostEqual(uc["NMW_Labor_Minutes_Confiscated"], 212.70, places=1)

        chickpea = audits["Commercial Australian Chickpea Protein Isolate / Functional Flour (min 75% Protein, Alkaline-Extracted, per Tonne)"]
        self.assertAlmostEqual(chickpea["P_retail_observed"], 3150.00)
        self.assertAlmostEqual(chickpea["RRP_D_recommended"], 1700.63, places=2)
        self.assertAlmostEqual(chickpea["Implied_Extractive_Drag_Ra"], 0.7899, places=3)
        self.assertAlmostEqual(chickpea["Fairness_Index_Percent"], 54.0, places=1)
        self.assertAlmostEqual(chickpea["INDEX_Observed_Pct_DSP_Baseline"], 509.0086, places=2)
        self.assertAlmostEqual(chickpea["INDEX_RRPD_Pct_DSP_Baseline"], 274.8049, places=2)
        self.assertAlmostEqual(chickpea["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 234.2038, places=2)
        self.assertAlmostEqual(chickpea["NMW_Labor_Minutes_Confiscated"], 3289.04, places=1)

    def test_uc310_118_and_faba_isolate_calibrations(self):
        """Audits calibration for Case 65 (Universal Column 310UC118) and Case 66 (Faba Bean Protein Isolate 85%)."""
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        uc = audits["Commercial Structural Steel Universal Column (310UC118, AS/NZS 3679.1 Grade 300PLUS)"]
        self.assertAlmostEqual(uc["P_retail_observed"], 438.00)
        self.assertAlmostEqual(uc["RRP_D_recommended"], 324.41, places=2)
        self.assertAlmostEqual(uc["Implied_Extractive_Drag_Ra"], 0.5591, places=3)
        self.assertAlmostEqual(uc["Fairness_Index_Percent"], 74.1, places=1)
        self.assertAlmostEqual(uc["INDEX_Observed_Pct_DSP_Baseline"], 70.7764, places=2)
        self.assertAlmostEqual(uc["INDEX_RRPD_Pct_DSP_Baseline"], 52.4214, places=2)
        self.assertAlmostEqual(uc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 18.3550, places=2)
        self.assertAlmostEqual(uc["NMW_Labor_Minutes_Confiscated"], 257.77, places=1)

        faba = audits["Commercial Australian Faba Bean Protein Isolate (min 85% Protein, Wet-Extracted & Spray-Dried, per Tonne)"]
        self.assertAlmostEqual(faba["P_retail_observed"], 3580.00)
        self.assertAlmostEqual(faba["RRP_D_recommended"], 1940.60, places=2)
        self.assertAlmostEqual(faba["Implied_Extractive_Drag_Ra"], 0.7906, places=3)
        self.assertAlmostEqual(faba["Fairness_Index_Percent"], 54.2, places=1)
        self.assertAlmostEqual(faba["INDEX_Observed_Pct_DSP_Baseline"], 578.4924, places=2)
        self.assertAlmostEqual(faba["INDEX_RRPD_Pct_DSP_Baseline"], 313.5822, places=2)
        self.assertAlmostEqual(faba["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 264.9102, places=2)
        self.assertAlmostEqual(faba["NMW_Labor_Minutes_Confiscated"], 3720.26, places=1)

    def test_pfc300_and_split_lentils_calibrations(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        pfc = audits["Commercial Structural Steel Parallel Flange Channel (300x90mm PFC, Grade 300PLUS / AS/NZS 3679.1)"]
        self.assertAlmostEqual(pfc["P_retail_observed"], 149.50)
        self.assertAlmostEqual(pfc["RRP_D_recommended"], 110.43, places=2)
        self.assertAlmostEqual(pfc["Implied_Extractive_Drag_Ra"], 0.5585, places=3)
        self.assertAlmostEqual(pfc["Fairness_Index_Percent"], 73.9, places=1)
        self.assertAlmostEqual(pfc["INDEX_Observed_Pct_DSP_Baseline"], 24.1577, places=2)
        self.assertAlmostEqual(pfc["INDEX_RRPD_Pct_DSP_Baseline"], 17.8449, places=2)
        self.assertAlmostEqual(pfc["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 6.3126, places=2)
        self.assertAlmostEqual(pfc["NMW_Labor_Minutes_Confiscated"], 88.65, places=1)

        lentils = audits["Commercial De-Hulled Split Red Lentils (Machine Dressed Export Grade, min 26% Protein)"]
        self.assertAlmostEqual(lentils["P_retail_observed"], 1050.00)
        self.assertAlmostEqual(lentils["RRP_D_recommended"], 603.57, places=2)
        self.assertAlmostEqual(lentils["Implied_Extractive_Drag_Ra"], 0.7372, places=3)
        self.assertAlmostEqual(lentils["Fairness_Index_Percent"], 57.5, places=1)
        self.assertAlmostEqual(lentils["INDEX_Observed_Pct_DSP_Baseline"], 169.6695, places=2)
        self.assertAlmostEqual(lentils["INDEX_RRPD_Pct_DSP_Baseline"], 97.5308, places=2)
        self.assertAlmostEqual(lentils["INDEX_Extractive_Toll_Pct_DSP_Baseline"], 72.1387, places=2)
        self.assertAlmostEqual(lentils["NMW_Labor_Minutes_Confiscated"], 1013.08, places=1)


    def test_index_income_normalised_difficulty_examination(self):
        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        bread = audits["Commercial Sliced White Bread (680g)"]
        # At $1,250/wk median disposable income: $4.10 is 0.328% of weekly income, RRP/D $3.03 is 0.2424%
        self.assertAlmostEqual(bread["INDEX_Observed_Pct_Median_Income"], 0.3280, places=3)
        self.assertAlmostEqual(bread["INDEX_RRPD_Pct_Median_Income"], 0.2422, places=3)
        self.assertAlmostEqual(bread["INDEX_Extractive_Toll_Pct_Median_Income"], 0.0858, places=3)
        # In working life minutes at ~$32.89/hr: $4.10 = 7.48 min, $3.03 = 5.52 min, confiscated = 1.96 min
        self.assertAlmostEqual(bread["Labor_Minutes_Observed"], 7.48, places=1)
        self.assertAlmostEqual(bread["Labor_Minutes_Fair_RRPD"], 5.52, places=1)
        self.assertAlmostEqual(bread["Labor_Minutes_Confiscated"], 1.96, places=1)

        nbn = audits["Domestic Broadband Data Transit (NBN 50/20 Mbps Tier)"]
        # $85.00/mo is 6.80% of a median weekly income ($1,250) or 9.659% of subsistence weekly income ($880)
        self.assertAlmostEqual(nbn["INDEX_Observed_Pct_Median_Income"], 6.8000, places=3)
        self.assertAlmostEqual(nbn["INDEX_RRPD_Pct_Median_Income"], 2.6573, places=3)
        self.assertAlmostEqual(nbn["INDEX_Extractive_Toll_Pct_Median_Income"], 4.1427, places=3)
        self.assertAlmostEqual(nbn["Labor_Minutes_Confiscated"], 94.44, places=1)

    def test_weekly_household_basket_index(self):
        basket = audit_weekly_household_basket_index()
        self.assertGreater(basket["total_weekly_observed_AUD"], basket["total_weekly_fair_RRPD_AUD"])
        self.assertGreater(basket["Basket_INDEX_Observed_Pct_Median_Income"], basket["Basket_INDEX_RRPD_Pct_Median_Income"])
        self.assertAlmostEqual(
            basket["Basket_INDEX_Observed_Pct_Median_Income"] - basket["Basket_INDEX_RRPD_Pct_Median_Income"],
            basket["Basket_INDEX_Extractive_Toll_Pct_Median_Income"],
            places=1
        )
        self.assertGreater(basket["Weekly_Labor_Hours_Confiscated_Median"], 2.0)
        self.assertGreater(basket["Weekly_Labor_Hours_Confiscated_Subsistence"], basket["Weekly_Labor_Hours_Confiscated_Median"])

    def test_multi_bracket_welfare_and_wage_index(self):
        from rrp_fairness_audit import (
            Y_DSP_BASELINE_WEEKLY_AUD,
            Y_JSP_SINGLE_WEEKLY_AUD,
            Y_YA_INDEPENDENT_WEEKLY_AUD,
            Y_YA_AT_HOME_WEEKLY_AUD,
            Y_NMW_GROSS_WEEKLY_AUD,
            Y_AWOTE_GROSS_WEEKLY_AUD
        )
        # Verify exact Services Australia (20 Sep 2026), FWO (1 Jul 2026) and ABS (May 2026) weekly rates
        self.assertAlmostEqual(Y_DSP_BASELINE_WEEKLY_AUD, 618.85, places=2)
        self.assertAlmostEqual(Y_JSP_SINGLE_WEEKLY_AUD, 412.45, places=2)
        self.assertAlmostEqual(Y_YA_INDEPENDENT_WEEKLY_AUD, 338.60, places=2)
        self.assertAlmostEqual(Y_YA_AT_HOME_WEEKLY_AUD, 241.20, places=2)
        self.assertAlmostEqual(Y_NMW_GROSS_WEEKLY_AUD, 1004.90, places=2)
        self.assertAlmostEqual(Y_AWOTE_GROSS_WEEKLY_AUD, 2083.70, places=2)

        audits = {a["commodity"]: a for a in run_full_fairness_audit()}
        bread = audits["Commercial Sliced White Bread (680g)"]
        # Bread ($4.10 Obs, $3.03 Fair) on DSP Baseline ($618.85/wk):
        self.assertAlmostEqual(bread["INDEX_Observed_Pct_DSP_Baseline"], (4.10 / 618.85) * 100.0, places=3)
        self.assertGreater(bread["INDEX_Observed_Pct_YA_Away"], bread["INDEX_Observed_Pct_JSP_Single"])
        self.assertGreater(bread["INDEX_Observed_Pct_JSP_Single"], bread["INDEX_Observed_Pct_DSP_Baseline"])
        self.assertGreater(bread["INDEX_Observed_Pct_DSP_Baseline"], bread["INDEX_Obs_Pct_NMW_Net_38hr"])
        self.assertGreater(bread["INDEX_Obs_Pct_NMW_Net_38hr"], bread["INDEX_Obs_Pct_All_Employees_Net"])
        self.assertGreater(bread["INDEX_Obs_Pct_All_Employees_Net"], bread["INDEX_Obs_Pct_FT_AWOTE_Net"])

        basket = audit_weekly_household_basket_index()
        bs = basket["Bracket_Summary"]
        # Verify regressive monotonic burden from YA_At_Home down to FT_AWOTE_Gross
        self.assertAlmostEqual(bs["DSP_Structural_Baseline"]["Basket_INDEX_Observed_Pct"], 46.06, places=1)
        self.assertAlmostEqual(bs["DSP_Structural_Baseline"]["Basket_INDEX_Fair_RRPD_Pct"], 33.94, places=1)
        self.assertAlmostEqual(bs["DSP_Structural_Baseline"]["Basket_INDEX_Extractive_Toll_Pct"], 12.12, places=1)
        self.assertAlmostEqual(bs["JSP_Single"]["Basket_INDEX_Observed_Pct"], 69.10, places=1)
        self.assertAlmostEqual(bs["YA_Away_From_Home"]["Basket_INDEX_Observed_Pct"], 84.18, places=1)

    def test_extractive_drag_sfc_sink_decomposition(self):
        from rrp_fairness_audit import decompose_extractive_drag_sinks
        basket = audit_weekly_household_basket_index()
        sinks = basket["SFC_Extractive_Drag_Sinks_Weekly_AUD"]
        total_toll = basket["total_weekly_extractive_toll_AUD"]
        # Verify Godley-Lavoie stock-flow closure: sum of 4 sinks == 100% of extractive toll
        sum_sinks = (
            sinks["Sink_1_Compound_Debt_Interest_AUD"]
            + sinks["Sink_2_Commercial_Land_Rent_Mortgages_AUD"]
            + sinks["Sink_3_Oligopoly_Dividends_EBIT_AUD"]
            + sinks["Sink_4_Brokerage_AntiWork_Admin_AUD"]
        )
        self.assertAlmostEqual(sum_sinks, total_toll, places=1)
        # 65% of all extractive drag goes to servicing compound debt & commercial real-estate mortgages
        self.assertAlmostEqual(sinks["Combined_Debt_And_Mortgage_Service_Pct_Of_Drag"], 65.0, places=1)
        self.assertAlmostEqual(sinks["Combined_Debt_And_Mortgage_Service_Share_AUD"], 48.75, places=1)


    def test_big4_bank_loan_spread_fairness_audit(self):
        loan_data = get_big4_bank_loan_benchmark_dataset()
        self.assertEqual(len(loan_data), 5)
        spread_audit = audit_big4_loan_spreads(rba_cash_rate_pct=4.60)
        self.assertEqual(len(spread_audit["scales"]), 5)
        # Scale 1: Credit Card (20.99% nominal, 21.71% effective vs 3.20% Fair RRP/D)
        cc = spread_audit["scales"][0]
        self.assertAlmostEqual(cc["monthly_fair_RRPD_AUD"], 13.32, places=2)
        self.assertAlmostEqual(cc["fair_RRPD_rate_pct"], 3.20, places=2)
        self.assertAlmostEqual(cc["Implied_Extractive_Drag_Ra"], 0.9526, places=3)
        self.assertAlmostEqual(cc["Fairness_Index_Percent"], 14.7, places=1)
        # Scale 2: Unsecured Personal Loan (14.50% nominal, 15.22% effective vs 1.87% Fair RRP/D)
        pers = spread_audit["scales"][1]
        self.assertAlmostEqual(pers["monthly_fair_RRPD_AUD"], 31.11, places=2)
        self.assertAlmostEqual(pers["fair_RRPD_rate_pct"], 1.87, places=2)
        self.assertAlmostEqual(pers["Implied_Extractive_Drag_Ra"], 0.9670, places=3)
        # Scale 3: Owner-Occupier Mortgage ($100k Tranche @ 6.46% nominal vs 0.30% Fair RRP/D)
        mort = spread_audit["scales"][2]
        self.assertAlmostEqual(mort["monthly_fair_RRPD_AUD"], 24.76, places=2)
        self.assertAlmostEqual(mort["fair_RRPD_rate_pct"], 0.30, places=2)
        self.assertAlmostEqual(mort["Implied_Extractive_Drag_Ra"], 0.9810, places=3)
        self.assertAlmostEqual(spread_audit["standard_500k_mortgage_monthly_interest_AUD"], 2724.60, places=2)
        self.assertAlmostEqual(spread_audit["standard_500k_mortgage_monthly_fair_RRPD_AUD"], 123.80, places=2)
        # Scale 4: Small Business SME & Agribusiness Loan ($100k @ 7.72% nominal vs 0.61% Fair RRP/D)
        sme = spread_audit["scales"][3]
        self.assertAlmostEqual(sme["monthly_fair_RRPD_AUD"], 50.92, places=2)
        self.assertAlmostEqual(sme["fair_RRPD_rate_pct"], 0.61, places=2)
        self.assertAlmostEqual(sme["Implied_Extractive_Drag_Ra"], 0.9756, places=3)
        # Scale 5: Large Corporate Syndicate Loan ($100k @ 5.79% nominal vs 0.19% Fair RRP/D)
        corp = spread_audit["scales"][4]
        self.assertAlmostEqual(corp["monthly_fair_RRPD_AUD"], 16.19, places=2)
        self.assertAlmostEqual(corp["fair_RRPD_rate_pct"], 0.19, places=2)
        self.assertAlmostEqual(corp["Implied_Extractive_Drag_Ra"], 0.9864, places=3)
        # Verify regressive spread inversion: credit card rate > 3.5x corporate rate
        self.assertGreater(spread_audit["credit_card_vs_corporate_rate_multiplier"], 3.5)
        self.assertAlmostEqual(spread_audit["sme_vs_corporate_spread_bps"], 193.0, places=1)


    def test_step_by_step_working_out_integrity(self):
        """Verifies all intermediate step-by-step working out numbers and derivation strings across all 66 goods and 5 loan scales."""
        audits = run_full_fairness_audit()
        self.assertEqual(len(audits), 66)
        for a in audits:
            prec = 4 if "nt-km" in a["unit"] else 2
            self.assertAlmostEqual(
                a["P_phys_Pe_plus_Pb"],
                round(a["P_energy_Pe"] + a["P_base_Pb"], prec),
                places=prec
            )
            self.assertAlmostEqual(
                a["Observed_Metabolic_Spread_Delta"],
                round(a["P_retail_observed"] - a["P_phys_Pe_plus_Pb"], prec),
                places=prec
            )
            self.assertAlmostEqual(
                a["Pure_Metabolic_Cost_M_pure"],
                round(a["Unextracted_Metabolic_Numerator_W"] / a["Regen_Capacity_Rn"], 4),
                places=3
            )
            self.assertAlmostEqual(
                a["Fair_Metabolic_Tier_M_fair"],
                round(a["Pure_Metabolic_Cost_M_pure"] / 0.98, 4),
                places=3
            )
            self.assertIn("[Step 1: Biophysical Base]", a["Step_By_Step_Working_Out"])
            self.assertIn("[Step 7: Fair RRP/D]", a["Step_By_Step_Working_Out"])
            self.assertIn("[Step 8: Implied Drag Ra]", a["Step_By_Step_Working_Out"])
            self.assertIn("[Step 10: DSP INDEX ($618.85/wk) & NMW ($26.44/hr)]", a["Step_By_Step_Working_Out"])

        loans = audit_big4_loan_spreads()
        self.assertEqual(len(loans["scales"]), 5)
        for s in loans["scales"]:
            self.assertIn("Loan_Step_By_Step_Working_Out", s)
            self.assertIn("[Step 11: Loan Rate & Per-$10k Working Out]", s["Loan_Step_By_Step_Working_Out"])


if __name__ == "__main__":
    unittest.main()
