# renderer.py
import os
import pygame

# ---------- Cores ----------
COLORS = {
    "background": (26, 26, 26),
    "white": (255, 255, 255),
    "grey": (170, 170, 170),
    "dark_grey": (40, 40, 40),
    "border_red": (255, 0, 4),
    "border_green": (57, 255, 20),
    "text_green": (57, 255, 20),
    "text_yellow": (255, 255, 0),
    "text_blue": (0, 191, 255),
    "rpm_blue": (0, 128, 255), "rpm_dk_green": (0, 128, 0), "rpm_lt_green": (0, 255, 0),
    "rpm_yellow": (255, 255, 0), "rpm_orange": (255, 128, 0), "rpm_red": (255, 0, 0),
    "pedal_green": (0, 255, 0), "pedal_red": (255, 0, 0),
    "temp_blue": (0, 191, 255), "temp_green": (57, 255, 20),
    "temp_yellow": (255, 215, 0), "temp_red": (255, 7, 58),
}
FONTS = {}
IMAGES = {}

# ---------- Paths ----------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def _apath(*parts): return os.path.join(_BASE_DIR, *parts)

def _load_image(name, size=None):
    surf = pygame.image.load(_apath("assets", "images", name)).convert_alpha()
    if size is not None:
        surf = pygame.transform.smoothscale(surf, size)
    return surf

# ---------- Gradiente por “stops” ----------
TEMP_COLOR_STOPS = [
    (0.00, (0x14, 0x66, 0xFF)),
    (0.25, (0x2B, 0x8E, 0x95)),
    (0.50, (0x41, 0xB6, 0x2C)),
    (0.75, (0xBA, 0xA0, 0x17)),
    (1.00, (0xFF, 0x00, 0x04)),
]
def _lerp(a, b, t): return a + (b - a) * t
def _lerp_color(c1, c2, t):
    return (int(_lerp(c1[0], c2[0], t)),
            int(_lerp(c1[1], c2[1], t)),
            int(_lerp(c1[2], c2[2], t)))
def _color_from_stops(stops, t):
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]; p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            u = (t - p0) / (p1 - p0) if p1 > p0 else 0
            return _lerp_color(c0, c1, u)
    return stops[-1][1]


# --------- gradientes auxiliares (LEDs RPM / SOC pílulas) ----------
def _grad_blue_to_darkgreen(t):
    c0, c1 = (0x78, 0xFF, 0x5E), (0x1B, 0x81, 0x07)
    return _lerp_color(c0, c1, max(0.0, min(1.0, t)))

def _grad_yellow_to_brown(t):
    c0, c1 = (0xFF, 0xDE, 0x2C), (0x70, 0x5E, 0x01)
    return _lerp_color(c0, c1, max(0.0, min(1.0, t)))

def _grad_red_to_darkred(t):
    c0, c1 = (0xFF, 0x38, 0x3C), (0x67, 0x02, 0x04)
    return _lerp_color(c0, c1, max(0.0, min(1.0, t)))

def _grad_red_yellow_green_pos(frac):
    # 0 -> vermelho (#FF0000), ~0.394 -> amarelo (#FFD900), 1 -> verde (#41B62C)
    if frac <= 0.394231:
        u = frac / 0.394231
        c0, c1 = (255, 0, 0), (255, 217, 0)
    else:
        u = (frac - 0.394231) / (1 - 0.394231)
        c0, c1 = (255, 217, 0), (0x41, 0xB6, 0x2C)
    return _lerp_color(c0, c1, u)

