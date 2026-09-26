"""9-3: grand_prix.py (8-1) on the book's course, 5 times, with the physical-car-like LIDAR (1080 points, 10 turns a second).
Writes data/real8.json: (time past the finish line or None, crashed, time of FINISH)."""
import sys, json; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','ch8')); sys.path.insert(0,os.path.join(HERE,'..'))
import builtins; P0=builtins.print
import ch8run as C, sim2d, numpy as np
from sim_real import real_like
orig=sim2d.World.__init__
def patched(self,*a,**k):
    orig(self,*a,**k); real_like(self)
sim2d.World.__init__=patched
r=[]
for seed in range(5):
    L,out,cr,fin=C.gp(T=180,seed=seed,spin_hz=10)
    stops=[f/60 for f,t in out if 'FINISH' in t]
    r.append((fin, cr, round(stops[0],1) if stops else None)); P0(seed, r[-1], flush=True)
json.dump(r,open(os.path.join(HERE,'data','real8.json'),'w'))
