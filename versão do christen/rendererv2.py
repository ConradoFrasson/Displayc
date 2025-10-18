# rendererv2.py
import os
import math
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

    # gradiente do mock
    "grad_0": (0x14, 0x66, 0xFF),  # 0%
    "grad_25": (0x2B, 0x8E, 0x95), # 25%
    "grad_50": (0x41, 0xB6, 0x2C), # 50%
    "grad_75": (0xBA, 0xA0, 0x17), # 75%
    "grad_100": (0xFF, 0x00, 0x04),# 100%

    "pedal_green": (0, 255, 0), "pedal_red": (255, 0, 0),
    "temp_red": (255, 7, 58),
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

# ---------- Gradiente stops ----------
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

# ---------- Carregamento ----------
def load_assets():
    try:
        pygame.font.init()
        orbit = _apath("assets","fonts","Orbitron-Bold.ttf")
        FONTS["speed_num"]     = pygame.font.Font(orbit, 96)
        FONTS["soc_title"]     = pygame.font.Font(orbit, 64)
        FONTS["rpm_num"]       = pygame.font.Font(orbit, 64)
        FONTS["speed_unit"]    = pygame.font.Font(orbit, 36)
        FONTS["rpm_unit"]      = pygame.font.Font(orbit, 24)
        FONTS["pedal_letters"] = pygame.font.Font(orbit, 24)
        FONTS["lap_num"]       = pygame.font.Font(orbit, 20)
        FONTS["soc_num"]       = pygame.font.Font(orbit, 20)
        FONTS["tyre_loc"]      = pygame.font.Font(orbit, 16)
        FONTS["temp_value"]    = pygame.font.Font(orbit, 16)
        FONTS["alert_text"]    = pygame.font.Font(orbit, 16)
        FONTS["lap_title"]     = pygame.font.Font(orbit, 14)
        FONTS["speed_mode"]    = pygame.font.Font(orbit, 24)  # modo dentro do círculo
        FONTS["tyre_info"]     = pygame.font.Font(orbit, 20)
        FONTS["temp_labels"]   = pygame.font.Font(orbit, 14)

        # Imagens
        IMAGES["battery_temp"]  = _load_image("icon_battery_temp.png", (24, 24))
        IMAGES["engine_temp"]   = _load_image("icon_engine_temp.png",  (24, 24))
        IMAGES["bms"]           = _load_image("icon_bms.png",            (36, 36))
        IMAGES["inverter"]      = _load_image("icon_inverter.png",       (36, 36))
        IMAGES["battery_fault"] = _load_image("icon_battery_fault.png",  (36, 36))
        IMAGES["engine_fault"]  = _load_image("icon_engine_fault.png",   (36, 36))
        # nome de arquivo conforme você informou: "logo_utforce.png"
        IMAGES["logo_utforce"]  = _load_image("logo_utforce.png",        (83, 83))
    except Exception as e:
        print(f"[renderer] Erro ao carregar assets: {e}. Usando fallbacks.")
        for k, size in {
            "speed_num":96,"soc_title":64,"rpm_num":64,"speed_unit":36,"rpm_unit":24,
            "pedal_letters":24,"lap_num":20,"soc_num":20,"tyre_loc":16,"temp_value":16,
            "alert_text":16,"lap_title":14,"speed_mode":24,"tyre_info":20,"temp_labels":14
        }.items():
            FONTS[k] = pygame.font.SysFont("Arial", size, bold=True)

# ---------- Utilidades ----------
def draw_text_with_outline(font, text, fg_color, outline_color, surface, center, ow=2):
    txt = font.render(text, True, fg_color)
    out = font.render(text, True, outline_color)
    rect = txt.get_rect(center=center)
    for dx in (-ow,0,ow):
        for dy in (-ow,0,ow):
            if dx or dy:
                surface.blit(out, rect.move(dx, dy))
    surface.blit(txt, rect)

