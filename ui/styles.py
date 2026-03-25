"""
styles.py — Zenit Vision Design System
Fuente única de verdad. Tokens mapeados 1:1 con el HTML zenit_v4.html.

IMPORTANTE: Las fuentes son TUPLAS (family, size, weight?).
CTkFont NO puede instanciarse antes de que exista la ventana raíz.
Los helpers de widget crean CTkFont internamente, en el momento correcto.

Uso:
    from ui.styles import *
"""

import customtkinter as ctk

# ── Modo oscuro global ─────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ══════════════════════════════════════════════════════════════════════════════
# COLORES  (equivalentes directos de las CSS variables --xxx)
# ══════════════════════════════════════════════════════════════════════════════

# Fondos (oscuro estilo "gym app")
BG_COLOR     = "#0b1220"    # --bg        fondo base (no negro puro)
BG1          = "#0f172a"    # --bg1       sidebar, topbar
BG2          = "#111827"    # --bg2       tarjetas, inputs
BG3          = "#1f2937"    # --bg3       hover de fondo

# Texto
TEXT_WHITE   = "#e5e7eb"    # --tx        texto principal
TEXT_GRAY    = "#9ca3af"    # --tx2       texto secundario
TEXT_MUTED   = "#6b7280"    # --tx3       texto apagado / placeholders

# Bordes
BORDER       = "#1f2937"    # --brd       líneas sutiles
BORDER2      = "#243447"    # --brd2

# Acento verde
ACCENT_GREEN = "#2d6a4a"    # --acc       verde oscuro (botones primarios)
ACCENT_HOVER = "#245538"    # --acc2      verde hover
ACCENT_TEXT  = "#4ade80"    # --acc-tx    verde brillante (texto acento)
ACCENT_DIM   = "#0d3320"  # --acc-dim   verde translúcido

# Error / peligro
ERROR_COLOR  = "#f87171"    # --dng-tx
ERROR_BG     = "#1a0d0d"    # --dng
ERROR_BORDER = "#3a1a1a"    # --dng-brd

# Alias compatibilidad con código anterior
CARD_COLOR    = BG2
PRIMARY_HOVER = ACCENT_HOVER

# ── Colores de reto ────────────────────────────────────────────────────────────
EASY_BG = "#0d1a10"; EASY_BRD = "#163022"; EASY_TX = "#4ade80"
NORM_BG = "#141a0d"; NORM_BRD = "#243018"; NORM_TX = "#a3e635"
HARD_BG = "#1a0d0d"; HARD_BRD = "#301616"; HARD_TX = "#f87171"
FREE_BG = "#0d1020"; FREE_BRD = "#162040"; FREE_TX = "#60a5fa"

# ── Colores de avatar (.a1 .a2 .a3 … del HTML) ───────────────────────────────
AVATAR_PALETTE = [
    {"bg": "#101018", "fg": "#a78bfa"},   # a1 – violeta
    {"bg": "#101810", "fg": "#4ade80"},   # a2 – verde
    {"bg": "#181010", "fg": "#fb923c"},   # a3 – naranja
    {"bg": "#0d1a10", "fg": "#4ade80"},   # a4 – verde oscuro
    {"bg": "#0d1020", "fg": "#60a5fa"},   # a5 – azul
    {"bg": "#1a0d0d", "fg": "#f87171"},   # a6 – rojo
]

# ══════════════════════════════════════════════════════════════════════════════
# FUENTES  — tuplas (family, size) o (family, size, weight)
# Tkinter acepta tuplas directamente en el parámetro `font`.
# CTkFont se instancia DENTRO de los helpers, nunca a nivel de módulo.
# ══════════════════════════════════════════════════════════════════════════════

# Display / Logo — Syne 800
FONT_LOGO     = ("Syne", 28, "bold")    # "ZENIT VISION"
FONT_TITLE    = ("Syne", 22, "bold")    # títulos de sección
FONT_SUBTITLE = ("Syne", 15, "bold")    # subtítulos de tarjeta

# Cuerpo — DM Sans
FONT_SLOGAN   = ("DM Sans", 12)         # tagline bajo el logo
FONT_LABEL    = ("DM Sans", 11, "bold") # etiquetas, botones
FONT_REGULAR  = ("DM Sans", 11)         # texto general
FONT_INPUT    = ("DM Sans", 11)         # campos de texto
FONT_SMALL    = ("DM Sans",  9)         # metadata, badges
FONT_TINY     = ("DM Sans",  8)         # uppercase labels, separadores

# Alias
FONT_BODY    = FONT_REGULAR
FONT_CAPTION = FONT_SMALL

# ══════════════════════════════════════════════════════════════════════════════
# DIMENSIONES
# ══════════════════════════════════════════════════════════════════════════════

RADIUS_SM   = 6     # chips, badges
RADIUS_MD   = 8     # botones, inputs
RADIUS_LG   = 9     # tarjetas
RADIUS_XL   = 11    # modales
RADIUS_PILL = 20    # botones redondeados (.lg-reg)

BTN_HEIGHT  = 36    # altura estándar de botón
INPUT_H     = 33    # altura estándar de input
TOPBAR_H    = 46    # altura topbar
SIDEBAR_W   = 190   # ancho sidebar

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — widgets pre-estilizados
# Se llaman DENTRO de los frames (ventana ya existe → CTkFont seguro aquí)
# ══════════════════════════════════════════════════════════════════════════════

def primary_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    """Botón primario verde — .ab.p del HTML."""
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family="DM Sans", size=11, weight="bold"),
        fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
        text_color="#071a0e",
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )


def secondary_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    """Botón secundario — .ab.s del HTML."""
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family="DM Sans", size=11),
        fg_color=BG2, hover_color=BG3,
        text_color=TEXT_GRAY,
        border_width=1, border_color=BORDER2,
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )


def danger_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    """Botón de peligro — .cfg-dl del HTML."""
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family="DM Sans", size=11),
        fg_color=ERROR_BG, hover_color="#2a1010",
        text_color=ERROR_COLOR,
        border_width=1, border_color=ERROR_BORDER,
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )


def styled_entry(parent, placeholder: str = "", show: str = "", **kw) -> ctk.CTkEntry:
    """Campo de texto — .cfg-in / .reg-in del HTML."""
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder, show=show,
        font=ctk.CTkFont(family="DM Sans", size=11),
        fg_color=BG2, border_width=1, border_color=BORDER,
        text_color=TEXT_WHITE, placeholder_text_color=TEXT_MUTED,
        corner_radius=RADIUS_MD, height=INPUT_H,
        **kw,
    )


def section_label(parent, text: str, **kw) -> ctk.CTkLabel:
    """Etiqueta uppercase — .cfg-lb del HTML."""
    return ctk.CTkLabel(
        parent, text=text.upper(),
        font=ctk.CTkFont(family="DM Sans", size=8),
        text_color=TEXT_MUTED, **kw,
    )


def card_frame(parent, **kw) -> ctk.CTkFrame:
    """Tarjeta estándar — .sc / .ai del HTML."""
    return ctk.CTkFrame(
        parent,
        fg_color=BG2, border_width=1, border_color=BORDER,
        corner_radius=RADIUS_LG, **kw,
    )