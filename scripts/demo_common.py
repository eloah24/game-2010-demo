"""Shared drawing helpers for the round demos (vong 2-4). Primitives come from demo_vong1."""
import math, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
from demo_vong1 import (W, H, FPS, font, emoji, paste_c, text_c, gradient, shadow_box, btn, tri, ease, overlay,
                        REG, SEMI, BOLD, BLACK, PINK, PINK_D, LAV, LAV_D, CREAM, MINT, MINT_D, INK, WHITE, RED)

PCOL = [PINK_D, LAV_D, MINT_D]
PHONES_X, PHONE_W, PHONE_H, PHONE_Y, PHONE_GAP = 868, 126, 330, 250, 11
PANEL = (36, 104, 784, 700)
PLAYERS = ["Lan", "Mai", "Hoa"]

def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def fmt(t):
    t = max(0, int(t))
    return f"{t // 60}:{t % 60:02d}"

def phone_box(i):
    x = PHONES_X + i * (PHONE_W + PHONE_GAP)
    return (x, PHONE_Y, x + PHONE_W, PHONE_Y + PHONE_H)

def fit_font(d, s, name, size, maxw):
    while size > 12 and d.textlength(s, font=font(name, size)) > maxw:
        size -= 1
    return font(name, size)

def make_bg(panel_title, panel_fill=(236, 250, 238), outline=MINT, lane_label="cổ vũ", seed=7):
    rnd = random.Random(seed)
    bg = gradient(W, H, (255, 228, 238), (232, 222, 255))
    d = ImageDraw.Draw(bg)
    for _ in range(40):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(2, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 120))
    shadow_box(bg, PANEL, 26, panel_fill, outline=outline, width=4)
    d = ImageDraw.Draw(bg)
    if panel_title:
        text_c(d, ((PANEL[0] + PANEL[2]) / 2, 127), panel_title, font(BLACK, 20), MINT_D)
    d.rounded_rectangle((800, 104, 852, 700), 24, fill=(255, 255, 255, 110))
    if lane_label:
        text_c(d, (826, 116), lane_label, font(SEMI, 13), LAV_D, anchor="mt")
    text_c(d, (W - 216, 615), "Điện thoại người chơi", font(SEMI, 19), LAV_D)
    return bg

def header(im, title, title_em, timer_txt, warn=False, right_label="ĐIỂM", right_val="0", team="Đội 2", timer_em="⏱️", tag=None):
    shadow_box(im, (36, 18, 470, 84), 30, WHITE)
    paste_c(im, emoji(title_em, 34), 76, 51)
    d = ImageDraw.Draw(im)
    text_c(d, (104, 51), title, fit_font(d, title, BLACK, 28, 350), PINK_D, anchor="lm")
    shadow_box(im, (488, 18, 760, 84), 30, LAV)
    d = ImageDraw.Draw(im)
    text_c(d, (624, 51), f"{team} đang chơi", font(BOLD, 24), WHITE)
    shadow_box(im, (800, 18, 1010, 84), 30, CREAM, outline=(RED if warn else (240, 210, 140)), width=3)
    paste_c(im, emoji(timer_em, 28), 836, 51)
    d = ImageDraw.Draw(im)
    text_c(d, (930, 52), timer_txt, fit_font(d, timer_txt, BLACK, 34, 140), RED if warn else INK)
    if tag:
        d.rounded_rectangle((850, 82, 1010, 104), 11, fill=LAV_D)
        text_c(d, (930, 93), tag, font(BOLD, 13), WHITE)
    shadow_box(im, (1028, 18, 1246, 84), 30, MINT)
    d = ImageDraw.Draw(im)
    text_c(d, (1052, 51), right_label, font(BOLD, 16), MINT_D, anchor="lm")
    text_c(d, (1228, 52), right_val, fit_font(d, right_val, BLACK, 36, 120), WHITE, anchor="rm", stroke_width=2, stroke_fill=MINT_D)

