"""Demo gameplay - Vong 3 Cho cay: A steers left, B steers right, C holds gas."""
import math, random, sys
from PIL import Image, ImageDraw
from demo_common import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "demo_vong3.mp4"
random.seed(3)

PX0, PY0, PX1, PY1 = PANEL
PW, PH = PX1 - PX0, PY1 - PY0
ROAD_L, ROAD_R = 170, 580                 # panel-local x
LANES = [238, 375, 512]
TRUCK_Y = 470                             # panel-local y
D_TOTAL = 3500.0
VMAX, ACC, DEC, STEER = 175.0, 120.0, 95.0, 230.0
HIT_IDX = 3
OBST = [(520, 375, "🚧"), (900, 238, "🪨"), (1220, 512, "📦"), (1560, 375, "📦"),
        (2000, 238, "🚧"), (2000, 512, "🚧"), (2330, 375, "🪨"), (2700, 238, "📦"), (3050, 512, "🚧")]
DECO = []
for k in range(0, int(D_TOTAL) + 600, 120):
    DECO.append((k + random.randint(0, 60), random.randint(40, 130), random.choice(["🌳", "🌷", "🌼", "🌸", "🌳", "🏡"])))
    DECO.append((k + random.randint(0, 60), random.randint(625, 715), random.choice(["🌳", "🌷", "🌻", "🌸", "🌳"])))
PUDDLES = [(700, 512), (1800, 375), (2900, 238)]

BG = make_bg(None, panel_fill=(205, 238, 200))
MASK = Image.new("L", (PW, PH), 0)
ImageDraw.Draw(MASK).rounded_rectangle((4, 4, PW - 4, PH - 4), 24, fill=255)

class Sim:
    def __init__(self):
        self.d = 0.0; self.v = 0.0; self.x = 375.0; self.vx = 0.0
        self.gas = False; self.hit_t = None; self.done_t = None
        self.knock = {}                        # obstacle idx -> time knocked
        self.bubbles = []; self.cheers = []; self.said = set()

    def say(self, key, i, s, t, dur=1.8):
        if key not in self.said:
            self.said.add(key); self.bubbles.append((i, s, t, dur))

    def target(self):
        ahead = [(k, o) for k, o in enumerate(OBST) if 0 < o[0] - self.d < 380 and k not in self.knock]
        if 1250 < self.d < 1560 and HIT_IDX not in self.knock:
            return 375                         # the scripted bump: driving straight into the box
        if not ahead:
            return self.x
        first = ahead[0][1][0]
        blocked = [o[1] for k, o in ahead if o[0] - first < 60 and k != HIT_IDX]
        free = [ln for ln in LANES if all(abs(ln - b) > 90 for b in blocked)]
        if not free:
            return self.x
        if all(abs(self.x - b) > 90 for b in blocked):
            return self.x
        return min(free, key=lambda ln: abs(ln - self.x))

    def step(self, t, dt):
        if self.done_t is not None:
            self.v = max(0, self.v - 200 * dt); self.d += self.v * dt; self.vx = 0; return
        recovering = self.hit_t is not None and t - self.hit_t < 1.0
        self.gas = t > 0.2 and not (1880 < self.d < 2260) and not recovering
        if self.gas:
            self.v = min(VMAX, self.v + ACC * dt)
        else:
            self.v = max(95 if not recovering else 25, self.v - DEC * dt)
        tg = self.target()
        if abs(tg - self.x) > 6:
            self.vx = STEER if tg > self.x else -STEER
        else:
            self.vx = 0
        self.x = clamp(self.x + self.vx * dt, ROAD_L + 50, ROAD_R - 50)
        self.d += self.v * dt
        for k, (od, ox, em) in enumerate(OBST):
            if k in self.knock: continue
            if abs(od - self.d) < 55 and abs(ox - self.x) < 70:
                self.knock[k] = t
                self.hit_t = t; self.v = 25
                self.cheers += [(t + 0.2, "😱"), (t + 0.4, "🙈"), (t + 0.6, "😂")]
                self.say("hit", 0, "Ối, đâm hộp rồi!", t + 0.1)
        if 1700 < self.d: self.say("slow", 2, "Thả ga, khúc này khó!", t)
        if 2260 < self.d: self.say("go", 2, "Ga lại nè!", t, 1.4)
        if 800 < self.d: self.say("l", 1, "Phải tí... ok!", t, 1.4)
        if D_TOTAL - 450 < self.d: self.say("shop", 1, "Thấy cửa hàng rồi!", t)
        if self.d >= D_TOTAL:
            self.done_t = t
            self.cheers += [(t + k * 0.15, em) for k, em in enumerate(["🎉", "👏", "💖", "🥳", "🌸"])]

