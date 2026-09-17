"""
AERO-PROPULSION: First-Principles Rocket Thermodynamics & Propellant Chemistry
Author & Architect: Md Mushfiqur Rahim
Version: 1.0.0
"""

import math
from typing import Dict, Any, Tuple

PROPELLANT_DATABASE = {
    "Hydrolox (LOX/LH2)": {
        "gamma": 1.20,
        "molecular_weight": 14.0,  # kg/kmol (rich H2 exhaust)
        "chamber_temp_k": 3500.0,
        "typical_isp_vac": 453.0,
        "description": "High-efficiency cryogenic hydrolox (Used in RS-25 Space Shuttle Main Engine)."
    },
    "Methalox (LOX/LCH4)": {
        "gamma": 1.22,
        "molecular_weight": 21.5,
        "chamber_temp_k": 3550.0,
        "typical_isp_vac": 380.0,
        "description": "Clean-burning, reusable cryogenic methalox (Used in SpaceX Raptor & Blue Origin BE-4)."
    },
    "Kerolox (LOX/RP-1)": {
        "gamma": 1.24,
        "molecular_weight": 23.5,
        "chamber_temp_k": 3670.0,
        "typical_isp_vac": 311.0,
        "description": "High-density booster propellant (Used in Saturn V F-1 & Falcon 9 Merlin 1D)."
    }
}

R_UNIVERSAL = 8314.462618  # J / (kmol * K)
G0 = 9.80665  # m/s^2 standard gravity

def compute_gas_constants(molecular_weight: float, gamma: float) -> Tuple[float, float, float]:
    """
    Computes Specific Gas Constant (R_spec), Cp, and Cv in J/(kg*K).
    """
    r_spec = R_UNIVERSAL / molecular_weight
    cp = (gamma * r_spec) / (gamma - 1.0)
    cv = cp / gamma
    return r_spec, cp, cv

def compute_characteristic_velocity(chamber_temp_k: float, gamma: float, molecular_weight: float) -> float:
    """
    Computes characteristic exhaust velocity c* (c-star) in m/s.
    c* = sqrt(R_spec * T_c) / Gamma(gamma)
    where Gamma(gamma) = sqrt(gamma) * (2 / (gamma + 1))^((gamma + 1)/(2*(gamma - 1)))
    """
    r_spec, _, _ = compute_gas_constants(molecular_weight, gamma)
    gamma_factor = math.sqrt(gamma) * math.pow(2.0 / (gamma + 1.0), (gamma + 1.0) / (2.0 * (gamma - 1.0)))
    c_star = math.sqrt(r_spec * chamber_temp_k) / gamma_factor
    return round(c_star, 2)