# ---------- Carregamento de assets ----------
def load_assets():
    try:
        pygame.font.init()
        FONTS["speed_num"]     = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 140)
        FONTS["soc_title"]     = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 64)
        FONTS["rpm_num"]       = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 80)
        FONTS["speed_unit"]    = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 36)
        FONTS["rpm_unit"]      = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 24)
        FONTS["pedal_letters"] = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 24)
        FONTS["lap_num"]       = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 20)
        FONTS["soc_num"]       = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 20)
        FONTS["tyre_loc"]      = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 16)
        FONTS["temp_value"]    = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 16)
        FONTS["alert_text"]    = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 16)
        FONTS["lap_title"]     = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 14)
        FONTS["speed_mode"]    = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 14)
        FONTS["tyre_info"]     = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 14)
        FONTS["temp_labels"]   = pygame.font.Font(_apath("assets","fonts","Orbitron-Bold.ttf"), 12)

        IMAGES["battery_temp"] = _load_image("icon_battery_temp.png", (24, 24))
        IMAGES["engine_temp"]  = _load_image("icon_engine_temp.png",  (24, 24))
        IMAGES["bms"]           = _load_image("icon_bms.png",            (36, 36))
        IMAGES["inverter"]      = _load_image("icon_inverter.png",       (36, 36))
        IMAGES["battery_fault"] = _load_image("icon_battery_fault.png",  (36, 36))
        IMAGES["engine_fault"]  = _load_image("icon_engine_fault.png",   (36, 36))
        IMAGES["logo_utforce"]  = _load_image("logo_utforce.png", (83, 83))
        IMAGES["chassis"] = _load_image("chassis_f1.png")  # escala será feita no draw

    except Exception as e:
        print(f"[renderer] Erro ao carregar assets: {e}. Usando fallbacks.")
        for k, size in {
            "speed_num":96,"soc_title":64,"rpm_num":64,"speed_unit":36,"rpm_unit":24,
            "pedal_letters":24,"lap_num":20,"soc_num":20,"tyre_loc":16,"temp_value":16,
            "alert_text":16,"lap_title":14,"speed_mode":14,"tyre_info":14,"temp_labels":12
        }.items():
            FONTS[k] = pygame.font.SysFont("Arial", size, bold=True)

# ---------- desenhar texto com contorno ----------
def draw_text_with_outline(font, text, fg_color, outline_color, surface, center, outline_width=2):
    text_surf = font.render(text, True, fg_color)
    outline_surf = font.render(text, True, outline_color)
    rect = text_surf.get_rect(center=center)
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                surface.blit(outline_surf, rect.move(dx, dy))
    surface.blit(text_surf, rect)

# ---------- pílula elíptica (LED RPM/SOC antigo) ----------
def _draw_gradient_pill(surface, center, rx, ry, color_fn, lit=True):
    w = int(rx * 2); h = int(ry * 2)
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    if lit:
        for y in range(h):
            t = y / max(1, h-1)
            c = color_fn(t)
            pygame.draw.line(pill, c, (0, y), (w-1, y))
    else:
        pill.fill((60,60,60))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255,255,255,255), (0,0,w,h))
    pill.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    rect = pill.get_rect(center=center)
    surface.blit(pill, rect)

# ---------- RPM bar (pílulas) ----------
def draw_rpm_bar(surface, data):
    """
    Strip de LEDs estilo SVG (916x26) em (54,10).
    20 elipses com raios e cores idênticos ao SVG fornecido.
    """
    # topo-esquerda do canvas dos LEDs
    ox, oy = 54, 10

    # centros X do SVG (em um canvas de 916 de largura) e raios X específicos
    # (ry é 13 para todos)
    cx_list = [
        16.6081, 62.5997, 109.23, 155.861, 201.852,
        248.483, 295.113, 341.105, 388.374, 434.365,
        480.996, 527.626, 573.618, 620.248, 666.879,
        712.87, 760.139, 806.77, 853.4, 899.392
    ]
    rx_list = [
        16.6081, 16.6081, 15.9693, 16.6081, 16.6081,
        15.9693, 16.6081, 16.6081, 16.6081, 16.6081,
        15.9693, 16.6081, 16.6081, 15.9693, 16.6081,
        16.6081, 16.6081, 15.9693, 16.6081, 16.6081
    ]
    ry = 13

    # mapeamento de cor por índice conforme o SVG:
    # 0–4: azul sólido; 5–9: verde gradiente; 10–14: amarelo gradiente; 15–19: vermelho gradiente
    def color_fn_for_index(i):
        if i <= 4:
            return lambda t: (0x14, 0x66, 0xFF)  # azul sólido
        if 5 <= i <= 9:
            return _grad_blue_to_darkgreen
        if 10 <= i <= 14:
            return _grad_yellow_to_brown
        return _grad_red_to_darkred

    # quantos LEDs acesos (0..20)
    lit = int(round(20 * max(0.0, min(1.0, data.rpm / 12000.0))))

    # desenha
    for i, (cx, rx) in enumerate(zip(cx_list, rx_list)):
        cx_abs = int(ox + cx)      # x absoluto no surface
        cy_abs = oy + ry           # y absoluto no surface
        _draw_gradient_pill(
            surface,
            (cx_abs, cy_abs),
            rx, ry,
            color_fn_for_index(i),
            lit=(i < lit)
        )