# ---------- Anel RPM (gradiente 25% + preenchimento por rpm) ----------
def _ring_color_by_fraction(f):
    # 0-0.25 azul->teal, 0.25-0.5 teal->verde, 0.5-0.75 verde->amarelo, 0.75-1 amarelo->vermelho
    stops = [
        (0.00, COLORS["grad_0"]),
        (0.25, COLORS["grad_25"]),
        (0.50, COLORS["grad_50"]),
        (0.75, COLORS["grad_75"]),
        (1.00, COLORS["grad_100"]),
    ]
    return _color_from_stops(stops, f)

def draw_rpm_ring(surface, rpm_value, rpm_max, center, radius, thickness=16):
    inner = radius - thickness
    segments = 64
    ratio = max(0.0, min(1.0, rpm_value / float(rpm_max)))
    lit = int(round(segments * ratio))

    phase_deg = 90.0  # 0% começa no BOTTOM (90° em tela pygame)

    for i in range(segments):
        a0 = i * (360.0 / segments) + phase_deg
        a1 = (i+1) * (360.0 / segments) + phase_deg
        color = _ring_color_by_fraction(i / max(segments-1, 1))
        seg_color = color if i < lit else (60, 60, 60)

        steps = 6
        for s in range(steps):
            ang = math.radians(_lerp(a0, a1, s/steps))
            x0 = center[0] + inner * math.cos(ang)
            y0 = center[1] + inner * math.sin(ang)
            x1 = center[0] + radius * math.cos(ang)
            y1 = center[1] + radius * math.sin(ang)
            pygame.draw.line(surface, seg_color, (x0, y0), (x1, y1), 3)

# ---------- Blocos ----------
def draw_rpm_box(surface, rpm, pos=(353,3), size=(298,106)):
    rect = pygame.Rect(pos, size)
    pygame.draw.rect(surface, (26,26,26), rect, border_radius=15)
    pygame.draw.rect(surface, COLORS["border_red"], rect, width=2, border_radius=15)
    draw_text_with_outline(FONTS["rpm_num"], f"{rpm}", COLORS["white"], COLORS["border_red"], surface, (rect.centerx-30, rect.centery-4))
    draw_text_with_outline(FONTS["rpm_unit"], "RPM", COLORS["white"], COLORS["border_red"], surface, (rect.right-40, rect.centery+22))

