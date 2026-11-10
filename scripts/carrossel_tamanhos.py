"""Carrossel 'Qual tamanho de container escolher?' — MLA Containers, 7 slides 1080x1350."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
BG = (28, 31, 39)
ORANGE = (255, 122, 26)
BLUE = (77, 163, 255)
TEAL = (45, 212, 191)
WHITE = (255, 255, 255)
FONTS = "C:/Windows/Fonts/"
HEAVY = FONTS + "seguibli.ttf"
BOLD = FONTS + "segoeuib.ttf"
REG = FONTS + "segoeui.ttf"
SEMI = FONTS + "seguisb.ttf"
SRC = Path("C:/Users/Anderson ALS/OneDrive - Luara Mel Vieira/Área de Trabalho/criativos-containers")
OUT = Path(__file__).resolve().parent.parent / "media" / "tamanhos"
OUT.mkdir(parents=True, exist_ok=True)
TOTAL = 7


def font(p, s):
    return ImageFont.truetype(p, s)


def fit(draw, text, path, max_w, size):
    while size > 20 and draw.textlength(text, font=font(path, size)) > max_w:
        size -= 2
    return font(path, size)


def shadow_text(d, xy, text, f, fill=WHITE, off=4):
    x, y = xy
    d.text((x + off, y + off), text, font=f, fill=(0, 0, 0))
    d.text((x, y), text, font=f, fill=fill)


def photo_top(img, path, box, height=720):
    """Foto no topo com fade para o fundo escuro e linha laranja diagonal."""
    im = Image.open(path).convert("RGB").crop(box).resize((W, height), Image.LANCZOS)
    img.paste(im, (0, 0))
    fade = Image.new("L", (W, height), 0)
    fd = ImageDraw.Draw(fade)
    for y in range(height):
        a = 0 if y < height - 150 else int(255 * (y - (height - 150)) / 150)
        fd.line([(0, y), (W, y)], fill=a)
    img.paste(Image.new("RGB", (W, height), BG), (0, 0), fade)
    d = ImageDraw.Draw(img)
    d.line([(0, height + 38), (W, height - 40)], fill=ORANGE, width=6)


def pill(d, xy, text, f, fill, color=(20, 20, 20), pad=(34, 14)):
    w = d.textlength(text, font=f)
    x, y = xy
    h = f.size + pad[1] * 2
    d.rounded_rectangle([x, y, x + w + pad[0] * 2, y + h], radius=h // 2, fill=fill)
    d.text((x + pad[0], y + pad[1] - 4), text, font=f, fill=color)
    return x + w + pad[0] * 2, y + h


def chrome(img, n, tag):
    d = ImageDraw.Draw(img)
    pill(d, (75, 50), tag, font(HEAVY, 34), ORANGE)
    shadow_text(d, (W - 120, 78), f"{n}/{TOTAL}", font(BOLD, 36), off=2)
    # rodape
    d.text((75, 1252), "Itajaí/SC · frete sob consulta", font=font(REG, 30), fill=(200, 205, 215))
    d.polygon([(640, 1310), (585, 1310), (640, 1218), (W, 1218), (W, 1310)], fill=ORANGE)
    d.text((672, 1232), "Chame no WhatsApp", font=font(REG, 26), fill=(20, 20, 20))
    d.text((672, 1256), "(47) 98917-3801", font=font(HEAVY, 44), fill=(20, 20, 20))


def ilus(img, y=640):
    d = ImageDraw.Draw(img)
    f = font(SEMI, 26)
    t = "Imagem ilustrativa"
    w = d.textlength(t, font=f)
    d.rounded_rectangle([W - w - 80, y, W - 40, y + 44], radius=22, fill=(0, 0, 0))
    d.text((W - w - 60, y + 4), t, font=f, fill=WHITE)


def spec_slide(n, tag, title, sub, color, photo, box, lines, price, illus):
    img = Image.new("RGB", (W, H), BG)
    photo_top(img, photo, box)
    d = ImageDraw.Draw(img)
    chrome(img, n, tag)
    if illus:
        ilus(img)
    shadow_text(d, (75, 745), title, fit(d, title, HEAVY, 930, 120))
    shadow_text(d, (75, 880), sub, fit(d, sub, HEAVY, 930, 62), fill=ORANGE, off=3)
    y = 965
    for ln in lines:
        d.rectangle([75, y + 14, 91, y + 30], fill=color)
        d.text((108, y), ln, font=fit(d, ln, SEMI, 900, 36), fill=WHITE)
        y += 52
    pill(d, (75, 1130), price, font(HEAVY, 40), color)
    return img


# ---------- 1 capa
def capa():
    img = Image.new("RGB", (W, H), BG)
    photo_top(img, SRC / "SEM_EVERGREEN/03_lateral_aberta_edit.png", (360, 250, 2160, 1517), 760)
    d = ImageDraw.Draw(img)
    chrome(img, 1, "GUIA RÁPIDO")
    shadow_text(d, (75, 790), "QUAL TAMANHO", fit(d, "QUAL TAMANHO", HEAVY, 930, 112))
    shadow_text(d, (75, 905), "DE CONTAINER", fit(d, "DE CONTAINER", HEAVY, 930, 112))
    shadow_text(d, (75, 1020), "ESCOLHER?", fit(d, "ESCOLHER?", HEAVY, 930, 112), fill=ORANGE)
    d.text((75, 1160), "20 pés · 40 Dry · 40 HC  —  arraste e descubra  →", font=fit(d, "20 pés · 40 Dry · 40 HC  —  arraste e descubra  →", SEMI, 930, 34), fill=WHITE)
    return img


# ---------- 5 comparativo
def comparativo():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chrome(img, 5, "COMPARATIVO")
    shadow_text(d, (75, 160), "COMPARE EM", fit(d, "COMPARE EM", HEAVY, 930, 100))
    shadow_text(d, (75, 270), "10 SEGUNDOS", fit(d, "10 SEGUNDOS", HEAVY, 930, 100), fill=ORANGE)
    rows = [
        ("20 pés", BLUE, "~14 m²", "~33 m³", "~2,39 m", "R$ 6.500"),
        ("40 Dry", TEAL, "~28 m²", "~67 m³", "~2,39 m", "R$ 8.200"),
        ("40 HC", ORANGE, "~28 m²", "~76 m³", "~2,69 m", "R$ 8.500"),
    ]
    cols = [75, 285, 445, 610, 790]
    hdr = ["", "Piso", "Volume", "Altura", "A partir de"]
    for x, t in zip(cols, hdr):
        d.text((x, 410), t, font=font(SEMI, 28), fill=(200, 205, 215))
    y = 460
    for name, c, piso, vol, alt, preco in rows:
        d.rounded_rectangle([60, y, W - 60, y + 150], radius=26, fill=c)
        d.text((cols[0], y + 40), name, font=font(HEAVY, 44), fill=(20, 20, 20))
        for x, t in zip(cols[1:], (piso, vol, alt, preco)):
            d.text((x, y + 48), t, font=fit(d, t, BOLD, 190, 36), fill=(20, 20, 20))
        y += 175
    d.text((75, 1000), "Medidas internas aproximadas. Cada unidade é única:", font=font(REG, 30), fill=(200, 205, 215))
    d.text((75, 1040), "tipo, ano e detalhes variam. Confirme na visita.", font=font(REG, 30), fill=(200, 205, 215))
    d.text((75, 1100), "HC = High Cube: cerca de 30 cm mais alto que o Dry.", font=font(SEMI, 30), fill=WHITE)
    return img


# ---------- 6 como escolher
def escolher():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    chrome(img, 6, "COMO ESCOLHER")
    shadow_text(d, (75, 160), "QUAL É O", fit(d, "QUAL É O", HEAVY, 930, 100))
    shadow_text(d, (75, 270), "IDEAL PRA VOCÊ?", fit(d, "IDEAL PRA VOCÊ?", HEAVY, 930, 100), fill=ORANGE)
    cards = [
        (BLUE, "20 PÉS", "Pouco espaço, obra, depósito pequeno,", "quiosque ou ateliê."),
        (TEAL, "40 DRY", "Mais espaço pelo melhor custo: loja,", "depósito grande ou casa compacta."),
        (ORANGE, "40 HC", "Quer morar, climatizar ou precisa de", "pé-direito alto: casa, loja, estúdio."),
    ]
    y = 430
    for c, t, l1, l2 in cards:
        d.rounded_rectangle([60, y, W - 60, y + 220], radius=26, fill=(41, 45, 56))
        d.rounded_rectangle([60, y, 84, y + 220], radius=12, fill=c)
        d.text((115, y + 22), t, font=font(HEAVY, 54), fill=c)
        d.text((115, y + 108), l1, font=fit(d, l1, SEMI, 880, 33), fill=WHITE)
        d.text((115, y + 154), l2, font=fit(d, l2, SEMI, 880, 33), fill=WHITE)
        y += 250
    return img


# ---------- 7 chamada
def chamada():
    img = Image.new("RGB", (W, H), BG)
    photo_top(img, SRC / "fotos-tratadas/04_interior_1.jpg", (0, 300, 1200, 922), 560)
    d = ImageDraw.Draw(img)
    chrome(img, 7, "FALE COM A GENTE")
    shadow_text(d, (75, 610), "NÃO SABE", fit(d, "NÃO SABE", HEAVY, 930, 110))
    shadow_text(d, (75, 725), "QUAL ESCOLHER?", fit(d, "QUAL ESCOLHER?", HEAVY, 930, 110), fill=ORANGE)
    d.text((75, 870), "Conte o seu projeto e a gente indica o ideal.", font=fit(d, "Conte o seu projeto e a gente indica o ideal.", SEMI, 930, 38), fill=WHITE)
    d.text((75, 925), "Visita agendada no pátio, antes de comprar.", font=fit(d, "Visita agendada no pátio, antes de comprar.", SEMI, 930, 38), fill=WHITE)
    pill(d, (75, 1010), "WhatsApp (47) 98917-3801", font(HEAVY, 46), ORANGE)
    d.text((75, 1130), "Av. Gov. Adolfo Konder, 2600 · São Vicente · Itajaí/SC", font=fit(d, "Av. Gov. Adolfo Konder, 2600 · São Vicente · Itajaí/SC", REG, 930, 32), fill=(200, 205, 215))
    return img


slides = [
    capa(),
    spec_slide(2, "TAMANHO 1", "20 PÉS", "O COMPACTO", BLUE, SRC / "SEM_EVERGREEN/20pes_edit.png", (396, 240, 2196, 1440),
               ["Piso: cerca de 14 m²  ·  Volume: cerca de 33 m³",
                "Ideal para: depósito, obra, quiosque, ateliê"], "a partir de R$ 6.500", True),
    spec_slide(3, "TAMANHO 2", "40 DRY", "ESPAÇO COM ÓTIMO CUSTO", TEAL, SRC / "SEM_EVERGREEN/40dry_edit.png", (120, 120, 2280, 1560),
               ["Piso: cerca de 28 m²  ·  Volume: cerca de 67 m³",
                "Ideal para: loja, depósito grande, casa compacta"], "a partir de R$ 8.200", True),
    spec_slide(4, "TAMANHO 3", "40 HC", "HIGH CUBE: MAIS ALTO", ORANGE, SRC / "SEM_EVERGREEN/03_lateral_aberta_edit.png", (360, 300, 2160, 1500),
               ["Piso: cerca de 28 m²  ·  Volume: cerca de 76 m³",
                "Cerca de 30 cm mais alto que o Dry",
                "Ideal para: casa, loja, estúdio"], "a partir de R$ 8.500", False),
    comparativo(), escolher(), chamada(),
]
for i, s in enumerate(slides, 1):
    s.save(OUT / f"slide_{i}.jpg", quality=93)
print("OK", len(slides), "slides ->", OUT)