def phone_shell(im, i, role_desc, letter=None):
    """Draw phone i, return screen rect (sx0, sy0, sx1, sy1)."""
    x0, y0, x1, y1 = phone_box(i)
    shadow_box(im, (x0, y0, x1, y1), 22, (60, 40, 70))
    d = ImageDraw.Draw(im)
    sx0, sy0, sx1, sy1 = x0 + 6, y0 + 16, x1 - 6, y1 - 14
    d.rounded_rectangle((sx0, sy0, sx1, sy1), 16, fill=(255, 250, 252))
    d.rounded_rectangle(((x0 + x1) / 2 - 18, y0 + 6, (x0 + x1) / 2 + 18, y0 + 11), 3, fill=(30, 20, 35))
    d.ellipse((sx0 + 8, sy0 + 10, sx0 + 36, sy0 + 38), fill=PCOL[i])
    text_c(d, (sx0 + 22, sy0 + 24), letter or "ABC"[i], font(BLACK, 16), WHITE)
    text_c(d, (sx0 + 44, sy0 + 17), PLAYERS[i], font(BOLD, 16), INK, anchor="lm")
    text_c(d, (sx0 + 44, sy0 + 33), role_desc, font(REG, 11), LAV_D, anchor="lm")
    d.ellipse((sx0 + 10, sy1 - 22, sx0 + 20, sy1 - 12), fill=(60, 200, 120))
    text_c(d, (sx0 + 26, sy1 - 17), "Đã kết nối", font(REG, 11), (110, 110, 120), anchor="lm")
    return sx0, sy0, sx1, sy1

def lock_screen(im, rect, em="🔒"):
    sx0, sy0, sx1, sy1 = rect
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((sx0, sy0 + 50, sx1, sy1 - 28), 12, fill=(70, 50, 80, 150))
    im.alpha_composite(ov)
    paste_c(im, emoji(em, 34), (sx0 + sx1) / 2, (sy0 + sy1) / 2 + 6)

def draw_bubbles(im, bubbles, t):
    d = ImageDraw.Draw(im)
    for i, s, t0, dur in bubbles:
        a = t - t0
        if not (0 <= a < dur): continue
        x0, y0, x1, y1 = phone_box(i)
        cx = (x0 + x1) / 2
        f = font(BOLD, 17)
        tw = d.textlength(s, font=f) + 28
        bx0 = min(max(cx - tw / 2, 864), W - 16 - tw)
        by1 = PHONE_Y - 16 - (0 if a > 0.15 else (0.15 - a) * 60)
        d.rounded_rectangle((bx0, by1 - 42, bx0 + tw, by1), 20, fill=WHITE, outline=PCOL[i], width=3)
        d.polygon([(cx - 8, by1 - 1), (cx + 8, by1 - 1), (cx, by1 + 12)], fill=PCOL[i])
        text_c(d, (bx0 + tw / 2, by1 - 21), s, f, INK)

def draw_cheers(im, cheers, t):
    for t0, em in cheers:
        a = t - t0
        if 0 <= a < 3.0:
            paste_c(im, emoji(em, 34), 826 + math.sin(a * 3 + t0) * 10, 680 - a * 190, alpha=min(1, 3.0 - a))

def title_scene(t, sub, big_em, line3):
    im = gradient(W, H, (255, 214, 230), (222, 206, 255))
    for k in range(14):
        x = (k * 97 + t * 40) % (W + 100) - 50
        y = 80 + (k * 53) % 560 + math.sin(t * 2 + k) * 10
        paste_c(im, emoji(["🌸", "🌷", "💐", "✨"][k % 4], 36), x, y, alpha=0.6)
    a = ease(t / 0.6); oy = (1 - a) * 40
    shadow_box(im, (240, 190 + oy, 1040, 530 + oy), 40, WHITE)
    d = ImageDraw.Draw(im)
    paste_c(im, emoji(big_em, 70), 640, 255 + oy)
    text_c(d, (640, 340 + oy), "CỬA HÀNG HOA 20/10", font(BLACK, 54), PINK_D)
    text_c(d, (640, 405 + oy), sub, font(BOLD, 30), LAV_D)
    text_c(d, (640, 465 + oy), line3, font(REG, 22), INK)
    return im

