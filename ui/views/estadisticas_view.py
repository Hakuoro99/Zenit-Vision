from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea,
    QDialog, QPushButton, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QCursor
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, BG_CARD_HOVER, BORDER_LIGHT, FONT_TITLE,
    EASY_BG, EASY_TX, NORM_BG, NORM_TX, HARD_BG, HARD_TX, FREE_BG, FREE_TX, ACCENT_GREEN,
    BG_SIDEBAR, BG_MAIN, ACCENT_GREEN_BG
)
from ui.icons import get_icon_pixmap


class DayExerciseTooltip(QFrame):
    """
    Ventanita flotante minimalista que aparece al pasar el cursor sobre una barra del gráfico.
    Muestra únicamente los ejercicios y las repeticiones correspondientes a ese día.
    """
    def __init__(self, day_info):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.ToolTip | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.day_info = day_info
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #0F172A;
                border: 1.5px solid {ACCENT_GREEN};
                border-radius: 10px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(14, 10, 14, 10)
        card_l.setSpacing(5)

        day_name = self.day_info.get("day_name", "Día")
        total_reps = self.day_info.get("total_reps", 0)

        # Encabezado: Día y total de repeticiones
        head_l = QHBoxLayout()
        head_l.setSpacing(10)
        
        t_lbl = QLabel(day_name)
        t_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 12px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        
        badge = QLabel(f"{total_reps} reps")
        badge.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        
        head_l.addWidget(t_lbl)
        head_l.addStretch()
        head_l.addWidget(badge)
        card_l.addLayout(head_l)

        # Línea divisoria
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background-color: {BORDER_DARK}; border: none;")
        card_l.addWidget(div)

        # Desglose de ejercicios y repeticiones realizadas
        exercises = self.day_info.get("exercises", {})
        if exercises and total_reps > 0:
            for ex_name, count in exercises.items():
                if count <= 0:
                    continue
                row = QHBoxLayout()
                row.setSpacing(8)
                
                dot = QLabel("•")
                dot.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
                
                name_lbl = QLabel(ex_name)
                name_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10.5px; border: none; background: transparent;")
                
                reps_lbl = QLabel(f"{count} reps")
                reps_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 10.5px; font-weight: bold; border: none; background: transparent;")
                
                row.addWidget(dot)
                row.addWidget(name_lbl)
                row.addStretch()
                row.addWidget(reps_lbl)
                card_l.addLayout(row)
        else:
            empty_lbl = QLabel("Sin actividad registrada este día")
            empty_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-style: italic; border: none; background: transparent; padding: 2px 0;")
            card_l.addWidget(empty_lbl)

        # Sugerencia de clic interactivo
        hint_lbl = QLabel("👆 Clic para ver el informe detallado")
        hint_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 8.5px; border: none; background: transparent; padding-top: 3px;")
        card_l.addWidget(hint_lbl)

        main_layout.addWidget(card)