def sy(sim, wd):
    return TRUCK_Y - (wd - sim.d)

def draw_truck(lay, x, y, tilt, shake):
    tw, th = 96, 150
    tr = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(tr)
    ox, oy = 20, 20
    for wx, wy in ((ox - 6, oy + 22), (ox + tw - 8, oy + 22), (ox - 6, oy + th - 46), (ox + tw - 8, oy + th - 46)):
        d.rounded_rectangle((wx, wy, wx + 14, wy + 30), 5, fill=(60, 50, 70))
    d.rounded_rectangle((ox, oy + 44, ox + tw, oy + th), 16, fill=(255, 150, 190), outline=(200, 70, 120), width=4)
    d.rounded_rectangle((ox + 6, oy, ox + tw - 6, oy + 52), 16, fill=(200, 182, 240), outline=LAV_D, width=4)
    d.rounded_rectangle((ox + 16, oy + 8, ox + tw - 16, oy + 26), 6, fill=(220, 240, 255))
    d.rounded_rectangle((ox + 10, oy + 60, ox + tw - 10, oy + th - 10), 10, fill=(255, 210, 225))
    for px, py in ((ox + 30, oy + 82), (ox + tw - 30, oy + 82), (ox + 30, oy + 120), (ox + tw - 30, oy + 120)):
        tr.alpha_composite(emoji("🪴", 34), (int(px - 17), int(py - 18)))
    tr = tr.rotate(-tilt, expand=True, resample=Image.BICUBIC)
    lay.alpha_composite(tr, (int(x - tr.width / 2 + shake), int(y - tr.height / 2)))

