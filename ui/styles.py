"""
styles.py — Zenit Vision Design System
Fuente única de verdad. Tokens mapeados 1:1 con el HTML zenit_v4.html (Optimizado Modo Mineral).
"""

import customtkinter as ctk

# ── Modo oscuro global ─────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ══════════════════════════════════════════════════════════════════════════════
# COLORES (Modo Mineral Mate - Ajustado al Mockup Premium)
# ══════════════════════════════════════════════════════════════════════════════

# Fondos (Negros y carbón puros, sin tinte azul)
BG_COLOR     = "#070809"    # Fondo base ultra oscuro (casi negro mate)
BG1          = "#0D0E10"    # Sidebar y Topbar (un toque más claro para separar)
BG2          = "#141619"    # Tarjetas, contenedores e inputs principales
BG3          = "#1F2226"    # Hover de fondos y estados activos

# Texto
TEXT_WHITE   = "#FFFFFF"    # Texto principal brillante
TEXT_GRAY    = "#9A9C9F"    # Texto secundario / descriptivo
TEXT_MUTED   = "#56585B"    # Texto apagado / labels pequeños / placeholders

# Bordes
BORDER       = "#1F2226"    # Líneas de división sutiles muy oscuras
BORDER2      = "#2B2E33"    # Bordes de inputs/botones secundarios enfocados

# Acento verde (Modo Mineral Activo)
ACCENT_GREEN = "#2BB371"    # Verde esmeralda deportivo plano para botones (Texto oscuro encima)
ACCENT_HOVER = "#228F5A"    # Verde hover controlado
ACCENT_TEXT  = "#2BB371"    # Texto verde brillante
ACCENT_DIM   = "#10261C"    # Fondo verde translúcido/opaco (.bg-green-soft)

# Error / peligro (.cfg-dl)
ERROR_COLOR  = "#E05A5A"    
ERROR_BG     = "#1C1212"    
ERROR_BORDER = "#331C1C"    

# Alias de compatibilidad
CARD_COLOR    = BG2
PRIMARY_HOVER = ACCENT_HOVER

# ── Colores de reto (Mapeados del mockup) ──────────────────────────────────────
EASY_BG = "#102118"; EASY_BRD = "#163827"; EASY_TX = "#2BB371"
NORM_BG = "#1A2110"; NORM_BRD = "#2C3B19"; NORM_TX = "#A3E635"
HARD_BG = "#211010"; HARD_BRD = "#3D1919"; HARD_TX = "#E05A5A"
FREE_BG = "#101626"; FREE_BRD = "#1A284C"; FREE_TX = "#4F93E6"

# ── Colores de avatar (Login / Selector de usuario) ───────────────────────────
AVATAR_PALETTE = [
    {"bg": "#14121F", "fg": "#906FFA"},   # violeta
    {"bg": "#102118", "fg": "#2BB371"},   # verde
    {"bg": "#211610", "fg": "#E67E22"},   # naranja
    {"bg": "#101626", "fg": "#4F93E6"},   # azul
]

# ══════════════════════════════════════════════════════════════════════════════
# FUENTES (Mapeadas a estilos expandidos y limpios)
# ══════════════════════════════════════════════════════════════════════════════

# Si el sistema no tiene Syne o DM Sans por defecto, usamos fuentes del sistema seguras
# que emulan perfectamente el look deportivo/robusto.
FONT_LOGO     = ("Impact", 26)               #ZENIT VISION (Mayúsculas estiradas)
FONT_TITLE    = ("Arial Black", 20)          # Títulos de sección ultra-bold expandidos
FONT_SUBTITLE = ("Arial Black", 14)          # Subtítulos de tarjeta

# Cuerpo y controles
FONT_SLOGAN   = ("Arial", 11)                
FONT_LABEL    = ("Arial", 11, "bold")        
FONT_REGULAR  = ("Arial", 11)                
FONT_INPUT    = ("Arial", 11)                
FONT_SMALL    = ("Arial", 9, "bold")         
FONT_TINY     = ("Arial", 8, "bold")         

FONT_BODY     = FONT_REGULAR
FONT_CAPTION  = FONT_SMALL

# ══════════════════════════════════════════════════════════════════════════════
# DIMENSIONES (Bordes un poco más limpios y marcados)
# ══════════════════════════════════════════════════════════════════════════════
RADIUS_SM   = 5
RADIUS_MD   = 8
RADIUS_LG   = 12
RADIUS_XL   = 16
RADIUS_PILL = 24

BTN_HEIGHT  = 38
INPUT_H     = 36
TOPBAR_H    = 48
SIDEBAR_W   = 200

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS MODIFICADOS (Alineados al contraste del mockup)
# ══════════════════════════════════════════════════════════════════════════════

def primary_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    """Botón primario verde mineral con texto oscuro de alto contraste."""
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family=FONT_LABEL, size=FONT_LABEL, weight="bold"),
        fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
        text_color="#070809", # Texto casi negro para legibilidad sobre verde brillante
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )

def secondary_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family=FONT_REGULAR, size=FONT_REGULAR),
        fg_color="transparent", # Botón plano transparente estilo mockup
        hover_color=BG3,
        text_color=TEXT_GRAY,
        border_width=1, border_color=BORDER,
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )

def danger_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text,
        font=ctk.CTkFont(family=FONT_REGULAR, size=FONT_REGULAR),
        fg_color=ERROR_BG, hover_color="#2B1414",
        text_color=ERROR_COLOR,
        border_width=1, border_color=ERROR_BORDER,
        corner_radius=RADIUS_MD, height=BTN_HEIGHT,
        command=command, **kw,
    )

def styled_entry(parent, placeholder: str = "", show: str = "", **kw) -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder, show=show,
        font=ctk.CTkFont(family=FONT_INPUT, size=FONT_INPUT),
        fg_color=BG1, border_width=1, border_color=BORDER, # Fondo más oscuro que la tarjeta
        text_color=TEXT_WHITE, placeholder_text_color=TEXT_MUTED,
        corner_radius=RADIUS_MD, height=INPUT_H,
        **kw,
    )

def section_label(parent, text: str, **kw) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent, text=text.upper(),
        font=ctk.CTkFont(family=FONT_TINY, size=FONT_TINY, weight="bold"),
        text_color=TEXT_MUTED, **kw,
    )

def card_frame(parent, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=CARD_COLOR, border_width=1, border_color=BORDER,
        corner_radius=RADIUS_LG, **kw,
    )