"""Figure 1 for 6-8: the graph that plot_log.py draws from wall_log.csv, for the run of wall_follow_p_log.py
in the sim2d model (KP 0.02, speed 0.3, 70 cm from the wall at the start, 15 seconds)."""
import os, tempfile
import matplotlib
matplotlib.use("Agg")
import wallsim

OUT = os.path.abspath("../images/racecar-neo-jp/6-8/fig1-log.png")
WALLS = [(100, -200, 100, 4000), (-100, -200, -100, 4000)]
ctrl = wallsim.P(0.02)
o, crashed = wallsim.simulate(WALLS, ctrl, 0.3, 15, x=30)
tmp = tempfile.mkdtemp()
with open(os.path.join(tmp, "wall_log.csv"), "w") as f:          # same format as wall_follow_p_log.py
    f.write("time,distance,error,angle\n")
    t = 0.0
    for row in o:
        t += wallsim.DT
        d, ang = row[5], row[4]
        f.write(f"{t:.3f},{d:.2f},{d - 50.0:.2f},{ang:.3f}\n")
# run the book's plot_log.py code as it is, in that folder, then keep its picture
code = open("plot_log_book.py").read().replace('fig.savefig("wall_log.png")', 'fig.savefig("wall_log.png", dpi=150)')
cwd = os.getcwd(); os.chdir(tmp)
exec(compile(code, "plot_log.py", "exec"), {"__name__": "__main__"})
os.chdir(cwd)
os.replace(os.path.join(tmp, "wall_log.png"), OUT)
print("ok", os.path.join(tmp, "wall_log.csv"))
