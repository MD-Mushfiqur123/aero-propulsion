"""
AERO-PROPULSION: Automated Physics & Thermodynamics Test Suite
Author: Md Mushfiqur Rahim
"""

import unittest
import math
from aero_propulsion.thermo import compute_gas_constants, compute_characteristic_velocity, PROPELLANT_DATABASE
from aero_propulsion.nozzle import solve_exit_mach, solve_nozzle_performance, generate_rao_bell_contour
from aero_propulsion.trajectory import get_atmospheric_density, compute_keplerian_elements, simulate_launch_trajectory

class TestAeroPropulsion(unittest.TestCase):

    def test_gas_constants_hydrolox(self):
        r_spec, cp, cv = compute_gas_constants(14.0, 1.20)
        self.assertAlmostEqual(r_spec, 593.89, places=1)
        self.assertAlmostEqual(cp, 3563.34, places=0)
        self.assertAlmostEqual(cv, 2969.45, places=0)
        self.assertAlmostEqual(cp / cv, 1.20, places=3)

    def test_characteristic_velocity(self):
        # c* for hydrolox (Tc=3500K, gamma=1.20, M=14.0) should be ~ 2300-2450 m/s
        c_star = compute_characteristic_velocity(3500.0, 1.20, 14.0)
        self.assertGreater(c_star, 2200.0)
        self.assertLess(c_star, 2550.0)

    def test_nozzle_supersonic_expansion(self):
        # Hydrolox RS-25 like parameters: Pc=20 MPa, eps=77.5
        res = solve_nozzle_performance(20e6, 3500.0, 0.15, 77.5, 1.20, 14.0)
        self.assertGreater(res["exit_mach"], 4.0)
        self.assertGreater(res["isp_vac_s"], 420.0)
        self.assertGreater(res["thrust_vac_kn"], 2000.0)

    def test_rao_bell_contour_continuity(self):
        points = generate_rao_bell_contour(0.15, 40.0, num_points=30)
        self.assertGreater(len(points), 40)
        # Verify monotonically increasing radius in divergent section
        divergent_radii = [p[1] for p in points[20:]]
        for i in range(len(divergent_radii) - 1):
            self.assertLessEqual(divergent_radii[i], divergent_radii[i+1])

    def test_atmospheric_density_decay(self):
        rho_0 = get_atmospheric_density(0.0)
        self.assertAlmostEqual(rho_0, 1.225, places=3)
        # At scale height 8.5 km, density should be 1/e of sea level ~ 0.45 kg/m3
        rho_8500 = get_atmospheric_density(8500.0)
        self.assertAlmostEqual(rho_8500, 1.225 / math.e, places=2)
        # At 150 km, density is vacuum = 0.0
        self.assertEqual(get_atmospheric_density(150000.0), 0.0)

    def test_keplerian_circular_orbit(self):
        # Circular orbit at 200 km altitude: r = 6571 km, v = sqrt(mu / r) ~ 7784 m/s
        r0 = 6571000.0
        v_circ = math.sqrt(3.986004418e14 / r0)
        kepler = compute_keplerian_elements(0.0, r0, v_circ, 0.0)
        self.assertAlmostEqual(kepler["eccentricity"], 0.0, places=3)
        self.assertAlmostEqual(kepler["periapsis_alt_km"], 200.0, places=0)
        self.assertAlmostEqual(kepler["apoapsis_alt_km"], 200.0, places=0)
        self.assertTrue(kepler["is_stable_orbit"])

if __name__ == "__main__":
    unittest.main()
