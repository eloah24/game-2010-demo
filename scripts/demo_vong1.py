"""Demo gameplay video - Vong 1 Trong cay (GDD Cua hang hoa 20/10).
Renders frames with Pillow and pipes them to ffmpeg -> MP4."""
import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

W, H, FPS = 1280, 720, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "demo_vong1.mp4"
FD = "C:/Windows/Fonts/"
random.seed(20)

_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name, size)
    return _fc[k]
REG, SEMI, BOLD, BLACK = "segoeui.ttf", "seguisb.ttf", "segoeuib.ttf", "seguibl.ttf"

_ec = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _ec:
        f = font("seguiemj.ttf", size)
        im = Image.new("RGBA", (int(size * 2.4), int(size * 2.4)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((size * 1.2, size * 1.2), ch.replace("️", ""), font=f, embedded_color=True, anchor="mm")
        _ec[k] = im.crop(im.getbbox()) if im.getbbox() else im
    return _ec[k]

def paste_c(base, im, cx, cy, alpha=1.0):
    if alpha < 1:
        im = im.copy()
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text_c(d, xy, s, f, fill, anchor="mm", **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)

# palette
PINK = (255, 182, 207); PINK_D = (231, 84, 128); LAV = (200, 182, 240); LAV_D = (120, 90, 190)
CREAM = (255, 246, 214); MINT = (176, 234, 210); MINT_D = (38, 150, 110); INK = (74, 44, 82)
WHITE = (255, 255, 255); RED = (226, 60, 70); SOIL = (176, 124, 92); SOIL_DRY = (214, 180, 140)

def gradient(w, h, c1, c2):
    g = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,))
    return g

def shadow_box(base, box, r, fill, sh=10, outline=None, width=0):
    x0, y0, x1, y1 = box
    s = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((x0 + 3, y0 + 6, x1 + 3, y1 + 6), r, fill=(120, 60, 110, 70))
    base.alpha_composite(s.filter(ImageFilter.GaussianBlur(sh)))
    ImageDraw.Draw(base).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

# ---------------- layout ----------------
ROWS, COLS, CELL = 4, 6, 108
GX, GY = 60, 150                      # grid origin
GARDEN = (36, 104, 784, 700)
PHONES_X, PHONE_W, PHONE_H, PHONE_Y, PHONE_GAP = 868, 126, 330, 250, 11
GAME_LEN = 45.0
X_POINTS = 10

PLAYERS = [("Lan", "A", "Lên / Xuống"), ("Mai", "B", "Trái / Phải"), ("Hoa", "C", "Dụng cụ")]
TOOLS = [("water", "💧", "Tưới"), ("bug", "🐛", "Bắt sâu"), ("trim", "✂️", "Tỉa")]
NEED_EMO = {"water": "💧", "bug": "🐛", "trim": "✂️"}
FLOWERS = ["🌷", "🌹", "🌻", "🌼", "🌸", "🪻"]

def cell_center(r, c):
    return GX + c * CELL + CELL / 2, GY + r * CELL + CELL / 2

def phone_box(i):
    x = PHONES_X + i * (PHONE_W + PHONE_GAP)
    return (x, PHONE_Y, x + PHONE_W, PHONE_Y + PHONE_H)

# static background
BG = gradient(W, H, (255, 228, 238), (232, 222, 255))
bd = ImageDraw.Draw(BG)
for _ in range(40):  # soft dots
    x, y, r = random.randint(0, W), random.randint(0, H), random.randint(2, 6)
    bd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 120))
shadow_box(BG, GARDEN, 26, (236, 250, 238), outline=MINT, width=4)
bd = ImageDraw.Draw(BG)
for r in range(ROWS):
    for c in range(COLS):
        x0, y0 = GX + c * CELL + 6, GY + r * CELL + 6
        bd.rounded_rectangle((x0, y0, x0 + CELL - 12, y0 + CELL - 12), 18, fill=(200, 236, 206))
text_c(bd, (GX + COLS * CELL / 2, 127), "VƯỜN CỦA ĐỘI 2", font(BLACK, 20), MINT_D)
# legend
lg_y = 640
text_c(bd, (GX + 10, lg_y + 20), "Cây cần:", font(SEMI, 20), INK, anchor="lm")
lx = GX + 110
for key, em, lab in TOOLS:
    bd.rounded_rectangle((lx, lg_y + 2, lx + 150, lg_y + 38), 18, fill=WHITE, outline=LAV, width=2)
    paste_c(BG, emoji(em, 22), lx + 24, lg_y + 20)
    text_c(bd, (lx + 44, lg_y + 20), lab, font(SEMI, 19), INK, anchor="lm")
    lx += 165
