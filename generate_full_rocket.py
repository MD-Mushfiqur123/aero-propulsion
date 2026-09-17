import math

class FullRocketCAD:
    def __init__(self, R_core=18.0, L_nose=50.0, L_s2=40.0, L_interstage=15.0, L_s1=110.0, t_wall=1.5, slices=64):
        self.R = R_core
        self.Ln = L_nose
        self.Ls2 = L_s2
        self.Lint = L_interstage
        self.Ls1 = L_s1
        self.tw = t_wall
        self.slices = slices

    def get_contour(self):
        outer, inner = [], []
        n_nose = 30
        for i in range(n_nose + 1):
            x = (i / n_nose) * self.Ln
            if x == 0.0:
                r = 0.0
            else:
                theta = math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * x / self.Ln)))
                r = self.R * math.sqrt((theta - 0.5 * math.sin(2.0 * theta)) / math.pi)
            outer.append((x, r))

        x_s2_end = self.Ln + self.Ls2
        outer.append((x_s2_end, self.R))
        outer.append((x_s2_end + 1.0, self.R + 0.8))
        outer.append((x_s2_end + self.Lint - 1.0, self.R + 0.8))
        outer.append((x_s2_end + self.Lint, self.R))

        x_s1_end = x_s2_end + self.Lint + self.Ls1
        outer.append((x_s1_end, self.R))

        x_skirt_end = x_s1_end + 12.0
        R_skirt = self.R * 0.88
        outer.append((x_skirt_end, R_skirt))

        x_base = x_skirt_end
        R_engine_exit = self.R * 0.55
        R_throat = self.R * 0.16
        L_nozzle = 18.0

        outer.append((x_base, R_engine_exit))
        n_bell = 16
        for i in range(n_bell + 1):
            frac = 1.0 - (i / n_bell)
            x = x_base + frac * L_nozzle
            r = R_throat + (R_engine_exit - R_throat) * math.sqrt(frac) + self.tw
            outer.append((x, r))

        outer.append((x_base + L_nozzle, R_engine_exit + self.tw))
        outer.append((x_base + L_nozzle, R_engine_exit))

        for i in range(n_bell, -1, -1):
            frac = i / n_bell
            x = x_base + frac * L_nozzle
            r = R_throat + (R_engine_exit - R_throat) * math.sqrt(frac)
            inner.append((x, r))

        x_throat = x_base
        inner.append((x_throat, R_throat))
        inner.append((x_throat - 8.0, R_throat * 1.8))
        inner.append((x_throat - 8.0, max(1.0, self.R - self.tw)))
        inner.append((x_s1_end, self.R - self.tw))
        inner.append((self.Ln, self.R - self.tw))

        for i in range(n_nose - 3, 0, -1):
            x = (i / n_nose) * self.Ln
            theta = math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * x / self.Ln)))
            r = max(0.0, (self.R * math.sqrt((theta - 0.5 * math.sin(2.0 * theta)) / math.pi)) - self.tw)
            inner.append((x, r))

        inner.append((self.tw, 0.0))
        return outer + inner

    def export(self, filepath):
        loop = self.get_contour()
        def pt(x, r, s):
            th = 2.0 * math.pi * s / self.slices
            return (x, r * math.cos(th), r * math.sin(th))
        def norm(p1, p2, p3):
            u = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
            v = (p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2])
            nx = u[1]*v[2] - u[2]*v[1]; ny = u[2]*v[0] - u[0]*v[2]; nz = u[0]*v[1] - u[1]*v[0]
            mag = math.sqrt(nx*nx + ny*ny + nz*nz)
            return (nx/mag, ny/mag, nz/mag) if mag > 0 else (0.0, 0.0, 1.0)

        facets = []
        for i in range(len(loop) - 1):
            x1, r1 = loop[i]; x2, r2 = loop[i+1]
            if abs(x1-x2) < 1e-5 and abs(r1-r2) < 1e-5: continue
            for s in range(self.slices):
                sn = (s + 1) % self.slices
                p1, p2, p3, p4 = pt(x1, r1, s), pt(x2, r2, s), pt(x2, r2, sn), pt(x1, r1, sn)
                facets.append((norm(p1, p2, p3), p1, p2, p3))
                facets.append((norm(p1, p3, p4), p1, p3, p4))

        fin_x_start = self.Ln + self.Ls2 + 2.0
        fin_l, fin_h, fin_t = 10.0, 8.0, 1.0
        for fin_idx in range(4):
            ang = fin_idx * (math.pi * 0.5)
            cos_a, sin_a = math.cos(ang), math.sin(ang)
            r_base, r_tip = self.R, self.R + fin_h
            v = []
            for dx in [0.0, fin_l]:
                for dr in [r_base, r_tip]:
                    for dt in [-fin_t*0.5, fin_t*0.5]:
                        v.append((fin_x_start + dx, dr * cos_a - dt * sin_a, dr * sin_a + dt * cos_a))
            faces = [(0,1,3,2), (4,6,7,5), (0,4,5,1), (2,3,7,6), (0,2,6,4), (1,5,7,3)]
            for f in faces:
                p1, p2, p3, p4 = v[f[0]], v[f[1]], v[f[2]], v[f[3]]
                facets.append((norm(p1, p2, p3), p1, p2, p3))
                facets.append((norm(p1, p3, p4), p1, p3, p4))

        with open(filepath, 'w') as f:
            f.write('solid full_orbital_rocket\n')
            for n, p1, p2, p3 in facets:
                f.write(f'  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n    outer loop\n      vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}\n      vertex {p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f}\n      vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}\n    endloop\n  endfacet\n')
            f.write('endsolid full_orbital_rocket\n')
        return len(facets)

cad = FullRocketCAD()
n = cad.export('projects/aero-propulsion/full_rocket.stl')
print(f'Done: {n} facets')
