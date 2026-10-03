"""Demo gameplay - Vong 2 Be cay: 3 players carry one pot; too far apart -> pot drops."""
import math, random, sys
from PIL import Image, ImageDraw
from demo_common import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "demo_vong2.mp4"
random.seed(2)

PATH = [(110, 600), (260, 600), (330, 520), (330, 400), (470, 330), (600, 330), (650, 235), (690, 190)]
SEG = []
cum = [0.0]
for a, b in zip(PATH, PATH[1:]):
    l = math.dist(a, b); SEG.append((a, b, l)); cum.append(cum[-1] + l)
L = cum[-1]
V, THR, PAUSE, PENALTY = 40.0, 110.0, 3.4, 3

def at(s):
    s = clamp(s, 0, L - 0.01)
    for k, (a, b, l) in enumerate(SEG):
        if s <= cum[k + 1]:
            u = (s - cum[k]) / l
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
    return PATH[-1], (0, -1)

S_DROP = cum[4] + 70
P_DROP, D_DROP = at(S_DROP)
PERP = (D_DROP[1], -D_DROP[0])            # left-ish/up side of the path
_pt, _ = at(S_DROP - 40)
TREE = (_pt[0] + PERP[0] * 52, _pt[1] + PERP[1] * 52)
OFFS = [(-38, 26), (38, 26), (0, -42)]
FACES = ["👩", "👧", "👱"]

# ---------------- static field ----------------
BG = make_bg("SÂN CỦA ĐỘI 2", panel_fill=(232, 247, 228))
d = ImageDraw.Draw(BG)
d.line(PATH, fill=(246, 232, 205), width=84, joint="curve")
for p in (PATH[0], PATH[-1]):
    d.ellipse((p[0] - 42, p[1] - 42, p[0] + 42, p[1] + 42), fill=(246, 232, 205))
for k in range(0, int(L), 46):
    (x, y), _ = at(k)
    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(232, 212, 180))
d.ellipse((470, 485, 600, 560), fill=(170, 215, 245), outline=(120, 180, 225), width=3)
paste_c(BG, emoji("🦆", 34), 545, 518)
deco = [("⛲", 175, 505, 72), ("🌳", 120, 300, 80), ("🪨", 235, 330, 40), ("🪑", 455, 450, 48), ("🌺", 700, 430, 44),
        ("🌷", 735, 600, 40), ("🪨", 560, 225, 40), ("🌳", TREE[0], TREE[1], 74), ("🌼", 640, 640, 36), ("🌳", 410, 220, 60)]
for em, x, y, s in deco:
    paste_c(BG, emoji(em, s), x, y)
d = ImageDraw.Draw(BG)
gx, gy = PATH[-1]
d.ellipse((gx - 46, gy - 46, gx + 46, gy + 46), fill=(255, 214, 230), outline=PINK_D, width=4)
paste_c(BG, emoji("🏁", 40), gx, gy - 4)
d.rounded_rectangle((gx - 92, gy + 50, gx + 78, gy + 80), 15, fill=WHITE, outline=PINK_D, width=2)
text_c(d, (gx - 7, gy + 65), "Điểm tập kết", font(BOLD, 17), PINK_D)
sx, sy = PATH[0]
d.rounded_rectangle((sx - 50, sy + 36, sx + 50, sy + 62), 13, fill=WHITE, outline=MINT_D, width=2)
text_c(d, (sx, sy + 49), "Xuất phát", font(BOLD, 15), MINT_D)
d.rounded_rectangle((60, 140, 330, 172), 16, fill=(255, 255, 255, 200))
text_c(d, (195, 156), "Đứng gần nhau thì chậu mới đi", font(SEMI, 15), INK)