def draw_speed_circle(surface, data, pos=(326,115), size=(356,356)):
    cx, cy = pos[0]+size[0]//2, pos[1]+size[1]//2
    radius = size[0]//2

    # anel rpm
    draw_rpm_ring(surface, data.rpm, 12000, (cx,cy), radius)

    # face interna
    pygame.draw.circle(surface, COLORS["background"], (cx,cy), radius-20)

    # número e unidade com afastamento garantido
    speed_rect = FONTS["speed_num"].render(str(data.speed), True, COLORS["white"]).get_rect()
    unit_rect  = FONTS["speed_unit"].render("Km/h", True, COLORS["white"]).get_rect()

    # posiciono primeiro o número, um pouquinho mais à esquerda
    num_center = (cx-24, cy-10)
    draw_text_with_outline(FONTS["speed_num"], f"{data.speed}",
                           COLORS["white"], COLORS["border_red"], surface, num_center)

    # agora posiciono a unidade à direita com folga mínima de 8 px
    unit_left = (num_center[0] + speed_rect.width//2) + 12
    unit_center = (max(unit_left + unit_rect.width//2, cx+92), cy+30)
    draw_text_with_outline(FONTS["speed_unit"], "Km/h",
                           COLORS["white"], COLORS["border_red"], surface, unit_center)

    # modo
    draw_text_with_outline(FONTS["speed_mode"],  data.mode,
                           COLORS["white"], COLORS["border_red"], surface, (cx, cy+80))


def draw_laps(surface, data, pos=(28,74), size=(178,206)):
    rect = pygame.Rect(pos, size)
    pygame.draw.rect(surface, (26,26,26), rect, border_radius=50)
    pygame.draw.rect(surface, COLORS["border_red"], rect, width=4, border_radius=50)

    y = rect.y + 14
    line_gap_title = 24
    line_gap_value = 36

    for key, title, color in [
        ("best", "Melhor volta", "text_green"),
        ("previous", "Volta Anterior", "text_yellow"),
        ("current", "Volta Atual", "text_blue"),
    ]:
        tit = FONTS["lap_title"].render(title, True, COLORS[color])
        surface.blit(tit, (rect.x + 14, y)); y += line_gap_title
        val = FONTS["lap_num"].render(data.lap_data[key], True, COLORS["white"])
        surface.blit(val, (rect.x + 14, y)); y += line_gap_value


def draw_soc(surface, data, pos=(342,473), size=(320,110)):
    """
    Desenha o bloco SOC (320x110) no estilo do SVG fornecido:
      - Título "SOC" com contorno vermelho
      - Delta de potência (kW) alinhado à direita
      - Barra inferior com gradiente (#FF0000 -> #FFD900 -> #41B62C), raio 11, stroke vermelho 2px
      - Divisórias verticais vermelhas nas mesmas posições do SVG
      - Preenchimento até o nível de SOC (data.soc em 0..1)
    """
    rect = pygame.Rect(pos, size)

    # ----------------- Cabeçalho -----------------
    # "SOC" com contorno vermelho (estética dos paths vermelhos do SVG)
    draw_text_with_outline(
        FONTS["soc_title"], "SOC",
        COLORS["white"], COLORS["border_red"],
        surface, (rect.left + 96, rect.top + 28)
    )

    # Delta kW à direita (verde para valores >=0; vermelho caso contrário)
    sign  = "+" if data.power_delta >= 0 else ""
    color = COLORS["pedal_green"] if data.power_delta >= 0 else COLORS["pedal_red"]
    delta_txt = f"{sign}{data.power_delta:.1f}kW"
    delta_surf = FONTS["soc_num"].render(delta_txt, True, color)
    surface.blit(delta_surf, delta_surf.get_rect(midright=(rect.right - 10, rect.top + 30)))

    # ----------------- Barra inferior -----------------
    # No SVG: y≈77.75, h≈33.25, rx=11, stroke=#FF0004 (2px)
    bar_h = 33  # ~ 33.25
    bar_rect = pygame.Rect(rect.left, rect.bottom - bar_h, rect.width, bar_h)

    # Fundo e borda (stroke) com cantos arredondados
    pygame.draw.rect(surface, COLORS["background"], bar_rect, border_radius=11)
    pygame.draw.rect(surface, COLORS["border_red"], bar_rect, width=2, border_radius=11)

    # Gradiente horizontal (como no <linearGradient> do SVG)
    # stops: 0 -> #FF0000 ; 0.394231 -> #FFD900 ; 1 -> #41B62C
    grad_w = bar_rect.width - 2
    grad_h = bar_rect.height - 2
    if grad_w > 0 and grad_h > 0:
        grad_surf = pygame.Surface((grad_w, grad_h), pygame.SRCALPHA)
        for x in range(grad_w):
            t = x / max(1, grad_w - 1)
            if t <= 0.394231:
                u = t / 0.394231
                c0, c1 = (255, 0, 0), (255, 217, 0)
            else:
                u = (t - 0.394231) / (1 - 0.394231)
                c0, c1 = (255, 217, 0), (0x41, 0xB6, 0x2C)
            col = (
                int(c0[0]*(1-u)+c1[0]*u),
                int(c0[1]*(1-u)+c1[1]*u),
                int(c0[2]*(1-u)+c1[2]*u),
            )
            pygame.draw.line(grad_surf, col, (x, 1), (x, grad_h - 2))

        # Máscara para manter o mesmo raio 11 do retângulo
        mask = pygame.Surface((grad_w, grad_h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=11)
        grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Nível do SOC (0..1) — renderiza só até essa fração
        level = max(0.0, min(1.0, float(getattr(data, "soc", 0.0))))
        level_w = int(grad_w * level)
        if level_w > 0:
            surface.blit(
                grad_surf.subsurface((0, 0, level_w, grad_h)),
                (bar_rect.left + 1, bar_rect.top + 1)
            )

    # ----------------- Divisórias (mesmas do SVG) -----------------
    # No SVG a barra tem largura útil 322px (x=1..323). As retas estão em:
    svg_ticks = [33.9321, 65.8641, 97.7961, 129.728, 161.66, 193.592, 225.524, 257.456, 289.388]
    # Escala para a largura atual de 320px (ret.width), preservando a referência (x-1)
    scale = (bar_rect.width) / 322.0
    for tx in svg_ticks:
        x = int(bar_rect.left + (tx - 1) * scale)
        # Altura das divisórias no SVG cobre quase toda a barra; aqui deixamos 1px de margem
        pygame.draw.rect(
            surface, COLORS["border_red"],
            pygame.Rect(x, bar_rect.top + 1, 1, bar_rect.height - 2)
        )


# ---- Temperaturas (caixa direita superior) ----
def _draw_temp_gauge(surface, rect, value, vmin, vmax, icon_surf, max_label, min_label="20°"):
    """Gauge vertical com labels FIXOS nas laterais e preenchimento por valor."""
    # ícone acima
    if icon_surf:
        surface.blit(icon_surf, icon_surf.get_rect(centerx=rect.centerx, top=rect.top - 4))

    # barra
    bar_rect = pygame.Rect(rect.x + rect.width // 4, rect.y + 20, rect.width // 2, rect.height - 50)
    pygame.draw.rect(surface, (40, 40, 40), bar_rect, border_radius=10)

    ratio = max(0.0, min(1.0, (value - vmin) / max(1e-6, (vmax - vmin))))
    fill_h = int((bar_rect.height - 8) * ratio)
    fill_rect = pygame.Rect(bar_rect.x + 4, bar_rect.bottom - 4 - fill_h, bar_rect.width - 8, fill_h)

    # gradiente de baixo (0) para cima (1)
    for i in range(max(fill_rect.height, 0)):
        t = i / max(1, fill_rect.height - 1)
        color = _color_from_stops(TEMP_COLOR_STOPS, t)
        y = fill_rect.bottom - 1 - i
        pygame.draw.line(surface, color, (fill_rect.left, y), (fill_rect.right - 1, y))

    pygame.draw.rect(surface, (60, 60, 60), bar_rect, width=2, border_radius=10)

    # labels fixos laterais (não mudam)
    max_s = FONTS["temp_labels"].render(max_label, True, COLORS["temp_red"])
    surface.blit(max_s, max_s.get_rect(midleft=(bar_rect.right + 14, bar_rect.top + 2)))
    c_top = FONTS["temp_labels"].render("C", True, COLORS["temp_red"])
    surface.blit(c_top, c_top.get_rect(midleft=(bar_rect.right + 14, bar_rect.top + 18)))

    min_s = FONTS["temp_labels"].render(min_label, True, COLORS["white"])
    surface.blit(min_s, min_s.get_rect(midright=(bar_rect.left - 14, bar_rect.bottom - 2)))
    c_bot = FONTS["temp_labels"].render("C", True, COLORS["white"])
    surface.blit(c_bot, c_bot.get_rect(midright=(bar_rect.left - 14, bar_rect.bottom - 18)))

def draw_temperatures_box(surface, data, pos=(833,129), size=(157,189)):
    """Caixa de temperaturas (bateria à esquerda, motor à direita)."""
    rect = pygame.Rect(pos, (size[0], int(size[1])))
    # sem borda (mock mostra a caixa "limpa"); se quiser, adicione:
    # pygame.draw.rect(surface, COLORS["border_red"], rect, width=2, border_radius=15)

    left  = pygame.Rect(rect.x, rect.y, rect.width // 2, rect.height)
    right = pygame.Rect(rect.centerx, rect.y, rect.width // 2, rect.height)

    _draw_temp_gauge(surface, left,  data.battery_temp, 20, 60,  IMAGES.get("battery_temp"), "60°")
    _draw_temp_gauge(surface, right, data.engine_temp,  20, 110, IMAGES.get("engine_temp"),  "110°")

# ---- Sistema de alertas (caixa esquerda inferior) ----
def draw_alerts(surface, data, pos=(50,305), size=(133,267)):
    rect = pygame.Rect(pos, size)
    pygame.draw.rect(surface, COLORS["background"], rect, border_radius=15)
    pygame.draw.rect(surface, COLORS["border_red"], rect, width=2, border_radius=15)

    # 4 slots em grid 2x2
    cells = [
        (rect.x + rect.width*0.25, rect.y + rect.height*0.25),
        (rect.x + rect.width*0.75, rect.y + rect.height*0.25),
        (rect.x + rect.width*0.25, rect.y + rect.height*0.75),
        (rect.x + rect.width*0.75, rect.y + rect.height*0.75),
    ]
    icon_map = {"bms":"bms","inverter":"inverter","battery":"battery_fault","engine":"engine_fault"}
    for i, (name, is_faulty) in enumerate(data.faults.items()):
        cx, cy = cells[i]
        badge = pygame.Rect(0,0,56,44); badge.center = (int(cx), int(cy))
        pygame.draw.rect(surface, (60,60,60) if not is_faulty else COLORS["pedal_red"], badge, border_radius=8)
        img = IMAGES.get(icon_map.get(name))
        if img:
            surface.blit(img, img.get_rect(center=badge.center))
        else:
            label = FONTS["alert_text"].render(name.upper(), True, (255,255,255))
            surface.blit(label, label.get_rect(center=badge.center))

# ---- Pneus (barras com stroke branco e linhas internas) ----
def _tyre_fill_color_by_temp(t):
    # azul/ideal/quente/extremo
    if t < 60:     return (0x14, 0x66, 0xFF)  # azul
    if t < 80:     return (0x41, 0xB6, 0x2C)  # verde
    if t < 95:     return (0xBA, 0xA0, 0x17)  # amarelo
    return (0xFF, 0x00, 0x04)                 # vermelho

def draw_tyre_bar(surface, x, y, w=40, h=82, temp=50):
    """Desenha a barra do pneu como no SVG fornecido."""
    rect = pygame.Rect(x, y, w, h)
    # preenchimento pela temperatura
    pygame.draw.rect(surface, _tyre_fill_color_by_temp(temp), rect, border_radius=5)
    # stroke branco
    pygame.draw.rect(surface, COLORS["white"], rect, width=1, border_radius=5)
    # linhas horizontais internas nas mesmas posições do SVG
    # (valores absolutos de Y a partir do topo do retângulo)
    for ly in (15.371, 28.5968, 41.8226, 55.0484, 68.2742):
        pygame.draw.line(surface, COLORS["white"], (x, y+int(ly)), (x+w, y+int(ly)), 1)

def draw_tyre_data_block(surface, topleft, temp, psi, align="center"):
    """Bloco 67x69 com textos (20px Orbitron)."""
    bx, by = topleft
    w, h = 67, 69
    # não desenha caixa — apenas textos como no mock
    t_text = FONTS["tyre_info"].render(f"{int(temp)}°C", True, COLORS["white"])
    p_text = FONTS["tyre_info"].render(f"{int(psi)}PSI", True, COLORS["white"])
    cx = bx + w//2
    surface.blit(t_text, t_text.get_rect(center=(cx, by + 20)))
    surface.blit(p_text, p_text.get_rect(center=(cx, by + 46)))

def draw_tyres_fixed(surface, data):
    # FL
    draw_tyre_bar(surface, 302, 100, 40, 82, data.tyre_data['FL']['temp'])
    label = FONTS["tyre_loc"].render("FL", True, COLORS["white"])
    surface.blit(label, label.get_rect(midbottom=(302+20, 100-6)))
    draw_tyre_data_block(surface, (236, 100), data.tyre_data['FL']['temp'], data.tyre_data['FL']['pressure'])

    # FR
    draw_tyre_bar(surface, 662, 100, 40, 82, data.tyre_data['FR']['temp'])
    label = FONTS["tyre_loc"].render("FR", True, COLORS["white"])
    surface.blit(label, label.get_rect(midbottom=(662+20, 100-6)))
    draw_tyre_data_block(surface, (709, 106), data.tyre_data['FR']['temp'], data.tyre_data['FR']['pressure'])

    # RL
    draw_tyre_bar(surface, 302, 430, 40, 82, data.tyre_data['RL']['temp'])
    label = FONTS["tyre_loc"].render("RL", True, COLORS["white"])
    surface.blit(label, label.get_rect(midbottom=(302+20, 430-6)))
    draw_tyre_data_block(surface, (228, 430), data.tyre_data['RL']['temp'], data.tyre_data['RL']['pressure'])

    # RR
    draw_tyre_bar(surface, 662, 430, 40, 82, data.tyre_data['RR']['temp'])
    label = FONTS["tyre_loc"].render("RR", True, COLORS["white"])
    surface.blit(label, label.get_rect(midbottom=(662+20, 430-6)))
    draw_tyre_data_block(surface, (709, 435), data.tyre_data['RR']['temp'], data.tyre_data['RR']['pressure'])

# ---- Pedais (caixa 94x168 em 833,341) ----
def draw_pedals_box(surface, data, pos=(833,341), size=(94,168)):
    rect = pygame.Rect(pos, size)
    # caixa "limpa" (mock não mostra borda)
    bar_w = 28
    bar_h = rect.height - 40
    # A (acelerador) à esquerda
    a_rect = pygame.Rect(rect.x + 12, rect.bottom - bar_h, bar_w, bar_h)
    # F (freio) à direita
    f_rect = pygame.Rect(rect.right - 12 - bar_w, rect.bottom - bar_h, bar_w, bar_h)

    # rótulos A/F no topo
    a_lbl = FONTS["pedal_letters"].render("A", True, COLORS["pedal_green"])
    f_lbl = FONTS["pedal_letters"].render("F", True, COLORS["pedal_red"])
    surface.blit(a_lbl, a_lbl.get_rect(center=(a_rect.centerx, rect.top + 6)))
    surface.blit(f_lbl, f_lbl.get_rect(center=(f_rect.centerx, rect.top + 6)))

    # molduras
    pygame.draw.rect(surface, (60,60,60), a_rect, border_radius=12)
    pygame.draw.rect(surface, (60,60,60), f_rect, border_radius=12)

    # preenchimentos
    a_h = int(bar_h * (data.accelerator/100))
    f_h = int(bar_h * (data.brake/100))
    pygame.draw.rect(surface, COLORS["pedal_green"], pygame.Rect(a_rect.left, a_rect.bottom - a_h, bar_w, a_h), border_radius=12)
    pygame.draw.rect(surface, COLORS["pedal_red"],   pygame.Rect(f_rect.left, f_rect.bottom - f_h, bar_w, f_h), border_radius=12)

# ---- RPM box (já implementada acima), Laps (acima), SOC (acima) ----

# ---- Logo ----
def draw_logo(surface, pos=(919,503)):
    img = IMAGES.get("logo_utforce")
    if img:
        surface.blit(img, img.get_rect(topleft=pos))

# ---- Função principal de desenho (layout 1024x600 fixo) ----
def draw_all(surface, data):
    surface.fill(COLORS["background"])

    # Círculo velocidade + anel RPM
    draw_speed_circle(surface, data, pos=(326,115), size=(356,356))

    # Caixa RPM
    draw_rpm_box(surface, data.rpm, pos=(353,3), size=(298,106))

    # Voltas
    draw_laps(surface, data, pos=(28,74), size=(178,206))

    # SOC
    draw_soc(surface, data, pos=(342,473), size=(320,110))

    # Temperaturas (bateria/motor)
    draw_temperatures_box(surface, data, pos=(833,129), size=(157,189))

    # Alertas
    draw_alerts(surface, data, pos=(50,305), size=(133,267))

    # Pneus + blocos de dados
    draw_tyres_fixed(surface, data)

    # Pedais
    draw_pedals_box(surface, data, pos=(833,341), size=(94,168))

    # Logo
    draw_logo(surface, pos=(919,503))

    pygame.display.flip()