"""9-3: combo_follow.py (7-13) on course D, 5 times each: the simulator-like LIDAR (720 points, 6 turns a second),
the physical-car-like LIDAR (1080 points, 10 turns a second), and the 1080-point LIDAR with the old 720-point angle list.
Writes data/real7.json."""
import sys, json; import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','ch7')); sys.path.insert(0,os.path.join(HERE,'..'))
import builtins; P0=builtins.print
import ch7run as C, courses7 as K, sim2d, wallsim, numpy as np
from sim_real import real_like
W=K.mixed_course(); FY=4600
orig=sim2d.World.__init__
def patched(self,*a,**k):
    orig(self,*a,**k)
    if MODE=='real': real_like(self)
sim2d.World.__init__=patched
OLD=("return np.radians(np.arange(len(scan)) * 360 / len(scan))","return np.radians(np.arange(720) * 0.5)")
res={}
for MODE,spin,subs in (('sim',6,[]),('real',10,[]),('real_old',10,[OLD])):
    if MODE=='real_old': MODE='real'; tag='real_old'
    else: tag=MODE
    r=[]
    for seed in range(5):
        try:
            L,out,cr=C.drive('combo_follow.py',W,110,subs=subs,seed=seed,spin_hz=spin)
            fin=np.where(L[:,2]>FY)[0]
            r.append(round(float(L[fin[0],0]),1) if len(fin) else ('X' if cr else '-'))
        except Exception as e:
            r.append('ERR '+type(e).__name__+': '+str(e)[:120]); break
    P0(tag, r, flush=True); res[tag]=r
json.dump(res,open(os.path.join(HERE,'data','real7.json'),'w'),ensure_ascii=False)