text_c(bd, (W - 216, 615), "Điện thoại người chơi", font(SEMI, 19), LAV_D)
# audience lane
bd.rounded_rectangle((800, 104, 852, 700), 24, fill=(255, 255, 255, 110))
text_c(bd, (826, 116), "cổ vũ", font(SEMI, 13), LAV_D, anchor="mt")

# soil tiles per cell (flower assignment)
flower_of = {(r, c): random.choice(FLOWERS) for r in range(ROWS) for c in range(COLS)}

# ---------------- simulation ----------------
class Sim:
    def __init__(self):
        self.needs = {}
        for cell in random.sample(list(flower_of), 6):
            self.needs[cell] = random.choice(list(NEED_EMO))
        self.cur = [1.0, 1.0]; self.cur_t = (1, 1); self.cur_from = (1.0, 1.0); self.cur_move_t = -9
        self.score = 0; self.correct = 0
        self.tool = None
        self.press = {}               # button -> time pressed
        self.fx = []                  # (kind, t0, data)
        self.bubbles = []             # (player_idx, text, t0, dur)
        self.state = "plan"; self.t_next = 0; self.target = None
        self.n_done = 0; self.lock_until = -1; self.mistake_done = False
        self.next_spawn = 3.0; self.locked = False

    def press_btn(self, b, t): self.press[b] = t

    def move(self, dr, dc, t):
        r, c = self.cur_t
        self.cur_from = tuple(self.pos(t)); self.cur_move_t = t
        self.cur_t = (r + dr, c + dc)
        if dr: self.press_btn("up" if dr < 0 else "down", t)
        if dc: self.press_btn("left" if dc < 0 else "right", t)

    def pos(self, t):
        k = min(1, (t - self.cur_move_t) / 0.16)
        k = 1 - (1 - k) ** 3
        return [self.cur_from[0] + (self.cur_t[0] - self.cur_from[0]) * k,
                self.cur_from[1] + (self.cur_t[1] - self.cur_from[1]) * k]

    def say(self, i, s, t, dur=1.6): self.bubbles.append((i, s, t, dur))

    def step(self, t):
        if self.locked: return
        if t >= self.next_spawn:
            free = [c for c in flower_of if c not in self.needs and c != self.target]
            if free and len(self.needs) < 8:
                cell = random.choice(free); self.needs[cell] = random.choice(list(NEED_EMO))
                self.fx.append(("spawn", t, cell))
            self.next_spawn = t + random.uniform(2.6, 3.6)
        if t < self.t_next: return
        r0, c0 = self.cur_t
        if self.state == "plan":
            if not self.needs: self.t_next = t + 0.3; return
            self.target = min(self.needs, key=lambda x: abs(x[0] - r0) + abs(x[1] - c0) + random.random() * 0.5)
            tr, tc = self.target
            dr, dc = tr - r0, tc - c0
            parts = []
            if dr: parts.append(f"{'Lên' if dr < 0 else 'Xuống'} {abs(dr)}")
            if dc: parts.append(f"{'trái' if dc < 0 else 'phải'} {abs(dc)}")
            need = self.needs[self.target]
            if parts:
                self.say(2, ", ".join(parts) + "!", t)
            self.wrong = (self.n_done == 3 and not self.mistake_done)
            self.state = "move"; self.t_tool = t + 0.35; self.t_next = t + 0.45
            self.pending_tool = ("bug" if need != "bug" else "water") if self.wrong else need
        elif self.state == "move":
            tr, tc = self.target
            if self.tool != self.pending_tool and t >= self.t_tool:
                self.tool = self.pending_tool; self.press_btn("tool_" + self.tool, t)
            dr = (tr > r0) - (tr < r0); dc = (tc > c0) - (tc < c0)
            if dr or dc:
                # A and B move together when both axes are needed
                self.move(dr, dc, t); self.t_next = t + 0.42
            else:
                if self.tool != self.pending_tool:
                    self.tool = self.pending_tool; self.press_btn("tool_" + self.tool, t)
                self.state = "confirm"; self.t_next = t + 0.35
        elif self.state == "confirm":
            self.press_btn("ok", t)
            need = self.needs.get(self.target)
            if need is None:
                self.state = "plan"; self.t_next = t + 0.2
            elif self.tool == need:
                del self.needs[self.target]
                self.score += X_POINTS; self.correct += 1; self.n_done += 1
                self.fx.append(("ok", t, self.target))
                for k in range(random.randint(2, 4)):
                    self.fx.append(("cheer", t + k * 0.12, random.choice(["👏", "💖", "🎉", "🌸", "😍", "🥳"])))
                if self.correct in (1, 5, 9): self.say(random.choice([0, 1]), random.choice(["Yeahhh!", "Đẹp quá!", "Tiếp tiếp!"]), t, 1.1)
                self.state = "plan"; self.t_next = t + 0.35
            else:
                self.mistake_done = True
                self.fx.append(("bad", t, (self.target, need)))
                self.say(0, "Ơ cây này cần nước mà!", t + 0.2, 1.8)
                self.lock_until = t + 1.5
                self.pending_tool = need; self.state = "move"; self.t_tool = t + 1.5; self.t_next = t + 1.55
                self.fx.append(("cheer", t + 0.3, "😂")); self.fx.append(("cheer", t + 0.5, "🙈"))