class DayDetailModal(QDialog):
    """
    Modal informativo interactivo al hacer clic en un día del gráfico.
    Muestra estadísticas consolidadas, desglose por ejercicio y el listado de rutinas ejecutadas.
    """
    def __init__(self, parent, day_info):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Rendimiento Diario")
        self.setFixedSize(500, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.day_info = day_info
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 2px solid {ACCENT_GREEN};
                border-radius: 16px;
            }}
        """)
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(22, 20, 22, 20)
        card_l.setSpacing(12)

        day_name = self.day_info.get("day_name", "Día")
        date_str = self.day_info.get("date_str", "")
        total_reps = self.day_info.get("total_reps", 0)
        total_min = self.day_info.get("total_minutes", 0.0)
        total_pts = self.day_info.get("total_puntos", 0)
        sessions = self.day_info.get("sessions", [])
        exercises = self.day_info.get("exercises", {})

        # ── 1. Encabezado con Botón Cerrar ──────────────────────────────────
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("chart", ACCENT_GREEN, size=28))
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        t_lbl = QLabel(f"Rendimiento del {day_name}")
        t_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 17px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        sub_text = f"Fecha: {date_str} · {len(sessions)} sesión(es)" if date_str else f"{len(sessions)} sesión(es) registrada(s)"
        sub_lbl = QLabel(sub_text)
        sub_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10.5px; border: none; background: transparent;")
        title_box.addWidget(t_lbl)
        title_box.addWidget(sub_lbl)

        btn_close_x = QPushButton("✕")
        btn_close_x.setFixedSize(28, 28)
        btn_close_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close_x.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {BORDER_DARK};
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
                color: {TEXT_WHITE};
                border-color: {BORDER_LIGHT};
            }}
        """)
        btn_close_x.clicked.connect(self.accept)

        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(btn_close_x)
        card_l.addLayout(header)

        # ── 2. Tarjetas de Métricas Resumen ─────────────────────────────────
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(8)

        def make_mini_box(title, val, unit, color):
            box = QFrame()
            box.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
            b_l = QVBoxLayout(box)
            b_l.setContentsMargins(10, 8, 10, 8)
            b_l.setSpacing(2)
            
            t = QLabel(title)
            t.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 8.5px; font-weight: bold; border: none; background: transparent;")
            v = QLabel(str(val))
            v.setStyleSheet(f"color: {color}; font-family: '{FONT_TITLE}'; font-size: 17px; font-weight: bold; border: none; background: transparent;")
            u = QLabel(unit)
            u.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 8px; border: none; background: transparent;")
            
            b_l.addWidget(t)
            b_l.addWidget(v)
            b_l.addWidget(u)
            return box

        metrics_row.addWidget(make_mini_box("REPETICIONES", total_reps, "reps totales", ACCENT_GREEN))
        metrics_row.addWidget(make_mini_box("TIEMPO", f"{total_min:.1f}", "minutos activos", TEXT_WHITE))
        metrics_row.addWidget(make_mini_box("PUNTOS", f"+{total_pts}", "ganados hoy", "#F59E0B"))
        card_l.addLayout(metrics_row)

        # ── 3. Desglose Detallado de Ejercicios ──────────────────────────────
        ex_card = QFrame()
        ex_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        ex_l = QVBoxLayout(ex_card)
        ex_l.setContentsMargins(14, 12, 14, 12)
        ex_l.setSpacing(8)

        ex_tag = QLabel("DESGLOSE POR EJERCICIO")
        ex_tag.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
        ex_l.addWidget(ex_tag)

        if exercises and total_reps > 0:
            for ex_name, count in exercises.items():
                if count <= 0:
                    continue
                pct = int((count / max(total_reps, 1)) * 100)
                
                row_container = QVBoxLayout()
                row_container.setSpacing(3)
                
                info_h = QHBoxLayout()
                lbl_name = QLabel(ex_name)
                lbl_name.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11.5px; font-weight: bold; border: none; background: transparent;")
                lbl_val = QLabel(f"{count} reps ({pct}%)")
                lbl_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
                
                info_h.addWidget(lbl_name)
                info_h.addStretch()
                info_h.addWidget(lbl_val)
                row_container.addLayout(info_h)

                pbar = QProgressBar()
                pbar.setFixedHeight(6)
                pbar.setTextVisible(False)
                pbar.setValue(pct)
                pbar.setStyleSheet(f"""
                    QProgressBar {{
                        background-color: {BG_SIDEBAR};
                        border: 1px solid {BORDER_DARK};
                        border-radius: 3px;
                    }}
                    QProgressBar::chunk {{
                        background-color: {ACCENT_GREEN};
                        border-radius: 3px;
                    }}
                """)
                row_container.addWidget(pbar)
                ex_l.addLayout(row_container)
        else:
            empty_msg = QLabel("Este día no se registraron repeticiones de ejercicios.\n¡Un día de descanso también es importante para recuperar músculos!")
            empty_msg.setWordWrap(True)
            empty_msg.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-style: italic; border: none; background: transparent;")
            ex_l.addWidget(empty_msg)

        card_l.addWidget(ex_card)

        # ── 4. Sesiones Realizadas en la Jornada ─────────────────────────────
        if sessions:
            sess_box = QFrame()
            sess_box.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
            sess_l = QVBoxLayout(sess_box)
            sess_l.setContentsMargins(14, 10, 14, 10)
            sess_l.setSpacing(6)

            sess_tag = QLabel("SESIONES DE LA JORNADA")
            sess_tag.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
            sess_l.addWidget(sess_tag)

            for s in sessions[:3]:  # Mostrar hasta 3 sesiones
                s_name = s.get("reto_nombre", "Entrenamiento Libre")
                s_reps = s.get("repeticiones_totales", 0)
                s_pts = f"+{s.get('puntos', 0)} pts"
                s_hora = s.get("fecha", "").split()[-1] if " " in s.get("fecha", "") else ""

                s_row = QHBoxLayout()
                s_lbl = QLabel(f"• {s_name} {f'({s_hora})' if s_hora else ''}")
                s_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
                
                s_meta = QLabel(f"{s_reps} reps · {s_pts}")
                s_meta.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 10.5px; font-weight: bold; border: none; background: transparent;")
                
                s_row.addWidget(s_lbl)
                s_row.addStretch()
                s_row.addWidget(s_meta)
                sess_l.addLayout(s_row)

            card_l.addWidget(sess_box)

        # ── 5. Botón de Aceptar / Cerrar ─────────────────────────────────────
        btn_close = QPushButton("¡Entendido!")
        btn_close.setFixedHeight(38)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                font-family: '{FONT_TITLE}';
                font-size: 12.5px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
        """)
        btn_close.clicked.connect(self.accept)
        card_l.addWidget(btn_close)

        layout.addWidget(card)


class WeeklyBarColumn(QFrame):
    """
    Columna interactiva para cada día de la semana en el gráfico de rendimiento.
    - Hover: cambia estilos visuales y despliega DayExerciseTooltip con ejercicios y reps.
    - Clic: abre DayDetailModal con estadísticas completas y desglose interactivo.
    """
    def __init__(self, parent_view, day_info, height_pct):
        super().__init__()
        self.parent_view = parent_view
        self.day_info = day_info
        self.val = day_info.get("total_reps", 0)
        self.height_pct = height_pct
        self.tooltip_popup = None

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
        self._init_ui()

    def _init_ui(self):
        col_layout = QVBoxLayout(self)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(4)
        col_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        # 1. Etiqueta con el valor exacto sobre la barra
        self.val_lbl = QLabel(str(self.val) if self.val > 0 else "")
        self.val_lbl.setStyleSheet(f"color: {ACCENT_GREEN if self.val > 0 else TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. Barra de progreso visual
        bar_h = max(16, int(self.height_pct * 90))
        self.bar_lbl = QLabel()
        self.bar_lbl.setFixedWidth(22)
        self.bar_lbl.setFixedHeight(bar_h)
        
        self._apply_normal_bar_style()

        # 3. Etiqueta del día de la semana
        self.day_lbl = QLabel(self.day_info.get("day_short", ""))
        self.day_lbl.setStyleSheet(f"color: {TEXT_WHITE if self.val > 0 else TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        self.day_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col_layout.addWidget(self.val_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        col_layout.addWidget(self.bar_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        col_layout.addWidget(self.day_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _apply_normal_bar_style(self):
        if self.val > 0:
            self.bar_lbl.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {ACCENT_GREEN}, stop:1 #059669);
                    border-radius: 5px;
                }}
            """)
        else:
            self.bar_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {BORDER_DARK};
                    border-radius: 4px;
                }}
            """)

    def _apply_hover_bar_style(self):
        if self.val > 0:
            self.bar_lbl.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34D399, stop:1 #10B981);
                    border: 1.5px solid #6EE7B7;
                    border-radius: 5px;
                }}
            """)
        else:
            self.bar_lbl.setStyleSheet(f"""
                QLabel {{
                    background-color: {BORDER_LIGHT};
                    border: 1px solid {ACCENT_GREEN};
                    border-radius: 4px;
                }}
            """)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._apply_hover_bar_style()
        self.day_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        self._show_tooltip()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._apply_normal_bar_style()
        self.day_lbl.setStyleSheet(f"color: {TEXT_WHITE if self.val > 0 else TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        self._hide_tooltip()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._hide_tooltip()
            dlg = DayDetailModal(self.window(), self.day_info)
            dlg.exec()
        super().mousePressEvent(event)

    def _show_tooltip(self):
        if not self.tooltip_popup:
            self.tooltip_popup = DayExerciseTooltip(self.day_info)

        self.tooltip_popup.adjustSize()
        tip_w = self.tooltip_popup.sizeHint().width()
        tip_h = self.tooltip_popup.sizeHint().height()

        bar_global = self.bar_lbl.mapToGlobal(QPoint(self.bar_lbl.width() // 2, 0))
        x = bar_global.x() - tip_w // 2
        y = bar_global.y() - tip_h - 8

        x = max(10, x)
        if y < 10:
            y = bar_global.y() + self.bar_lbl.height() + 8

        self.tooltip_popup.move(x, y)
        self.tooltip_popup.show()
        self.tooltip_popup.raise_()

    def _hide_tooltip(self):
        if self.tooltip_popup:
            self.tooltip_popup.hide()

    def hideEvent(self, event):
        self._hide_tooltip()
        super().hideEvent(event)

    def closeEvent(self, event):
        if self.tooltip_popup:
            self.tooltip_popup.close()
            self.tooltip_popup.deleteLater()
            self.tooltip_popup = None
        super().closeEvent(event)


class EstadisticasView(QWidget):
    """
    Vista de Estadísticas completas con métricas de rendimiento y gráfico de actividad semanal
    conectado en tiempo real al perfil del usuario.
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
        sub_lbl = QLabel("Monitorea tu crecimiento diario y tus métricas físicas acumuladas")
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

        # ── 2.2 Gráfico de Actividad Semanal Mejorado ────────────────────────
        self.chart_card = QFrame()
        self.chart_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 14px;
            }}
        """)
        self.chart_card_layout = QVBoxLayout(self.chart_card)
        self.chart_card_layout.setContentsMargins(22, 20, 22, 20)
        self.chart_card_layout.setSpacing(14)

        chart_header = QHBoxLayout()
        
        header_text_container = QVBoxLayout()
        header_text_container.setSpacing(2)
        chart_title = QLabel("Rendimiento Semanal (Repeticiones Diarias)")
        chart_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; border: none;")
        self.chart_subtitle = QLabel("Pasa el cursor sobre una barra para ver ejercicios o haz clic para ver el detalle")
        self.chart_subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none;")
        header_text_container.addWidget(chart_title)
        header_text_container.addWidget(self.chart_subtitle)

        self.weekly_total_lbl = QLabel("0 reps esta semana")
        self.weekly_total_lbl.setStyleSheet(f"""
            background-color: {BG_CARD_HOVER};
            color: {ACCENT_GREEN};
            border: 1px solid {ACCENT_GREEN};
            border-radius: 6px;
            font-size: 10px;
            font-weight: bold;
            padding: 4px 10px;
        """)

        chart_header.addLayout(header_text_container)
        chart_header.addStretch()
        chart_header.addWidget(self.weekly_total_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.chart_card_layout.addLayout(chart_header)

        # Contenedor visual de las barras de rendimiento
        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(150)
        self.bar_container.setStyleSheet("border: none; background: transparent;")
        self.bar_layout = QHBoxLayout(self.bar_container)
        self.bar_layout.setContentsMargins(10, 10, 10, 10)
        self.bar_layout.setSpacing(14)
        
        self.chart_card_layout.addWidget(self.bar_container)
        self.scroll_layout.addWidget(self.chart_card)

        # ── 2.3 Historial Completo de Entrenamientos ──────────────────────────
        hist_title = QLabel("Historial Completo de Entrenamientos")
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
        """Lee datos desde FirebaseDB o controller.guest_data y actualiza la UI."""
        controller = getattr(self.shell, 'controller', None)
        if not controller:
            return

        uid = getattr(controller, 'current_user_id', None)
        total_puntos = 0
        total_reps = 0
        total_tiempo = 0.0
        total_sesiones = 0
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

        # Renderizar gráfico de actividad semanal
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
                title_lbl = QLabel(nombre)
                title_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11.5px; font-weight: bold;")
                date_lbl = QLabel(fecha)
                date_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px;")
                left_info.addWidget(title_lbl)
                left_info.addWidget(date_lbl)

                right_info = QVBoxLayout()
                right_info.setSpacing(2)
                pts_lbl = QLabel(pts)
                pts_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11.5px; font-weight: bold;")
                pts_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
                sub_lbl = QLabel(f"{reps} reps · {dur} min")
                sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px;")
                sub_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
                right_info.addWidget(pts_lbl)
                right_info.addWidget(sub_lbl)

                hist_row_layout.addLayout(left_info)
                hist_row_layout.addStretch()
                hist_row_layout.addLayout(right_info)

                self.history_layout.addWidget(hist_row)

    def _update_weekly_chart(self, historial):
        while self.bar_layout.count():
            item = self.bar_layout.takeAt(0)
            if item.widget():
                if hasattr(item.widget(), '_hide_tooltip'):
                    item.widget()._hide_tooltip()
                item.widget().deleteLater()

        # Días de la semana en español
        days = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        days_full = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        
        # Estructura consolidada por cada día de la semana
        weekly_days_info = []
        for i in range(7):
            weekly_days_info.append({
                "day_idx": i,
                "day_short": days[i],
                "day_name": days_full[i],
                "date_str": "",
                "total_reps": 0,
                "total_minutes": 0.0,
                "total_puntos": 0,
                "sessions": [],
                "exercises": {}
            })

        total_weekly_reps = 0
        now = datetime.now()

        # Mapeo de nombres limpios de ejercicios
        EXERCISE_NAMES = {
            "knee_raise": "Levantamiento de Rodillas",
            "rodillas": "Levantamiento de Rodillas",
            "jumping_jacks": "Levantamiento de Rodillas",
            "squat": "Sentadillas",
            "sentadillas": "Sentadillas",
            "pushup": "Lagartijas (Flexiones)",
            "lagartijas": "Lagartijas (Flexiones)"
        }

        for item in historial:
            ts = item.get("timestamp")
            dt = None
            if ts:
                try:
                    dt = datetime.fromtimestamp(ts)
                except Exception:
                    dt = None
            if not dt and item.get("fecha"):
                try:
                    dt = datetime.strptime(item["fecha"][:10], "%Y-%m-%d")
                except Exception:
                    dt = None

            if dt and (now - dt).days < 7:
                day_idx = (dt.weekday() + 1) % 7
                reps = item.get("repeticiones_totales", 0)
                dur = item.get("duracion_minutos", 0.0)
                pts = item.get("puntos", 0)
                
                day_data = weekly_days_info[day_idx]
                day_data["total_reps"] += reps
                day_data["total_minutes"] += dur
                day_data["total_puntos"] += pts
                day_data["sessions"].append(item)
                if not day_data["date_str"]:
                    day_data["date_str"] = dt.strftime("%d/%m/%Y")
                total_weekly_reps += reps

                # Extraer desglose de ejercicios
                desglose = item.get("desglose_ejercicios", {})
                if desglose and isinstance(desglose, dict):
                    for k, count in desglose.items():
                        c_name = EXERCISE_NAMES.get(k.lower(), k.capitalize())
                        day_data["exercises"][c_name] = day_data["exercises"].get(c_name, 0) + count
                else:
                    # Atribución inteligente por tipo de reto si no tiene desglose explícito
                    reto_id = str(item.get("reto_id", "")).lower()
                    reto_nom = str(item.get("reto_nombre", "")).lower()

                    if "principiante" in reto_id or "principiante" in reto_nom:
                        rodillas = int(round(reps * 20 / 45))
                        sentadillas = int(round(reps * 15 / 45))
                        lagartijas = max(0, reps - rodillas - sentadillas)
                        day_data["exercises"]["Levantamiento de Rodillas"] = day_data["exercises"].get("Levantamiento de Rodillas", 0) + rodillas
                        day_data["exercises"]["Sentadillas"] = day_data["exercises"].get("Sentadillas", 0) + sentadillas
                        day_data["exercises"]["Lagartijas (Flexiones)"] = day_data["exercises"].get("Lagartijas (Flexiones)", 0) + lagartijas
                    elif "estandar" in reto_id or "estándar" in reto_nom or "estandar" in reto_nom:
                        rodillas = int(round(reps * 40 / 90))
                        sentadillas = int(round(reps * 30 / 90))
                        lagartijas = max(0, reps - rodillas - sentadillas)
                        day_data["exercises"]["Levantamiento de Rodillas"] = day_data["exercises"].get("Levantamiento de Rodillas", 0) + rodillas
                        day_data["exercises"]["Sentadillas"] = day_data["exercises"].get("Sentadillas", 0) + sentadillas
                        day_data["exercises"]["Lagartijas (Flexiones)"] = day_data["exercises"].get("Lagartijas (Flexiones)", 0) + lagartijas
                    elif "avanzado" in reto_id or "avanzado" in reto_nom:
                        rodillas = int(round(reps * 60 / 135))
                        sentadillas = int(round(reps * 45 / 135))
                        lagartijas = max(0, reps - rodillas - sentadillas)
                        day_data["exercises"]["Levantamiento de Rodillas"] = day_data["exercises"].get("Levantamiento de Rodillas", 0) + rodillas
                        day_data["exercises"]["Sentadillas"] = day_data["exercises"].get("Sentadillas", 0) + sentadillas
                        day_data["exercises"]["Lagartijas (Flexiones)"] = day_data["exercises"].get("Lagartijas (Flexiones)", 0) + lagartijas
                    else:
                        general_name = item.get("ejercicio_nombre") or item.get("reto_nombre", "Levantamiento de Rodillas")
                        day_data["exercises"][general_name] = day_data["exercises"].get(general_name, 0) + reps

        self.weekly_total_lbl.setText(f"{total_weekly_reps} reps esta semana")

        max_val = max([d["total_reps"] for d in weekly_days_info] + [1])

        for i in range(7):
            d_info = weekly_days_info[i]
            val = d_info["total_reps"]
            height_pct = min(1.0, val / max_val) if max_val > 0 else 0.05
            
            bar_col = WeeklyBarColumn(self, d_info, height_pct)
            self.bar_layout.addWidget(bar_col)