def roles_scene(t, heading, sub, cards, rule_main, rule_sub):
    """cards: list of (letter, name, role, emoji, desc, color)."""
    im = gradient(W, H, (255, 228, 238), (232, 222, 255))
    d = ImageDraw.Draw(im)
    text_c(d, (640, 80), heading, font(BLACK, 42), PINK_D)
    text_c(d, (640, 128), sub, font(REG, 24), INK)
    for i, (r, n, role, em, desc, col) in enumerate(cards):
        a = ease((t - 0.3 - i * 0.35) / 0.5)
        if a <= 0: continue
        x0 = 110 + i * 360; y0 = 190 + (1 - a) * 60
        shadow_box(im, (x0, y0, x0 + 320, y0 + 300), 30, WHITE, outline=col, width=4)
        d = ImageDraw.Draw(im)
        d.ellipse((x0 + 125, y0 + 24, x0 + 195, y0 + 94), fill=col)
        text_c(d, (x0 + 160, y0 + 59), r, font(BLACK, 38), WHITE)
        text_c(d, (x0 + 160, y0 + 125), f"{n} · {role}", fit_font(d, f"{n} · {role}", BOLD, 26, 300), INK)
        paste_c(im, emoji(em, 60), x0 + 160, y0 + 200)
        text_c(d, (x0 + 160, y0 + 268), desc, fit_font(d, desc, REG, 19, 300), LAV_D)
    a = ease((t - 2.0) / 0.5)
    if a > 0:
        shadow_box(im, (160, 540, 1120, 660), 30, CREAM)
        d = ImageDraw.Draw(im)
        text_c(d, (640, 575), rule_main, fit_font(d, rule_main, BLACK, 30, 920), INK)
        text_c(d, (640, 625), rule_sub, fit_font(d, rule_sub, REG, 22, 920), LAV_D)
    return im

def countdown(im, a):
    overlay(im, 120)
    d = ImageDraw.Draw(im)
    k = int(a)
    if k < 3:
        sc = 1 + (a - k) * 0.6
        text_c(d, (640, 360), "321"[k], font(BLACK, int(160 * sc)), WHITE, stroke_width=6, stroke_fill=PINK_D)

def start_flash(im, gt, cx=410):
    if gt < 0.9:
        d = ImageDraw.Draw(im)
        al = int(255 * (1 - gt / 0.9))
        text_c(d, (cx, 400), "BẮT ĐẦU!", font(BLACK, 90), (255, 255, 255, al), stroke_width=6, stroke_fill=(*PINK_D, al))

def banner(im, a, text, sub, col):
    overlay(im, 110)
    d = ImageDraw.Draw(im)
    sc = ease(a / 0.4)
    text_c(d, (640, 330), text, font(BLACK, int(40 + 80 * sc)), WHITE, stroke_width=6, stroke_fill=col)
    text_c(d, (640, 430), sub, font(BOLD, 30), WHITE)

def result_scene(t, title, line, rows, note, highlight="Đội 2"):
    """rows: list of (team, middle, value, is_strong)."""
    im = gradient(W, H, (255, 214, 230), (222, 206, 255))
    for k in range(30):
        x = (k * 131) % W + math.sin(t * 2 + k) * 20
        y = (t * 160 + k * 77) % (H + 60) - 30
        paste_c(im, emoji(["🌸", "🎉", "✨", "💖"][k % 4], 30), x, y, alpha=0.7)
    a = ease(t / 0.5); oy = (1 - a) * 40
    shadow_box(im, (190, 70 + oy, 1090, 640 + oy), 40, WHITE)
    d = ImageDraw.Draw(im)
    text_c(d, (640, 130 + oy), title, font(BLACK, 40), PINK_D)
    text_c(d, (640, 212 + oy), line, fit_font(d, line, BOLD, 32, 840), INK)
    for k, (tm, mid, val, strong) in enumerate(rows):
        y = 270 + k * 56 + oy
        hl = tm == highlight
        d.rounded_rectangle((300, y, 980, y + 46), 23, fill=((255, 222, 236) if hl else (246, 240, 252)),
                            outline=(PINK_D if hl else None), width=3 if hl else 0)
        text_c(d, (330, y + 23), tm, font(BOLD, 24), INK, anchor="lm")
        text_c(d, (640, y + 23), mid, font(REG, 20), LAV_D)
        text_c(d, (950, y + 23), val, font(BLACK if strong else REG, 26 if strong else 20),
               MINT_D if strong else (150, 140, 160), anchor="rm")
    text_c(d, (640, 600 + oy), note, fit_font(d, note, REG, 18, 860), (150, 120, 160))
    return im

def encode(out, total, frame_fn):
    import os
    pv = os.environ.get("PREVIEW")
    if pv:  # PREVIEW="12,30.5" -> save PNG stills only (still steps every frame for stateful sims)
        times = sorted(float(x) for x in pv.split(","))
        n = int(min(total, times[-1] + 0.05) * FPS) + 1
        base = out.rsplit(".", 1)[0]
        for f in range(n):
            im = frame_fn(f / FPS)
            for tm in times:
                if f == int(tm * FPS):
                    im.convert("RGB").save(f"{base}_{tm:g}.png")
        print("preview", total)
        return
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([exe, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                             "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    n = int(total * FPS)
    for f in range(n):
        im = frame_fn(f / FPS)
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    print("done", out, f"{total:.1f}s")