# ---------------- drawing ----------------
def draw_header(im, t_left, score, team="Đội 2", show_timer=True):
    d = ImageDraw.Draw(im)
    shadow_box(im, (36, 18, 470, 84), 30, WHITE)
    paste_c(im, emoji("🌱", 34), 76, 51)
    d = ImageDraw.Draw(im)
    text_c(d, (104, 51), "VÒNG 1 · TRỒNG CÂY", font(BLACK, 28), PINK_D, anchor="lm")
    shadow_box(im, (488, 18, 760, 84), 30, LAV)
    d = ImageDraw.Draw(im)
    text_c(d, (624, 51), f"{team} đang chơi", font(BOLD, 24), WHITE)
    if show_timer:
        warn = t_left <= 10
        col = RED if warn and int(t_left * 2) % 2 == 0 else INK
        shadow_box(im, (800, 18, 1010, 84), 30, CREAM, outline=(RED if warn else (240, 210, 140)), width=3)
        d = ImageDraw.Draw(im)
        paste_c(im, emoji("⏱️", 28), 836, 51)
        s = max(0, math.ceil(t_left))
        text_c(d, (930, 52), f"0:{s:02d}", font(BLACK, 34), col)
    shadow_box(im, (1028, 18, 1246, 84), 30, MINT)
    d = ImageDraw.Draw(im)
    text_c(d, (1056, 51), "ĐIỂM", font(BOLD, 18), MINT_D, anchor="lm")
    text_c(d, (1228, 52), str(score), font(BLACK, 36), WHITE, anchor="rm", stroke_width=2, stroke_fill=MINT_D)

def draw_garden(im, sim, t):
    d = ImageDraw.Draw(im)
    for (r, c), fl in flower_of.items():
        cx, cy = cell_center(r, c)
        need = sim.needs.get((r, c))
        shake = 0
        for kind, t0, data in sim.fx:
            if kind == "bad" and data[0] == (r, c) and 0 <= t - t0 < 0.5:
                shake = math.sin((t - t0) * 60) * 6
        soil = SOIL_DRY if need == "water" else SOIL
        d.ellipse((cx - 30 + shake, cy + 18, cx + 30 + shake, cy + 36), fill=soil)
        size = 52 if need else 58
        if need == "trim":
            paste_c(im, emoji("🌿", 34), cx - 22 + shake, cy + 4)
            paste_c(im, emoji("🌿", 30), cx + 22 + shake, cy + 8)
        paste_c(im, emoji(fl, size), cx + shake, cy - 4, alpha=0.55 if need == "water" else 1)
        if need:
            p = 1 + 0.08 * math.sin(t * 6 + r + c)
            bx, by = cx + 30, cy - 34
            rr = 19 * p
            d.ellipse((bx - rr, by - rr, bx + rr, by + rr), fill=WHITE, outline=PINK_D, width=2)
            paste_c(im, emoji(NEED_EMO[need], int(24 * p)), bx, by)
    # cursor
    pr, pc = sim.pos(t)
    cx, cy = GX + pc * CELL + CELL / 2, GY + pr * CELL + CELL / 2
    g = 3 * math.sin(t * 8)
    half = CELL / 2 - 2 + g
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((cx - half, cy - half, cx + half, cy + half), 22, outline=(255, 90, 160, 200), width=10)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - half, cy - half, cx + half, cy + half), 22, outline=PINK_D, width=5)
    if sim.tool:
        em = dict((k, e) for k, e, _ in TOOLS)[sim.tool]
        d.ellipse((cx - half - 14, cy + half - 40, cx - half + 26, cy + half), fill=CREAM, outline=PINK_D, width=2)
        paste_c(im, emoji(em, 24), cx - half + 6, cy + half - 20)

