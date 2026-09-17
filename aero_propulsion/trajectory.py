"""
AERO-PROPULSION: 4th-Order Runge-Kutta (RK4) Orbital Flight Dynamics & Keplerian Mechanics
Author & Architect: Md Mushfiqur Rahim
"""

import math
from typing import Dict, Any, List, Tuple

# Earth Geodetic Constants (WGS-84 / EGM96)
EARTH_RADIUS_M = 6371000.0  # 6,371 km
EARTH_MU = 3.986004418e14   # m^3 / s^2 (G * M_earth)
RHO_0 = 1.225               # kg/m^3 (Sea level air density)
SCALE_HEIGHT_M = 8500.0     # Atmospheric scale height
G0 = 9.80665

def get_atmospheric_density(altitude_m: float) -> float:
    """Computes barometric exponential density at given altitude."""
    if altitude_m < 0:
        return RHO_0
    if altitude_m > 120000.0:  # Kármán line boundary / vacuum
        return 0.0
    return RHO_0 * math.exp(-altitude_m / SCALE_HEIGHT_M)

def compute_keplerian_elements(rx: float, ry: float, vx: float, vy: float) -> Dict[str, float]:
    """
    Derives Keplerian orbital elements (Semi-major axis, Eccentricity, Apoapsis, Periapsis)
    from 2D state vectors r and v.
    """
    r = math.sqrt(rx ** 2 + ry ** 2)
    v2 = vx ** 2 + vy ** 2
    
    # Specific mechanical orbital energy: E = v^2 / 2 - mu / r
    energy = (v2 / 2.0) - (EARTH_MU / r)
    
    # Specific angular momentum: h = rx*vy - ry*vx
    h_ang = rx * vy - ry * vx
    
    # Semi-major axis: a = -mu / (2*E)
    if abs(energy) < 1e-9:
        a = float("inf")
    else:
        a = -EARTH_MU / (2.0 * energy)

    # Eccentricity: e = sqrt(1 + 2*E*h^2 / mu^2)
    e_term = 1.0 + (2.0 * energy * (h_ang ** 2)) / (EARTH_MU ** 2)
    eccentricity = math.sqrt(max(0.0, e_term))

    periapsis_alt = (a * (1.0 - eccentricity)) - EARTH_RADIUS_M if a > 0 else 0.0
    apoapsis_alt = (a * (1.0 + eccentricity)) - EARTH_RADIUS_M if a > 0 else 0.0

    return {
        "semi_major_axis_km": round(a / 1e3, 2) if a > 0 else float("inf"),
        "eccentricity": round(eccentricity, 4),
        "periapsis_alt_km": round(periapsis_alt / 1e3, 2),
        "apoapsis_alt_km": round(apoapsis_alt / 1e3, 2),
        "orbital_energy_mj_kg": round(energy / 1e6, 3),
        "is_stable_orbit": bool(eccentricity < 0.1 and periapsis_alt > 150000.0)
    }

