import numpy as np
import pandas as pd
import json

def run_stress_test(n_sims=1000, seed=42):
    np.random.seed(seed)
    
    # 10 Nodes
    nodes = [
        "Wellington", "Gilgandra", "Gunnedah", "Narrabri", 
        "Dubbo", "Mudgee", "Tamworth", "Warren", "Walgett", "Moree"
    ]
    n_nodes = len(nodes)
    pop_per_node = 600
    total_pop = n_nodes * pop_per_node
    
    # Baseline weekly demand per citizen
    grain_demand_per_cap = 0.0035  # tonnes/wk (~3.5 kg flour/grain)
    water_demand_per_cap = 0.0014  # ML/wk (1.4 kL/wk = 200 L/day)
    energy_demand_per_cap = 0.025  # MWh/wk (25 kWh/wk)
    
    total_grain_demand = total_pop * grain_demand_per_cap # 21.0 t/wk
    total_water_demand = total_pop * water_demand_per_cap # 8.4 ML/wk
    total_energy_demand = total_pop * energy_demand_per_cap # 150 MWh/wk
    
    # Baseline weekly production capacities (tonnes, ML, MWh)
    base_grain = np.array([45.0, 40.0, 65.0, 70.0, 15.0, 25.0, 30.0, 55.0, 50.0, 75.0])
    base_water = np.array([18.0, 20.0, 22.0, 15.0, 30.0, 35.0, 28.0, 25.0, 10.0, 12.0])
    base_energy = np.array([25.0, 22.0, 20.0, 28.0, 24.0, 18.0, 20.0, 26.0, 32.0, 30.0])
    
    # Initial Debt ($M AUD) across 100 farm enterprises
    initial_debt_total = 180.0 # $1.8M per farm, 10 farms per node
    
    # Simulation Horizon
    weeks = 156
    
    # Storage parameters for Value Physics buffers (weeks of reserve)
    # Testing buffer scenarios: 12 wks, 26 wks, 39 wks, 52 wks
    buffer_scenarios = [12, 26, 39, 52]
    
    results = {}
    
    for buf_wks in buffer_scenarios:
        neo_insolvencies = 0
        neo_exhaust_weeks = []
        neo_final_debts = []
        neo_famine_weeks = []
        
        vp_insolvencies = 0
        vp_exhaust_weeks = []
        vp_final_debts = []
        vp_famine_weeks = []
        vp_buffer_survivals = 0
        
        for sim in range(n_sims):
            # Stochastic drought severity: northern nodes hit by 90-100% collapse, southern by 60-80%
            # Drought duration: Weeks 20 to 124 (104 weeks of catastrophic shock)
            drought_severity_north = np.random.uniform(0.05, 0.15, size=(weeks, 4)) # Walgett, Moree, Narrabri, Warren
            drought_severity_south = np.random.uniform(0.20, 0.40, size=(weeks, 6)) # Other 6 nodes
            
            # Combine weather multiplier
            weather_mult = np.ones((weeks, n_nodes))
            for w in range(20, 124):
                weather_mult[w, [7, 8, 9, 3]] = drought_severity_north[w-20]
                weather_mult[w, [0, 1, 2, 4, 5, 6]] = drought_severity_south[w-20]
                
            # --- MODEL A: NEOCLASSICAL STATUS QUO ---
            neo_debt = initial_debt_total
            neo_cash_reserves = 15.0 # $15M Farm Management Deposits across all 100 farms
            neo_grain_stock = total_grain_demand * 6.0 # Commercial inventory = 6 weeks
            neo_water_stock = total_water_demand * 12.0 # Standard municipal water storage = 12 weeks
            
            neo_failed = False
            neo_fail_week = None
            neo_famine_count = 0
            
            r_commercial_base = 0.055 / 52 # 5.5% cash rate base + 3% margin = 8.5% p.a.
            r_commercial_shock = 0.085 / 52
            
            for w in range(weeks):
                current_rate = r_commercial_shock if w >= 20 else r_commercial_base
                # Production
                g_prod = np.sum(base_grain * weather_mult[w])
                w_prod = np.sum(base_water * weather_mult[w])
                
                # Farm revenue vs cost under neoclassical spot market
                # Farmers face surging diesel cost ($2.80/L) and interest expense
                interest_payment = neo_debt * current_rate
                operating_cost = 0.85 + (0.35 if w >= 20 else 0.0) # $M/wk operating expenses
                revenue = g_prod * 0.00032 # $320/t farmgate price (monopsony locked)
                
                cash_flow = revenue - operating_cost - interest_payment
                if cash_flow < 0:
                    if neo_cash_reserves >= abs(cash_flow):
                        neo_cash_reserves -= abs(cash_flow)
                    else:
                        uncovered = abs(cash_flow) - neo_cash_reserves
                        neo_cash_reserves = 0.0
                        neo_debt += uncovered # Compound debt expansion
                        
                # Inventory update
                neo_grain_stock += g_prod - total_grain_demand
                neo_water_stock += w_prod - total_water_demand
                
                if neo_grain_stock < 0 or neo_water_stock < 0:
                    neo_famine_count += 1
                    if not neo_failed:
                        neo_failed = True
                        neo_fail_week = w
                        
                # Bankruptcy condition: Debt > $220M (122% of asset backing) and cash reserves == 0
                if neo_debt > 220.0 and not neo_failed:
                    neo_failed = True
                    neo_fail_week = w
                    
            if neo_failed:
                neo_insolvencies += 1
                neo_exhaust_weeks.append(neo_fail_week)
            else:
                neo_exhaust_weeks.append(weeks)
            neo_final_debts.append(neo_debt)
            neo_famine_weeks.append(neo_famine_count)
            
            # --- MODEL B: VALUE PHYSICS TRI-FOLD NETWORK ---
            vp_debt = initial_debt_total
            # Strategic Book 2 buffers: buf_wks of grain and water
            vp_grain_stock = total_grain_demand * buf_wks
            vp_water_stock = total_water_demand * buf_wks
            
            vp_failed = False
            vp_fail_week = None
            vp_famine_count = 0
            
            # Theorem 5: Linear amortization over 25 years (1300 weeks) at 0.0% interest
            # During declared drought (w in [20, 124]), statutory disaster pause applies: Amortization = 0
            linear_amort_weekly = initial_debt_total / 1300 # ~$0.1385M/wk
            
            for w in range(weeks):
                # Production
                g_prod = np.sum(base_grain * weather_mult[w])
                w_prod = np.sum(base_water * weather_mult[w])
                
                # Debt update: 0.0% interest! If disaster period, pause amortization. Otherwise, pay linear principal.
                if not (20 <= w < 124):
                    vp_debt = max(0.0, vp_debt - linear_amort_weekly)
                    
                # Inter-Sovereign Trade Tensor balances physical buffers across all 10 nodes
                # Net buffer change
                vp_grain_stock += g_prod - total_grain_demand
                vp_water_stock += w_prod - total_water_demand
                
                if vp_grain_stock < 0 or vp_water_stock < 0:
                    vp_famine_count += 1
                    if not vp_failed:
                        vp_failed = True
                        vp_fail_week = w
                        
            if vp_failed:
                vp_insolvencies += 1
                vp_exhaust_weeks.append(vp_fail_week)
            else:
                vp_buffer_survivals += 1
                vp_exhaust_weeks.append(weeks)
            vp_final_debts.append(vp_debt)
            vp_famine_weeks.append(vp_famine_count)
            
        results[f"Buffer_{buf_wks}wks"] = {
            "Neoclassical": {
                "Insolvency_Rate": neo_insolvencies / n_sims,
                "Mean_Failure_Week": float(np.mean([w for w in neo_exhaust_weeks if w < weeks])) if neo_insolvencies > 0 else None,
                "Mean_Final_Debt_M": float(np.mean(neo_final_debts)),
                "Mean_Famine_Weeks": float(np.mean(neo_famine_weeks)),
                "Survival_Probability": 1.0 - (neo_insolvencies / n_sims)
            },
            "Value_Physics": {
                "Insolvency_Rate": vp_insolvencies / n_sims,
                "Mean_Failure_Week": float(np.mean([w for w in vp_exhaust_weeks if w < weeks])) if vp_insolvencies > 0 else None,
                "Mean_Final_Debt_M": float(np.mean(vp_final_debts)),
                "Mean_Famine_Weeks": float(np.mean(vp_famine_weeks)),
                "Survival_Probability": vp_buffer_survivals / n_sims,
                "Debt_Amortized_M": float(initial_debt_total - np.mean(vp_final_debts))
            }
        }
        
    print(json.dumps(results, indent=2))
    with open('/working_dir/c_78d465851f96cf57/stress_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_stress_test()