def draw_fx(im, sim, t):
    d = ImageDraw.Draw(im)
    for kind, t0, data in sim.fx:
        a = t - t0
        if a < 0: continue
        if kind == "ok" and a < 1.2:
            cx, cy = cell_center(*data)
            al = 1 - a / 1.2
            for k in range(6):
                ang = k * math.pi / 3 + a * 2
                rad = 20 + a * 70
                paste_c(im, emoji("✨", 22), cx + math.cos(ang) * rad, cy + math.sin(ang) * rad, alpha=al)
            text_c(d, (cx, cy - 40 - a * 50), f"+{X_POINTS}", font(BLACK, 34), (255, 255, 255, int(255 * al)),
                   stroke_width=3, stroke_fill=(*MINT_D, int(255 * al)))
        elif kind == "bad" and a < 1.6:
            (r, c), need = data
            cx, cy = cell_center(r, c)
            al = min(1, (1.6 - a) * 3)
            paste_c(im, emoji("❌", 44), cx, cy, alpha=al)
            bx0, by0 = cx - 120, cy + 58
            d.rounded_rectangle((bx0, by0, bx0 + 240, by0 + 44), 22, fill=(255, 235, 238), outline=RED, width=2)
            text_c(d, (cx, by0 + 22), "Sai dụng cụ · khóa 1,5s", font(BOLD, 19), RED)
        elif kind == "spawn" and a < 0.6:
            cx, cy = cell_center(*data)
            rr = 20 + a * 60
            d.ellipse((cx + 30 - rr, cy - 34 - rr, cx + 30 + rr, cy - 34 + rr), outline=(*PINK_D, int(255 * (1 - a / 0.6))), width=3)
        elif kind == "cheer" and a < 3.0:
            x = 826 + math.sin(a * 3 + t0) * 10
            y = 680 - a * 190
            paste_c(im, emoji(data, 34), x, y, alpha=min(1, (3.0 - a)))

def btn(d, im, box, pressed, fill, label=None, em=None, sel=False, fsize=20):
    x0, y0, x1, y1 = box
    off = 4 if pressed else 0
    if not pressed:
        d.rounded_rectangle((x0, y0 + 5, x1, y1 + 5), 16, fill=tuple(int(v * 0.75) for v in fill[:3]))
    d.rounded_rectangle((x0, y0 + off, x1, y1 + off), 16, fill=fill, outline=(PINK_D if sel else None), width=(4 if sel else 0))
    cy = (y0 + y1) / 2 + off
    if em and label:
        paste_c(im, emoji(em, 24), x0 + 22, cy)
        text_c(d, (x0 + 40, cy), label, font(BOLD, 15), INK, anchor="lm")
    elif em:
        paste_c(im, emoji(em, 30), (x0 + x1) / 2, cy)
    elif label:
        text_c(d, ((x0 + x1) / 2, cy), label, font(BLACK, fsize), WHITE)

def tri(d, cx, cy, s, direction, fill):
    pts = {"up": [(cx, cy - s), (cx - s, cy + s * .7), (cx + s, cy + s * .7)],
           "down": [(cx, cy + s), (cx - s, cy - s * .7), (cx + s, cy - s * .7)],
           "left": [(cx - s, cy), (cx + s * .7, cy - s), (cx + s * .7, cy + s)],
           "right": [(cx + s, cy), (cx - s * .7, cy - s), (cx - s * .7, cy + s)]}[direction]
    d.polygon(pts, fill=fill)

