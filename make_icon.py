#!/usr/bin/env python3
"""Gera o icon.png do TypeClipboard (1024x1024).

Uso:  python3 make_icon.py
Requer: pip3 install pillow
"""

from PIL import Image, ImageDraw

S = 1024
SS = 4  # supersampling
W = S * SS

# ---------------------------------------------------------------- paleta
BG_TOP = (56, 78, 168)
BG_BOTTOM = (26, 32, 64)
CLIP_BODY = (245, 247, 252)
CLIP_EDGE = (206, 213, 230)
CLIP_TOP = (150, 160, 190)
DOT = (58, 66, 96)
CARET = (74, 222, 128)
ACCENT = (99, 132, 255)


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius, fill=255)
    return m


def vertical_gradient(size, top, bottom):
    g = Image.new("RGB", (1, size))
    px = g.load()
    for y in range(size):
        t = y / (size - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return g.resize((size, size))


# ---------------------------------------------------------------- fundo
bg = vertical_gradient(W, BG_TOP, BG_BOTTOM).convert("RGBA")

# brilho diagonal suave no canto superior esquerdo
glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for i in range(60):
    a = int(26 * (1 - i / 60))
    gd.ellipse(
        [-W * 0.35 + i * 6, -W * 0.45 + i * 6, W * 0.75 - i * 6, W * 0.55 - i * 6],
        fill=(255, 255, 255, a),
    )
bg = Image.alpha_composite(bg, glow)

icon = Image.new("RGBA", (W, W), (0, 0, 0, 0))
icon.paste(bg, (0, 0), rounded_mask(W, int(W * 0.225)))

d = ImageDraw.Draw(icon)

# ---------------------------------------------------------------- clipboard
cx = W // 2
cw, ch = int(W * 0.50), int(W * 0.60)
cl, ct = cx - cw // 2, int(W * 0.235)
cr, cb = cl + cw, ct + ch
r = int(W * 0.055)

# sombra
d.rounded_rectangle([cl, ct + int(W * 0.018), cr, cb + int(W * 0.018)],
                    r, fill=(10, 14, 34, 110))
# corpo
d.rounded_rectangle([cl, ct, cr, cb], r, fill=CLIP_BODY,
                    outline=CLIP_EDGE, width=int(W * 0.006))

# presilha de metal no topo
gw, gh = int(cw * 0.42), int(W * 0.075)
gl, gt = cx - gw // 2, ct - gh // 2
d.rounded_rectangle([gl, gt, gl + gw, gt + gh], int(gh * 0.42),
                    fill=CLIP_TOP)
d.rounded_rectangle([gl + int(gw * 0.16), gt - int(gh * 0.30),
                     gl + gw - int(gw * 0.16), gt + int(gh * 0.30)],
                    int(gh * 0.32), fill=CLIP_TOP)

# ---------------------------------------------------------------- conteudo
pad = int(cw * 0.155)
line_y = ct + int(ch * 0.44)

# pontinhos de senha
dot_r = int(W * 0.0255)
gap = int(W * 0.075)
start_x = cl + pad + dot_r
for i in range(4):
    x = start_x + i * gap
    d.ellipse([x - dot_r, line_y - dot_r, x + dot_r, line_y + dot_r], fill=DOT)

# cursor piscando logo apos os pontos
car_x = start_x + 4 * gap - int(gap * 0.18)
car_h = int(W * 0.095)
car_w = int(W * 0.020)
d.rounded_rectangle([car_x, line_y - car_h // 2, car_x + car_w, line_y + car_h // 2],
                    int(car_w * 0.35), fill=CARET)

# duas linhas de "texto" abaixo, sugerindo o campo
lb_h = int(W * 0.016)
for i, frac in enumerate((0.78, 0.52)):
    y = line_y + int(W * 0.105) + i * int(W * 0.055)
    d.rounded_rectangle([cl + pad, y, cl + pad + int((cw - 2 * pad) * frac), y + lb_h],
                        lb_h // 2, fill=(196, 204, 224))

# ---------------------------------------------------------------- finaliza
icon = icon.resize((S, S), Image.LANCZOS)
icon.save("icon.png")

# preview menor, so para conferir como fica no Dock
icon.resize((128, 128), Image.LANCZOS).save("icon-preview.png")
print("icon.png gerado (1024x1024)")