def draw_rpm_display(surface, data, pos):
    rect = pygame.Rect(pos, (298, 159))
    pygame.draw.rect(surface, COLORS["background"], rect, border_radius=15)
    pygame.draw.rect(surface, (255,0,4), rect, width=2, border_radius=15)
    draw_text_with_outline(FONTS["rpm_num"], f"{data.rpm}", COLORS["white"], (255,0,4), surface, (rect.centerx, rect.centery - 10))
    draw_text_with_outline(FONTS["rpm_unit"], "RPM", COLORS["grey"], (255,0,4), surface, (rect.centerx, rect.centery + 45))

def draw_speed_display(surface, data, pos):
    rect = pygame.Rect(pos, (365, 210))
    pygame.draw.rect(surface, COLORS["background"], rect, border_radius=15)
    pygame.draw.rect(surface, (255,0,4), rect, width=2, border_radius=15)
    draw_text_with_outline(FONTS["speed_num"], f"{data.speed}", COLORS["white"], (255,0,4), surface, (rect.centerx, rect.centery - 30))
    draw_text_with_outline(FONTS["speed_unit"], "Km/h", COLORS["white"], (255,0,4), surface, (rect.centerx, rect.centery + 60))
    draw_text_with_outline(FONTS["speed_mode"], data.mode, COLORS["grey"], (255,0,4), surface, (rect.centerx, rect.bottom - 25))

# ---------- SOC NOVO (SVG 515x102 em 255,478) ----------
def _hgrad_fill(surface, rect, stops):
    """Preenche rect com gradiente horizontal baseado em stops [(pos,color), ...]."""
    x0 = rect.x
    for x in range(rect.width):
        t = x / max(1, rect.width - 1)
        color = _color_from_stops(stops, t)
        pygame.draw.line(surface, color, (x0 + x, rect.y), (x0 + x, rect.bottom-1))

def _rounded_rect_mask(size, radius):
    w, h = size
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), (0,0,w,h), border_radius=radius)
    return mask

def draw_soc(surface, data, pos):
    # medidas do SVG
    outer = pygame.Rect(pos, (515, 102))

    # Título "SOC" à esquerda, verticalmente centralizado na metade superior
    soc_text = FONTS["soc_title"].render("SOC", True, COLORS["white"])
    # alinhado com a esquerda da caixa e um pequeno offset
    surface.blit(soc_text, soc_text.get_rect(midleft=(outer.left + 8, outer.top + 30)))

    # Delta kW (sem colisões; encaixado à direita do texto)
    delta_color = (0,255,0) if data.power_delta >= 0 else (255,0,0)
    sign = "+" if data.power_delta >= 0 else ""
    delta_surf = FONTS["soc_num"].render(f"{sign}{data.power_delta:.1f}kW", True, delta_color)
    surface.blit(delta_surf, delta_surf.get_rect(midleft=(soc_text.get_rect(midleft=(outer.left + 8, outer.top + 30)).right + 10,
                                                          outer.top + 38)))

    # Barra (parte inferior) — área 517x42, borda vermelha, cantos 11px
    bar = pygame.Rect(outer.left, outer.bottom - 44, 515, 42)
    radius = 11

    # fundo escuro + borda
    pygame.draw.rect(surface, COLORS["background"], bar, border_radius=radius)
    pygame.draw.rect(surface, (255,0,4), bar, width=2, border_radius=radius)

    # gradiente horizontal como no SVG (vermelho->amarelo->verde)
    grad_stops = [(0.0, (255,0,0)), (0.394231, (255,217,0)), (1.0, (0x41,0xB6,0x2C))]
    # superfície do gradiente com máscara arredondada
    grad = pygame.Surface(bar.size, pygame.SRCALPHA)
    _hgrad_fill(grad, grad.get_rect(), grad_stops)
    mask = _rounded_rect_mask(bar.size, radius)
    grad.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    # preencher proporcional ao SOC (0..1), mantendo canto esquerdo arredondado
    ratio = max(0.0, min(1.0, float(data.soc)))
    fill_w = int(bar.width * ratio)
    if fill_w > 0:
        fill_slice = grad.subsurface((0, 0, fill_w, bar.height))
        surface.blit(fill_slice, bar.topleft)

    # divisórias vermelhas nas mesmas posições do SVG (ajustadas ao retângulo atual)
    # x relativos do SVG para 515px: [53.391, 104.781, 156.172, 207.563, 258.953, 310.344, 361.735, 413.125, 464.516]
    ticks = [53.391, 104.781, 156.172, 207.563, 258.953, 310.344, 361.735, 413.125, 464.516]
    for tx in ticks:
        x = int(bar.left + tx)
        pygame.draw.line(surface, (255,0,4), (x, bar.top+1), (x, bar.bottom-1), 1)

