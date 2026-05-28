from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, FONT_TITLE,
    EASY_BG, EASY_TX, NORM_BG, NORM_TX, HARD_BG, HARD_TX, FREE_BG, FREE_TX
)
from ui.icons import get_icon_pixmap

class EstadisticasView(QWidget):
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # ── 1. Cabecera (Header) ─────────────────────────────────────────────
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_container = QFrame()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title_lbl = QLabel("Estadísticas de Rendimiento")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 22px; color: {TEXT_WHITE}; font-weight: bold;")
        sub_lbl = QLabel("Monitorea tu crecimiento diario y tus logros físicos")
        sub_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_GRAY};")

        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        header_layout.addWidget(title_container)
        main_layout.addWidget(header_frame)

        # ── 2. Área de Scroll ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(18)

        # ── 2.1 Tarjetas de Resumen Acumulador (Mini Cards Grid) ──────────────
        summary_grid = QFrame()
        summary_layout = QHBoxLayout(summary_grid)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(10)

        # Cargar métricas reales o stubs
        stats_data = {"sesiones": 0, "pts": 0, "tiempo": 0, "reps": 0}
        uid = self.shell.controller.current_user_id
        if uid == "invitado":
            stats_data = {"sesiones": 0, "pts": 0, "tiempo": 0, "reps": 0}
        elif uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"actividades/{uid}")
                if data and isinstance(data, list):
                    stats_data["sesiones"] = len(data)
                    stats_data["pts"] = sum(int(a.get("puntos", 0)) for a in data)
                    stats_data["tiempo"] = sum(int(a.get("tiempo", 0)) for a in data)
                    stats_data["reps"] = sum(int(a.get("reps", 0)) for a in data)
            except Exception:
                pass

        summary_layout.addWidget(self._build_mini_card("document", "SESIONES", f"{stats_data['sesiones']}", "rutinas", FREE_TX))
        summary_layout.addWidget(self._build_mini_card("star", "PUNTOS", f"{stats_data['pts']:,}", "pts", EASY_TX))
        summary_layout.addWidget(self._build_mini_card("clock", "TIEMPO TOTAL", f"{stats_data['tiempo']}", "minutos", NORM_TX))
        summary_layout.addWidget(self._build_mini_card("dumbbell", "REPETICIONES", f"{stats_data['reps']:,}", "reps", HARD_TX))
        scroll_layout.addWidget(summary_grid)

        # ── 2.2 Gráfico de Actividad Semanal ──────────────────────────────────
        chart_card = QFrame()
        chart_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(20, 18, 20, 18)
        chart_layout.setSpacing(12)

        chart_header = QHBoxLayout()
        chart_title = QLabel("Actividad Semanal")
        chart_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 13px; color: {TEXT_WHITE}; font-weight: bold; border: none;")
        chart_range = QLabel("últimos 7 días")
        chart_range.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none;")
        
        chart_header.addWidget(chart_title)
        chart_header.addWidget(chart_range, alignment=Qt.AlignmentFlag.AlignRight)
        chart_layout.addLayout(chart_header)

        # Contenedor de barras
        bar_container = QFrame()
        bar_container.setStyleSheet("border: none; background: transparent;")
        bar_layout = QHBoxLayout(bar_container)
        bar_layout.setContentsMargins(0, 10, 0, 10)
        bar_layout.setSpacing(10)

        # Valores semanales simulados
        valores_semana = [2, 0, 3, 1, 2, 0, 1]
        max_val = max(valores_semana) if max(valores_semana) > 0 else 1
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        dia_actual = datetime.now().weekday()

        for idx, (dia, val) in enumerate(zip(dias, valores_semana)):
            col = QFrame()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(4)

            is_today = (idx == dia_actual)
            color_bar = EASY_TX if is_today else "#22C55E" # Verde vibrante
            if not is_today and val > 0:
                color_bar = "#1E3B2F" # Verde-grisáceo elegante para días anteriores con actividad

            # Pistas y llenado planos premium con QFrame (evita efecto 3D nativo de Windows)
            bar_track = QFrame()
            bar_track.setFixedSize(20, 100)
            bar_track.setStyleSheet(f"""
                QFrame {{
                    background-color: #08090C;
                    border: 1px solid {BORDER_DARK};
                    border-radius: 6px;
                }}
            """)
            track_layout = QVBoxLayout(bar_track)
            track_layout.setContentsMargins(0, 0, 0, 0)
            track_layout.setSpacing(0)
            track_layout.addStretch()

            # Relleno de la barra
            val_height = int((val / max_val) * 98) if max_val > 0 else 0
            if val_height < 4 and val > 0:
                val_height = 4 # Asegura visibilidad si hay actividad baja
            
            bar_fill = QFrame()
            bar_fill.setFixedSize(18, val_height)
            bar_fill.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_bar};
                    border-radius: 4px;
                    border: none;
                }}
            """)
            track_layout.addWidget(bar_fill, alignment=Qt.AlignmentFlag.AlignHCenter)

            val_lbl = QLabel(str(val) if val > 0 else "-")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setStyleSheet(f"color: {EASY_TX if is_today else TEXT_MUTED}; font-size: 9px; font-weight: bold; border: none;")

            day_lbl = QLabel(dia)
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            day_lbl.setStyleSheet(f"color: {EASY_TX if is_today else TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")

            col_layout.addWidget(val_lbl)
            col_layout.addWidget(bar_track, alignment=Qt.AlignmentFlag.AlignHCenter)
            col_layout.addWidget(day_lbl)
            bar_layout.addWidget(col)

        chart_layout.addWidget(bar_container)
        scroll_layout.addWidget(chart_card)

        # ── 2.3 Historial de Sesiones ─────────────────────────────────────────
        hist_title = QLabel("Historial de Entrenamientos")
        hist_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; margin-top: 10px;")
        scroll_layout.addWidget(hist_title)

        # Cargar historial
        historial_data = [
            ("Sentadillas · Reto Fácil", "Hoy", "+45 pts"),
            ("Lagartijas · Reto Normal", "Ayer", "+80 pts"),
            ("Jumping Jacks · Reto Normal", "Ayer", "+80 pts"),
            ("Reto Avanzado completo", "Domingo", "+200 pts"),
        ]

        for nombre, fecha, pts in historial_data:
            hist_row = QFrame()
            hist_row.setFixedHeight(46)
            hist_row.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 8px;")
            hist_row_layout = QHBoxLayout(hist_row)
            hist_row_layout.setContentsMargins(14, 0, 14, 0)

            name_lbl = QLabel(nombre)
            name_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
            
            pts_lbl = QLabel(pts)
            pts_lbl.setStyleSheet(f"color: {EASY_TX}; font-size: 11px; font-weight: bold; border: none; background: transparent;")

            fecha_lbl = QLabel(fecha)
            fecha_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none; background: transparent;")

            hist_row_layout.addWidget(name_lbl)
            hist_row_layout.addWidget(fecha_lbl, alignment=Qt.AlignmentFlag.AlignRight)
            hist_row_layout.addWidget(pts_lbl, alignment=Qt.AlignmentFlag.AlignRight)

            scroll_layout.addWidget(hist_row)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _build_mini_card(self, icon_name, label, value, unit, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

        # Fila de Cabecera con Icono Vectorial
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap(icon_name, color, size=12))
        icon_lbl.setStyleSheet("border: none; background: transparent;")

        title = QLabel(label)
        title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 7px; font-weight: bold; border: none; background: transparent;")

        title_layout.addWidget(icon_lbl)
        title_layout.addWidget(title)
        title_layout.addStretch()

        val_frame = QFrame()
        val_frame.setStyleSheet("background: transparent; border: none;")
        val_layout = QHBoxLayout(val_frame)
        val_layout.setContentsMargins(0, 0, 0, 0)
        val_layout.setSpacing(4)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 18px; font-weight: bold; border: none;")
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; border: none; padding-top: 6px;")

        val_layout.addWidget(val_lbl)
        val_layout.addWidget(unit_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(title_layout)
        layout.addWidget(val_frame)

        return card