def draw_phones(im, sim, t, locked=False):
    def pressed(b): return 0 <= t - sim.press.get(b, -9) < 0.2
    for i, (name, role, desc) in enumerate(PLAYERS):
        box = phone_box(i)
        x0, y0, x1, y1 = box
        shadow_box(im, box, 22, (60, 40, 70))
        d = ImageDraw.Draw(im)
        sx0, sy0, sx1, sy1 = x0 + 6, y0 + 16, x1 - 6, y1 - 14
        d.rounded_rectangle((sx0, sy0, sx1, sy1), 16, fill=(255, 250, 252))
        d.rounded_rectangle(((x0 + x1) / 2 - 18, y0 + 6, (x0 + x1) / 2 + 18, y0 + 11), 3, fill=(30, 20, 35))
        cx = (sx0 + sx1) / 2
        d.ellipse((sx0 + 8, sy0 + 10, sx0 + 36, sy0 + 38), fill=[PINK_D, LAV_D, MINT_D][i])
        text_c(d, (sx0 + 22, sy0 + 24), role, font(BLACK, 16), WHITE)
        text_c(d, (sx0 + 44, sy0 + 17), name, font(BOLD, 16), INK, anchor="lm")
        text_c(d, (sx0 + 44, sy0 + 33), desc, font(REG, 11), LAV_D, anchor="lm")
        bx0, bx1 = sx0 + 10, sx1 - 10
        if role == "A":
            for k, dr in enumerate(["up", "down"]):
                yb = sy0 + 62 + k * 112
                p = pressed(dr)
                btn(d, im, (bx0, yb, bx1, yb + 96), p, PINK if not p else PINK_D)
                tri(d, cx, yb + 48 + (4 if p else 0), 24, dr, WHITE)
        elif role == "B":
            for k, dr in enumerate(["left", "right"]):
                yb = sy0 + 62 + k * 112
                p = pressed(dr)
                btn(d, im, (bx0, yb, bx1, yb + 96), p, LAV if not p else LAV_D)
                tri(d, cx, yb + 48 + (4 if p else 0), 24, dr, WHITE)
        else:
            for k, (key, em, lab) in enumerate(TOOLS):
                yb = sy0 + 56 + k * 52
                p = pressed("tool_" + key)
                btn(d, im, (bx0, yb, bx1, yb + 44), p, CREAM if sim.tool != key else (255, 222, 236), label=lab, em=em, sel=(sim.tool == key))
            yb = sy0 + 56 + 3 * 52 + 8
            p = pressed("ok")
            btn(d, im, (bx0, yb, bx1, yb + 46), p, MINT_D if not p else (20, 110, 80), label="XÁC NHẬN", fsize=14)
        d.ellipse((sx0 + 10, sy1 - 22, sx0 + 20, sy1 - 12), fill=(60, 200, 120))
        text_c(d, (sx0 + 26, sy1 - 17), "Đã kết nối", font(REG, 11), (110, 110, 120), anchor="lm")
        if locked or 0 <= t - getattr(sim, "lock_until", -9) + 1.5 < 1.5 and sim.lock_until > t:
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            od.rounded_rectangle((sx0, sy0 + 50, sx1, sy1 - 28), 12, fill=(70, 50, 80, 150))
            im.alpha_composite(ov)
            d = ImageDraw.Draw(im)
            paste_c(im, emoji("🔒", 34), cx, (sy0 + sy1) / 2 + 6)
    # speech bubbles
    d = ImageDraw.Draw(im)
    for i, s, t0, dur in sim.bubbles:
        a = t - t0
        if not (0 <= a < dur): continue
        x0, y0, x1, y1 = phone_box(i)
        cx = (x0 + x1) / 2
        f = font(BOLD, 17)
        tw = d.textlength(s, font=f) + 28
        bx0 = min(max(cx - tw / 2, 864), W - 16 - tw)
        by1 = PHONE_Y - 16 - (0 if a > 0.15 else (0.15 - a) * 60)
        d.rounded_rectangle((bx0, by1 - 42, bx0 + tw, by1), 20, fill=WHITE, outline=[PINK_D, LAV_D, MINT_D][i], width=3)
        d.polygon([(cx - 8, by1 - 1), (cx + 8, by1 - 1), (cx, by1 + 12)], fill=[PINK_D, LAV_D, MINT_D][i])
        text_c(d, (bx0 + tw / 2, by1 - 21), s, f, INK)

def overlay(im, alpha=150):
    ov = Image.new("RGBA", im.size, (70, 40, 90, alpha))
    im.alpha_composite(ov)

