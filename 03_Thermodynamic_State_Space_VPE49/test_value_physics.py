import sys
sys.path.insert(0, "/working_dir")
sys.path.insert(0, "/working_dir/c_78d465851f96cf57")
import numpy as np
import unittest
import hashlib
import json
from spatial_trade_optimizer import SpatialTradeOptimizer
from multi_commodity_dispatch import MultiCommodityDispatchSolver
from closed_loop_logistics import ClosedLoopLogisticsSolver
from hvnl_fatigue_dispatch import HVNLFatigueDispatchSolver

class TestValuePhysicsEngine(unittest.TestCase):

    # 1. Three-Layer Cost & UPE Canonical Formulation
    def test_upe_three_layer_decomposition(self):
        Pe = 0.45 # Energy/material exergy
        Pb = 0.70 # Human metabolic difficulty
        Pm = 3.85 # Financial and retail markup
        Pt = Pe + Pb + Pm
        self.assertTrue(np.isclose(Pt, 5.00), "Three-layer cost decomposition sum mismatch")
        
        # UPE Calculation
        m1, m2, v_rel, S, U, Rn, Ra = 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.77
        gamma_v = 1.0 / np.sqrt(max(1e-9, 1.0 - (v_rel**2)))
        scarcity_term = (S * U) / (Rn * (1.0 - Ra))
        nominal_price = m1 * m2 * gamma_v * scarcity_term + Pe + Pb
        Ph = Pe + Pb
        
        self.assertTrue(np.isclose(Ph, 1.15), "Physical base price Ph mismatch")
        self.assertTrue(nominal_price > Ph, "Nominal market price must exceed physical base price")

    def test_relativistic_coercion_and_boundary_regularization(self):
        UA = 100.0 # High existential urgency
        UB = 1.0   # Low urgency supplier
        eps_U = 1e-6 # Cost of Being floor
        v_rel = abs(UA - UB) / (max(UA, UB) + eps_U)
        
        self.assertTrue(0.0 <= v_rel < 1.0, "Relative urgency velocity must be bounded in [0, 1)")
        gamma = 1.0 / np.sqrt(1.0 - (v_rel**2))
        self.assertTrue(gamma > 1.0, "Lorentz coercion factor must exceed unity under urgency asymmetry")

    # 2. 56-Cell Empirical Matrix Normalization & Distortion Quotient (DQ)
    def test_56_cell_bread_matrix_dq(self):
        stages = [
            {"stage": "1. Planting", "price": 0.12, "west": 0.41, "dq": 0.27},
            {"stage": "2. Maturation", "price": 0.18, "west": 0.65, "dq": 0.26},
            {"stage": "3. Harvesting", "price": 0.25, "west": 0.89, "dq": 0.27},
            {"stage": "4. Milling", "price": 0.35, "west": 0.54, "dq": 0.61},
            {"stage": "5. Leavening", "price": 0.20, "west": 0.32, "dq": 0.59},
            {"stage": "6. Baking", "price": 0.90, "west": 1.32, "dq": 0.64},
            {"stage": "7. Slicing/Pack", "price": 0.50, "west": 0.31, "dq": 1.51},
            {"stage": "8. Retail Toll", "price": 2.50, "west": 0.22, "dq": 10.66}
        ]
        
        total_price = 5.00
        total_west = 4.69
        
        for s in stages:
            computed_dq = (s["price"] / total_price) / (s["west"] / total_west)
            self.assertTrue(np.isclose(computed_dq, s["dq"], atol=0.03), f"DQ mismatch at {s['stage']}: computed {computed_dq:.2f} vs expected {s['dq']}")

    # 3. Multi-Sector Leontief-Value Inverse
    def test_leontief_value_tensor_inverse(self):
        A = np.array([
            [0.000, 0.001, 0.002, 0.500, 0.100],
            [0.050, 0.000, 0.450, 15.000, 1.200],
            [0.002, 0.001, 0.000, 0.800, 0.050],
            [0.001, 0.0005, 0.0005, 0.000, 0.020],
            [0.002, 0.001, 0.001, 0.050, 0.000]
        ])
        
        I = np.eye(5)
        L_inv = np.linalg.inv(I - A)
        
        d_direct = np.array([0.5474, 0.1025, 0.1400, 5.4000, 1.7500])
        d_integrated = np.dot(d_direct, L_inv)
        
        self.assertTrue(np.isclose(d_integrated[0], 0.5650, atol=0.01), "Food integrated difficulty mismatch")
        self.assertTrue(np.isclose(d_integrated[1], 0.1092, atol=0.01), "Energy integrated difficulty mismatch")
        self.assertTrue(np.isclose(d_integrated[2], 0.1961, atol=0.01), "Water integrated difficulty mismatch")
        self.assertTrue(np.isclose(d_integrated[3], 7.5816, atol=0.05), "Shelter integrated difficulty mismatch")
        self.assertTrue(np.isclose(d_integrated[4], 2.0989, atol=0.02), "Care integrated difficulty mismatch")

    # 4. Theorem 5 Linear Amortization & Zero-Sum Stock-Flow Consistency
    def test_theorem_5_linear_amortization(self):
        principal = 180.0 # $180.0M AUD total across 100 farms
        term_weeks = 1300 # 25 years
        weekly_linear_payment = principal / term_weeks
        
        debt = principal
        for w in range(156):
            if not (20 <= w < 90): # 70-week disaster pause
                debt -= weekly_linear_payment
                
        expected_debt = principal - (156 - 70) * weekly_linear_payment
        self.assertTrue(np.isclose(debt, expected_debt), "Theorem 5 linear amortization balance mismatch")
        self.assertTrue(np.isclose(debt, 168.09, atol=0.02), "Final debt mismatch after disaster pause")

    # 5. Proof-of-Difficulty (PoD) Deterministic Hashing
    def test_pod_block_header_state_hashing(self):
        header = {
            "previous_block_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "merkle_root_west": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
            "timestamp": 1787884800,
            "exergy_mj_burned": 2845000.0,
            "metabolic_west_logged": 4200.0,
            "guild_multisig": [
                "0x028c7f...guild_agri",
                "0x039d8e...guild_energy",
                "0x027b4a...guild_water"
            ]
        }
        
        serialized = json.dumps(header, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(serialized).hexdigest()
        self.assertEqual(len(block_hash), 64, "SHA-256 state hash must be 64 hexadecimal characters")

    # 6. Finite Boundary Exhaustion Horizon
    def test_finite_boundary_exhaustion_formula(self):
        S_buffer_0 = 52.0 * 21.0
        weekly_demand = 21.0
        depleted_inflow = 21.0 * 0.1
        
        t_exhaust_weeks = S_buffer_0 / (weekly_demand - depleted_inflow)
        self.assertTrue(np.isclose(t_exhaust_weeks, 57.78, atol=0.1), "Exhaustion horizon formula mismatch")

    # 7. Spatial Trade Optimization & Linear Programming Dispatch
    def test_spatial_trade_optimization(self):
        optimizer = SpatialTradeOptimizer()
        net_grain = np.array([5.0, 20.0, 35.0, -15.0, 0.0, 5.0, 10.0, -10.0, -20.0, -25.0])
        res = optimizer.solve_optimal_dispatch(net_grain)
        
        self.assertEqual(res["status"], "Optimal", "Linear program solver must find optimal dispatch")
        self.assertTrue(np.isclose(res["total_tonnes_moved"], 70.0), "Total grain moved must match total deficit")
        self.assertTrue(res["total_exergy_friction_west"] > 0.0, "Transport friction must be strictly positive")

    # 8. Kantorovich-Samuelson Spatial Value Duality & Complementary Slackness
    def test_kantorovich_samuelson_duality(self):
        optimizer = SpatialTradeOptimizer()
        net_grain = np.array([5.0, 20.0, 35.0, -15.0, 0.0, 5.0, 10.0, -10.0, -20.0, -25.0])
        res = optimizer.solve_optimal_dispatch(net_grain)
        
        self.assertTrue(res["complementary_slackness_verified"], 
                        "Kantorovich-Samuelson complementary slackness condition must hold on active routes")
        self.assertEqual(len(res["nodal_potentials_west"]), optimizer.n_nodes, 
                         "Nodal shadow potential vector must span all 10 nodes")

    # 9. Coupled Multi-Commodity Spatial Dispatch & Fleet Capacity
    def test_coupled_multi_commodity_dispatch(self):
        solver = MultiCommodityDispatchSolver()
        net_supplies = np.zeros((10, 3))
        net_supplies[8] = [-25.0, -0.20, -5.0]
        net_supplies[9] = [-30.0, -0.30, -8.0]
        net_supplies[3] = [-15.0, -0.10, -4.0]
        net_supplies[0] = [ 15.0,  0.25,  6.0]
        net_supplies[2] = [ 40.0,  0.15,  8.0]
        net_supplies[1] = [ 25.0,  0.25,  5.0]
        net_supplies[4] = [ 10.0,  0.20, 10.0]
        
        res = solver.solve(net_supplies)
        self.assertEqual(res["status"], "Optimal", "Multi-commodity solver must achieve optimal status")
        self.assertTrue(res["max_link_utilization"] <= 1.0, "Highway link tonnage must not exceed capacity")
        self.assertTrue(res["total_exergy_friction_west"] > 0.0, "Exergy friction must be positive")
        
        total_grain_delivered = np.sum(res["dispatch_flows"][0, :, [3, 8, 9]])
        self.assertTrue(np.isclose(total_grain_delivered, 70.0), "Total grain delivered must match 70t deficit")

    # 10. Closed-Loop Fleet Conservation & Deadheading Tare Exergy
    def test_closed_loop_fleet_balance(self):
        solver = ClosedLoopLogisticsSolver()
        net_supplies = np.zeros((10, 3))
        net_supplies[8] = [-40.0, -0.060, -2.0]
        net_supplies[9] = [-80.0, -0.090, -4.0]
        net_supplies[3] = [-40.0, -0.030, -2.0]
        net_supplies[0] = [ 40.0,  0.060,  3.0]
        net_supplies[2] = [ 80.0,  0.060,  3.0]
        net_supplies[1] = [ 40.0,  0.060,  2.0]
        
        res = solver.solve_closed_loop(net_supplies)
        self.assertEqual(res["status"], "Optimal", "Closed-loop solver must find optimal solution")
        self.assertTrue(res["fleet_balance_conserved"], "Depot fleet inflow must strictly balance outflow at all nodes")
        self.assertTrue(res["deadhead_exergy_west"] > 0.0, "Empty repositioning exergy must be strictly positive")
        self.assertTrue(40.0 <= res["deadhead_overhead_percentage"] <= 70.0, 
                        "Tare deadhead overhead must be within empirical 40-70% freight range")
        self.assertTrue(res["peak_link_utilization"] <= 1.0, "Link capacity must not be exceeded")

    # 11. HVNL Heavy Vehicle Driver Fatigue & Staging Compliance
    def test_hvnl_fatigue_compliance(self):
        fatigue_solver = HVNLFatigueDispatchSolver()
        
        # Test short compliant route (Regional Hub <-> Narrabri, 240km roundtrip)
        short_route = fatigue_solver.evaluate_route_fatigue(0, 3)
        self.assertTrue(short_route["is_single_driver_compliant"], "Short route must be single-driver compliant")
        self.assertEqual(short_route["recommended_staging_hub"], None, "Compliant route should not require staging")
        
        # Test long route exceeding 12 hours work (Mudgee <-> Moree with extended handling)
        fatigue_solver_extended = HVNLFatigueDispatchSolver()
        fatigue_solver_extended.loading_time_hrs = 1.5
        fatigue_solver_extended.unloading_time_hrs = 1.5
        long_route = fatigue_solver_extended.evaluate_route_fatigue(5, 9)
        
        self.assertFalse(long_route["is_single_driver_compliant"], "Route exceeding 12h work must trigger non-compliance")
        self.assertTrue(long_route["requires_staging_swap"], "Staging swap must be required")
        self.assertIn(long_route["recommended_staging_hub"], ["Regional Hub", "Gilgandra"], 
                      "Recommended staging hub must be Regional Hub or Gilgandra crossroads")

    # 13. Work-Antiwork State-Space Dynamics & 45-Degree Rotation Isometry
    def test_work_antiwork_bifurcation(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test Condition 1: Pure Productive Surplus
        s1 = model.evaluate_state(W_a=50.0, A_a=10.0, W_p=200.0, A_p=20.0)
        self.assertEqual(s1["condition"], "Condition 1: Pure Productive Surplus")
        self.assertTrue(s1["is_surplus_generating"])
        
        # Test Condition 4: The Treadmill Trap
        s4 = model.evaluate_state(W_a=60.0, A_a=15.0, W_p=30.0, A_p=250.0)
        self.assertEqual(s4["condition"], "Condition 4: The Treadmill Trap")
        self.assertFalse(s4["is_surplus_generating"])
        
        # Test 45-degree rotation isometry: P^2 + A^2 == x^2 + y^2
        x, y = s1["x_raw"], s1["y_raw"]
        P, A = s1["P_potential"], s1["A_activity"]
        self.assertTrue(np.isclose(P**2 + A**2, x**2 + y**2), "45-degree rotation must preserve norm isometry")

    # 14. Finite-Time Sclerosis Blowup & Multi-Sector Leontief Floor Tensor
    def test_multisector_floor_tensor_and_finite_blowup(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test analytical finite-time blowup horizon
        t_blow = model.calculate_finite_time_blowup(20.0)
        expected_blow = 1.0 / (0.04 * 0.15 * (20.0 ** 0.15))
        self.assertTrue(np.isclose(t_blow, expected_blow), "Finite-time blowup calculation mismatch")
        self.assertTrue(np.isclose(t_blow, 106.3, atol=0.5), "Empirical blowup horizon mismatch")
        
        # Test multi-sector Leontief floor tensor
        direct_W = np.array([0.5474, 0.1025, 0.1400, 5.4000, 1.7500])
        direct_A = np.array([2.50, 0.20, 1.50, 44.0, 28.0])
        int_W, int_A = model.integrate_multisector_floors(direct_W, direct_A)
        
        self.assertTrue(np.isclose(int_W[0], 0.565, atol=0.01), "Food integrated constructive floor mismatch")
        self.assertTrue(np.isclose(int_W[1], 0.109, atol=0.01), "Energy integrated constructive floor mismatch")
        self.assertTrue(np.isclose(int_W[2], 0.196, atol=0.01), "Water integrated constructive floor mismatch")
        self.assertTrue(np.isclose(int_W[3], 7.582, atol=0.01), "Shelter integrated constructive floor mismatch")
        self.assertTrue(np.isclose(int_W[4], 2.099, atol=0.01), "Care integrated constructive floor mismatch")
        self.assertTrue(int_A[0] > direct_A[0], "Integrated regressive drag must exceed direct retail markup")

    # 15. Analytical Separatrix Boundary & Kinetic Leverage Regimes
    def test_analytical_separatrix_boundary(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        W_a = 50.0
        A_a = 10.0
        L_crit = A_a / W_a # 0.20
        
        # State strictly in supercritical growth basin: W_p > L_crit * A_p
        state_above = model.evaluate_state(W_a=W_a, A_a=A_a, W_p=30.0, A_p=100.0)
        self.assertTrue(state_above["is_surplus_generating"], "State above separatrix must generate surplus")
        self.assertTrue(state_above["kinetic_leverage"] > L_crit, "Leverage must exceed critical threshold")
        
        # State strictly in subcritical collapse basin: W_p < L_crit * A_p
        state_below = model.evaluate_state(W_a=W_a, A_a=A_a, W_p=10.0, A_p=100.0)
        self.assertFalse(state_below["is_surplus_generating"], "State below separatrix must not generate surplus")
        self.assertTrue(state_below["kinetic_leverage"] < L_crit, "Leverage must fall below critical threshold")

    # 16. Dynamic Drag Propagation Theorem (Theorem 4)
    def test_dynamic_drag_propagation(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test case: downstream food sector has ZERO local active antiwork and 100% maintenance
        # Upstream energy has high regressive debt: A_p,energy = 50.0
        init_state = np.array([200.0, 100.0, 150.0, 50.0, 80.0, # W_p
                                 0.0,  50.0,   0.0,  0.0,  0.0]) # A_p (only energy has drag)
        W_a_v = np.array([50.0, 30.0, 25.0, 10.0, 15.0])
        A_a_v = np.array([0.0, 0.0, 0.0, 0.0, 0.0]) # Zero active antiwork across all sectors
        M_v = 0.05 * init_state[:5] # 100% maintenance across all sectors
        
        derivs = model.multisector_derivatives(0.0, init_state, W_a_v, A_a_v, M_v)
        dA_p_dt = derivs[5:]
        
        # Verify that food (index 0) experiences forced positive drag growth despite zero local antiwork
        # because energy is required for farming (A_leontief[1, 0] = 0.050)
        self.assertTrue(dA_p_dt[0] > 0.0, "Upstream energy drag must induce positive drag growth in food")
        self.assertTrue(np.isclose(dA_p_dt[0], 0.05 * (0.050 * 50.0), atol=1e-3), "Drag propagation rate mismatch")

    # 17. Endogenous Leontief Degradation & Thermodynamic Singularity (Theorem 5.1)
    def test_endogenous_leontief_singularity(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test monotonic spectral radius growth
        res_0 = model.compute_endogenous_leontief(drag_ratio=0.0)
        res_10 = model.compute_endogenous_leontief(drag_ratio=10.0)
        res_25 = model.compute_endogenous_leontief(drag_ratio=25.0)
        
        self.assertTrue(res_0["spectral_radius"] < res_10["spectral_radius"] < res_25["spectral_radius"],
                        "Spectral radius must strictly increase with physical drag intensity")
        self.assertTrue(np.isclose(res_0["spectral_radius"], 0.1294, atol=1e-3))
        
        # Test critical singularity threshold
        crit_ratio = res_0["critical_drag_ratio"]
        self.assertTrue(np.isclose(crit_ratio, 44.87, atol=0.5), "Critical singularity ratio mismatch")
        
        # Test supercritical singularity divergence
        res_super = model.compute_endogenous_leontief(drag_ratio=50.0)
        self.assertTrue(res_super["is_singular"], "System must be singular when drag ratio exceeds critical bound")
        self.assertEqual(res_super["multiplier_norm"], float('inf'), "Multiplier norm must diverge to infinity")

    # 18. Transcritical Bifurcation & Singularity Curve Verification
    def test_bifurcation_diagram_and_singularity_curve(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        W_a = 50.0
        A_a = 10.0
        L_crit = A_a / W_a # 0.20
        
        # Test net kinetic yield at critical bifurcation threshold
        yield_crit = W_a * L_crit - A_a
        self.assertTrue(np.isclose(yield_crit, 0.0), "Net kinetic yield at bifurcation point must equal 0")
        
        # Test supercritical yield
        yield_super = W_a * (L_crit + 0.10) - A_a
        self.assertTrue(yield_super > 0.0, "Supercritical yield must be strictly positive")
        
        # Test subcritical yield
        yield_sub = W_a * (L_crit - 0.10) - A_a
        self.assertTrue(yield_sub < 0.0, "Subcritical yield must be strictly negative")
        
        # Test critical singularity ratio matches Theorem 5.1
        rho_0 = float(np.max(np.abs(np.linalg.eigvals(model.A_leontief))))
        lambda_val = 0.15
        expected_r_crit = ((1.0 / rho_0) - 1.0) / lambda_val
        self.assertTrue(np.isclose(expected_r_crit, 44.87, atol=0.5), "Critical singularity ratio mismatch")

    # 19. Stochastic Langevin Dynamics & Kramers Escape Rate (Section 5.5)
    def test_kramers_escape_rate_and_stochastic_stability(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test baseline escape from buffer distance 30 (W_p=50, A_p=100, L_crit=0.20)
        res_30 = model.compute_kramers_escape(W_p=50.0, A_p=100.0, W_a=50.0, A_a=10.0)
        self.assertTrue(np.isclose(res_30["buffer_distance"], 30.0))
        self.assertTrue(np.isclose(res_30["tau_escape_years"], 114.63, atol=0.5))
        
        # Test expanded buffer distance 180 (W_p=200, A_p=100)
        res_180 = model.compute_kramers_escape(W_p=200.0, A_p=100.0, W_a=50.0, A_a=10.0)
        self.assertTrue(res_180["tau_escape_years"] > res_30["tau_escape_years"])
        self.assertTrue(np.isclose(res_180["tau_escape_years"], 199.54, atol=0.5))
        
        # Test zero/negative buffer (already collapsed)
        res_zero = model.compute_kramers_escape(W_p=10.0, A_p=100.0, W_a=50.0, A_a=10.0)
        self.assertEqual(res_zero["tau_escape_years"], 0.0)
        self.assertEqual(res_zero["escape_rate_annual"], float('inf'))

    # 20. Ornstein-Uhlenbeck Colored Noise Kramers Escape (Theorem 5.3)
    def test_colored_noise_kramers_escape(self):
        from work_antiwork_dynamics import WorkAntiworkDynamics
        model = WorkAntiworkDynamics()
        
        # Test zero correlation length (matches white noise)
        res_0 = model.compute_colored_noise_kramers(W_p=50.0, A_p=100.0, W_a=50.0, A_a=10.0, tau_corr=0.0)
        res_white = model.compute_kramers_escape(W_p=50.0, A_p=100.0, W_a=50.0, A_a=10.0)
        self.assertTrue(np.isclose(res_0["tau_colored_years"], res_white["tau_escape_years"], atol=1e-3))
        
        # Test persistent 2.5-year ENSO correlation length
        res_enso = model.compute_colored_noise_kramers(W_p=50.0, A_p=100.0, W_a=50.0, A_a=10.0, tau_corr=2.5)
        self.assertTrue(res_enso["D_eff_colored"] < res_enso["D_0_white"])
        self.assertTrue(np.isclose(res_enso["color_prefactor_boost"], np.sqrt(1.0 + 0.05 * 2.5)))
        self.assertTrue(np.isclose(res_enso["tau_colored_years"], 121.59, atol=0.5))

    # 21. Invertible Algebraic State Equation & Diagnostic Inversions (Theorem 2.6)
    def test_invertible_upe_diagnostic_rearrangements(self):
        from work_antiwork_dynamics import InvertibleUPESolver
        solver = InvertibleUPESolver()
        
        # Ground truth forward parameters
        m1, m2, v_rel, S, U, Rn, Ra, Pe, Pb = 1.0, 1.0, 0.60, 1.25, 1.50, 2.00, 0.75, 0.45, 0.70
        P_forward = solver.calculate_price(m1, m2, v_rel, S, U, Rn, Ra, Pe, Pb)
        
        # Test exact inverted Ra
        Ra_calc = solver.solve_Ra(P_forward, m1, m2, v_rel, S, U, Rn, Pe, Pb)
        self.assertTrue(np.isclose(Ra_calc, Ra, atol=1e-5), "Inverted Ra must match ground truth")
        
        # Test exact inverted Rn
        Rn_calc = solver.solve_Rn(P_forward, m1, m2, v_rel, S, U, Ra, Pe, Pb)
        self.assertTrue(np.isclose(Rn_calc, Rn, atol=1e-5), "Inverted Rn must match ground truth")
        
        # Test exact inverted v_rel
        v_calc = solver.solve_v_rel(P_forward, m1, m2, S, U, Rn, Ra, Pe, Pb)
        self.assertTrue(np.isclose(v_calc, v_rel, atol=1e-5), "Inverted v_rel must match ground truth")
        
        # Test exact inverted Pb
        Pb_calc = solver.solve_Pb(P_forward, m1, m2, v_rel, S, U, Rn, Ra, Pe)
        self.assertTrue(np.isclose(Pb_calc, Pb, atol=1e-5), "Inverted Pb must match ground truth")

    # 22. Longitudinal Decoupled Identification Theorem (Theorem 2.7)
    def test_longitudinal_identification_decoupling(self):
        from work_antiwork_dynamics import InvertibleUPESolver
        solver = InvertibleUPESolver()
        
        T = 8
        R_n_0 = 100.0
        R_a_0 = 0.40
        delta_n = 0.05
        alpha_n = 0.80
        
        I_n = np.array([4.0, 3.0, 2.0, 1.0, 6.0, 10.0, 12.0, 15.0])
        R_a_true = np.array([0.40, 0.45, 0.52, 0.60, 0.68, 0.65, 0.60, 0.55])
        
        R_n_true = np.zeros(T)
        R_n_true[0] = R_n_0
        for t in range(T - 1):
            R_n_true[t+1] = (1.0 - delta_n) * R_n_true[t] + alpha_n * I_n[t]
            
        m1, m2, v_rel, S, U = 1.0, 1.0, 0.4, 1.1, 1.2
        Pe, Pb = 0.50, 0.75
        g = solver.gamma(v_rel)
        
        P_obs = np.zeros(T)
        for t in range(T):
            P_kinetic = (m1 * m2 * g * S * U) / (R_n_true[t] * (1.0 - R_a_true[t]))
            P_obs[t] = P_kinetic + Pe + Pb
            
        R_n_est, R_a_est = solver.estimate_longitudinal_decoupling(
            P_obs=P_obs, I_n=I_n, R_n_0=R_n_0, R_a_0=R_a_0,
            delta_n=delta_n, alpha_n=alpha_n,
            m1=m1, m2=m2, v_rel=v_rel, S=S, U=U, Pe=Pe, Pb=Pb
        )
        
        self.assertTrue(np.allclose(R_n_est, R_n_true, atol=1e-5), "Estimated R_n must match true physical trajectory")
        self.assertTrue(np.allclose(R_a_est, R_a_true, atol=1e-5), "Estimated R_a must match true monopoly trajectory")

    # 23. Extended Kalman Filter Decoupling Observer (Theorem 2.8)
    def test_extended_kalman_decoupling_observer(self):
        from work_antiwork_dynamics import ExtendedKalmanDecoupler
        np.random.seed(42)
        T = 12
        R_n_0, R_a_0 = 100.0, 0.40
        I_n = np.array([4.0, 3.0, 2.0, 1.0, 5.0, 8.0, 12.0, 15.0, 15.0, 12.0, 10.0, 8.0])
        R_a_true = np.array([0.40, 0.44, 0.50, 0.58, 0.65, 0.65, 0.62, 0.58, 0.55, 0.52, 0.50, 0.50])
        
        R_n_true = np.zeros(T)
        R_n_true[0] = R_n_0
        for t in range(T - 1):
            R_n_true[t+1] = (1.0 - 0.05) * R_n_true[t] + 0.80 * I_n[t]
            
        m1, m2, v_rel, S, U, Pe, Pb = 1.0, 1.0, 0.4, 1.1, 1.2, 0.50, 0.75
        g = 1.0 / np.sqrt(1.0 - v_rel**2)
        P_obs_noisy = np.zeros(T)
        for t in range(T):
            P_kin_true = (m1 * m2 * g * S * U) / (R_n_true[t] * (1.0 - R_a_true[t]))
            noise = np.random.normal(0, 0.02)
            P_obs_noisy[t] = P_kin_true * np.exp(noise) + Pe + Pb
            
        ekf = ExtendedKalmanDecoupler(delta_n=0.05, alpha_n=0.80, q_z=1e-4, q_theta=1e-3, r_meas=0.02**2)
        R_n_est, R_a_est = ekf.filter_panel(P_obs_noisy, I_n, R_n_0, R_a_0, m1, m2, v_rel, S, U, Pe, Pb)
        
        rel_err_Rn = np.mean(np.abs(R_n_true - R_n_est) / R_n_true)
        mse_Ra = np.mean((R_a_true - R_a_est)**2)
        
        self.assertTrue(rel_err_Rn < 0.06, f"Mean relative error in R_n ({rel_err_Rn:.2%}) must be under 6%")
        self.assertTrue(mse_Ra < 0.005, f"MSE in R_a ({mse_Ra:.6f}) must be under 0.005")

    # 24. Unscented Kalman Filter High-Order Decoupling Observer (Theorem 5.4)
    def test_unscented_kalman_decoupling_observer(self):
        from work_antiwork_dynamics import UnscentedKalmanDecoupler
        np.random.seed(42)
        T = 12
        R_n_0, R_a_0 = 100.0, 0.40
        I_n = np.array([4.0, 3.0, 2.0, 1.0, 5.0, 8.0, 12.0, 15.0, 15.0, 12.0, 10.0, 8.0])
        R_a_true = np.array([0.40, 0.44, 0.50, 0.58, 0.65, 0.65, 0.62, 0.58, 0.55, 0.52, 0.50, 0.50])
        
        R_n_true = np.zeros(T)
        R_n_true[0] = R_n_0
        for t in range(T - 1):
            R_n_true[t+1] = (1.0 - 0.05) * R_n_true[t] + 0.80 * I_n[t]
            
        m1, m2, v_rel, S, U, Pe, Pb = 1.0, 1.0, 0.4, 1.1, 1.2, 0.50, 0.75
        g = 1.0 / np.sqrt(1.0 - v_rel**2)
        P_obs_noisy = np.zeros(T)
        for t in range(T):
            P_kin_true = (m1 * m2 * g * S * U) / (R_n_true[t] * (1.0 - R_a_true[t]))
            noise = np.random.normal(0, 0.02)
            P_obs_noisy[t] = P_kin_true * np.exp(noise) + Pe + Pb
            
        ukf = UnscentedKalmanDecoupler(delta_n=0.05, alpha_n=0.80, q_z=1e-4, q_theta=1e-3, r_meas=0.02**2)
        R_n_est, R_a_est = ukf.filter_panel(P_obs_noisy, I_n, R_n_0, R_a_0, m1, m2, v_rel, S, U, Pe, Pb)
        
        rel_err_Rn = np.mean(np.abs(R_n_true - R_n_est) / R_n_true)
        mse_Ra = np.mean((R_a_true - R_a_est)**2)
        
        self.assertTrue(rel_err_Rn < 0.06, f"Mean relative error in R_n ({rel_err_Rn:.2%}) must be under 6%")
        self.assertTrue(mse_Ra < 0.005, f"MSE in R_a ({mse_Ra:.6f}) must be under 0.005")
        self.assertTrue(rel_err_Rn <= 0.0482, "UKF error must be at least as accurate as EKF")

if __name__ == "__main__":
    unittest.main()
