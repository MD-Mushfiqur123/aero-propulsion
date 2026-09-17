"""
AERO-PROPULSION: de Laval Supersonic Isentropic Solver & Rao Bell Nozzle Generator
Author & Architect: Md Mushfiqur Rahim
"""

import math
from typing import Dict, Any, List, Tuple
from .thermo import compute_gas_constants, compute_characteristic_velocity, G0

def area_mach_relation(mach: float, gamma: float) -> float:
    """Computes Area Ratio A/A* for a given Mach number."""
    if mach <= 0:
        return float("inf")
    term = (2.0 / (gamma + 1.0)) * (1.0 + 0.5 * (gamma - 1.0) * mach * mach)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return (1.0 / mach) * math.pow(term, exponent)

def solve_exit_mach(expansion_ratio: float, gamma: float, supersonic: bool = True) -> float:
    """
    Newton-Raphson numerical solver to determine exit Mach number for a given expansion ratio epsilon = Ae/At.
    """
    mach = 2.5 if supersonic else 0.3  # Initial guess
    tol = 1e-7
    max_iter = 100

    for _ in range(max_iter):
        f = area_mach_relation(mach, gamma) - expansion_ratio
        if abs(f) < tol:
            return round(mach, 4)
        
        # Numerical derivative
        h = 1e-5
        df = (area_mach_relation(mach + h, gamma) - area_mach_relation(mach - h, gamma)) / (2 * h)
        if abs(df) < 1e-12:
            break
        mach -= f / df
        if mach <= 0:
            mach = 0.1

    return round(mach, 4)

def solve_nozzle_performance(
    chamber_pressure_pa: float,
    chamber_temp_k: float,
    throat_radius_m: float,
    expansion_ratio: float,
    gamma: float,
    molecular_weight: float,
    ambient_pressure_pa: float = 101325.0
) -> Dict[str, Any]:
    """
    Calculates full isentropic performance of a de Laval rocket nozzle:
    Thrust, Exhaust Velocity, Isp (Sea-Level and Vacuum), Mass Flow Rate, and Exit Pressure.
    """
    r_spec, cp, cv = compute_gas_constants(molecular_weight, gamma)
    throat_area = math.pi * (throat_radius_m ** 2)
    exit_area = throat_area * expansion_ratio
    exit_radius_m = math.sqrt(exit_area / math.pi)

    # Exit Mach
    exit_mach = solve_exit_mach(expansion_ratio, gamma, supersonic=True)

    # Pressure & Temperature at Exit
    p_ratio = math.pow(1.0 + 0.5 * (gamma - 1.0) * exit_mach * exit_mach, -gamma / (gamma - 1.0))
    t_ratio = math.pow(1.0 + 0.5 * (gamma - 1.0) * exit_mach * exit_mach, -1.0)

    exit_pressure_pa = chamber_pressure_pa * p_ratio
    exit_temp_k = chamber_temp_k * t_ratio

    # Exit Velocity
    speed_of_sound_exit = math.sqrt(gamma * r_spec * exit_temp_k)
    exit_velocity_m_s = exit_mach * speed_of_sound_exit

    # Mass Flow Rate (Choked Flow at Throat where M=1)
    c_star = compute_characteristic_velocity(chamber_temp_k, gamma, molecular_weight)
    mass_flow_kg_s = (chamber_pressure_pa * throat_area) / c_star

    # Thrust Forces (Momentum thrust + Pressure difference thrust)
    thrust_vac_n = (mass_flow_kg_s * exit_velocity_m_s) + (exit_pressure_pa * exit_area)
    thrust_sea_level_n = (mass_flow_kg_s * exit_velocity_m_s) + ((exit_pressure_pa - ambient_pressure_pa) * exit_area)

    # Specific Impulse (Isp)
    isp_vac_s = thrust_vac_n / (mass_flow_kg_s * G0)
    isp_sl_s = thrust_sea_level_n / (mass_flow_kg_s * G0)

    # Thrust Coefficient (Cf)
    cf_vac = thrust_vac_n / (chamber_pressure_pa * throat_area)

    return {
        "throat_area_m2": round(throat_area, 6),
        "exit_area_m2": round(exit_area, 6),
        "throat_radius_m": round(throat_radius_m, 4),
        "exit_radius_m": round(exit_radius_m, 4),
        "exit_mach": exit_mach,
        "exit_pressure_bar": round(exit_pressure_pa / 1e5, 3),
        "exit_pressure_pa": round(exit_pressure_pa, 1),
        "exit_temp_k": round(exit_temp_k, 1),
        "exit_velocity_m_s": round(exit_velocity_m_s, 1),
        "mass_flow_kg_s": round(mass_flow_kg_s, 2),
        "thrust_vac_kn": round(thrust_vac_n / 1e3, 2),
        "thrust_sl_kn": round(thrust_sea_level_n / 1e3, 2),
        "isp_vac_s": round(isp_vac_s, 1),
        "isp_sl_s": round(isp_sl_s, 1),
        "thrust_coeff_cf": round(cf_vac, 4),
        "c_star_m_s": c_star
    }

def generate_rao_bell_contour(throat_radius: float, expansion_ratio: float, num_points: int = 50) -> List[Tuple[float, float]]:
    """
    Generates 2D coordinates (x, y) for a Rao 80% Parabolic Bell Nozzle contour.
    x is the axial distance from throat (x=0 is throat), y is the local radius.
    """
    r_t = throat_radius
    r_e = r_t * math.sqrt(expansion_ratio)
    
    # Rao 80% Bell parameters
    theta_n = math.radians(28.0)  # Initial expansion angle at throat exit
    theta_e = math.radians(8.5)   # Final exit lip angle
    length_conical_15deg = (r_e - r_t) / math.tan(math.radians(15.0))
    bell_length = 0.80 * length_conical_15deg

    points = []

    # 1. Convergent Inlet Section (Chamber into Throat)
    inlet_radius = 2.5 * r_t
    inlet_length = 1.8 * r_t
    for i in range(20):
        t = i / 19.0
        x = -inlet_length * (1.0 - t)
        # Cosine blend from inlet_radius to throat_radius
        y = r_t + (inlet_radius - r_t) * 0.5 * (1.0 + math.cos(math.pi * t))
        points.append((round(x, 4), round(y, 4)))

    # 2. Throat Region (Circular Arc, downstream radius = 0.382 * r_t)
    r_c = 0.382 * r_t
    x_n = r_c * math.sin(theta_n)
    y_n = r_t + r_c * (1.0 - math.cos(theta_n))

    # 3. Parabolic Divergent Bell: y = a*x^2 + b*x + c
    # Solved from boundary conditions at (x_n, y_n) and (bell_length, r_e)
    matrix_a = (math.tan(theta_e) - math.tan(theta_n)) / (2.0 * (bell_length - x_n))
    matrix_b = math.tan(theta_n) - 2.0 * matrix_a * x_n
    matrix_c = y_n - matrix_a * (x_n ** 2) - matrix_b * x_n

    for i in range(num_points):
        t = i / float(num_points - 1)
        x = x_n + t * (bell_length - x_n)
        y = matrix_a * (x ** 2) + matrix_b * x + matrix_c
        points.append((round(x, 4), round(y, 4)))

    return points
