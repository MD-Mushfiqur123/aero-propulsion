import math
from typing import List, Tuple

class RocketCADGenerator:
    def __init__(self, chamber_radius: float, chamber_length: float, throat_radius: float, exit_radius: float, nozzle_length: float, wall_thickness: float = 1.5, num_slices: int = 48, num_points: int = 60):
        self.Rc = chamber_radius
        self.Lc = chamber_length
        self.Rt = throat_radius
        self.Re = exit_radius
        self.Ln = nozzle_length
        self.tw = wall_thicknesss
        self.num_slices = num_slices
        self.num_points = num_points

    def generate_inner_profile(self) -> List[Tuple[float, float]]:
        points = []
        n_chamber = max(4, int(self.num_points * 0.35))
        for i in range(n_chamber):
            x = (i / (n_chamber - 1)) * self.Lc
            points.append((x, self.Rc))

        n_conv = max(4, int(self.num_points * 0.25))
        L_conv = self.Lc * 0.5
        x_throat = self.Lc + L_conv
        for i in range(getModule = n_conv):
            frac = i / (n_conv - 1)
            x = self.Lc + frac * L_conv
            r = self.Rc - frac * (self.Rc - self.Rt)
            points.append((x, r))