def draw_laps(surface, data, pos):
    rect = pygame.Rect(pos, (150, 200))
    pygame.draw.rect(surface, COLORS["background"], rect, border_radius=15)
    pygame.draw.rect(surface, COLORS["border_red"], rect, width=2, border_radius=15)
    y = rect.y + 14
    for key, title, color in [
        ("best", "Melhor volta", "text_green"),
        ("previous", "Volta Anterior", "text_yellow"),
        ("current", "Volta Atual", "text_blue"),
    ]:
        title_surf = FONTS["lap_title"].render(title, True, COLORS[color])
        surface.blit(title_surf, (rect.x + 16, y)); y += 24
        value_surf = FONTS["lap_num"].render(data.lap_data[key], True, COLORS["white"])
        surface.blit(value_surf, (rect.x + 16, y)); y += 34

# ---------- Temperaturas ----------
# ---------- Temperaturas (v2 — barras sem ícones, cor por faixa 0/25/50/75/100) ----------
# cores dos steps (iguais ao SVG)
TEMP_STEP_COLORS = {
    0.00: (0x14, 0x66, 0xFF),  # 0%   #1466FF
    0.25: (0x2B, 0x8E, 0x96),  # 25%  #2B8E96
    0.50: (0x41, 0xB6, 0x2C),  # 50%  #41B62C
    0.75: (0xBA, 0xA0, 0x17),  # 75%  #BAA017
    1.00: (0xFF, 0x00, 0x04),  # 100% #FF0004
}

def _temp_color_by_pct(p):
    p = max(0.0, min(1.0, p))
    if p < 0.25:   return TEMP_STEP_COLORS[0.00]
    if p < 0.50:   return TEMP_STEP_COLORS[0.25]
    if p < 0.75:   return TEMP_STEP_COLORS[0.50]
    if p < 1.00:   return TEMP_STEP_COLORS[0.75]
    return TEMP_STEP_COLORS[1.00]

def draw_temperature_bar(surface, value, vmin, vmax, topleft, size=(34,138), radius=10,
                         outline_color=(255,255,255), bg_color=(26,26,26), outline_width=2,
                         show_ticks=False, show_side_labels=True, min_color=(255,255,255),
                         max_color=(255,0,4), min_side="left", max_side="right"):
    import pygame
    x, y = topleft
    w, h = size
    rect = pygame.Rect(x, y, w, h)

    # fundo + contorno
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
    if outline_width > 0:
        pygame.draw.rect(surface, outline_color, rect, width=outline_width, border_radius=radius)

    # % preenchida
    span = max(1e-6, (vmax - vmin))
    pct  = max(0.0, min(1.0, (value - vmin) / span))
    fill_h = int((h - outline_width*2) * pct)

    # preenchimento com cor discreta por faixa
    if fill_h > 0:
        fill_color = _temp_color_by_pct(pct)
        fill_surf = pygame.Surface((w - outline_width*2, h - outline_width*2), pygame.SRCALPHA)
        pygame.draw.rect(fill_surf, fill_color, fill_surf.get_rect(), border_radius=radius-1)
        mask = pygame.Surface((w - outline_width*2, h - outline_width*2), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), mask.get_rect(), border_radius=radius-1)
        fill_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        visible = fill_surf.subsurface((0, (h - outline_width*2) - fill_h, w - outline_width*2, fill_h))
        surface.blit(visible, (x + outline_width, y + outline_width + (h - outline_width*2) - fill_h))

    # (opcional) linhas internas
    if show_ticks:
        for ty in (15, 29, 42, 55, 68):
            if 0 < ty < h:
                pygame.draw.line(surface, outline_color, (x+2, y+ty), (x+w-2, y+ty), 1)

    # legendas laterais (mín e máx) — lados configuráveis
    if show_side_labels:
        try:
            min_txt = FONTS["temp_labels"].render(f"{int(vmin)}°C", True, min_color)
            max_txt = FONTS["temp_labels"].render(f"{int(vmax)}°C", True, max_color)
        except:
            font = pygame.font.SysFont("Arial", 12, bold=True)
            min_txt = font.render(f"{int(vmin)}°C", True, min_color)
            max_txt = font.render(f"{int(vmax)}°C", True, max_color)

        # posições: mín = base; máx = topo
        if min_side == "left":
            surface.blit(min_txt, min_txt.get_rect(midright=(rect.left - 8, rect.bottom - 4)))
        else:  # right
            surface.blit(min_txt, min_txt.get_rect(midleft=(rect.right + 8, rect.bottom - 4)))

        if max_side == "left":
            surface.blit(max_txt, max_txt.get_rect(midright=(rect.left - 8, rect.top + 4)))
        else:  # right
            surface.blit(max_txt, max_txt.get_rect(midleft=(rect.right + 8, rect.top + 4)))


