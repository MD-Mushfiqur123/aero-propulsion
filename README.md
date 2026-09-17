# 🚀 AERO-PROPULSION // First-Principles Rocket Propulsion & Orbital Dynamics Engine

> **Architect & Lead Developer:** **Md Mushfiqur Rahim**  
> **Philosophy:** Pure First-Principles Aerospace Physics, Exact de Laval CFD, 4th-Order Runge-Kutta (RK4) Orbital Ascent.

---

## ⚡ Mathematical & Physics Foundations

### 1. Tsiolkovsky Rocket Equation
$$\Delta v = I_{sp} \cdot g_0 \ln\left(\frac{m_0}{m_f}\right)$$

### 2. Isentropic de Laval Nozzle Supersonic Expansion
$$\frac{A}{A^*} = \frac{1}{M} \left[ \frac{2}{\gamma + 1} \left( 1 + \frac{\gamma - 1}{2} M^2 \right) \right]^{\frac{\gamma + 1}{2(\gamma - 1)}}$$

### 3. Characteristic Velocity ($c^*$)
$$c^* = \frac{\sqrt{R_{\text{spec}} T_c}}{\sqrt{\gamma} \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma + 1}{2(\gamma - 1)}}}$$

### 4. 4th-Order Runge-Kutta Flight Dynamics
$$\frac{d\vec{v}}{dt} = \frac{\vec{T}}{m(t)} - \frac{\mu}{r^3}\vec{r} - \frac{1}{2}\rho_0 e^{-h/H_0} v^2 \frac{C_d A}{m(t)} \hat{v}$$

---

## 🎮 Interactive Visualizer
Open [`visualizer/index.html`](file:///c:/Users/mushfiqur/Desktop/agent/projects/aero-propulsion/visualizer/index.html) in any modern browser for:
1. **Live de Laval & Rao 80% Bell Contour CFD:** Interactive Mach color gradients from subsonic chamber ($M < 1$) to supersonic exhaust ($M > 4.5$) with atmospheric shock diamonds.
2. **Propellant Comparison:** Hydrolox ($\text{LOX}/\text{LH}_2$), Methalox ($\text{LOX}/\text{CH}_4$), Kerolox ($\text{LOX}/\text{RP}-1$).
3. **Live RK4 Orbital Launch Simulator:** Watch the rocket launch from Earth's surface, execute gravity turn pitchover, and insert into stable orbit.

---

## 🧪 Automated Physics Tests
```bash
cd projects/aero-propulsion
python -m unittest discover tests -v
```

---

## 📜 Intellectual Property
Copyright (c) 2026 **Md Mushfiqur Rahim**. All rights reserved.