# ---------------- simulation ----------------
class Sim:
    def __init__(self):
        self.s = 0.0; self.t_drop = None; self.drop_pos = None; self.done_t = None
        self.prev = None; self.vel = [(0, 0)] * 3
        self.bubbles = []; self.cheers = []; self.said = set()

    def extra(self, t):
        if self.t_drop is None:
            return clamp((self.s - (S_DROP - 85)) / 85) * 115
        return 115 * (1 - clamp((t - self.t_drop - 0.9) / 1.0))

    def paused(self, t):
        return self.t_drop is not None and t < self.t_drop + PAUSE

    def players(self, t):
        c, _ = at(self.s)
        e = self.extra(t)
        out = []
        for i, (ox, oy) in enumerate(OFFS):
            wob = math.sin(t * 7 + i * 2) * 2.5
            x, y = c[0] + ox, c[1] + oy + wob
            if i == 2:
                x += PERP[0] * e; y += PERP[1] * e
            out.append((x, y))
        return out

    def maxdist(self, ps):
        return max(math.dist(ps[a], ps[b]) for a, b in ((0, 1), (0, 2), (1, 2)))

    def say(self, key, i, s, t, dur=1.8):
        if key not in self.said:
            self.said.add(key); self.bubbles.append((i, s, t, dur))

    def step(self, t, dt):
        if self.done_t is not None: return
        if not self.paused(t):
            self.s = min(L, self.s + V * dt * clamp(t / 0.6, 0.2, 1))
        ps = self.players(t)
        if self.prev:
            self.vel = [((p[0] - q[0]) / dt, (p[1] - q[1]) / dt) for p, q in zip(ps, self.prev)]
        self.prev = ps
        if self.t_drop is None and self.maxdist(ps) > THR:
            self.t_drop = t; self.drop_pos = at(self.s)[0]
            self.cheers += [(t + 0.2, "😱"), (t + 0.4, "😂"), (t + 0.7, "🙈")]
            self.say("drop", 0, "Ơ chậu rơi rồiii!", t + 0.1)
        if self.s > S_DROP - 110: self.say("go", 2, "Em vòng bên này nhé!", t, 1.6)
        if self.t_drop and t > self.t_drop + 1.2: self.say("hot", 1, "Hốt nhanh nào!", t, 1.5)
        if self.s > L - 120: self.say("near", 1, "Sắp tới rồi!", t, 1.6)
        if self.s >= L:
            self.done_t = t
            self.cheers += [(t + k * 0.15, em) for k, em in enumerate(["🎉", "👏", "💖", "🥳", "🌸"])]

    def elapsed(self, t):
        return t + (PENALTY if self.t_drop is not None and t >= self.t_drop else 0)

def dist_col(dd):
    return (60, 190, 120) if dd < 88 else ((240, 180, 40) if dd < THR else RED)

def draw_field(im, sim, t):
    d = ImageDraw.Draw(im)
    ps = sim.players(t)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for a, b in ((0, 1), (0, 2), (1, 2)):
        dd = math.dist(ps[a], ps[b])
        od.line([ps[a], ps[b]], fill=(*dist_col(dd), 220), width=6)
    im.alpha_composite(ov)
    paused = sim.paused(t)
    c, _ = at(sim.s)
    if sim.t_drop is not None and paused:
        a = t - sim.t_drop
        x, y = sim.drop_pos
        # spilled soil pile shrinking while the team sweeps it up
        k = clamp((a - 0.5) / (PAUSE - 0.9))
        for j in range(14):
            ang = j * 2.4
            rad = 12 + (j % 5) * 7
            r = 7 * (1 - k)
            if r > 0.5:
                px, py = x + math.cos(ang) * rad, y + 18 + math.sin(ang) * rad * 0.5
                d.ellipse((px - r, py - r, px + r, py + r), fill=(150, 100, 70))
        if a < 0.6:
            pot = emoji("🪴", 52).rotate(-a * 200, expand=True)
            paste_c(im, pot, x + a * 30, y - 20 + a * 50)
        else:
            paste_c(im, emoji("🪴", 46).rotate(-100, expand=True), x + 22, y + 12, alpha=0.9)
            paste_c(im, emoji("🧹", 40), x - 18 + math.sin(t * 14) * 12, y + 6)
        d = ImageDraw.Draw(im)
        bx0 = x - 80
        d.rounded_rectangle((bx0, y - 92, bx0 + 160, y - 54), 19, fill=WHITE, outline=(150, 100, 70), width=3)
        d.rounded_rectangle((bx0 + 6, y - 86, bx0 + 6 + 148 * k, y - 60), 13, fill=(214, 170, 120))
        text_c(d, (x, y - 73), "Hốt đất...", font(BOLD, 17), INK)
    for i, p in enumerate(ps):
        d.ellipse((p[0] - 22, p[1] - 22, p[0] + 22, p[1] + 22), fill=WHITE, outline=PCOL[i], width=4)
        paste_c(im, emoji(FACES[i], 30), p[0], p[1])
        d = ImageDraw.Draw(im)
        d.ellipse((p[0] + 10, p[1] - 26, p[0] + 28, p[1] - 8), fill=PCOL[i])
        text_c(d, (p[0] + 19, p[1] - 17), "ABC"[i], font(BLACK, 11), WHITE)
    if not paused:
        cx = sum(p[0] for p in ps) / 3; cy = sum(p[1] for p in ps) / 3
        if sim.t_drop is not None and t - sim.t_drop - PAUSE < 0.6:
            sp = t - sim.t_drop - PAUSE
            for j in range(6):
                ang = j * math.pi / 3 + sp * 3
                paste_c(im, emoji("✨", 18), cx + math.cos(ang) * (20 + sp * 50), cy + math.sin(ang) * (20 + sp * 50), alpha=1 - sp / 0.6)
        paste_c(im, emoji("🪴", 52), cx, cy - 6 + math.sin(t * 10) * 2)
    if sim.t_drop is not None and 0 <= t - sim.t_drop < 1.6:
        a = t - sim.t_drop
        d = ImageDraw.Draw(im)
        x, y = sim.drop_pos
        text_c(d, (x, y + 70 - a * 10), "Rơi chậu! Phạt +3s", font(BLACK, 26), WHITE, stroke_width=4, stroke_fill=RED)

