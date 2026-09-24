"""
iou_nms.py
2つの枠の重なり具合（IoU）と、重なった枠を1つにまとめる NMS を計算する。
枠は (左の x, 上の y, 右の x, 下の y) の画素で表す。
"""


def iou(a, b):
    """2つの枠の IoU（重なりの面積 ÷ 2つを合わせた面積）"""
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    overlap = max(0, right - left) * max(0, bottom - top)     # 重なった部分の面積
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return overlap / (area_a + area_b - overlap)


def nms(boxes, scores, iou_threshold=0.5):
    """自信の高い順に選び、選んだ枠と大きく重なる枠は捨てる"""
    order = sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
    keep = []
    for i in order:
        if all(iou(boxes[i], boxes[k]) < iou_threshold for k in keep):
            keep.append(i)
    return keep


# 同じコーンに3つの枠が重なって出て、別のコーンに1つ出た、という例
boxes = [(100, 200, 180, 320), (108, 196, 190, 316), (96, 210, 176, 330), (400, 230, 450, 300)]
scores = [0.91, 0.84, 0.62, 0.77]

print(f"枠0 と 枠1 の IoU：{iou(boxes[0], boxes[1]):.2f}")
print(f"枠0 と 枠3 の IoU：{iou(boxes[0], boxes[3]):.2f}")
print("NMS で残った枠：", nms(boxes, scores))
