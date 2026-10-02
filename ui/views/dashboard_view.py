from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QSize
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, BG_CARD_HOVER, BORDER_LIGHT, FONT_TITLE,
    EASY_BG, EASY_BRD, EASY_TX,
    NORM_BG, NORM_BRD, NORM_TX,
    HARD_BG, HARD_BRD, HARD_TX,
    FREE_BG, FREE_BRD, FREE_TX,
    ACCENT_GREEN
)
from ui.icons import get_icon, get_icon_pixmap
from core.gamification import GamificationEngine

def get_current_date_spanish():
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    now = datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

class DashboardView(QWidget):
    """
    Panel de Control principal con métricas de gamificación del usuario (50 Niveles, Rangos, Misiones Diarias y Racha).
    """
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self._init_ui()

    def showEvent(self, event):
        """Se activa automáticamente cada vez que la vista se hace visible."""
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

        title_lbl = QLabel("Panel de Control")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 22px; color: {TEXT_WHITE}; font-weight: bold;")
        sub_lbl = QLabel("Actividades y resumen de rendimiento")
        sub_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_GRAY};")

        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        header_layout.addWidget(title_container)

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
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(16)

        # ── 2.1 Tarjetas de Estadísticas (Gamificación) ──────────────────────
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        self.puntos_card, self.puntos_val_lbl, self.puntos_tag_lbl = self._create_stat_card_widget("star", "TOTAL PUNTOS", "0 pts", "0 / 100 pts", EASY_BG, EASY_TX)
        self.nivel_card, self.nivel_val_lbl, self.nivel_tag_lbl = self._create_stat_card_widget("level", "NIVEL DE USUARIO", "Nivel 1", "Novato Explorador", FREE_BG, FREE_TX)
        self.racha_card, self.racha_val_lbl, self.racha_tag_lbl = self._create_stat_card_widget("streak", "RACHA DIARIA", "1 días", "Activa 🔥", NORM_BG, NORM_TX)

        stats_layout.addWidget(self.puntos_card)
        stats_layout.addWidget(self.nivel_card)
        stats_layout.addWidget(self.racha_card)
        self.scroll_layout.addWidget(stats_frame)

        # Barra de progreso del nivel
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px; padding: 6px;")
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setContentsMargins(12, 8, 12, 8)
        progress_layout.setSpacing(4)

        prog_title_layout = QHBoxLayout()
        self.prog_label = QLabel("Progreso de Nivel")
        self.prog_label.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; font-weight: bold;")
        self.prog_val_lbl = QLabel("0%")
        self.prog_val_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold;")
        prog_title_layout.addWidget(self.prog_label)
        prog_title_layout.addStretch()
        prog_title_layout.addWidget(self.prog_val_lbl)
        progress_layout.addLayout(prog_title_layout)

        self.level_bar = QProgressBar()
        self.level_bar.setFixedHeight(8)
        self.level_bar.setTextVisible(False)
        self.level_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_CARD_HOVER};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_GREEN};
                border-radius: 4px;
            }}
        """)
        progress_layout.addWidget(self.level_bar)
        self.scroll_layout.addWidget(self.progress_frame)

        # ── 2.2 Botones de Acción Rápida ──────────────────────────────────────
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(0, 4, 0, 4)
        actions_layout.setSpacing(12)

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
        self.scroll_layout.addWidget(actions_frame)

        # ── 2.3 Misiones Diarias (Daily Quests) ──────────────────────────────
        quest_title = QLabel("Misiones Diarias")
        quest_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; margin-top: 6px;")
        self.scroll_layout.addWidget(quest_title)

        self.quests_container = QFrame()
        self.quests_container.setStyleSheet("background: transparent; border: none;")
        self.quests_layout = QHBoxLayout(self.quests_container)
        self.quests_layout.setContentsMargins(0, 0, 0, 0)
        self.quests_layout.setSpacing(10)
        self.scroll_layout.addWidget(self.quests_container)

        # ── 2.4 Listado de Actividades Recientes ──────────────────────────────
        act_title = QLabel("Actividades de la sesión")
        act_title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14px; color: {TEXT_WHITE}; font-weight: bold; margin-top: 6px;")
        self.scroll_layout.addWidget(act_title)

        # Contenedor dinámico de lista de actividades
        self.activities_container = QFrame()
        self.activities_container.setStyleSheet("background: transparent; border: none;")
        self.activities_layout = QVBoxLayout(self.activities_container)
        self.activities_layout.setContentsMargins(0, 0, 0, 0)
        self.activities_layout.setSpacing(8)

        self.scroll_layout.addWidget(self.activities_container)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Cargar datos por primera vez
        self.refresh_data()

    def _create_stat_card_widget(self, icon_name, label, value, badge, bg_color, tx_color):
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
        val.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 20px; font-weight: bold; border: none;")

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

        return card, val, tag

    def refresh_data(self):
        """Lee datos desde FirebaseDB o controller.guest_data y actualiza la UI."""
        controller = getattr(self.shell, 'controller', None)
        if not controller:
            return

        uid = getattr(controller, 'current_user_id', None)
        puntos = 0
        racha = 1
        historial = []
        user_data_dict = {}

        if uid == "invitado" or not uid:
            guest_data = getattr(controller, 'guest_data', {})
            user_data_dict = guest_data
            puntos = guest_data.get("puntos", 0)
            racha = guest_data.get("racha", 1)
            historial = guest_data.get("historial", [])
        else:
            try:
                fb_db = getattr(controller, 'fb_db', None)
                if fb_db:
                    user_data_dict = fb_db.read_record(f"users/{uid}") or {}
                    puntos = user_data_dict.get("puntos", 0)
                    racha = user_data_dict.get("racha", 1)

                    hist_raw = user_data_dict.get("historial", {})
                    if isinstance(hist_raw, dict):
                        historial = [v for k, v in sorted(hist_raw.items(), reverse=True)]
                    elif isinstance(hist_raw, list):
                        historial = hist_raw
            except Exception as e:
                print(f"[DashboardView] Error leyendo datos de Firebase: {e}")

        # Calcular nivel y rangos (50 Niveles)
        lvl_info = GamificationEngine.get_level_data(puntos)
        level = lvl_info["level"]
        title_rank = lvl_info["title"]
        curr_pts = lvl_info["current_level_pts"]
        next_req = lvl_info["next_level_req"]
        pct = lvl_info["progress_pct"]

        # Actualizar Tarjetas
        self.puntos_val_lbl.setText(f"{puntos:,} pts")
        self.puntos_tag_lbl.setText(f"{curr_pts}/{next_req} pts")
        
        self.nivel_val_lbl.setText(f"Nivel {level}")
        self.nivel_tag_lbl.setText(title_rank)
        self.nivel_tag_lbl.setStyleSheet(f"background-color: {BG_CARD_HOVER}; color: {lvl_info['color']}; border-radius: 4px; font-size: 9px; font-weight: bold; padding: 3px 8px; border: none;")

        self.racha_val_lbl.setText(f"{racha} días")

        # Actualizar Barra de Progreso
        self.prog_label.setText(f"Progreso a Nivel {min(50, level + 1)}: {curr_pts} / {next_req} pts")
        self.prog_val_lbl.setText(f"{pct}%")
        self.level_bar.setValue(int(pct))

        # ── Renderizar Misiones Diarias ──
        while self.quests_layout.count():
            item = self.quests_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        quests = GamificationEngine.get_daily_quests(user_data_dict)
        for q in quests:
            q_card = self._build_quest_card(q)
            self.quests_layout.addWidget(q_card)

        # ── Renderizar Lista de Actividades ──
        while self.activities_layout.count():
            item = self.activities_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not historial:
            empty_lbl = QLabel("Aún no has registrado sesiones de entrenamiento.\n¡Haz clic en 'Iniciar ejercicio' para comenzar!")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding: 20px; background-color: {BG_CARD}; border-radius: 8px;")
            self.activities_layout.addWidget(empty_lbl)
        else:
            for item_data in historial[:6]:
                nombre = item_data.get("reto_nombre", "Entrenamiento Libre")
                fecha = item_data.get("fecha", "Reciente")
                pts = f"+{item_data.get('puntos', 0)} pts"
                reps = item_data.get("repeticiones_totales", 0)
                dur = item_data.get("duracion_minutos", 0)
                desc = f"{reps} reps · {dur} min"
                
                ex_type = item_data.get("reto_id", "squat")
                icon_name = "squat"
                bg, tx, brd = EASY_BG, EASY_TX, EASY_BRD
                
                if "avanzado" in ex_type or "dificil" in str(item_data.get("dificultad")).lower():
                    bg, tx, brd = HARD_BG, HARD_TX, HARD_BRD
                elif "estandar" in ex_type or "normal" in str(item_data.get("dificultad")).lower():
                    bg, tx, brd = NORM_BG, NORM_TX, NORM_BRD
                elif "libre" in ex_type:
                    bg, tx, brd = FREE_BG, FREE_TX, FREE_BRD

                item_frame = self._build_activity_item(nombre, fecha, pts, desc, icon_name, bg, tx, brd)
                self.activities_layout.addWidget(item_frame)

    def _build_quest_card(self, quest):
        card = QFrame()
        card.setFixedHeight(68)
        border_col = ACCENT_GREEN if quest["completed"] else BORDER_DARK
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {border_col};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        top_row = QHBoxLayout()
        title_lbl = QLabel(quest["title"])
        title_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none;")
        
        status_txt = "✓ HECHO" if quest["completed"] else f"+{quest['reward_pts']} pts"
        status_color = ACCENT_GREEN if quest["completed"] else EASY_TX
        status_lbl = QLabel(status_txt)
        status_lbl.setStyleSheet(f"color: {status_color}; font-size: 10px; font-weight: bold; border: none;")

        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(status_lbl)
        layout.addLayout(top_row)

        desc_lbl = QLabel(quest["desc"])
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; border: none;")
        layout.addWidget(desc_lbl)

        # Barra de progreso individual de misión
        bar = QProgressBar()
        bar.setFixedHeight(4)
        bar.setTextVisible(False)
        bar.setRange(0, quest["target"])
        bar.setValue(quest["current"])
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_CARD_HOVER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_GREEN if quest['completed'] else EASY_TX};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(bar)

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

        icon_pixmap = get_icon_pixmap(icon_name, tx, size=16)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon_pixmap)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setStyleSheet(f"background-color: {bg}; border-radius: 6px; border: none;")
        layout.addWidget(icon_lbl)

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

        detail_frame = QFrame()
        detail_frame.setStyleSheet("background: transparent; border: none;")
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(0, 0, 10, 0)
        detail_layout.setSpacing(2)

        pts_lbl = QLabel(pts)
        pts_lbl.setStyleSheet(f"color: {tx}; font-size: 12px; font-weight: bold;")
        pts_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

        detail_layout.addWidget(pts_lbl)
        detail_layout.addWidget(desc_lbl)
        layout.addWidget(detail_frame, alignment=Qt.AlignmentFlag.AlignRight)

        return item