def draw_phones(im, sim, t):
    ps = sim.players(t)
    paused = sim.paused(t)
    for i in range(3):
        rect = phone_shell(im, i, "Tự di chuyển")
        sx0, sy0, sx1, sy1 = rect
        d = ImageDraw.Draw(im)
        cx = (sx0 + sx1) / 2
        if paused and t - sim.t_drop > 0.6:
            k = clamp((t - sim.t_drop - 0.6) / (PAUSE - 0.9))
            p = int(t * 7 + i) % 2 == 0
            btn(d, im, (sx0 + 10, sy0 + 70, sx1 - 10, sy0 + 190), p, (214, 170, 120) if not p else (170, 120, 80))
            paste_c(im, emoji("🧹", 40), cx, sy0 + 115 + (4 if p else 0))
            d = ImageDraw.Draw(im)
            text_c(d, (cx, sy0 + 165 + (4 if p else 0)), "HỐT ĐẤT", font(BLACK, 16), WHITE)
            text_c(d, (cx, sy0 + 215), "Bấm liên tục!", font(BOLD, 13), INK)
            d.rounded_rectangle((sx0 + 12, sy0 + 232, sx1 - 12, sy0 + 248), 8, fill=(240, 230, 220))
            d.rounded_rectangle((sx0 + 12, sy0 + 232, sx0 + 12 + (sx1 - sx0 - 24) * k, sy0 + 248), 8, fill=(214, 170, 120))
            continue
        jy = sy0 + 135
        d.ellipse((cx - 46, jy - 46, cx + 46, jy + 46), fill=(246, 238, 250), outline=PCOL[i], width=3)
        for ang in range(0, 360, 90):
            ax, ay = cx + math.cos(math.radians(ang)) * 34, jy + math.sin(math.radians(ang)) * 34
            tri(d, ax, ay, 5, {0: "right", 90: "down", 180: "left", 270: "up"}[ang], (200, 180, 220))
        vx, vy = sim.vel[i] if not paused else (0, 0)
        sp = math.hypot(vx, vy)
        kx, ky = (vx / sp * 22, vy / sp * 22) if sp > 8 else (0, 0)
        d.ellipse((cx + kx - 22, jy + ky - 22, cx + kx + 22, jy + ky + 22), fill=PCOL[i])
        d.ellipse((cx + kx - 12, jy + ky - 16, cx + kx + 4, jy + ky - 6), fill=(255, 255, 255, 90))
        far = max(math.dist(ps[i], ps[j]) for j in range(3) if j != i)
        col = dist_col(far)
        lab = "Gần đội" if far < 88 else ("Hơi xa!" if far < THR else "Xa quá!")
        d.rounded_rectangle((sx0 + 12, sy0 + 205, sx1 - 12, sy0 + 237), 16, fill=col)
        text_c(d, (cx, sy0 + 221), lab, font(BLACK, 15), WHITE)
        if far >= 88:
            text_c(d, (cx, sy0 + 256), "rung nhẹ ~", font(REG, 11), RED)
    draw_bubbles(im, sim.bubbles, t)