def draw_road(im, sim, t):
    lay = Image.new("RGBA", (PW, PH), (205, 238, 200, 255))
    d = ImageDraw.Draw(lay)
    d.rectangle((ROAD_L - 14, 0, ROAD_R + 14, PH), fill=(255, 255, 255))
    d.rectangle((ROAD_L, 0, ROAD_R, PH), fill=(186, 178, 200))
    off = sim.d % 90
    for lx in ((LANES[0] + LANES[1]) / 2, (LANES[1] + LANES[2]) / 2):
        y = -90 + off
        while y < PH:
            d.rounded_rectangle((lx - 4, y, lx + 4, y + 44), 4, fill=(255, 255, 255))
            y += 90
    for wd, px in PUDDLES:
        y = sy(sim, wd)
        if -60 < y < PH + 60:
            d.ellipse((px - 52, y - 24, px + 52, y + 24), fill=(160, 205, 240), outline=(120, 180, 225), width=3)
    fy = sy(sim, D_TOTAL)
    if -40 < fy < PH + 40:
        for k in range(int((ROAD_R - ROAD_L) / 20)):
            for r in range(2):
                c = (40, 30, 50) if (k + r) % 2 == 0 else WHITE
                d.rectangle((ROAD_L + k * 20, fy + r * 20 - 20, ROAD_L + k * 20 + 20, fy + r * 20), fill=c)
    shop_y = sy(sim, D_TOTAL + 220)
    if shop_y > -200:
        d.rounded_rectangle((260, shop_y - 120, 490, shop_y + 30), 14, fill=(255, 240, 246), outline=PINK_D, width=4)
        for k in range(6):
            d.rectangle((260 + k * 38.4, shop_y - 120, 260 + (k + 1) * 38.4, shop_y - 84), fill=PINK if k % 2 == 0 else WHITE)
        lay.alpha_composite(emoji("🏪", 70), (340, int(shop_y - 80)))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle((280, shop_y - 160, 470, shop_y - 124), 12, fill=CREAM, outline=PINK_D, width=3)
        text_c(d, (375, shop_y - 142), "CỬA HÀNG HOA", font(BLACK, 18), PINK_D)
    for wd, px, em in DECO:
        y = sy(sim, wd)
        if -50 < y < PH + 50:
            e = emoji(em, 44)
            lay.alpha_composite(e, (int(px - e.width / 2), int(y - e.height / 2)))
    for k, (wd, ox, em) in enumerate(OBST):
        y = sy(sim, wd)
        if k in sim.knock:
            a = t - sim.knock[k]
            if a > 1.2: continue
            e = emoji(em, 54).rotate(a * 400, expand=True)
            e.putalpha(e.getchannel("A").point(lambda v: int(v * (1 - a / 1.2))))
            lay.alpha_composite(e, (int(ox + a * 260 - e.width / 2), int(y - a * 120 - e.height / 2)))
            continue
        if -60 < y < PH + 60:
            e = emoji(em, 54)
            lay.alpha_composite(e, (int(ox - e.width / 2), int(y - e.height / 2)))
    shake = 0
    if sim.hit_t is not None and t - sim.hit_t < 0.6:
        shake = math.sin((t - sim.hit_t) * 70) * 8
    tilt = 7 if sim.vx > 0 else (-7 if sim.vx < 0 else 0)
    if sim.v > 120:
        for k in range(3):
            yy = TRUCK_Y + 95 + k * 16
            d.line((sim.x - 30 + k * 30, yy, sim.x - 30 + k * 30, yy + 18), fill=(255, 255, 255), width=3)
    draw_truck(lay, sim.x, TRUCK_Y, tilt, shake)
    d = ImageDraw.Draw(lay)
    if sim.hit_t is not None and t - sim.hit_t < 1.4:
        a = t - sim.hit_t
        lay.alpha_composite(emoji("💥", 64), (int(sim.x - 32), int(TRUCK_Y - 120)))
        d = ImageDraw.Draw(lay)
        text_c(d, (sim.x, TRUCK_Y - 150 - a * 10), "Va chạm! Chậm lại", font(BLACK, 26), WHITE, stroke_width=4, stroke_fill=RED)
    lay.putalpha(MASK)
    im.alpha_composite(lay, (PX0, PY0))

def draw_progress(im, sim):
    d = ImageDraw.Draw(im)
    top, bot = 190, 650
    d.rounded_rectangle((820, top, 832, bot), 6, fill=(230, 220, 245))
    k = clamp(sim.d / D_TOTAL)
    y = bot - (bot - top) * k
    d.rounded_rectangle((820, y, 832, bot), 6, fill=PINK)
    paste_c(im, emoji("🏪", 34), 826, top - 26)
    paste_c(im, emoji("🚚", 30), 826, y)

