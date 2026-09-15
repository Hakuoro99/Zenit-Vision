from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, FONT_TITLE,
    EASY_BG, EASY_TX, NORM_BG, NORM_TX, HARD_BG, HARD_TX, FREE_BG, FREE_TX
)
from ui.icons import get_icon_pixmap

class EstadisticasView(QWidget):
    """
    Vista de Estadísticas completas con métricas acumuladas de FirebaseDB / Sesión Activa.
    """
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self._init_ui()

    def showEvent(self, event):
        """Se ejecuta al hacer visible la pestaña de Estadísticas."""
        super().showEvent(event)
        self.refresh_data()

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
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(18)

        # ── 2.1 Tarjetas de Resumen Acumulador ──────────────────────────────
        summary_grid = QFrame()
        summary_layout = QHBoxLayout(summary_grid)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(10)

        self.card_sesiones, self.sesiones_lbl = self._create_mini_card("document", "SESIONES", "0", "rutinas", FREE_TX)
        self.card_puntos, self.puntos_lbl = self._create_mini_card("star", "PUNTOS", "0", "pts", EASY_TX)
        self.card_tiempo, self.tiempo_lbl = self._create_mini_card("clock", "TIEMPO TOTAL", "0.0", "minutos", NORM_TX)
        self.card_reps, self.reps_lbl = self._create_mini_card("dumbbell", "REPETICIONES", "0", "reps", HARD_TX)

        summary_layout.addWidget(self.card_sesiones)
        summary_layout.addWidget(self.card_puntos)
        summary_layout.addWidget(self.card_tiempo)
        summary_layout.addWidget(self.card_reps)
        self.scroll_layout.addWidget(summary_grid)

        # ── 2.2 Gráfico de Actividad Semanal ──────────────────────────────────
        self.chart_card = QFrame()
        self.chart_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        self.chart_card_layout = QVBoxLayout(self.chart_card)
        self.chart_card_layout.setContentsMargins(20, 18, 20, 18)
        self.chart_card_layout.setSpacing(12)

        chart_header = QHBoxLayout()
        chart_title = QLabel("Actividad Semanal")
        chart_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 13px; color: {TEXT_WHITE}; font-weight: bold; border: none;")
        chart_range = QLabel("últimos 7 días")
        chart_range.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none;")
        
        chart_header.addWidget(chart_title)
        chart_header.addWidget(chart_range, alignment=Qt.AlignmentFlag.AlignRight)
        self.chart_card_layout.addLayout(chart_header)

        # Contenedor de las barras
        self.bar_container = QFrame()
        self.bar_container.setStyleSheet("border: none; background: transparent;")
        self.bar_layout = QHBoxLayout(self.bar_container)
        self.bar_layout.setContentsMargins(0, 10, 0, 10)
        self.bar_layout.setSpacing(10)
        
        self.chart_card_layout.addWidget(self.bar_container)
        self.scroll_layout.addWidget(self.chart_card)

        # ── 2.3 Historial Completo de Entrenamientos ──────────────────────────
        hist_title = QLabel("Historial de Entrenamientos")
        hist_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; margin-top: 10px;")
        self.scroll_layout.addWidget(hist_title)

        self.history_container = QFrame()
        self.history_container.setStyleSheet("background: transparent; border: none;")
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(8)

        self.scroll_layout.addWidget(self.history_container)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Cargar datos por primera vez
        self.refresh_data()

    def _create_mini_card(self, icon_name, label, value, unit, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(4)

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

        return card, val_lbl

    def refresh_data(self):
        """Carga métricas reales desde FirebaseDB o controller.guest_data."""
        controller = getattr(self.shell, 'controller', None)
        if not controller:
            return

        uid = getattr(controller, 'current_user_id', None)
        total_sesiones = 0
        total_puntos = 0
        total_tiempo = 0.0
        total_reps = 0
        historial = []

        if uid == "invitado" or not uid:
            guest_data = getattr(controller, 'guest_data', {})
            total_puntos = guest_data.get("puntos", 0)
            total_reps = guest_data.get("total_reps", 0)
            total_tiempo = guest_data.get("total_minutos", 0.0)
            total_sesiones = guest_data.get("total_sesiones", 0)
            historial = guest_data.get("historial", [])
        else:
            try:
                fb_db = getattr(controller, 'fb_db', None)
                if fb_db:
                    user_data = fb_db.read_record(f"users/{uid}") or {}
                    total_puntos = user_data.get("puntos", 0)
                    total_reps = user_data.get("total_reps", 0)
                    total_tiempo = user_data.get("total_minutos", 0.0)
                    total_sesiones = user_data.get("total_sesiones", 0)

                    hist_raw = user_data.get("historial", {})
                    if isinstance(hist_raw, dict):
                        historial = [v for k, v in sorted(hist_raw.items(), reverse=True)]
                    elif isinstance(hist_raw, list):
                        historial = hist_raw
            except Exception as e:
                print(f"[EstadisticasView] Error leyendo datos de Firebase: {e}")

        # Actualizar recuadros superiores
        self.sesiones_lbl.setText(str(total_sesiones))
        self.puntos_lbl.setText(f"{total_puntos:,}")
        self.tiempo_lbl.setText(f"{total_tiempo:.1f}")
        self.reps_lbl.setText(f"{total_reps:,}")

        # Renderizar gráfico de actividad semanal dinámico
        self._update_weekly_chart(historial)

        # Renderizar historial completo
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not historial:
            empty_lbl = QLabel("No hay registros de entrenamiento en tu historial.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 20px; background-color: {BG_CARD}; border-radius: 8px;")
            self.history_layout.addWidget(empty_lbl)
        else:
            for session in historial:
                nombre = session.get("reto_nombre", "Entrenamiento Libre")
                fecha = session.get("fecha", "Reciente")
                pts = f"+{session.get('puntos', 0)} pts"
                reps = session.get("repeticiones_totales", 0)
                dur = session.get("duracion_minutos", 0)

                hist_row = QFrame()
                hist_row.setFixedHeight(50)
                hist_row.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 8px;")
                hist_row_layout = QHBoxLayout(hist_row)
                hist_row_layout.setContentsMargins(14, 0, 14, 0)

                left_info = QVBoxLayout()
                left_info.setSpacing(2)
                name_lbl = QLabel(nombre)
                name_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none;")
                sub_lbl = QLabel(f"{reps} reps · {dur} min")
                sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; border: none;")
                left_info.addWidget(name_lbl)
                left_info.addWidget(sub_lbl)

                pts_lbl = QLabel(pts)
                pts_lbl.setStyleSheet(f"color: {EASY_TX}; font-size: 11px; font-weight: bold; border: none;")

                fecha_lbl = QLabel(fecha)
                fecha_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none;")

                hist_row_layout.addLayout(left_info)
                hist_row_layout.addWidget(fecha_lbl, alignment=Qt.AlignmentFlag.AlignRight)
                hist_row_layout.addWidget(pts_lbl, alignment=Qt.AlignmentFlag.AlignRight)

                self.history_layout.addWidget(hist_row)

    def _update_weekly_chart(self, historial):
        """Calcula las sesiones realizadas por día de la semana actual y dibuja las barras."""
        while self.bar_layout.count():
            item = self.bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Contador por día de la semana (0 = Lunes, 6 = Domingo)
        semana_counts = [0] * 7
        now = datetime.now()

        for session in historial:
            try:
                # Tratar de parsear fecha "YYYY-MM-DD HH:MM"
                f_str = session.get("fecha", "")
                if f_str:
                    dt = datetime.strptime(f_str, "%Y-%m-%d %H:%M")
                    # Verificar si corresponde a los últimos 7 días
                    delta = (now - dt).days
                    if 0 <= delta < 7:
                        semana_counts[dt.weekday()] += 1
            except Exception:
                pass

        max_val = max(semana_counts) if max(semana_counts) > 0 else 1
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        dia_actual = now.weekday()

        for idx, (dia, val) in enumerate(zip(dias, semana_counts)):
            col = QFrame()
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(4)

            is_today = (idx == dia_actual)
            color_bar = EASY_TX if is_today else "#22C55E"
            if not is_today and val > 0:
                color_bar = "#1E3B2F"

            bar_track = QFrame()
            bar_track.setFixedSize(20, 100)
            bar_track.setStyleSheet(f"background-color: #08090C; border: 1px solid {BORDER_DARK}; border-radius: 6px;")
            track_layout = QVBoxLayout(bar_track)
            track_layout.setContentsMargins(0, 0, 0, 0)
            track_layout.setSpacing(0)
            track_layout.addStretch()

            val_height = int((val / max_val) * 98) if max_val > 0 else 0
            if val_height < 4 and val > 0:
                val_height = 4
            
            bar_fill = QFrame()
            bar_fill.setFixedSize(18, val_height)
            bar_fill.setStyleSheet(f"background-color: {color_bar}; border-radius: 4px; border: none;")
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
            self.bar_layout.addWidget(col)