def game_frame(sim, t, locked=False):
    im = BG.copy()
    el = sim.elapsed(t)
    header(im, "VÒNG 2 · BÊ CÂY", "🪴", fmt(el), right_label="MỐC", right_val="2:30")
    if sim.t_drop is not None and 0 <= t - sim.t_drop < 1.6:
        d = ImageDraw.Draw(im)
        a = t - sim.t_drop
        text_c(d, (1010, 96 - a * 8), "+3s", font(BLACK, 26), RED, stroke_width=3, stroke_fill=WHITE)
    draw_field(im, sim, t)
    draw_cheers(im, sim.cheers, t)
    draw_phones(im, sim, t)
    return im

# ---------------- timeline ----------------
T_TITLE, T_ROLES, T_COUNT = 3.5, 6.0, 3.0
T_GAME0 = T_TITLE + T_ROLES + T_COUNT
sim = Sim()
DT = 1 / FPS
state = {"end": None}

CARDS = [("A", "Lan", "Một tay bê", "👩", "Tự di chuyển nhân vật của mình", PINK_D),
         ("B", "Mai", "Một tay bê", "👧", "Tự di chuyển nhân vật của mình", LAV_D),
         ("C", "Hoa", "Một tay bê", "👱", "Tự di chuyển nhân vật của mình", MINT_D)]

def frame(T):
    if T < T_TITLE:
        return title_scene(T, "Demo gameplay · Vòng 2 — Bê cây", "🪴", "Ba người cùng bê một chậu tới điểm tập kết")
    if T < T_TITLE + T_ROLES:
        return roles_scene(T - T_TITLE, "Ba người cùng bê một chậu", "Chậu chỉ đi khi cả ba đứng gần nhau — tách xa là chậu rơi",
                           CARDS, "Rơi chậu → dừng lại hốt đất, phạt thời gian", "Về đích càng nhanh càng cao hạng · quá mốc tối đa thì 0 điểm")
    if T < T_GAME0:
        im = game_frame(sim, 0); countdown(im, T - T_TITLE - T_ROLES); return im
    gt = T - T_GAME0
    if state["end"] is None:
        sim.step(gt, DT)
        if sim.done_t is not None:
            state["end"] = T
        im = game_frame(sim, gt); start_flash(im, gt); return im
    a = T - state["end"]
    if a < 2.6:
        im = game_frame(sim, sim.done_t)
        banner(im, a, "VỀ ĐÍCH!", f"Thời gian {fmt(sim.elapsed(sim.done_t))} (đã cộng 3s phạt)", MINT_D)
        return im
    tt = fmt(sim.elapsed(sim.done_t))
    rows = [("Đội 1", "0:41", "hạng 2", False), ("Đội 2", tt, "hạng 1", True),
            ("Đội 3", "chờ lượt", "", False), ("Đội 4", "chờ lượt", "", False), ("Đội 5", "chờ lượt", "", False)]
    return result_scene(a - 2.6, "KẾT QUẢ LƯỢT · ĐỘI 2", f"Về đích {tt} · tạm xếp hạng 1 → quy đổi điểm theo hạng",
                        rows, "Số liệu minh họa — ngưỡng khoảng cách, tốc độ, phạt, mốc tối đa sẽ chốt sau playtest")

# game length is decided by the simulation; run it once to know the total
probe = Sim(); tt = 0.0
while probe.done_t is None:
    probe.step(tt, DT); tt += DT
TOTAL = T_GAME0 + probe.done_t + 2.6 + 6.0
encode(OUT, TOTAL, frame)