def draw_phones(im, sim, t):
    for i, desc in enumerate(["Giữ để rẽ trái", "Giữ để rẽ phải", "Giữ để tăng tốc"]):
        sx0, sy0, sx1, sy1 = phone_shell(im, i, desc)
        d = ImageDraw.Draw(im)
        cx = (sx0 + sx1) / 2
        if i < 2:
            p = (sim.vx < 0) if i == 0 else (sim.vx > 0)
            col = (PINK, PINK_D) if i == 0 else (LAV, LAV_D)
            btn(d, im, (sx0 + 10, sy0 + 62, sx1 - 10, sy0 + 230), p, col[1] if p else col[0])
            tri(d, cx, sy0 + 135 + (4 if p else 0), 30, "left" if i == 0 else "right", WHITE)
            text_c(d, (cx, sy0 + 195 + (4 if p else 0)), "TRÁI" if i == 0 else "PHẢI", font(BLACK, 20), WHITE)
            text_c(d, (cx, sy0 + 255), "đang giữ" if p else "thả", font(BOLD, 13), PCOL[i] if p else (160, 150, 170))
        else:
            p = sim.gas
            r = 46
            cy = sy0 + 125
            if not p:
                d.ellipse((cx - r, cy - r + 6, cx + r, cy + r + 6), fill=(20, 110, 80))
            oy = 4 if p else 0
            d.ellipse((cx - r, cy - r + oy, cx + r, cy + r + oy), fill=MINT_D if not p else (30, 130, 95),
                      outline=(255, 220, 120) if p else None, width=4)
            text_c(d, (cx, cy + oy - 2), "GA", font(BLACK, 30), WHITE)
            text_c(d, (cx, cy + oy + 24), "giữ" if p else "thả", font(BOLD, 12), WHITE)
            text_c(d, (cx, sy0 + 200), "Tốc độ", font(BOLD, 13), INK)
            d.rounded_rectangle((sx0 + 12, sy0 + 214, sx1 - 12, sy0 + 232), 9, fill=(230, 240, 236))
            k = sim.v / VMAX
            d.rounded_rectangle((sx0 + 12, sy0 + 214, sx0 + 12 + (sx1 - sx0 - 24) * k, sy0 + 232), 9,
                                fill=(MINT_D if k < 0.85 else (240, 160, 40)))
            text_c(d, (cx, sy0 + 252), f"{int(sim.v / 3.5)} km/h", font(BLACK, 15), MINT_D)
    draw_bubbles(im, sim.bubbles, t)

def elapsed(sim, t): return t

def game_frame(sim, t):
    im = BG.copy()
    header(im, "VÒNG 3 · CHỞ CÂY", "🚚", fmt(t), right_label="MỐC", right_val="2:30")
    draw_road(im, sim, t)
    draw_progress(im, sim)
    draw_cheers(im, sim.cheers, t)
    draw_phones(im, sim, t)
    return im

T_TITLE, T_ROLES, T_COUNT = 3.5, 6.0, 3.0
T_GAME0 = T_TITLE + T_ROLES + T_COUNT
DT = 1 / FPS
sim = Sim()
state = {"end": None}
CARDS = [("A", "Lan", "Rẽ trái", "⬅️", "Giữ nút để lái sang trái", PINK_D),
         ("B", "Mai", "Rẽ phải", "➡️", "Giữ nút để lái sang phải", LAV_D),
         ("C", "Hoa", "Chân ga", "🚀", "Giữ để tăng tốc, thả ra xe tự chậm", MINT_D)]

def frame(T):
    if T < T_TITLE:
        return title_scene(T, "Demo gameplay · Vòng 3 — Chở cây", "🚚", "Lái xe chở cây tới cửa hàng, tránh chướng ngại vật")
    if T < T_TITLE + T_ROLES:
        return roles_scene(T - T_TITLE, "Ba người lái chung một xe", "Hai người lái trái/phải, một người giữ chân ga",
                           CARDS, "Va chướng ngại vật → xe khựng lại, mất thời gian", "Tới cửa hàng càng nhanh càng cao hạng · quá mốc tối đa thì 0 điểm")
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
        sim.step(sim.done_t + a, DT)
        im = game_frame(sim, sim.done_t)
        banner(im, a, "GIAO THÀNH CÔNG!", f"Thời gian {fmt(sim.done_t)}", MINT_D)
        return im
    tt = fmt(sim.done_t)
    rows = [("Đội 1", "0:39", "hạng 2", False), ("Đội 2", tt, "hạng 1", True),
            ("Đội 3", "chờ lượt", "", False), ("Đội 4", "chờ lượt", "", False), ("Đội 5", "chờ lượt", "", False)]
    return result_scene(a - 2.6, "KẾT QUẢ LƯỢT · ĐỘI 2", f"Về cửa hàng {tt} · tạm xếp hạng 1 → quy đổi điểm theo hạng",
                        rows, "Số liệu minh họa — cách lái (giữ hay bấm nhịp), va chạm, tốc độ, mốc tối đa sẽ chốt sau playtest")

probe = Sim(); tt = 0.0
while probe.done_t is None:
    probe.step(tt, DT); tt += DT
TOTAL = T_GAME0 + probe.done_t + 2.6 + 6.0
encode(OUT, TOTAL, frame)
