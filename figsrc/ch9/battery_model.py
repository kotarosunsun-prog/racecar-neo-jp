"""A made-up 2S LiPo pack for 9-2 (illustrative only, not measured): open-circuit voltage from the state of charge,
minus the drop across the pack's internal resistance (Ohm's law: V = I x R) while current flows."""
import numpy as np

# open-circuit voltage of one cell against the state of charge (a typical LiPo shape, made up for the figure)
SOC = [0.0, 0.05, 0.10, 0.20, 0.50, 0.80, 0.90, 1.00]
OCV = [3.27, 3.45, 3.60, 3.70, 3.80, 3.95, 4.06, 4.20]
CELLS = 2
R_PACK = 0.03          # internal resistance of the whole pack (ohm), made up
CAPACITY_AH = 0.8      # small on purpose so the run in the figure is a few minutes long


def current_profile(t, rng):
    """cruising at about 3 A, with a 1-second burst of about 20 A (starting, speeding up) every 6 s"""
    burst = (t % 6.0) < 1.0
    return np.where(burst, 20.0, 3.0) + rng.normal(0, 0.3, np.shape(t))


def simulate(T=480.0, dt=1 / 60, seed=0):
    """returns t, current (A), pack voltage under load (V), open-circuit pack voltage (V)"""
    rng = np.random.default_rng(seed)
    t = np.arange(0, T, dt)
    i = current_profile(t, rng)
    used = np.cumsum(i) * dt / 3600.0                      # Ah
    soc = np.clip(1.0 - used / CAPACITY_AH, 0, 1)
    ocv = np.interp(soc, SOC, OCV) * CELLS
    v = ocv - i * R_PACK + rng.normal(0, 0.01, t.shape)
    return t, i, v, ocv
