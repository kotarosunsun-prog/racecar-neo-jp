"""Figure for 5-13: a Pascal VOC XML annotation next to the image it describes."""
import os, cv2 as cv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NotoSansCJK-Regular" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = "../images/racecar-neo-jp/5-13"
img = cv.cvtColor(cv.imread("scene_5-11.png"), cv.COLOR_BGR2RGB)
fig = plt.figure(figsize=(10.4, 4.6), dpi=200)
ax = fig.add_axes([0.02, 0.08, 0.5, 0.84])
ax.imshow(img); ax.set_xticks([]); ax.set_yticks([])
for (x0, y0, x1, y1), col in [((104, 203, 177, 320), "#2F9E44"), ((405, 234, 446, 300), "#1C7ED6")]:
    ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=col, lw=2.4))
    ax.text(x0, y0 - 6, "cone", color="white", fontsize=9, bbox=dict(fc=col, ec="none", pad=1.2))
ax.plot([104], [203], "o", color="#E8590C", ms=6); ax.plot([177], [320], "o", color="#E8590C", ms=6)
ax.text(98, 222, "(xmin, ymin)", fontsize=8, ha="right", color="#D9480F")
ax.text(180, 335, "(xmax, ymax)", fontsize=8, color="#D9480F")
ax.set_title("1a2b3c4d-img_0000.jpg", fontsize=10)
xml = """<annotation>
  <folder>images</folder>
  <filename>1a2b3c4d-img_0000.jpg</filename>
  <size>
    <width>640</width>
    <height>480</height>
    <depth>3</depth>
  </size>
  <object>
    <name>cone</name>
    <bndbox>
      <xmin>104</xmin>
      <ymin>203</ymin>
      <xmax>177</xmax>
      <ymax>320</ymax>
    </bndbox>
  </object>
  <object>
    <name>cone</name>
    <bndbox> ... </bndbox>
  </object>
</annotation>"""
fig.text(0.55, 0.92, "Annotations/1a2b3c4d-img_0000.xml（一部を省略）", fontsize=10, va="top")
fig.text(0.55, 0.86, xml, fontsize=8.6, va="top", family="DejaVu Sans Mono",
         bbox=dict(boxstyle="round", fc="#F8F9FA", ec="#CED4DA"))
fig.savefig(f"{OUT}/fig2-voc.png", facecolor="white"); plt.close(fig)
