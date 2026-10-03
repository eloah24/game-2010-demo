"""Demo gameplay - Vong 4 Lam bien hieu: two players draw, drawings are merged checkerboard-style, third guesses."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
from demo_common import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "demo_vong4.mp4"
random.seed(4)
COL_A, COL_B = (226, 70, 120), (110, 80, 200)

# ---------------- stroke shapes (unit square, y down) ----------------
def ell(cx, cy, rx, ry=None, a0=0, a1=360, rot=0, n=40):
    ry = rx if ry is None else ry
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        r = math.radians(rot)
        pts.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return pts

def petal(cx, cy, ang, ln, wd, n=16):
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
    side1 = [(cx + ux * ln * u + px * wd * math.sin(math.pi * u), cy + uy * ln * u + py * wd * math.sin(math.pi * u)) for u in [k / n for k in range(n + 1)]]
    side2 = [(cx + ux * ln * u - px * wd * math.sin(math.pi * u), cy + uy * ln * u - py * wd * math.sin(math.pi * u)) for u in [k / n for k in range(n, -1, -1)]]
    return side1 + side2

def wave(x0, x1, y, amp, cyc, n=40):
    return [(x0 + (x1 - x0) * k / n, y + amp * math.sin(2 * math.pi * cyc * k / n)) for k in range(n + 1)]

def ln(*pts): return list(pts)

WORDS = {
    "SEN": (
        [petal(.5, .62, a, .34, .11) for a in (-90, -55, -125, -20, -160)] + [ell(.5, .62, .05), wave(.08, .92, .84, .03, 3)],
        [petal(.5, .55, -90, .32, .12), petal(.5, .55, -125, .27, .1), petal(.5, .55, -55, .27, .1),
         ln((.5, .55), (.52, .78)), ell(.32, .82, .18, .05), ell(.74, .86, .13, .04)]),
    "HỚN HỞ": (
        [ell(.5, .5, .36), ln((.33, .43), (.38, .36), (.43, .43)), ln((.57, .43), (.62, .36), (.67, .43)),
         ell(.5, .55, .2, .16, 10, 170), ell(.3, .6, .04), ell(.7, .6, .04)],
        [ell(.5, .24, .09), ln((.5, .33), (.5, .6)), ln((.5, .42), (.3, .22)), ln((.5, .42), (.7, .22)),
         ln((.5, .6), (.36, .78)), ln((.5, .6), (.64, .78)), ell(.5, .25, .05, .04, 20, 160),
         ln((.16, .88), (.36, .88)), ln((.64, .88), (.84, .88)), ln((.18, .2), (.24, .28)), ln((.82, .2), (.76, .28))]),
    "BÁNH MÌ": (
        [ell(.5, .5, .4, .13, rot=-25), ln((.33, .5), (.4, .4)), ln((.45, .55), (.52, .45)), ln((.58, .6), (.64, .5))],
        [ell(.5, .5, .38, .2, 180, 360), ln((.12, .5), (.88, .5)), wave(.14, .86, .55, .025, 5), wave(.14, .86, .6, .02, 4),
         ell(.5, .63, .38, .12, 0, 180), ln((.12, .63), (.88, .63)), petal(.3, .56, -150, .12, .04)]),
}

def render(strokes, p, size, color, wdt=None):
    """Draw strokes revealed up to fraction p. Returns (image, tip)."""
    im = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    wdt = wdt or max(3, size // 38)
    segs = []
    for s in strokes:
        for a, b in zip(s, s[1:]):
            segs.append((a, b, math.dist(a, b)))
    total = sum(x[2] for x in segs)
    left = total * clamp(p)
    tip = None
    for a, b, l in segs:
        if left <= 0: break
        u = min(1, left / l) if l > 0 else 1
        e = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        A = (a[0] * size, a[1] * size); E = (e[0] * size, e[1] * size)
        d.line([A, E], fill=color, width=wdt)
        r = wdt / 2
        d.ellipse((E[0] - r, E[1] - r, E[0] + r, E[1] + r), fill=color)
        d.ellipse((A[0] - r, A[1] - r, A[0] + r, A[1] + r), fill=color)
        left -= l; tip = E
    return im, tip

def merged(word, size, m=1.0):
    """Checkerboard merge: dark cells from A's drawing, light cells from B's. m = merge animation progress."""
    a, _ = render(WORDS[word][0], 1, size, COL_A)
    b, _ = render(WORDS[word][1], 1, size, COL_B)
    out = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    c = size / 4
    order = sorted(((r, cc) for r in range(4) for cc in range(4)), key=lambda x: x[0] * 4 + x[1])
    for k, (r, cc) in enumerate(order):
        src = a if (r + cc) % 2 == 0 else b
        tk = clamp(m * 1.6 - k / 16 * 0.6)
        if tk <= 0: continue
        tile = src.crop((int(cc * c), int(r * c), int((cc + 1) * c), int((r + 1) * c)))
        if (r + cc) % 2 == 0:
            tint = Image.new("RGBA", tile.size, (255, 225, 236, 255))
            tint.alpha_composite(Image.composite(tile, tint, tile.convert("L").point(lambda v: 255 if v < 250 else 0)))
            tile = tint
        dx = (-1 if (r + cc) % 2 == 0 else 1) * (1 - ease(tk)) * size * 0.7
        out.alpha_composite(tile, (int(cc * c + dx), int(r * c)))
    d = ImageDraw.Draw(out)
    for k in range(1, 4):
        d.line((k * c, 0, k * c, size), fill=(220, 210, 230), width=1)
        d.line((0, k * c, size, k * c), fill=(220, 210, 230), width=1)
    return out

# ---------------- script ----------------
TURNS = [
    dict(word="SEN", cat="Tên hoa", limit=60, left=14, intro=1.6, draw=9.0, merge=3.4,
         guesses=[("ĐÀO", False), ("SEN", True)], gtime=7.0, pa=0.95, pb=1.0),
    dict(word="HỚN HỞ", cat="Tính từ", limit=90, left=21, intro=1.3, draw=5.0, merge=2.6,
         guesses=[("HỚN HỞ", True)], gtime=4.2, pa=1.0, pb=0.9),
    dict(word="BÁNH MÌ", cat="Danh từ", limit=75, left=9, intro=1.3, draw=5.0, merge=2.6,
         guesses=[("BÁNH BAO", False), ("BÁNH MÌ", True)], gtime=6.2, pa=1.0, pb=1.0),
]
MAXG, WORD_PTS, BONUS = 3, 10, 5
for tn in TURNS:
    rem = MAXG - len(tn["guesses"])
    tn["pts"] = (WORD_PTS, BONUS * rem, rem)

T_TITLE, T_ROLES = 3.5, 7.0
t = T_TITLE + T_ROLES
for tn in TURNS:
    tn["t0"] = t
    t += tn["intro"] + tn["draw"] + tn["merge"] + tn["gtime"]
T_SIGN = t
TOTAL = T_SIGN + 7.0
NAME = ["SEN", "HỚN HỞ", "BÁNH MÌ"]

def blanks(word, solved):
    return "   ".join(" ".join(ch if solved else "_" for ch in w) for w in word.split())

def turn_state(T):
    for k, tn in enumerate(TURNS):
        end = tn["t0"] + tn["intro"] + tn["draw"] + tn["merge"] + tn["gtime"]
        if T < end:
            a = T - tn["t0"]
            if a < tn["intro"]: return k, "intro", a
            a -= tn["intro"]
            if a < tn["draw"]: return k, "draw", a
            a -= tn["draw"]
            if a < tn["merge"]: return k, "merge", a
            return k, "guess", a - tn["merge"]
    return None, "sign", T - T_SIGN

def guess_state(tn, a):
    """-> list of (text, ok, shown_chars, resolved) for guesses so far."""
    out = []; tt = 0.3
    for g, ok in tn["guesses"]:
        if a < tt: break
        typed = clamp((a - tt) / 1.1)
        n = int(len(g) * typed + 0.999) if typed < 1 else len(g)
        resolved = a >= tt + 1.4
        out.append((g, ok, n, resolved))
        tt += 2.3
    return out

def score_before(k): return sum(sum(TURNS[j]["pts"][:2]) for j in range(k))

def solved_words(k, phase, a):
    s = [True] * k + [False] * (3 - k)
    if phase == "guess":
        gs = guess_state(TURNS[k], a)
        if gs and gs[-1][1] and gs[-1][3]: s[k] = True
    return s

BG = make_bg(None, panel_fill=(255, 248, 236), outline=PINK)

def sign_bar(im, solved):
    d = ImageDraw.Draw(im)
    labels = ["Tên hoa", "Tính từ", "Danh từ"]
    for k in range(3):
        x0 = 60 + k * 244
        ok = solved[k]
        d.rounded_rectangle((x0, 118, x0 + 210, 178), 16, fill=(255, 226, 236) if ok else WHITE, outline=PINK_D if ok else LAV, width=3)
        text_c(d, (x0 + 105, 132), labels[k], font(SEMI, 13), LAV_D)
        text_c(d, (x0 + 105, 156), NAME[k] if ok else "?", font(BLACK, 24), PINK_D if ok else (190, 180, 200))
        if k < 2:
            text_c(d, (x0 + 227, 148), "+", font(BLACK, 26), LAV_D)

def big_screen(im, k, phase, a):
    tn = TURNS[k]
    d = ImageDraw.Draw(im)
    sign_bar(im, solved_words(k, phase, a))
    d = ImageDraw.Draw(im)
    if phase == "intro":
        sc = ease(a / 0.4)
        text_c(d, (410, 380), f"Lượt {k + 1}/3 · {tn['cat']}", font(BLACK, int(30 + 22 * sc)), PINK_D)
        text_c(d, (410, 450), f"{tn['limit']} giây vẽ · Hoa đoán", font(BOLD, 26), LAV_D)
        return
    if phase == "draw":
        p = a / tn["draw"]
        for j, (who, col) in enumerate((("Lan", COL_A), ("Mai", COL_B))):
            x0 = 80 + j * 350
            shadow_box(im, (x0, 205, x0 + 310, 560), 22, WHITE, outline=PCOL[j], width=3)
            img, _ = render(WORDS[tn["word"]][j], p * (tn["pa"] if j == 0 else tn["pb"]), 270, col)
            img = img.filter(ImageFilter.GaussianBlur(9))
            im.alpha_composite(img, (x0 + 20, 220))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((x0 + 70, 365, x0 + 240, 405), 20, fill=(255, 255, 255, 220))
            text_c(d, (x0 + 155, 385), f"{who} đang vẽ...", font(BOLD, 18), INK)
            paste_c(im, emoji("✏️", 30), x0 + 282, 530)
        d = ImageDraw.Draw(im)
        text_c(d, (410, 600), "Hoa (người đoán) chỉ thấy số chữ cái:", font(SEMI, 20), INK)
        text_c(d, (410, 648), blanks(tn["word"], False), font(BLACK, 34), LAV_D)
        return
    if phase == "merge":
        m = clamp(a / (tn["merge"] - 0.6))
        img = merged(tn["word"], 360, m)
        shadow_box(im, (228, 200, 592, 564), 18, WHITE, outline=LAV, width=3)
        im.alpha_composite(img, (230, 202))
        d = ImageDraw.Draw(im)
        text_c(d, (410, 590), "Ghép xen kẽ 16 ô", font(BLACK, 24), PINK_D)
        d.rounded_rectangle((60, 340, 210, 420), 16, fill=(255, 226, 236))
        text_c(d, (135, 365), "Ô hồng", font(BOLD, 18), COL_A); text_c(d, (135, 395), "← tranh Lan", font(REG, 16), INK)
        d.rounded_rectangle((610, 340, 760, 420), 16, fill=(236, 230, 252))
        text_c(d, (685, 365), "Ô trắng", font(BOLD, 18), COL_B); text_c(d, (685, 395), "tranh Mai →", font(REG, 16), INK)
        text_c(d, (410, 645), blanks(tn["word"], False), font(BLACK, 34), LAV_D)
        return
    # guess
    img = merged(tn["word"], 320, 1)
    shadow_box(im, (68, 205, 392, 529), 18, WHITE, outline=LAV, width=3)
    im.alpha_composite(img, (70, 207))
    d = ImageDraw.Draw(im)
    gs = guess_state(tn, a)
    solved = bool(gs and gs[-1][1] and gs[-1][3])
    text_c(d, (230, 575), blanks(tn["word"], solved), font(BLACK, 34), PINK_D if solved else LAV_D)
    text_c(d, (590, 220), "Hoa đoán:", font(BLACK, 24), INK)
    used = sum(1 for g in gs if g[3])
    for j in range(MAXG):
        paste_c(im, emoji("💖" if j >= used else "🤍", 26), 520 + j * 34, 262)
    d = ImageDraw.Draw(im)
    text_c(d, (590, 290), f"còn {MAXG - used}/{MAXG} lượt đoán", font(REG, 15), LAV_D)
    for j, (g, ok, n, res) in enumerate(gs):
        y = 320 + j * 64
        col = (MINT_D if ok else RED) if res else LAV
        d.rounded_rectangle((440, y, 740, y + 52), 26, fill=WHITE, outline=col, width=3)
        text_c(d, (470, y + 26), g[:n] + ("|" if not res and int(a * 3) % 2 == 0 else ""), font(BLACK, 26), INK, anchor="lm")
        if res:
            paste_c(im, emoji("✅" if ok else "❌", 30), 712, y + 26)
            d = ImageDraw.Draw(im)
    if solved:
        ta = a - (0.3 + 2.3 * (len(tn["guesses"]) - 1) + 1.4)
        wp, bp, rem = tn["pts"]
        al = clamp(ta / 0.3)
        d.rounded_rectangle((440, 470, 740, 560), 20, fill=(236, 250, 240), outline=MINT_D, width=3)
        text_c(d, (590, 497), f"+{wp} đoán đúng", font(BLACK, 24), MINT_D)
        text_c(d, (590, 535), f"+{bp} thưởng (còn {rem} lượt)", font(BOLD, 20), PINK_D)
        if ta < 1.2:
            for s in range(6):
                ang = s * math.pi / 3 + ta * 2
                paste_c(im, emoji("✨", 22), 230 + math.cos(ang) * (60 + ta * 120), 575 + math.sin(ang) * (20 + ta * 40), alpha=1 - ta / 1.2)

def phones(im, k, phase, a):
    tn = TURNS[k]
    for j in range(2):
        rect = phone_shell(im, j, "Người vẽ")
        sx0, sy0, sx1, sy1 = rect
        d = ImageDraw.Draw(im)
        cx = (sx0 + sx1) / 2
        d.rounded_rectangle((sx0 + 8, sy0 + 50, sx1 - 8, sy0 + 82), 10, fill=(255, 226, 236) if j == 0 else (236, 230, 252))
        text_c(d, (cx, sy0 + 59), "Từ khóa", font(REG, 10), INK)
        text_c(d, (cx, sy0 + 73), tn["word"], fit_font(d, tn["word"], BLACK, 15, 100), COL_A if j == 0 else COL_B)
        p = clamp(a / tn["draw"]) * (tn["pa"] if j == 0 else tn["pb"]) if phase == "draw" else (0 if phase == "intro" else 1)
        img, tip = render(WORDS[tn["word"]][j], p, 102, COL_A if j == 0 else COL_B, wdt=3)
        im.alpha_composite(img, (int(sx0 + 6), int(sy0 + 92)))
        d = ImageDraw.Draw(im)
        d.rectangle((sx0 + 6, sy0 + 92, sx0 + 108, sy0 + 194), outline=(220, 210, 230))
        if phase == "draw" and tip:
            paste_c(im, emoji("✏️", 22), sx0 + 6 + tip[0] + 8, sy0 + 92 + tip[1] - 8)
        d = ImageDraw.Draw(im)
        for c_i, c in enumerate([COL_A if j == 0 else COL_B, (40, 40, 40), (250, 190, 40), (60, 180, 120)]):
            d.ellipse((sx0 + 12 + c_i * 25, sy0 + 202, sx0 + 30 + c_i * 25, sy0 + 220), fill=c,
                      outline=INK if c_i == 0 else None, width=2)
        submitted = phase in ("merge", "guess") or (phase == "draw" and a > tn["draw"] - 0.6)
        pr = phase == "draw" and tn["draw"] - 0.6 < a < tn["draw"] - 0.4
        btn(d, im, (sx0 + 12, sy0 + 230, sx1 - 12, sy0 + 262), pr, (190, 190, 200) if submitted else MINT_D,
            label="ĐÃ NỘP" if submitted else "NỘP", fsize=14)
    # guesser
    sx0, sy0, sx1, sy1 = phone_shell(im, 2, "Người đoán")
    d = ImageDraw.Draw(im)
    cx = (sx0 + sx1) / 2
    d.rounded_rectangle((sx0 + 8, sy0 + 50, sx1 - 8, sy0 + 82), 10, fill=(232, 247, 238))
    text_c(d, (cx, sy0 + 59), "Số chữ cái", font(REG, 10), INK)
    text_c(d, (cx, sy0 + 73), blanks(tn["word"], False).replace("   ", "  "), fit_font(d, "x", BLACK, 14, 100), MINT_D)
    if phase in ("intro", "draw"):
        paste_c(im, emoji("⏳", 40), cx, sy0 + 140)
        d = ImageDraw.Draw(im)
        text_c(d, (cx, sy0 + 186), "Chờ đồng đội", font(BOLD, 13), INK)
        text_c(d, (cx, sy0 + 204), "vẽ và nộp...", font(BOLD, 13), INK)
        text_c(d, (cx, sy0 + 236), "Không thấy từ khóa", font(REG, 11), LAV_D)
        return
    img = merged(tn["word"], 102, clamp(a / (tn["merge"] - 0.6)) if phase == "merge" else 1)
    im.alpha_composite(img, (int(sx0 + 6), int(sy0 + 92)))
    d = ImageDraw.Draw(im)
    d.rectangle((sx0 + 6, sy0 + 92, sx0 + 108, sy0 + 194), outline=(220, 210, 230))
    gs = guess_state(tn, a) if phase == "guess" else []
    cur = ""
    if gs:
        g, ok, n, res = gs[-1]
        cur = g[:n] if not res else ""
    d.rounded_rectangle((sx0 + 8, sy0 + 202, sx1 - 8, sy0 + 228), 8, fill=WHITE, outline=MINT_D, width=2)
    text_c(d, (sx0 + 14, sy0 + 215), cur + ("|" if int(a * 3) % 2 == 0 else ""), fit_font(d, cur or "x", BOLD, 14, 90), INK, anchor="lm")
    pr = bool(gs) and not gs[-1][3] and gs[-1][2] == len(gs[-1][0])
    btn(d, im, (sx0 + 12, sy0 + 236, sx1 - 12, sy0 + 264), pr, MINT_D, label="ĐOÁN", fsize=14)

def bubbles_for(T):
    out = []
    b0 = TURNS[0]
    tg = b0["t0"] + b0["intro"] + b0["draw"] + b0["merge"]
    out.append((2, "Hoa đào hả?", tg + 0.1, 1.4))
    out.append((0, "Không phải đâu!", tg + 1.8, 1.2))
    out.append((2, "À, hoa sen!", tg + 2.5, 1.4))
    b2 = TURNS[2]
    tg2 = b2["t0"] + b2["intro"] + b2["draw"] + b2["merge"]
    out.append((1, "Gần đúng rồi!", tg2 + 1.8, 1.3))
    return out

def cheers_for():
    out = []
    for tn in TURNS:
        tg = tn["t0"] + tn["intro"] + tn["draw"] + tn["merge"]
        tt = 0.3
        for g, ok in tn["guesses"]:
            ems = ["👏", "💖", "🎉", "😍"] if ok else ["😂", "🙈"]
            out += [(tg + tt + 1.4 + q * 0.15, e) for q, e in enumerate(ems)]
            tt += 2.3
    return out
BUBBLES, CHEERS = bubbles_for(0), cheers_for()

def sign_scene(a):
    im = gradient(W, H, (255, 214, 230), (222, 206, 255))
    for q in range(26):
        x = (q * 131) % W + math.sin(a * 2 + q) * 20
        y = (a * 150 + q * 77) % (H + 60) - 30
        paste_c(im, emoji(["🌸", "🎉", "✨", "💐"][q % 4], 30), x, y, alpha=0.7)
    d = ImageDraw.Draw(im)
    text_c(d, (640, 62), "Tên cửa hàng của Đội 2", font(BLACK, 34), PINK_D)
    # shop facade
    shadow_box(im, (300, 120, 980, 610), 20, (255, 250, 245), outline=PINK_D, width=4)
    d = ImageDraw.Draw(im)
    for q in range(10):
        x0 = 300 + q * 68
        d.rectangle((x0, 120, x0 + 68, 190), fill=PINK if q % 2 == 0 else WHITE)
        d.pieslice((x0, 160, x0 + 68, 220), 0, 180, fill=PINK if q % 2 == 0 else WHITE)
    sa = ease(a / 0.6)
    sy = 250 - (1 - sa) * 30
    d.rounded_rectangle((350, sy, 930, sy + 120), 20, fill=CREAM, outline=(200, 150, 90), width=6)
    words = NAME
    shown = clamp((a - 0.5) / 1.8) * 3
    x = 640
    full = "  ".join(words)
    f = fit_font(d, full, BLACK, 50, 540)
    tw = d.textlength(full, font=f)
    xx = 640 - tw / 2
    for q, w in enumerate(words):
        if shown > q:
            al = int(255 * clamp(shown - q))
            d.text((xx, sy + 60), w, font=f, fill=(*PINK_D, al), anchor="lm")
        xx += d.textlength(w + "  ", font=f)
    d.rectangle((370, 400, 600, 600), fill=(220, 240, 255), outline=LAV_D, width=4)
    d.rectangle((680, 400, 910, 600), fill=(255, 236, 244), outline=PINK_D, width=4)
    paste_c(im, emoji("🪷", 70), 485, 500)
    paste_c(im, emoji("🥖", 70), 795, 500)
    for q, em in enumerate(["🌷", "🌸", "🌼", "🌷"]):
        paste_c(im, emoji(em, 44), 330 + q * 210 + (40 if q > 1 else 0), 630)
    if a > 2.4:
        shadow_box(im, (430, 650, 850, 706), 28, WHITE)
        d = ImageDraw.Draw(im)
        tot = score_before(3)
        text_c(d, (640, 678), f"Điểm vòng 4: {tot} · 3/3 từ đoán đúng", font(BLACK, 24), MINT_D)
    return im

def frame(T):
    if T < T_TITLE:
        return title_scene(T, "Demo gameplay · Vòng 4 — Làm biển hiệu", "🪧", "Vẽ – ghép – đoán để đặt tên cửa hàng thật hài hước")
    if T < T_TITLE + T_ROLES:
        return roles_scene(T - T_TITLE, "Tên hoa + Tính từ + Danh từ", "3 lượt, mỗi lượt một từ — hai người vẽ, một người đoán",
                           [("A", "Lan", "Người vẽ", "🎨", "Thấy từ khóa, vẽ tranh riêng", PINK_D),
                            ("B", "Mai", "Người vẽ", "🖍️", "Thấy từ khóa, vẽ tranh riêng", LAV_D),
                            ("C", "Hoa", "Người đoán", "🤔", "Chỉ thấy số chữ cái + ảnh ghép", MINT_D)],
                           "Hai tranh được ghép xen kẽ 16 ô như bàn cờ", "Đoán đúng +10 · còn lượt đoán thì thưởng thêm · thời gian vẽ 60/90/75 giây")
    k, phase, a = turn_state(T)
    if phase == "sign":
        return sign_scene(a)
    tn = TURNS[k]
    im = BG.copy()
    if phase == "draw":
        rem = tn["limit"] - (tn["limit"] - tn["left"]) * clamp(a / tn["draw"])
        timer, warn, tag = fmt(rem), rem <= 10, "tua nhanh x6"
    elif phase == "intro":
        timer, warn, tag = fmt(tn["limit"]), False, None
    else:
        timer, warn, tag = "Đoán", False, None
    sc = score_before(k)
    if phase == "guess":
        gs = guess_state(tn, a)
        if gs and gs[-1][1] and gs[-1][3]:
            sc += sum(tn["pts"][:2])
    header(im, "VÒNG 4 · LÀM BIỂN HIỆU", "🪧", timer, warn=warn, right_val=str(sc), tag=tag)
    big_screen(im, k, phase, a)
    draw_cheers(im, CHEERS, T)
    phones(im, k, phase, a)
    draw_bubbles(im, BUBBLES, T)
    return im

encode(OUT, TOTAL, frame)