def ease(a): return 1 - (1 - min(max(a, 0), 1)) ** 3

# ---------------- scenes ----------------
T_TITLE, T_ROLES, T_COUNT = 3.5, 6.0, 3.0
T_GAME0 = T_TITLE + T_ROLES + T_COUNT
T_END = T_GAME0 + GAME_LEN
T_TIMEUP, T_RESULT = 2.2, 6.0
TOTAL = T_END + T_TIMEUP + T_RESULT

def scene_title(t):
    im = gradient(W, H, (255, 214, 230), (222, 206, 255))
    d = ImageDraw.Draw(im)
    for k in range(14):
        x = (k * 97 + t * 40) % (W + 100) - 50
        y = 80 + (k * 53) % 560 + math.sin(t * 2 + k) * 10
        paste_c(im, emoji(["🌸", "🌷", "💐", "✨"][k % 4], 36), x, y, alpha=0.6)
    a = ease(t / 0.6)
    shadow_box(im, (240, 190 + (1 - a) * 40, 1040, 530 + (1 - a) * 40), 40, (255, 255, 255))
    d = ImageDraw.Draw(im)
    oy = (1 - a) * 40
    paste_c(im, emoji("💐", 70), 640, 255 + oy)
    text_c(d, (640, 340 + oy), "CỬA HÀNG HOA 20/10", font(BLACK, 54), PINK_D)
    text_c(d, (640, 405 + oy), "Demo gameplay · Vòng 1 — Trồng cây", font(BOLD, 30), LAV_D)
    text_c(d, (640, 465 + oy), "5 đội × 3 người · điều khiển bằng điện thoại · màn hình lớn", font(REG, 22), INK)
    return im

def scene_roles(t):
    im = gradient(W, H, (255, 228, 238), (232, 222, 255))
    d = ImageDraw.Draw(im)
    text_c(d, (640, 80), "Mỗi người giữ một phần điều khiển", font(BLACK, 42), PINK_D)
    text_c(d, (640, 128), "Cả đội nhìn vườn trên màn hình lớn và gọi nhau di chuyển con trỏ", font(REG, 24), INK)
    cards = [("A", "Lan", "Lên / Xuống", "⬆️", "Di chuyển con trỏ theo hàng", PINK_D),
             ("B", "Mai", "Trái / Phải", "➡️", "Di chuyển con trỏ theo cột", LAV_D),
             ("C", "Hoa", "Chọn dụng cụ", "🧰", "Tưới · Bắt sâu · Tỉa, rồi XÁC NHẬN", MINT_D)]
    for i, (r, n, role, em, desc, col) in enumerate(cards):
        a = ease((t - 0.3 - i * 0.35) / 0.5)
        if a <= 0: continue
        x0 = 110 + i * 360; y0 = 190 + (1 - a) * 60
        shadow_box(im, (x0, y0, x0 + 320, y0 + 300), 30, WHITE, outline=col, width=4)
        d = ImageDraw.Draw(im)
        d.ellipse((x0 + 125, y0 + 24, x0 + 195, y0 + 94), fill=col)
        text_c(d, (x0 + 160, y0 + 59), r, font(BLACK, 38), WHITE)
        text_c(d, (x0 + 160, y0 + 125), f"{n} · {role}", font(BOLD, 26), INK)
        paste_c(im, emoji(em, 60), x0 + 160, y0 + 200)
        text_c(d, (x0 + 160, y0 + 268), desc, font(REG, 19), LAV_D)
    a = ease((t - 2.0) / 0.5)
    if a > 0:
        shadow_box(im, (200, 540, 1080, 660), 30, CREAM)
        d = ImageDraw.Draw(im)
        text_c(d, (640, 575), f"Chăm đúng cây đúng dụng cụ  =  +{X_POINTS} điểm", font(BLACK, 30), INK)
        text_c(d, (640, 625), f"{int(GAME_LEN)} giây · hết giờ khóa điều khiển và chốt điểm", font(REG, 22), LAV_D)
    return im

def game_frame(sim, t, t_left, locked=False):
    im = BG.copy()
    draw_header(im, t_left, sim.score)
    draw_garden(im, sim, t)
    draw_fx(im, sim, t)
    draw_phones(im, sim, t, locked)
    return im

