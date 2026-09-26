"""Things the physical car's LIDAR does that the simulator's does not (for 9-3, sim2d model):
1080 points per turn, and clear glass it cannot see (walls the car can hit but the LIDAR misses)."""
import math
import numpy as np
import sim2d


class GlassWorld(sim2d.World):
    """walls the car can hit but the LIDAR cannot see (clear glass): glass = list of segments"""
    def __init__(self, walls, glass, **kw):
        super().__init__(list(walls) + list(glass), **kw)
        self._seen = np.array(walls, float).reshape(-1, 4)
        self._all = self.seg

    def _raw_scan(self):
        self.seg = self._seen
        try:
            return super()._raw_scan()
        finally:
            self.seg = self._all


def real_like(world, n=1080):
    """make a world's LIDAR return n points per turn (the physical car: 1080)"""
    world.n = n
    world.phi = np.arange(n) * 2 * math.pi / n
    return world
