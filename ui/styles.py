"""
styles.py — Zenit-Visión Premium PyQt6 Design System
Fuente única de verdad de estilos y tokens visuales mapeados a QSS (Qt Style Sheets).
Concepto: Neodark Cyberpunk & Glassmorphic Matte.
"""

# ── Colores base del tema (cyber-mineral) ──────────────────────────────────────
BG_MAIN      = "#08090C"    # Fondo ultra oscuro de la ventana principal
BG_SIDEBAR   = "#0F1115"    # Fondo del sidebar y paneles de control
BG_CARD      = "#14171E"    # Fondo de las tarjetas
BG_CARD_HOVER= "#1D212A"    # Estado activo / hover de tarjetas
BG_INPUT     = "#090A0C"    # Fondo empotrado oscuro (alto contraste contra la tarjeta)

# Colores de texto (Legibilidad WCAG AA Garantizada)
TEXT_WHITE   = "#FFFFFF"    # Títulos y texto de alto contraste
TEXT_GRAY    = "#C5C7CA"    # Cuerpo de texto / descriptivo
TEXT_MUTED   = "#8A8E98"    # Elementos secundarios / placeholders / subtítulos

# Colores de bordes (Definidos y limpios)
BORDER_DARK  = "#262A34"    # Bordes generales e inactivos
BORDER_LIGHT = "#3E4456"    # Bordes de inputs / enfoque secundario

# Acento Verde Deportivo (Para Hovers y Estados Activos)
ACCENT_GREEN = "#10B981"    # Verde esmeralda premium
ACCENT_GREEN_BG = "#0D1F17" # Fondo verde oscuro translúcido

# Colores por dificultad refinados
EASY_BG      = "#0D1F17"
EASY_BRD     = "#143D2A"
EASY_TX      = "#10B981"

NORM_BG      = "#1F170A"
NORM_BRD     = "#3D2B11"
NORM_TX      = "#F59E0B"

HARD_BG      = "#240E0E"
HARD_BRD     = "#4F1B1B"
HARD_TX      = "#EF4444"

FREE_BG      = "#0E1124"
FREE_BRD     = "#1B204C"
FREE_TX      = "#6366F1"

# Colores de avatar (Login / Selector de usuario)
AVATAR_PALETTE = [
    {"bg": "#1D1635", "fg": "#8B5CF6"},   # Violeta
    {"bg": "#0D1F17", "fg": "#10B981"},   # Verde
    {"bg": "#1F130A", "fg": "#F59E0B"},   # Naranja
    {"bg": "#0E1124", "fg": "#6366F1"},   # Azul
]

# ── Tipografías recomendadas ──────────────────────────────────────────────────
FONT_TITLE    = "Arial"      # Arial estándar para evitar ensimados extremos
FONT_BODY     = "Arial"
FONT_MONO     = "Consolas"

# ── Hoja de Estilos Globales (QSS - Qt Style Sheets) ───────────────────────────
GLOBAL_STYLESHEET = f"""
/* ── Reset y Ventana Principal ── */
QMainWindow {{
    background-color: {BG_MAIN};
    font-family: "{FONT_BODY}";
}}

QWidget#MainContent {{
    background-color: {BG_MAIN};
}}

/* ── Sidebar Navigation ── */
QFrame#Sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER_DARK};
}}

QFrame#SidebarLogo {{
    background-color: transparent;
}}

/* Botones de navegación del Sidebar */
QPushButton.NavButton {{
    background-color: transparent;
    color: {TEXT_GRAY};
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-weight: bold;
    text-align: left;
}}

QPushButton.NavButton:hover {{
    background-color: {BG_CARD};
    color: {TEXT_WHITE};
}}

QPushButton.NavButton:checked {{
    background-color: {ACCENT_GREEN_BG};
    color: {ACCENT_GREEN};
    border-left: 3px solid {ACCENT_GREEN};
}}

/* Fila de Usuario Sidebar */
QFrame#UserCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_DARK};
    border-radius: 8px;
}}

/* ── Formulario e Inputs (Altamente Visibles y Contrastados) ── */
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER_DARK};
    border-radius: 8px;
    color: {TEXT_WHITE};
    font-size: 12px;
    padding: 9px 12px;
}}

QLineEdit:hover {{
    border: 1px solid {BORDER_LIGHT};
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT_GREEN};
    background-color: {BG_MAIN};
}}

QLineEdit:disabled {{
    background-color: #0E0F12;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_DARK};
}}

/* ── Tarjetas Generales ── */
QFrame.Card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_DARK};
    border-radius: 12px;
}}

QFrame.Card:hover {{
    border: 1px solid {BORDER_LIGHT};
    background-color: {BG_CARD_HOVER};
}}

/* ── Botón de Acción Principal (Premium Green Gradient) ── */
QPushButton.PrimaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_GREEN}, stop:1 #059669);
    color: {BG_MAIN};
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 20px;
}}

QPushButton.PrimaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 {ACCENT_GREEN});
}}

QPushButton.PrimaryButton:pressed {{
    background-color: #047857;
}}

/* ── Botón de Acción Outline Secundario (Premium Green Hover) ── */
QPushButton.SecondaryButton {{
    background-color: {BG_CARD};
    color: {TEXT_GRAY};
    border: 1px solid {BORDER_DARK};
    border-radius: 8px;
    font-size: 12px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton.SecondaryButton:hover {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_WHITE};
    border: 1px solid {ACCENT_GREEN};
}}

QPushButton.SecondaryButton:pressed {{
    background-color: {BG_INPUT};
}}

/* ── Zona de Peligro / Botón Danger ── */
QPushButton.DangerButton {{
    background-color: {HARD_BG};
    color: {HARD_TX};
    border: 1px solid {HARD_BRD};
    border-radius: 8px;
    font-size: 12px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton.DangerButton:hover {{
    background-color: #3B1414;
    color: {TEXT_WHITE};
    border: 1px solid {HARD_TX};
}}

QPushButton.DangerButton:pressed {{
    background-color: #4F1B1B;
}}

/* ── Badges y Etiquetas Especiales ── */
QLabel#BadgeFacil {{
    background-color: {EASY_BG};
    color: {EASY_TX};
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 3px 6px;
}}

QLabel#BadgeNormal {{
    background-color: {NORM_BG};
    color: {NORM_TX};
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 3px 6px;
}}

QLabel#BadgeDificil {{
    background-color: {HARD_BG};
    color: {HARD_TX};
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 3px 6px;
}}

QLabel#BadgeLibre {{
    background-color: {FREE_BG};
    color: {FREE_TX};
    border-radius: 4px;
    font-size: 9px;
    font-weight: bold;
    padding: 3px 6px;
}}

/* ── Barras de Scroll Personalizadas ── */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {BORDER_DARK};
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {BORDER_LIGHT};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: transparent;
    height: 0px;
}}
"""
