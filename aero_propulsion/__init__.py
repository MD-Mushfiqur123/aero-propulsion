"""
AERO-PROPULSION: First-Principles Rocket Propulsion & Orbital Dynamics Engine
Author & Architect: Md Mushfiqur Rahim
Version: 1.0.0
"""

from .thermo import PROPELLANT_DATABASE, compute_gas_constants, compute_characteristic_velocity
from .nozzle import solve_nozzle_performance, solve_exit_mach, generate_rao_bell_contour
from .trajectory import simulate_launch_trajectory, compute_keplerian_elements

__all__ = [
    "PROPELLANT_DATABASE",
    "compute_gas_constants",
    "compute_characteristic_velocity",
    "solve_nozzle_performance",
    "solve_exit_mach",
    "generate_rao_bell_contour",
    "simulate_launch_trajectory",
    "compute_keplerian_elements"
]
