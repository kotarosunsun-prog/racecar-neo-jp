# How the Lab D instruction queue is consumed: three snapshots in time.
W, H = 920, 470
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans CJK JP, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
     '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#495057"/></marker></defs>']
steps = [("まっすぐ", 0.5, 0.0), ("右に曲がる", 0.5, 1.0), ("まっすぐ", 0.5, 0.0), ("右に曲がる", 0.5, 1.0)]
times0 = [1.5, 1.3, 1.5, 1.3]
snaps = [("ボタンを押した直後", [1.5, 1.3, 1.5, 1.3], 0),
         ("0.7秒後", [0.8, 1.3, 1.5, 1.3], 0),
         ("1.5秒後", [None, 1.3, 1.5, 1.3], 1)]
bx, bw, bh, gap = 190, 150, 92, 18
for r, (title, times, head) in enumerate(snaps):
    y = 30 + r * 140
    o.append(f'<text x="20" y="{y + 52}" font-size="16" font-weight="700" fill="#343A40">{title}</text>')
    for i, t in enumerate(times):
        x = bx + i * (bw + gap)
        if t is None:
            o.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="#F8F9FA" stroke="#CED4DA" stroke-dasharray="6 5" stroke-width="2"/>')
            o.append(f'<text x="{x + bw/2}" y="{y + 42}" font-size="14" fill="#ADB5BD" text-anchor="middle">取り除いた</text>')
            o.append(f'<text x="{x + bw/2}" y="{y + 66}" font-size="12" fill="#ADB5BD" text-anchor="middle">pop(0)</text>')
            continue
        is_head = (i == head)
        fill, stroke = ("#FFF4E6", "#FD7E14") if is_head else ("#F1F3F5", "#CED4DA")
        name, sp, an = steps[i]
        o.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="{3 if is_head else 2}"/>')
        o.append(f'<text x="{x + bw/2}" y="{y + 28}" font-size="15" font-weight="700" fill="#212529" text-anchor="middle">{name}</text>')
        col = "#D9480F" if is_head and t != times0[i] else "#495057"
        o.append(f'<text x="{x + bw/2}" y="{y + 56}" font-size="15" fill="{col}" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="{700 if col != "#495057" else 400}">残り {t:.1f} 秒</text>')
        o.append(f'<text x="{x + bw/2}" y="{y + 80}" font-size="12" fill="#868E96" text-anchor="middle" font-family="DejaVu Sans Mono, monospace">[{t:.1f}, {sp}, {an}]</text>')
        if is_head:
            o.append(f'<text x="{x + bw/2}" y="{y - 8}" font-size="13" fill="#E8590C" text-anchor="middle" font-weight="700">▼ 先頭：今これを実行中</text>')
    o.append(f'<text x="{bx + 4*(bw+gap) + 2}" y="{y + 52}" font-size="20" fill="#868E96">…</text>')
o.append(f'<text x="20" y="{H - 16}" font-size="14" fill="#495057">毎コマ：先頭の命令の speed と angle で走り、残り時間から経過時間を引く。残り時間が 0 以下になったら先頭を取り除き、次の命令へ。</text>')
o.append('</svg>')
open("fig4-1_queue.svg", "w").write("\n".join(o))
