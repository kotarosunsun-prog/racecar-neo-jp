import numpy as np
from gaps import find_gaps, widest_gap, gap_center, add_bubble, extend_disparities

angles = np.arange(-60, 61, 15).astype(float)
dists = np.array([120, 140, 260, 300, 300, 90, 80, 220, 250], float)

for name, d in (("そのまま", dists),
                ("バブル", add_bubble(angles, dists, 35.0)),
                ("のばして、バブル", add_bubble(angles, extend_disparities(angles, dists, 35.0, 50.0), 35.0))):
    gaps = find_gaps(d, 150.0)
    print(name, [(float(angles[a]), float(angles[b])) for a, b in gaps], "真ん中", float(gap_center(widest_gap(gaps), angles)))