def scene_result(t, sim):
    im = gradient(W, H, (255, 214, 230), (222, 206, 255))
    for k in range(30):
        x = (k * 131) % W + math.sin(t * 2 + k) * 20
        y = (t * 160 + k * 77) % (H + 60) - 30
        paste_c(im, emoji(["🌸", "🎉", "✨", "💖"][k % 4], 30), x, y, alpha=0.7)
    a = ease(t / 0.5)
    shadow_box(im, (190, 70 + (1 - a) * 40, 1090, 640 + (1 - a) * 40), 40, WHITE)
    d = ImageDraw.Draw(im)
    oy = (1 - a) * 40
    text_c(d, (640, 130 + oy), "KẾT QUẢ LƯỢT · ĐỘI 2", font(BLACK, 40), PINK_D)
    text_c(d, (640, 215 + oy), f"{sim.correct} lần chăm đúng × {X_POINTS} = {sim.score} điểm", font(BOLD, 34), INK)
    rows = [("Đội 1", "95"), ("Đội 2", str(sim.score)), ("Đội 3", "chờ lượt"), ("Đội 4", "chờ lượt"), ("Đội 5", "chờ lượt")]
    for k, (tm, sc) in enumerate(rows):
        y = 270 + k * 56 + oy
        hl = tm == "Đội 2"
        d.rounded_rectangle((330, y, 950, y + 46), 23, fill=((255, 222, 236) if hl else (246, 240, 252)), outline=(PINK_D if hl else None), width=3 if hl else 0)
        text_c(d, (360, y + 23), tm, font(BOLD, 24), INK, anchor="lm")
        text_c(d, (640, y + 23), "Vòng 1", font(REG, 20), LAV_D)
        text_c(d, (920, y + 23), sc, font(BLACK if sc.isdigit() else REG, 26 if sc.isdigit() else 20), (MINT_D if sc.isdigit() else (150, 140, 160)), anchor="rm")
    text_c(d, (640, 600 + oy), "Số liệu minh họa — cỡ lưới, thời lượng, điểm X, hình phạt sẽ chốt sau playtest", font(REG, 18), (150, 120, 160))
    return im

def main():
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([exe, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                             "-preset", "medium", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    sim = Sim()
    n = int(TOTAL * FPS)
    for f in range(n):
        T = f / FPS
        if T < T_TITLE:
            im = scene_title(T)
        elif T < T_TITLE + T_ROLES:
            im = scene_roles(T - T_TITLE)
        elif T < T_GAME0:
            a = T - T_TITLE - T_ROLES
            im = game_frame(sim, 0, GAME_LEN, locked=True)
            overlay(im, 120)
            d = ImageDraw.Draw(im)
            k = int(a)
            s = ["3", "2", "1"][k] if k < 3 else ""
            sc = 1 + (a - k) * 0.6
            text_c(d, (640, 360), s, font(BLACK, int(160 * sc)), WHITE, stroke_width=6, stroke_fill=PINK_D)
        elif T < T_END:
            gt = T - T_GAME0
            sim.step(gt)
            im = game_frame(sim, gt, GAME_LEN - gt)
            if gt < 0.9:
                d = ImageDraw.Draw(im)
                al = int(255 * (1 - gt / 0.9))
                text_c(d, (410, 400), "BẮT ĐẦU!", font(BLACK, 90), (255, 255, 255, al), stroke_width=6, stroke_fill=(*PINK_D, al))
        elif T < T_END + T_TIMEUP:
            a = T - T_END
            sim.tool = sim.tool
            im = game_frame(sim, GAME_LEN + a, 0, locked=True)
            overlay(im, 110)
            d = ImageDraw.Draw(im)
            sc = ease(a / 0.4)
            text_c(d, (640, 330), "HẾT GIỜ!", font(BLACK, int(40 + 80 * sc)), WHITE, stroke_width=6, stroke_fill=RED)
            text_c(d, (640, 430), "Khóa điều khiển · chốt điểm", font(BOLD, 30), WHITE)
        else:
            im = scene_result(T - T_END - T_TIMEUP, sim)
        proc.stdin.write(im.convert("RGB").tobytes())
        if f % 300 == 0:
            print(f"frame {f}/{n}", flush=True)
    proc.stdin.close(); proc.wait()
    print("done", OUT, "score", sim.score, "correct", sim.correct)

if __name__ == "__main__":
    main()