def _draw_top_icon(surface, centerx, top, img, badge=None):
    """Desenha um ícone acima da barra; se 'badge' for dado, desenha um fundo (ex.: falha)."""
    import pygame
    if not img:
        return
    icon_rect = img.get_rect(midtop=(centerx, top))
    if badge:
        pad = 6
        brect = icon_rect.inflate(pad*2, pad*2)
        pygame.draw.rect(surface, badge, brect, border_radius=8)
    surface.blit(img, icon_rect)

def draw_temperatures_box(surface, data, pos, size=(157,189),
                          bar_size=(34,138), gap=22,
                          battery_range=(20,60), engine_range=(20,110),
                          label_color=(255,255,255)):
    import pygame
    rect = pygame.Rect(pos, size)

    # centraliza as duas barras dentro da caixa
    total_w = bar_size[0]*2 + gap
    start_x = rect.centerx - total_w//2
    y       = rect.top + (rect.height - bar_size[1])//2

    # escolher ícones: se houver falha, usa o ícone de falha; senão, o ícone “normal”
    bat_fault = bool(getattr(data, "faults", {}).get("battery", False))
    eng_fault = bool(getattr(data, "faults", {}).get("engine",  False))
    bat_icon  = IMAGES.get("battery_fault") if bat_fault else IMAGES.get("battery_temp")
    eng_icon  = IMAGES.get("engine_fault")  if eng_fault else IMAGES.get("engine_temp")

    # bateria (esq)
    bx = start_x
    _draw_top_icon(surface, centerx=bx + bar_size[0]//2, top=y - 30,
                   img=bat_icon, badge=(255,0,0) if bat_fault else None)
    draw_temperature_bar(
        surface, data.battery_temp, battery_range[0], battery_range[1],
        (bx, y), size=bar_size, show_ticks=False, show_side_labels=True,
        min_side="left", max_side="left")

    # motor (dir)
    mx = start_x + bar_size[0] + gap
    _draw_top_icon(surface, centerx=mx + bar_size[0]//2, top=y - 30,
                   img=eng_icon, badge=(255,0,0) if eng_fault else None)
    draw_temperature_bar(
        surface, data.engine_temp, engine_range[0], engine_range[1],
        (mx, y), size=bar_size, show_ticks=False, show_side_labels=True,
        min_side="right", max_side="right")
    
    # rótulos pequenos abaixo (opcional)
    try:
        b = FONTS["temp_labels"].render("BAT", True, label_color)
        m = FONTS["temp_labels"].render("MOT", True, label_color)
        surface.blit(b, b.get_rect(center=(bx + bar_size[0]//2, y + bar_size[1] + 14)))
        surface.blit(m, m.get_rect(center=(mx + bar_size[0]//2, y + bar_size[1] + 14)))
    except:
        pass

# ---------- Pedais ----------
def draw_pedals(surface, data, pos):
    rect = pygame.Rect(pos, (67, 143))
    accel_label = FONTS["pedal_letters"].render("A", True, (0,255,0))
    brake_label = FONTS["pedal_letters"].render("F", True, (255,0,0))
    surface.blit(accel_label, accel_label.get_rect(centerx=rect.centerx - 15, top=rect.top))
    surface.blit(brake_label, brake_label.get_rect(centerx=rect.centerx + 15, top=rect.top))
    bar_width, bar_height = 25, rect.height - 40
    accel_bar_rect = pygame.Rect(rect.centerx - bar_width - 5, rect.bottom - bar_height, bar_width, bar_height)
    brake_bar_rect = pygame.Rect(rect.centerx + 5,           rect.bottom - bar_height, bar_width, bar_height)
    pygame.draw.rect(surface, (60,60,60), accel_bar_rect, border_radius=12)
    pygame.draw.rect(surface, (60,60,60), brake_bar_rect, border_radius=12)
    a_h = int(bar_height * (data.accelerator / 100))
    b_h = int(bar_height * (data.brake / 100))
    a_fill = pygame.Rect(accel_bar_rect.left, accel_bar_rect.bottom - a_h, bar_width, a_h)
    b_fill = pygame.Rect(brake_bar_rect.left,  brake_bar_rect.bottom - b_h, bar_width, b_h)
    pygame.draw.rect(surface, (0,255,0), a_fill, border_radius=12)
    pygame.draw.rect(surface, (255,0,0),   b_fill, border_radius=12)

# ---------- Pneus no visual do SVG ----------
def _state_color_temp(t):
    if t < 60:     return ( 40, 120, 255)
    if t < 80:     return (  0, 200,  80)
    if t < 95:     return (240, 200,  40)
    return (230,  60,  60)

def _state_color_pressure(p):
    if p < 8:      return ( 40, 120, 255)
    if p <= 12:    return (  0, 200,  80)
    if p <= 14:    return (240, 200,  40)
    return (230,  60,  60)

def _draw_tyre_svg(surface, x, y, w=40, h=82, color=(20,102,255)):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, COLORS["white"], rect, width=1, border_radius=5)
    lines = [15.371, 28.5968, 41.8226, 55.0484, 68.2742]
    for ly in lines:
        yy = y + int(ly / 82.0 * h)
        pygame.draw.line(surface, COLORS["white"], (x, yy), (x + w, yy), 1)

def draw_tyres(surface, data, pos):
    """
    Desenha a silhueta do carro (PNG) e posiciona os 4 pneus sobre as rodas.
    >>> PONTOS DE AJUSTE:
    1) POSIÇÃO DAS RODAS  -> edite o dicionário wheel_uv (coordenadas normalizadas 0..1)
    2) TAMANHO DAS RODAS  -> edite vis_w e vis_h
    3) TAMANHO DO PNG     -> edite a margem (margin) ou force um scale_factor
    """
    # área do widget (ajuste se quiser deslocar todo o bloco na tela)
    rect = pygame.Rect(pos, (300, 260))

    # --- desenha/centraliza o chassis ---
    car_png = IMAGES.get("chassis")
    if car_png:
        iw, ih = car_png.get_size()

        # (3) TAMANHO DO PNG ------------- EDITAR AQUI -------------------------
        margin = 6           # aumenta/diminui margens internas (mais margem = carro menor)
        scale_factor = 0.5# ex.: 0.90 para reduzir 10%; deixe None para ajustar automático
        # ----------------------------------------------------------------------

        sx = (rect.width  - 2*margin) / iw
        sy = (rect.height - 1.5*margin) / ih
        s  = min(sx, sy) if scale_factor is None else scale_factor
        car = pygame.transform.smoothscale(car_png, (int(iw*s), int(ih*s)))
        car_rect = car.get_rect(center=rect.center)
        surface.blit(car, car_rect.topleft)
    else:
        car_rect = rect  # fallback sem PNG

    # (1) POSIÇÃO DAS RODAS ------------- EDITAR AQUI --------------------------
    # Coordenadas normalizadas (u,v): 0..1 na largura/altura do PNG
    wheel_uv = {
        "FL": (0.12, 0.22),  # Front-Left
        "FR": (0.88, 0.22),  # Front-Right
        "RL": (0.11, 0.92),  # Rear-Left
        "RR": (0.89, 0.92),  # Rear-Right
    }
    # Dica: mude apenas os números; x mais perto de 0 vai para esquerda, de 1 para direita.
    #       y mais perto de 0 sobe; mais perto de 1 desce.
    # --------------------------------------------------------------------------

    # (2) TAMANHO DAS RODAS -------------- EDITAR AQUI -------------------------
    vis_w, vis_h = 33, 60   # largura e altura do "pneu" (a barra azul)
    # --------------------------------------------------------------------------

    # converte UV -> pixels no surface
    def uv_to_xy(u, v):
        return (car_rect.left + int(u * car_rect.width),
                car_rect.top  + int(v * car_rect.height))

    # cria rect de cada pneu já centralizado no ponto da roda
    tyre_rects = {}
    for code, (u, v) in wheel_uv.items():
        cx, cy = uv_to_xy(u, v)
        r = pygame.Rect(0, 0, vis_w, vis_h)
        r.center = (cx, cy)
        tyre_rects[code] = r

    # --- DESENHA CADA PNEU + textos (sem linhas de ligação) ---
    for code, r in tyre_rects.items():
        temp = data.tyre_data[code]['temp']
        pres = data.tyre_data[code]['pressure']

        # corpo do pneu (a barra colorida com listras)
        _draw_tyre_svg(surface, r.left, r.top, r.width, r.height, _state_color_temp(temp))

        # label (FL/FR/RL/RR) acima
        loc = FONTS["tyre_loc"].render(code, True, COLORS["white"])
        surface.blit(loc, loc.get_rect(center=(r.centerx, r.top - 10)))

        # dados (temperatura/pressão) nas laterais
        t_color = _state_color_temp(temp)
        p_color = _state_color_pressure(pres)
        temp_text = FONTS["tyre_info"].render(f"{int(temp)}°C",  True, t_color)
        pres_text = FONTS["tyre_info"].render(f"{int(pres)}PSI", True, p_color)

        if code in ("FL", "RL"):  # lado esquerdo: textos à esquerda
            surface.blit(temp_text, temp_text.get_rect(midright=(r.left - 10, r.top + 16)))
            surface.blit(pres_text, pres_text.get_rect(midright=(r.left - 10, r.top + 36)))
        else:                     # lado direito: textos à direita
            surface.blit(temp_text, temp_text.get_rect(midleft=(r.right + 10, r.top + 16)))
            surface.blit(pres_text, pres_text.get_rect(midleft=(r.right + 10, r.top + 36)))

def draw_alerts(surface, data, pos):
    rect = pygame.Rect(pos, (194, 134))
    pygame.draw.rect(surface, COLORS["background"], rect, border_radius=15)
    pygame.draw.rect(surface, (255,0,4), rect, width=2, border_radius=15)
    positions = [
        (rect.centerx - 45, rect.centery - 30),
        (rect.centerx + 45, rect.centery - 30),
        (rect.centerx - 45, rect.centery + 30),
        (rect.centerx + 45, rect.centery + 30),
    ]
    icon_map = {"bms":"bms","inverter":"inverter","battery":"battery_fault","engine":"engine_fault"}
    for i, (name, is_faulty) in enumerate(data.faults.items()):
        center = positions[i]
        img = IMAGES.get(icon_map.get(name))
        if img:
            badge = pygame.Rect(0, 0, 56, 44); badge.center = center
            pygame.draw.rect(surface, (60,60,60) if not is_faulty else (255,0,0), badge, border_radius=8)
            surface.blit(img, img.get_rect(center=center))
        else:
            label = FONTS["alert_text"].render(name.upper(), True, (255,0,0) if is_faulty else COLORS["grey"])
            pygame.draw.rect(surface, (60,60,60) if not is_faulty else (255,0,0),
                             label.get_rect(center=center).inflate(20, 10), border_radius=8)
            surface.blit(label, label.get_rect(center=center))

def draw_logo(surface, pos=(919, 503)):
    img = IMAGES.get("logo_utforce")
    if img:
        surface.blit(img, img.get_rect(topleft=pos))

def draw_all(surface, data):
    surface.fill(COLORS["background"])
    draw_rpm_bar(surface, data)
    draw_rpm_display(surface, data, pos=(363, 62))
    draw_speed_display(surface, data, pos=(329, 237))
    draw_temperatures_box(surface, data, pos=(738, 110))
    draw_pedals(surface, data, pos=(919, 156))
    draw_laps(surface, data, pos=(740, 328))
    draw_tyres(surface, data, pos=(0, 112))
    draw_alerts(surface, data, pos=(32, 440))
    # SOC no exato posicionamento/dimensão do SVG
    draw_soc(surface, data, pos=(255, 478))
    draw_logo(surface, pos=(919, 503))
    pygame.display.flip()