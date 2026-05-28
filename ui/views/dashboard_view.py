from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, BG_CARD_HOVER, BORDER_LIGHT, FONT_TITLE,
    EASY_BG, EASY_BRD, EASY_TX,
    NORM_BG, NORM_BRD, NORM_TX,
    HARD_BG, HARD_BRD, HARD_TX,
    FREE_BG, FREE_BRD, FREE_TX,
    ACCENT_GREEN
)
from PyQt6.QtCore import Qt, QSize
from ui.icons import get_icon, get_icon_pixmap

def get_current_date_spanish():
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    now = datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

class DashboardView(QWidget):
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self._init_ui()

    def _init_ui(self):
        # Layout vertical principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # ── 1. Cabecera (Header) ─────────────────────────────────────────────
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Título
        title_container = QFrame()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title_lbl = QLabel("Panel de Control")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 22px; color: {TEXT_WHITE}; font-weight: bold;")
        sub_lbl = QLabel("Actividades de la semana")
        sub_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_GRAY};")

        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        header_layout.addWidget(title_container)

        # Fecha derecha
        date_card = QFrame()
        date_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 5px;")
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(14, 6, 14, 6)

        date_lbl = QLabel(get_current_date_spanish())
        date_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        date_layout.addWidget(date_lbl)
        
        header_layout.addWidget(date_card, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(header_frame)

        # ── 2. Área de Scroll para Contenido ──────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(16)

        # ── 2.1 Tarjetas de Estadísticas (Stats Grid) ──────────────────────────
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        puntos = 0
        nivel = 1
        racha = 0

        # Consultar datos reales de Firebase
        uid = self.shell.controller.current_user_id
        if uid == "invitado":
            puntos = 0
            nivel = 1
            racha = 0
        elif uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    puntos = data.get("puntos", 0)
                    nivel = data.get("nivel", 1)
                    racha = data.get("racha", 0)
            except Exception:
                pass

        stats_layout.addWidget(self._build_stat_card("star", "TOTAL DE PUNTOS", f"{puntos:,} pts", "+45 hoy", EASY_BG, EASY_TX))
        stats_layout.addWidget(self._build_stat_card("level", "NIVEL ACTUAL", f"{nivel}", "Explorador", FREE_BG, FREE_TX))
        stats_layout.addWidget(self._build_stat_card("streak", "MEJOR RACHA", f"{racha} días", "Activa", NORM_BG, NORM_TX))
        scroll_layout.addWidget(stats_frame)

        # ── 2.2 Botones de Acción Rápida ──────────────────────────────────────
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 4, 0, 4)
        actions_layout.setSpacing(12)

        # Botón Ejercicio
        btn_ej = QPushButton(" Iniciar ejercicio\n Nueva sesión de entrenamiento")
        btn_ej.setFixedHeight(60)
        btn_ej.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ej.setIcon(get_icon("play", "#090A0C", size=22))
        btn_ej.setIconSize(QSize(22, 22))
        btn_ej.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_GREEN}, stop:1 #059669);
                color: #090A0C;
                border: none;
                border-radius: 10px;
                font-family: 'Arial';
                font-size: 13px;
                font-weight: bold;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 {ACCENT_GREEN});
            }}
        """)
        btn_ej.clicked.connect(lambda: self.shell.navigate("ejercicios"))

        # Botón Estadísticas
        btn_est = QPushButton(" Ver estadísticas\n Revisa tu progreso semanal")
        btn_est.setFixedHeight(60)
        btn_est.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_est.setIcon(get_icon("stats", TEXT_WHITE, size=22))
        btn_est.setIconSize(QSize(22, 22))
        btn_est.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT_WHITE};
                border: 1px solid {BORDER_DARK};
                border-radius: 10px;
                font-family: 'Arial';
                font-size: 13px;
                font-weight: bold;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD_HOVER};
                border: 1px solid {BORDER_LIGHT};
            }}
        """)
        btn_est.clicked.connect(lambda: self.shell.navigate("estadisticas"))

        actions_layout.addWidget(btn_ej)
        actions_layout.addWidget(btn_est)
        scroll_layout.addWidget(actions_frame)

        # ── 2.3 Listado de Actividades Recientes ──────────────────────────────
        act_title = QLabel("Actividades de esta semana")
        act_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; margin-top: 10px;")
        scroll_layout.addWidget(act_title)

        activities_list = [
            ("Sentadillas · Reto Fácil", "Hoy — 08:30 am", "+45 pts", "15 reps · 10 min", "squat", EASY_BG, EASY_TX, EASY_BRD),
            ("Lagartijas · Reto Normal", "Ayer — 07:15 am", "+80 pts", "30 reps · 20 min", "pushup", FREE_BG, FREE_TX, FREE_BRD),
            ("Jumping Jacks · Reto Normal", "Ayer — 07:50 am", "+80 pts", "40 reps · 20 min", "jumping_jacks", NORM_BG, NORM_TX, NORM_BRD),
            ("Reto Avanzado completo", "Domingo — 06:00 am", "+200 pts", "180 reps · 35 min", "streak", HARD_BG, HARD_TX, HARD_BRD),
        ]

        for nombre, hora, pts, desc, icon, bg, tx, brd in activities_list:
            item_frame = self._build_activity_item(nombre, hora, pts, desc, icon, bg, tx, brd)
            scroll_layout.addWidget(item_frame)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _build_stat_card(self, icon_name, label, value, badge, bg_color, tx_color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {tx_color};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        # Fila de Cabecera con Icono Vectorial
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(6)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap(icon_name, tx_color, size=14))
        icon_lbl.setStyleSheet("border: none; background: transparent;")

        title = QLabel(label)
        title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 8px; font-weight: bold; border: none; background: transparent;")

        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(title)
        title_layout.addStretch()

        val = QLabel(value)
        val.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 24px; font-weight: bold; border: none;")

        tag = QLabel(badge)
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {tx_color};
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
                padding: 3px 8px;
                border: none;
            }}
        """)

        layout.addLayout(title_layout)
        layout.addWidget(val)
        layout.addWidget(tag, alignment=Qt.AlignmentFlag.AlignLeft)

        return card

    def _build_activity_item(self, nombre, hora, pts, desc, icon_name, bg, tx, brd):
        item = QFrame()
        item.setFixedHeight(56)
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border: 1px solid {brd};
                background-color: {BG_CARD_HOVER};
            }}
        """)
        layout = QHBoxLayout(item)
        layout.setContentsMargins(14, 0, 14, 0)

        # Icono de Actividad Vectorial
        icon_pixmap = get_icon_pixmap(icon_name, tx, size=16)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon_pixmap)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setStyleSheet(f"background-color: {bg}; border-radius: 6px; border: none;")
        layout.addWidget(icon_lbl)

        # Info del Ejercicio (Izquierda)
        info_frame = QFrame()
        info_frame.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 0, 0, 0)
        info_layout.setSpacing(2)

        name_lbl = QLabel(nombre)
        name_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 12px; font-weight: bold;")
        time_lbl = QLabel(hora)
        time_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px;")
        
        info_layout.addWidget(name_lbl)
        info_layout.addWidget(time_lbl)
        layout.addWidget(info_frame)

        # Detalles del Ejercicio (Derecha)
        detail_frame = QFrame()
        detail_frame.setStyleSheet("background: transparent; border: none;")
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(0, 0, 10, 0)
        detail_layout.setSpacing(2)

        pts_lbl = QLabel(pts)
        pts_lbl.setStyleSheet(f"color: {tx}; font-size: 12px; font-weight: bold; text-align: right;")
        pts_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; text-align: right;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        detail_layout.addWidget(pts_lbl)
        detail_layout.addWidget(desc_lbl)
        layout.addWidget(detail_frame, alignment=Qt.AlignmentFlag.AlignRight)

        return item