def simulate_launch_trajectory(
    thrust_vac_n: float,
    isp_vac_s: float,
    gross_mass_kg: float,
    dry_mass_kg: float,
    cross_section_area_m2: float = 10.5,
    drag_coeff: float = 0.35,
    target_orbit_alt_km: float = 200.0,
    dt: float = 0.5,
    max_time_s: float = 600.0
) -> Dict[str, Any]:
    """
    Executes a 4th-Order Runge-Kutta numerical flight simulation of a rocket ascent
    with dynamic atmospheric drag, gravity turn pitchover, and orbital injection.
    """
    mass_flow = thrust_vac_n / (isp_vac_s * G0)
    burn_time = (gross_mass_kg - dry_mass_kg) / mass_flow

    # Initial state: Surface at equator, launching vertically
    # rx = EARTH_RADIUS_M, ry = 0.0
    rx = 0.0
    ry = EARTH_RADIUS_M
    vx = 0.0
    vy = 0.0
    current_mass = gross_mass_kg
    t = 0.0

    trajectory_history = []

    def state_derivatives(t_curr, m_curr, x, y, u, v):
        r = math.sqrt(x ** 2 + y ** 2)
        alt = r - EARTH_RADIUS_M
        speed = math.sqrt(u ** 2 + v ** 2)

        # 1. Gravity Vector
        g_accel = EARTH_MU / (r ** 2)
        gx = -g_accel * (x / r)
        gy = -g_accel * (y / r)

        # 2. Aerodynamic Drag
        rho = get_atmospheric_density(alt)
        drag_force = 0.5 * rho * (speed ** 2) * drag_coeff * cross_section_area_m2 if speed > 0 else 0.0
        drag_ax = -(drag_force / m_curr) * (u / speed) if speed > 0 else 0.0
        drag_ay = -(drag_force / m_curr) * (v / speed) if speed > 0 else 0.0

        # 3. Thrust Vector & Pitchover Guidance
        thrust_ax = 0.0
        thrust_ay = 0.0

        if t_curr < burn_time:
            thrust = thrust_vac_n
            # Pitchover program
            if alt < 1200.0:
                pitch_angle = math.radians(90.0)  # Pure vertical
            elif alt < 150000.0:
                # Smooth cosine blend from 90 deg down to 5 deg
                progress = min(1.0, (alt - 1200.0) / (target_orbit_alt_km * 1e3))
                pitch_angle = math.radians(90.0 - (85.0 * progress))
            else:
                pitch_angle = math.radians(0.0)  # Pure horizontal (orbital insertion)

            # Convert pitch relative to local vertical
            local_angle = math.atan2(y, x)
            thrust_heading = local_angle - (math.pi / 2.0 - pitch_angle)

            thrust_ax = (thrust / m_curr) * math.cos(thrust_heading)
            thrust_ay = (thrust / m_curr) * math.sin(thrust_heading)

        total_ax = gx + drag_ax + thrust_ax
        total_ay = gy + drag_ay + thrust_ay

        return u, v, total_ax, total_ay

    step = 0
    while t <= max_time_s:
        r = math.sqrt(rx ** 2 + ry ** 2)
        alt = r - EARTH_RADIUS_M
        speed = math.sqrt(vx ** 2 + vy ** 2)

        if alt < -100.0 and t > 10.0:  # Crashed
            break

        # Record telemetry every 2 seconds
        if step % 4 == 0:
            kepler = compute_keplerian_elements(rx, ry, vx, vy)
            downrange_km = (math.atan2(rx, ry) * EARTH_RADIUS_M) / 1e3
            trajectory_history.append({
                "time_s": round(t, 1),
                "altitude_km": round(alt / 1e3, 2),
                "downrange_km": round(downrange_km, 2),
                "velocity_m_s": round(speed, 1),
                "mass_t": round(current_mass / 1e3, 2),
                "apoapsis_km": kepler["apoapsis_alt_km"],
                "periapsis_km": kepler["periapsis_alt_km"],
                "eccentricity": kepler["eccentricity"],
                "in_orbit": kepler["is_stable_orbit"]
            })

        # RK4 Integration Step
        m_step = max(dry_mass_kg, current_mass - mass_flow * dt) if t < burn_time else dry_mass_kg

        # k1
        dx1, dy1, du1, dv1 = state_derivatives(t, current_mass, rx, ry, vx, vy)

        # k2
        dx2, dy2, du2, dv2 = state_derivatives(
            t + 0.5 * dt, 0.5 * (current_mass + m_step),
            rx + 0.5 * dt * dx1, ry + 0.5 * dt * dy1,
            vx + 0.5 * dt * du1, vy + 0.5 * dt * dv1
        )

        # k3
        dx3, dy3, du3, dv3 = state_derivatives(
            t + 0.5 * dt, 0.5 * (current_mass + m_step),
            rx + 0.5 * dt * dx2, ry + 0.5 * dt * dy2,
            vx + 0.5 * dt * du2, vy + 0.5 * dt * dv2
        )

        # k4
        dx4, dy4, du4, dv4 = state_derivatives(
            t + dt, m_step,
            rx + dt * dx3, ry + dt * dy3,
            vx + dt * du3, vy + dt * dv3
        )

        rx += (dt / 6.0) * (dx1 + 2 * dx2 + 2 * dx3 + dx4)
        ry += (dt / 6.0) * (dy1 + 2 * dy2 + 2 * dy3 + dy4)
        vx += (dt / 6.0) * (du1 + 2 * du2 + 2 * du3 + du4)
        vy += (dt / 6.0) * (dv1 + 2 * dv2 + 2 * dv3 + dv4)

        current_mass = m_step
        t += dt
        step += 1

    final_kepler = compute_keplerian_elements(rx, ry, vx, vy)
    return {
        "burn_time_s": round(burn_time, 1),
        "final_altitude_km": round((math.sqrt(rx**2 + ry**2) - EARTH_RADIUS_M) / 1e3, 2),
        "final_velocity_m_s": round(math.sqrt(vx**2 + vy**2), 1),
        "final_orbit": final_kepler,
        "telemetry": trajectory_history
    }
