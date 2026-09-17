import math

class IntegratedRocketCAD:
    def __init__(self, R_tank=16.0, L_cyl=40.0, t_tank=1.0, R_pipe=2.5, L_pipe=8.0, t_pipe=0.8, Rf=5.0, Lf=1.5, Rc=3.5, Lc=10.0, Rt=0.315, Re=1.988, Ln=8.0, tw=1.2, slices=64):
        self.R_tank, self.L_cyl, self.t_tank = R_tank, L_cyl, t_tank
        self.R_pipe, self.L_pipe, self.t_pipe = R_pipe, L_pipe, t_pipe
        self.Rf, self.Lf, self.Rc, self.Lc = Rf, Lf, Rc, Lc
        self.Rt, self.Re, self.Ln, self.tw = Rt, Re, Ln, tw
        self.slices = slices

    def get_loop(self):
        outer, inner = [], []
        n_dome, R_out, R_in = 16, self.R_tank, self.R_tank - self.t_tank
        for i in range(n_dome + 1):
            theta = math.pi * 0.5 * (1.0 - i / n_dome)
            outer.append((R_out * (1.0 - math.sin(theta)), R_out * math.cos(theta)))
        x_tank_end = R_out + self.L_cyl
        outer.append((x_tank_end, R_out))
        for i in range(1, n_dome + 1):
            theta = math.pi * 0.5 * (i / n_dome)
            r = R_out * math.cos(theta)
            if r <= self.R_pipe:
                outer.append((x_tank_end + R_out * math.sin(theta), self.R_pipe))
                break
            outer.append((x_tank_end + R_out * math.sin(theta), r))
        x_pipe_end = outer[-1][0] + self.L_pipe
        outer.append((x_pipe_end, self.R_pipe))
        outer.append((x_pipe_end, self.Rf))
        x_flange_end = x_pipe_end + self.Lf
        outer.append((x_flange_end, self.Rf))
        outer.append((x_flange_end, self.Rc + self.tw))
        x_ch_end = x_flange_end + self.Lc
        outer.append((x_ch_end, self.Rc + self.tw))
        x_throat = x_ch_end + self.Lc * 0.5
        outer.append((x_throat, self.Rt + self.tw))
        n_div = 20
        for i in range(1, n_div + 1):
            frac = i / n_div
            outer.append((x_throat + frac * self.Ln, (self.Rt + (self.Re - self.Rt) * math.sqrt(frac)) + self.tw))
        for i in range(n_div, -1, -1):
            frac = i / n_div
            inner.append((x_throat + frac * self.Ln, self.Rt + (self.Re - self.Rt) * math.sqrt(frac)))
        inner.append((x_ch_end, self.Rc))
        inner.append((x_pipe_end, self.Rc))
        r_pipe_in = self.R_pipe - self.t_pipe
        inner.append((x_pipe_end, r_pipe_in))
        inner.append((outer[n_dome + 1 + len(outer[n_dome+2:n_dome+2])][0] if False else x_pipe_end - self.L_pipe, r_pipe_in))
        for i in range(n_dome, 0, -1):
            theta = math.pi * 0.5 * (i / n_dome)
            r = R_in * math.cos(theta)
            if r >= r_pipe_in:
                inner.append((x_tank_end + R_in * math.sin(theta), r))
        inner.append((R_out, R_in))
        for i in range(n_dome, -1, -1):
            theta = math.pi * 0.5 * (1.0 - i / n_dome)
            inner.append((self.t_tank + R_in * (1.0 - math.sin(theta)), max(0.0, R_in * math.cos(theta))))
        return outer + inner

    def export(self, filepath):
        loop = self.get_loop()
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
        with open(filepath, 'w') as f:
            f.write('solid integrated_tank_and_engine\n')
            for n, p1, p2, p3 in facets:
                f.write(f'  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n    outer loop\n      vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}\n      vertex {p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f}\n      vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}\n    endloop\n  endfacet\n')
            f.write('endsolid integrated_tank_and_engine\n')
        return len(facets)

cad = IntegratedRocketCAD()
n = cad.export('projects/aero-propulsion/cubesat_thruster.stl')
print(f'Done: {n} facets')
