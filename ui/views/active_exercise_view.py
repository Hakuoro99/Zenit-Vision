import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QDialog, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QImage, QPixmap

from ui.styles import (
    BG_MAIN, BG_CARD, BG_SIDEBAR, BORDER_DARK, BORDER_LIGHT, TEXT_WHITE, 
    TEXT_GRAY, TEXT_MUTED, ACCENT_GREEN, ACCENT_GREEN_BG, HARD_TX, HARD_BG,
    FONT_TITLE, EASY_BG, EASY_TX, NORM_BG, NORM_TX, FREE_BG, FREE_TX
)
from ui.icons import get_icon, get_icon_pixmap
from core.camera_worker import CameraThread
from core.analyzer import SessionAnalyzer
from core.audio_manager import AudioManager

# ── Catálogo de Información e Instrucciones de Ejercicios ────────────────────
EXERCISE_INFO = {
    "squat": {
        "nombre": "Sentadillas",
        "descripcion": "1. Colócate de pie con los pies a la anchura de los hombros y la espalda recta.\n2. Flexiona tus rodillas bajando la cadera como si fueras a sentarte en una silla (hasta ~90°).\n3. Empuja con los talones manteniendo el pecho erguido para subir a la posición inicial.",
        "distancia": "1.5m - 2.5m de la cámara (cuerpo completo visible de frente o perfil)"
    },
    "pushup": {
        "nombre": "Lagartijas (Flexiones)",
        "descripcion": "1. Colócate en posición de tabla con las manos alineadas a los hombros y el cuerpo recto.\n2. Flexiona los codos bajando el pecho de forma controlada hasta estar cerca del suelo.\n3. Empuja firmemente con ambos brazos hasta extender completamente los codos.",
        "distancia": "1.5m - 2.0m de la cámara (cuerpo entero visible en posición horizontal o diagonal)"
    },
    "jumping_jacks": {
        "nombre": "Jumping Jacks (Saltos)",
        "descripcion": "1. Inicia erguido con los pies juntos y los brazos pegados a los costados del cuerpo.\n2. Salta abriendo las piernas y elevando simultáneamente ambos brazos por encima de la cabeza.\n3. Salta nuevamente para regresar a la postura inicial con pies juntos y brazos abajo.",
        "distancia": "1.8m - 2.5m de la cámara (brazos extendidos arriba y piernas completas visibles)"
    }
}


class WorkoutSummaryModal(QDialog):
    """Modal emergente al finalizar el entrenamiento con resumen de estadísticas y puntos de gamificación."""
    def __init__(self, parent, session_summary):
        super().__init__(parent)
        self.setWindowTitle("Resumen de Entrenamiento")
        self.setFixedSize(470, 460)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.summary = session_summary
        self._init_ui()

    def _init_ui(self):
        AudioManager.instance().play_victory()
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
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("star", ACCENT_GREEN, size=32))
        
        title_lbl = QLabel("¡Entrenamiento Completado! 🎉")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 18px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        card_layout.addLayout(header)

        # Nombre del Reto
        reto_name = self.summary.get("reto_nombre", "Entrenamiento Libre")
        sub_lbl = QLabel(f"¡Felicitaciones! Has completado exitosamente {reto_name}.")
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        card_layout.addWidget(sub_lbl)

        # Banner de Puntos Ganados
        pts_banner = QFrame()
        pts_banner.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {ACCENT_GREEN}; border-radius: 10px;")
        pts_banner_layout = QHBoxLayout(pts_banner)
        pts_banner_layout.setContentsMargins(14, 8, 14, 8)
        
        pts_label = QLabel("PUNTOS GANADOS")
        pts_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        pts_val = QLabel(f"+{self.summary.get('puntos', 0)} pts")
        pts_val.setStyleSheet(f"color: {ACCENT_GREEN}; font-family: '{FONT_TITLE}'; font-size: 18px; font-weight: bold; border: none;")

        pts_banner_layout.addWidget(pts_label)
        pts_banner_layout.addStretch()
        pts_banner_layout.addWidget(pts_val)
        card_layout.addWidget(pts_banner)

        # Rejilla de Métricas
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        metrics_layout = QVBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(14, 12, 14, 12)
        metrics_layout.setSpacing(8)

        def add_metric(label, value, icon_name, color):
            row = QHBoxLayout()
            ic = QLabel()
            ic.setPixmap(get_icon_pixmap(icon_name, color, size=14))
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {TEXT_WHITE}; font-weight: bold; font-size: 11.5px; border: none; background: transparent;")
            
            row.addWidget(ic)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            metrics_layout.addLayout(row)

        add_metric("Repeticiones Totales", f"{self.summary.get('repeticiones_totales', 0)} reps ({self.summary.get('rep_points', 0)} pts)", "squat", ACCENT_GREEN)
        add_metric("Precisión Postural", f"{self.summary.get('precision_postural', 0)}% (+{self.summary.get('precision_bonus', 0)} pts)", "stats", "#8B5CF6")
        add_metric("Duración Total", f"{self.summary.get('duracion_minutos', 0)} min", "clock", "#3B82F6")
        add_metric("Calorías Estimadas", f"{self.summary.get('calorias_estimadas', 0)} kcal", "streak", "#F59E0B")

        card_layout.addWidget(metrics_frame)

        # Aviso de Logros Desbloqueados si los hay
        logros_nuevos = self.summary.get("logros_nuevos", [])
        if logros_nuevos:
            logro_lbl = QLabel(f"🏆 ¡Has desbloqueado {len(logros_nuevos)} nuevo(s) logro(s)!")
            logro_lbl.setStyleSheet(f"color: #F59E0B; font-size: 10.5px; font-weight: bold; border: none; background: transparent;")
            logro_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(logro_lbl)

        # Botón Aceptar
        btn_accept = QPushButton("Guardar y Volver a Ejercicios")
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.setFixedHeight(36)
        btn_accept.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                font-family: '{FONT_TITLE}';
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
        """)
        btn_accept.clicked.connect(self.accept)
        card_layout.addWidget(btn_accept)

        layout.addWidget(card)


class ExerciseStartModal(QDialog):
    """Modal informativo al iniciar la sesión con instrucciones completas (sentadillas, lagartijas, saltos), posicionamiento y descanso."""
    def __init__(self, parent, challenge_name, first_ex_type, target_reps):
        super().__init__(parent)
        self.setWindowTitle("Instrucciones de Entrenamiento")
        self.setFixedSize(510, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.challenge_name = challenge_name
        self.ex_type = first_ex_type
        self.target_reps = target_reps
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
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("camera", ACCENT_GREEN, size=28))
        
        title_lbl = QLabel("¡Instrucciones de Sesión!")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 18px; color: {TEXT_WHITE}; font-weight: bold; border: none;")
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        card_layout.addLayout(header)

        # Subtítulo Reto
        sub_lbl = QLabel(f"Reto seleccionado: {self.challenge_name}")
        sub_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none;")
        card_layout.addWidget(sub_lbl)

        info = EXERCISE_INFO.get(self.ex_type, EXERCISE_INFO["squat"])
        ex_name = info["nombre"]
        meta_str = f"{self.target_reps} repeticiones" if self.target_reps > 0 else "Estilo Libre"

        # Card Ejercicio Inicial & Meta
        ex_card = QFrame()
        ex_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {ACCENT_GREEN}; border-radius: 10px;")
        ex_l = QVBoxLayout(ex_card)
        ex_l.setContentsMargins(12, 10, 12, 10)
        ex_l.setSpacing(4)

        tag_lbl = QLabel("1. EJERCICIO INICIAL Y META")
        tag_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; border: none;")
        val_lbl = QLabel(f"{ex_name} — Meta: {meta_str}")
        val_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 15px; font-weight: bold; border: none;")
        ex_l.addWidget(tag_lbl)
        ex_l.addWidget(val_lbl)
        card_layout.addWidget(ex_card)

        # Card Instrucciones de Movimiento
        inst_card = QFrame()
        inst_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        inst_l = QVBoxLayout(inst_card)
        inst_l.setContentsMargins(12, 10, 12, 10)
        inst_l.setSpacing(4)

        inst_tag = QLabel("2. TÉCNICA E INSTRUCCIONES DE EJECUCIÓN")
        inst_tag.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none;")
        inst_text = QLabel(info["descripcion"])
        inst_text.setWordWrap(True)
        inst_text.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11.5px; border: none;")
        inst_l.addWidget(inst_tag)
        inst_l.addWidget(inst_text)
        card_layout.addWidget(inst_card)

        # Card Distancia Recomendada
        dist_card = QFrame()
        dist_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        dist_l = QVBoxLayout(dist_card)
        dist_l.setContentsMargins(12, 10, 12, 10)
        dist_l.setSpacing(4)

        dist_tag = QLabel("3. DISTANCIA Y ENCUADRE DE CÁMARA")
        dist_tag.setStyleSheet(f"color: #F59E0B; font-size: 10px; font-weight: bold; border: none;")
        dist_text = QLabel(f"📐 {info['distancia']}.\nAsegúrate de que la cámara encuadre todo tu cuerpo claramente para el conteo automático.")
        dist_text.setWordWrap(True)
        dist_text.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11.5px; border: none;")
        dist_l.addWidget(dist_tag)
        dist_l.addWidget(dist_text)
        card_layout.addWidget(dist_card)

        # Botón Continuar
        btn_start = QPushButton("¡Entendido, Comenzar!")
        btn_start.setFixedHeight(38)
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                font-family: '{FONT_TITLE}';
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
        """)
        btn_start.clicked.connect(self.accept)
        card_layout.addWidget(btn_start)

        layout.addWidget(card)


class ExerciseTransitionModal(QDialog):
    """Modal emergente felicitando al usuario al completar cada ejercicio y mostrando las instrucciones del siguiente con descanso."""
    def __init__(self, parent, completed_ex_name, completed_reps, next_ex_type, next_target_reps):
        super().__init__(parent)
        self.setWindowTitle("¡Felicitaciones!")
        self.setFixedSize(510, 520)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.completed_ex_name = completed_ex_name
        self.completed_reps = completed_reps
        self.next_ex_type = next_ex_type
        self.next_target_reps = next_target_reps

        self._init_ui()

    def _init_ui(self):
        AudioManager.instance().play_transition()
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
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(12)

        # Header con felicitación
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("star", ACCENT_GREEN, size=32))
        
        title_lbl = QLabel("¡Felicitaciones! 🎉")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 20px; color: {TEXT_WHITE}; font-weight: bold; border: none;")
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        card_layout.addLayout(header)

        # Banner de logro del ejercicio finalizado
        comp_banner = QFrame()
        comp_banner.setStyleSheet(f"background-color: {ACCENT_GREEN_BG}; border: 1px solid {ACCENT_GREEN}; border-radius: 10px;")
        cb_l = QHBoxLayout(comp_banner)
        cb_l.setContentsMargins(14, 10, 14, 10)
        
        cb_lbl = QLabel(f"✓ ¡Has completado {self.completed_ex_name}! ({self.completed_reps}/{self.completed_reps} reps)")
        cb_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 13px; font-weight: bold; border: none;")
        cb_l.addWidget(cb_lbl)
        card_layout.addWidget(comp_banner)

        # Card de descanso
        rest_card = QFrame()
        rest_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid #F59E0B; border-radius: 10px;")
        rest_l = QVBoxLayout(rest_card)
        rest_l.setContentsMargins(12, 8, 12, 8)
        rest_l.setSpacing(2)

        rest_title = QLabel("🧘 ZONA DE DESCANSO Y PREPARACIÓN")
        rest_title.setStyleSheet("color: #F59E0B; font-size: 10px; font-weight: bold; border: none;")
        rest_desc = QLabel("Tómate un momento para recuperar el aliento y descansar. Observa atentamente las instrucciones del siguiente ejercicio.")
        rest_desc.setWordWrap(True)
        rest_desc.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; border: none;")

        rest_l.addWidget(rest_title)
        rest_l.addWidget(rest_desc)
        card_layout.addWidget(rest_card)

        # Información e Instrucciones del Siguiente Ejercicio
        info = EXERCISE_INFO.get(self.next_ex_type, EXERCISE_INFO["squat"])
        next_name = info["nombre"]
        meta_str = f"{self.next_target_reps} repeticiones" if self.next_target_reps > 0 else "Estilo Libre"

        next_card = QFrame()
        next_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        nc_l = QVBoxLayout(next_card)
        nc_l.setContentsMargins(14, 12, 14, 12)
        nc_l.setSpacing(6)

        n_tag = QLabel("SIGUIENTE EJERCICIO EN TU RUTINA:")
        n_tag.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none;")
        
        n_val = QLabel(f"{next_name} — Meta: {meta_str}")
        n_val.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 15px; font-weight: bold; border: none;")
        
        n_inst = QLabel(f"📋 Instrucciones:\n{info['descripcion']}")
        n_inst.setWordWrap(True)
        n_inst.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none;")

        n_dist = QLabel(f"📐 Posicionamiento: {info['distancia']}")
        n_dist.setWordWrap(True)
        n_dist.setStyleSheet(f"color: #F59E0B; font-size: 10.5px; font-weight: bold; border: none;")

        nc_l.addWidget(n_tag)
        nc_l.addWidget(n_val)
        nc_l.addWidget(n_inst)
        nc_l.addWidget(n_dist)
        card_layout.addWidget(next_card)

        # Nota informativa para continuar
        note_lbl = QLabel("Presiona 'Continuar' cuando te sientas listo para comenzar.")
        note_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: bold; border: none;")
        card_layout.addWidget(note_lbl)

        # Botón Continuar (el usuario decide cuándo seguir)
        self.btn_next = QPushButton("Continuar ▷")
        self.btn_next.setFixedHeight(40)
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                font-family: '{FONT_TITLE}';
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
        """)
        self.btn_next.clicked.connect(self._on_continue)
        card_layout.addWidget(self.btn_next)

        layout.addWidget(card)

    def _on_continue(self):
        self.accept()


class ActiveExerciseView(QWidget):
    """
    Vista de pantalla completa para el entrenamiento con visión por computadora en tiempo real.
    Soporta rutinas por sesiones multi-ejercicio con cambios automáticos y avisos emergentes.
    """
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self.camera_thread = None
        self.current_challenge = None
        self.latest_stats = {}
        self.session_exercises = []
        self.current_ex_index = 0
        self.is_transitioning = False
        
        # Audio manager y estados de sonido
        self.audio = AudioManager.instance()
        self._last_reps_count = 0
        self._last_prep_sec = None
        self._was_in_prep = True
        self._last_feedback_type = "info"
        
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # ── 1. Barra de Navegación Superior ───────────────────────────────────
        top_bar = QFrame()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Botón Regresar
        btn_back = QPushButton("  Volver")
        btn_back.setIcon(get_icon("logout", TEXT_GRAY, size=14))
        btn_back.setFixedSize(90, 32)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT_GRAY};
                border: 1px solid {BORDER_DARK};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BORDER_DARK};
                color: {TEXT_WHITE};
            }}
        """)
        btn_back.clicked.connect(self._confirm_exit)
        top_layout.addWidget(btn_back)

        # Título del Reto Activo
        self.title_lbl = QLabel("Entrenamiento Activo")
        self.title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 18px; color: {TEXT_WHITE}; font-weight: bold;")
        top_layout.addWidget(self.title_lbl)

        # Indicador "CÁMARA EN VIVO"
        self.live_badge = QLabel(" ● CÁMARA EN VIVO HD")
        self.live_badge.setStyleSheet(f"""
            color: {ACCENT_GREEN};
            font-size: 11px;
            font-weight: bold;
            background-color: {ACCENT_GREEN_BG};
            border: 1px solid {ACCENT_GREEN};
            border-radius: 4px;
            padding: 4px 8px;
        """)
        top_layout.addWidget(self.live_badge, alignment=Qt.AlignmentFlag.AlignRight)

        # Botón para silenciar / activar efectos de sonido
        self.btn_sound = QPushButton()
        self.btn_sound.setFixedSize(32, 32)
        self.btn_sound.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sound.setIcon(get_icon("volume", ACCENT_GREEN, size=16))
        self.btn_sound.setIconSize(QSize(16, 16))
        self.btn_sound.setToolTip("Silenciar / Activar Efectos de Sonido")
        self.btn_sound.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {BORDER_DARK};
            }}
        """)
        self.btn_sound.clicked.connect(self._toggle_sound)
        top_layout.addWidget(self.btn_sound)

        main_layout.addWidget(top_bar)

        # ── 2. Zona de Contenido Principal (Video Feed Panorámico + Panel Lateral) ────────
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Contenedor de Video (Izquierda - Widescreen Panorámico)
        video_card = QFrame()
        video_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        video_card_layout = QVBoxLayout(video_card)
        video_card_layout.setContentsMargins(8, 8, 8, 8)

        self.video_feed_lbl = QLabel("Iniciando cámara web HD...")
        self.video_feed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_feed_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; background-color: #000000; border-radius: 8px;")
        self.video_feed_lbl.setMinimumSize(854, 480)  # Formato 16:9 Panorámico HD
        
        video_card_layout.addWidget(self.video_feed_lbl)
        content_layout.addWidget(video_card, stretch=4)  # Mayor amplitud para video feed

        # Panel Control & Dashboard de Métricas (Derecha)
        panel_card = QFrame()
        panel_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        panel_layout = QVBoxLayout(panel_card)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(14)

        # Card Repeticiones (Realizadas / Meta + Progreso)
        reps_box = QFrame()
        reps_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        reps_layout = QVBoxLayout(reps_box)
        reps_layout.setContentsMargins(14, 12, 14, 12)
        reps_layout.setSpacing(6)
        
        reps_title_row = QHBoxLayout()
        reps_title = QLabel("REPETICIONES (ACTUAL / META)")
        reps_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
        
        self.reps_total_lbl = QLabel("Total: 0 reps")
        self.reps_total_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
        
        reps_title_row.addWidget(reps_title)
        reps_title_row.addStretch()
        reps_title_row.addWidget(self.reps_total_lbl)
        reps_layout.addLayout(reps_title_row)

        self.reps_val_lbl = QLabel("0 / 0")
        self.reps_val_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 32px; color: {ACCENT_GREEN}; font-weight: bold; border: none; background: transparent;")
        reps_layout.addWidget(self.reps_val_lbl)

        self.reps_progress_bar = QProgressBar()
        self.reps_progress_bar.setFixedHeight(8)
        self.reps_progress_bar.setTextVisible(False)
        self.reps_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_GREEN};
                border-radius: 4px;
            }}
        """)
        reps_layout.addWidget(self.reps_progress_bar)
        panel_layout.addWidget(reps_box)

        # Fila Métricas Secundarias (Tiempo y Calorías)
        sec_layout = QHBoxLayout()
        sec_layout.setSpacing(10)

        # Tiempo
        time_box = QFrame()
        time_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        t_layout = QVBoxLayout(time_box)
        t_layout.setContentsMargins(10, 8, 10, 8)
        t_title = QLabel("TIEMPO")
        t_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        self.time_val_lbl = QLabel("00:00")
        self.time_val_lbl.setStyleSheet(f"font-size: 16px; color: {TEXT_WHITE}; font-weight: bold;")
        t_layout.addWidget(t_title)
        t_layout.addWidget(self.time_val_lbl)

        # Calorías
        cal_box = QFrame()
        cal_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        c_layout = QVBoxLayout(cal_box)
        c_layout.setContentsMargins(10, 8, 10, 8)
        c_title = QLabel("CALORÍAS")
        c_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        self.cal_val_lbl = QLabel("0.0 kcal")
        self.cal_val_lbl.setStyleSheet(f"font-size: 16px; color: #F59E0B; font-weight: bold;")
        c_layout.addWidget(c_title)
        c_layout.addWidget(self.cal_val_lbl)

        sec_layout.addWidget(time_box)
        sec_layout.addWidget(cal_box)
        panel_layout.addLayout(sec_layout)

        # Banner de Retroalimentación Postural y Distancia
        feedback_box = QFrame()
        feedback_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        f_layout = QVBoxLayout(feedback_box)
        f_layout.setContentsMargins(12, 10, 12, 10)

        f_title = QLabel("POSTURA Y RETROALIMENTACIÓN")
        f_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        self.feedback_val_lbl = QLabel("Posiciónate a 1.5m - 2.5m de la cámara")
        self.feedback_val_lbl.setWordWrap(True)
        self.feedback_val_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 12px; font-weight: bold;")

        f_layout.addWidget(f_title)
        f_layout.addWidget(self.feedback_val_lbl)
        panel_layout.addWidget(feedback_box)

        # Selector rápido de Ejercicio
        ex_select_lbl = QLabel("SELECCIÓN DE EJERCICIO EN SESIÓN")
        ex_select_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        panel_layout.addWidget(ex_select_lbl)

        ex_btns_layout = QHBoxLayout()
        ex_btns_layout.setSpacing(6)

        self.btn_ex_squat = QPushButton("Sentadillas")
        self.btn_ex_pushup = QPushButton("Lagartijas")
        self.btn_ex_jacks = QPushButton("Jacks")

        for b in [self.btn_ex_squat, self.btn_ex_pushup, self.btn_ex_jacks]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(28)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_SIDEBAR};
                    color: {TEXT_GRAY};
                    border: 1px solid {BORDER_DARK};
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 1px solid {ACCENT_GREEN};
                    color: {TEXT_WHITE};
                }}
            """)

        self.btn_ex_squat.clicked.connect(lambda: self._manual_switch_exercise("squat"))
        self.btn_ex_pushup.clicked.connect(lambda: self._manual_switch_exercise("pushup"))
        self.btn_ex_jacks.clicked.connect(lambda: self._manual_switch_exercise("jumping_jacks"))

        ex_btns_layout.addWidget(self.btn_ex_squat)
        ex_btns_layout.addWidget(self.btn_ex_pushup)
        ex_btns_layout.addWidget(self.btn_ex_jacks)
        panel_layout.addLayout(ex_btns_layout)

        panel_layout.addStretch()

        # Botones de Acción Iniciar/Pausar/Finalizar
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        self.btn_pause = QPushButton("Pausar Entrenamiento")
        self.btn_pause.setFixedHeight(34)
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_WHITE};
                border: 1px solid {BORDER_LIGHT};
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BORDER_DARK};
            }}
        """)
        self.btn_pause.clicked.connect(self._toggle_pause)

        self.btn_finish = QPushButton("Finalizar Entrenamiento")
        self.btn_finish.setFixedHeight(40)
        self.btn_finish.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finish.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                font-family: '{FONT_TITLE}';
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
        """)
        self.btn_finish.clicked.connect(self._finish_workout)

        actions_layout.addWidget(self.btn_pause)
        actions_layout.addWidget(self.btn_finish)
        panel_layout.addLayout(actions_layout)

        content_layout.addWidget(panel_card, stretch=1)
        main_layout.addLayout(content_layout)

    def start_session(self, challenge_data):
        """Inicializa la captura de cámara con la rutina por sesiones del reto seleccionado."""
        self.current_challenge = challenge_data or {
            "id": "ejercicio_libre",
            "nombre": "Ejercicio Libre",
            "badge": "LIBRE"
        }

        self.title_lbl.setText(f"Entrenamiento: {self.current_challenge['nombre']}")

        # Parsear secuencia de ejercicios en la rutina
        raw_exercises = self.current_challenge.get("ejercicios", [("Sentadillas", "Libre", "squat")])
        self.session_exercises = []
        for item in raw_exercises:
            name = item[0]
            reps_str = item[1]
            ex_type = item[2] if len(item) > 2 else "squat"
            target_reps = 0
            if "reps" in reps_str.lower():
                try:
                    target_reps = int(reps_str.split()[0])
                except Exception:
                    target_reps = 0
            self.session_exercises.append({
                "name": name,
                "reps_str": reps_str,
                "ex_type": ex_type,
                "target_reps": target_reps
            })

        self.current_ex_index = 0
        self.is_transitioning = False
        self._last_reps_count = 0
        self._last_prep_sec = None
        self._was_in_prep = True
        self._last_feedback_type = "info"

        first_ex = self.session_exercises[0]

        # 1. Modal informativo de bienvenida antes de iniciar la rutina
        start_modal = ExerciseStartModal(
            self,
            self.current_challenge.get("nombre", "Entrenamiento"),
            first_ex["ex_type"],
            first_ex["target_reps"]
        )
        start_modal.exec()

        self._switch_exercise(first_ex["ex_type"], target_reps=first_ex["target_reps"])

        # Detener hilo previo si existe
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()

        # Iniciar nuevo hilo de cámara con resolución HD y meta del primer ejercicio
        self.camera_thread = CameraThread(
            camera_index=0, 
            exercise_type=first_ex["ex_type"], 
            target_reps=first_ex["target_reps"]
        )
        self.camera_thread.frame_processed.connect(self._on_frame_processed)
        self.camera_thread.stats_updated.connect(self._on_stats_updated)
        self.camera_thread.error_occurred.connect(self._on_camera_error)
        self.camera_thread.start()

    def _manual_switch_exercise(self, ex_type):
        """Permite cambio manual rápido de ejercicio sin meta forzada."""
        self._switch_exercise(ex_type, target_reps=0, preserve_session_totals=True)

    def _switch_exercise(self, ex_type, target_reps=0, preserve_session_totals=False):
        """Cambia el ejercicio activo y actualiza los estilos de la interfaz."""
        self._last_reps_count = 0
        if self.camera_thread:
            self.camera_thread.set_exercise(
                ex_type, 
                target_reps=target_reps, 
                preserve_session_totals=preserve_session_totals
            )

        btn_map = {
            "squat": self.btn_ex_squat,
            "pushup": self.btn_ex_pushup,
            "jumping_jacks": self.btn_ex_jacks
        }

        for key, btn in btn_map.items():
            if key == ex_type:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {ACCENT_GREEN_BG};
                        color: {ACCENT_GREEN};
                        border: 1.5px solid {ACCENT_GREEN};
                        border-radius: 6px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {BG_SIDEBAR};
                        color: {TEXT_GRAY};
                        border: 1px solid {BORDER_DARK};
                        border-radius: 6px;
                        font-size: 10px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        border: 1px solid {ACCENT_GREEN};
                        color: {TEXT_WHITE};
                    }}
                """)

    def _on_frame_processed(self, q_img):
        """Renderiza la imagen procesada en el widget QLabel."""
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.video_feed_lbl.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_feed_lbl.setPixmap(scaled_pixmap)

    def _on_stats_updated(self, stats):
        """Actualiza las tarjetas con información en tiempo real y gestiona cambios por sesiones."""
        self.latest_stats = stats
        
        reps = stats["reps"]
        target_reps = stats.get("target_reps", 0)
        total_session_reps = stats.get("total_session_reps", reps)

        # ── Audio Feedback en Vivo ───────────────────────────────────────────
        in_prep = stats.get("in_prep", False)
        rem_prep = stats.get("remaining_prep", 0)

        if in_prep:
            if rem_prep != self._last_prep_sec and rem_prep > 0:
                self._last_prep_sec = rem_prep
                self.audio.play_countdown_tick()
        elif self._was_in_prep and not in_prep:
            # Cambio de preparación a entrenamiento activo
            self.audio.play_countdown_go()

        self._was_in_prep = in_prep

        if not in_prep:
            if reps > self._last_reps_count:
                self.audio.play_rep()
                self._last_reps_count = reps
            elif reps < self._last_reps_count:
                self._last_reps_count = reps

        fb_type = stats.get("feedback_type", "info")
        if fb_type == "warning" and self._last_feedback_type != "warning" and not in_prep:
            self.audio.play_warning()
        self._last_feedback_type = fb_type

        if target_reps > 0:
            self.reps_val_lbl.setText(f"{reps} / {target_reps}")
            progress_pct = int((reps / float(target_reps)) * 100)
            self.reps_progress_bar.setValue(min(100, progress_pct))
        else:
            self.reps_val_lbl.setText(f"{reps} reps")
            self.reps_progress_bar.setValue(min(100, stats.get("progress", 0)))

        self.reps_total_lbl.setText(f"Total: {total_session_reps} reps")

        # Formatear tiempo en mm:ss
        elapsed = stats["elapsed"]
        mins = elapsed // 60
        secs = elapsed % 60
        self.time_val_lbl.setText(f"{mins:02d}:{secs:02d}")
        
        self.cal_val_lbl.setText(f"{stats['calories']} kcal")
        
        self.feedback_val_lbl.setText(stats["feedback"])
        if stats["feedback_type"] == "good":
            self.feedback_val_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 12px; font-weight: bold;")
        elif stats["feedback_type"] == "warning":
            self.feedback_val_lbl.setStyleSheet(f"color: #F59E0B; font-size: 12px; font-weight: bold;")
        else:
            self.feedback_val_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 12px; font-weight: bold;")

        # Transición automática de ejercicios al cumplir repeticiones de la sesión (solo fuera de preparación)
        if not stats.get("in_prep", False) and target_reps > 0 and reps >= target_reps and not getattr(self, 'is_transitioning', False) and not getattr(self, '_is_finishing', False):
            self.is_transitioning = True
            current_ex = self.session_exercises[self.current_ex_index]
            
            if self.current_ex_index + 1 < len(self.session_exercises):
                next_ex = self.session_exercises[self.current_ex_index + 1]
                
                # Pausar la cámara durante la notificación de transición
                if self.camera_thread:
                    self.camera_thread.pause()
                
                trans_dlg = ExerciseTransitionModal(
                    self,
                    completed_ex_name=current_ex["name"],
                    completed_reps=reps,
                    next_ex_type=next_ex["ex_type"],
                    next_target_reps=next_ex["target_reps"]
                )
                trans_dlg.exec()
                
                self.current_ex_index += 1
                self._switch_exercise(
                    next_ex["ex_type"], 
                    target_reps=next_ex["target_reps"], 
                    preserve_session_totals=True
                )
                
                if self.camera_thread:
                    self.camera_thread.resume()
                
                self.is_transitioning = False
            else:
                # Rutina completa finalizada
                if self.camera_thread:
                    self.camera_thread.stop()
                    self.camera_thread = None
                self._finish_workout()

    def _on_camera_error(self, err_msg):
        QMessageBox.warning(self, "Error de Cámara", err_msg)
        self._exit_view()

    def _toggle_pause(self):
        self.audio.play_click()
        if not self.camera_thread:
            return
        if self.camera_thread.paused:
            self.camera_thread.resume()
            self.btn_pause.setText("Pausar Entrenamiento")
            self.live_badge.setText(" ● CÁMARA EN VIVO HD")
            self.live_badge.setStyleSheet(f"color: {ACCENT_GREEN}; background-color: {ACCENT_GREEN_BG}; border: 1px solid {ACCENT_GREEN}; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: bold;")
        else:
            self.camera_thread.pause()
            self.btn_pause.setText("Reanudar Entrenamiento")
            self.live_badge.setText(" ❚❚ PAUSADO")
            self.live_badge.setStyleSheet(f"color: #F59E0B; background-color: #1F170A; border: 1px solid #F59E0B; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: bold;")

    def _confirm_exit(self):
        self.audio.play_click()
        reply = QMessageBox.question(
            self, "Confirmar Salida",
            "¿Deseas salir del entrenamiento actual? Se perderá el progreso sin guardar.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._exit_view()

    def _finish_workout(self):
        if getattr(self, '_is_finishing', False):
            return
        self._is_finishing = True

        # Detener hilo de cámara limpiamente
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None

        # Calcular métricas finales consolidadas
        reps = self.latest_stats.get("total_session_reps", self.latest_stats.get("reps", 0))
        elapsed = self.latest_stats.get("elapsed", 0)
        calories = self.latest_stats.get("calories", 0.0)

        summary = SessionAnalyzer.calculate_session_stats(
            self.current_challenge, reps, elapsed, calories
        )

        # Guardar en Firebase o sesión de invitado
        controller = getattr(self.shell, 'controller', None)
        user_id = getattr(controller, 'current_user_id', None)
        fb_db = getattr(controller, 'fb_db', None)

        try:
            SessionAnalyzer.save_session_to_firebase(fb_db, user_id, summary, controller=controller)
        except Exception as e:
            print(f"[ActiveExerciseView] Error guardando sesión: {e}")

        # Mostrar resumen modal
        try:
            dlg = WorkoutSummaryModal(self, summary)
            dlg.exec()
        except Exception as e:
            print(f"[ActiveExerciseView] Error en modal de resumen: {e}")

        self._exit_view()
        self._is_finishing = False

    def _exit_view(self):
        self.audio.play_click()
        if self.camera_thread:
            if self.camera_thread.isRunning():
                self.camera_thread.stop()
            self.camera_thread = None
        
        # Volver a la vista de ejercicios
        if hasattr(self.shell, 'navigate'):
            self.shell.navigate("ejercicios")

    def _toggle_sound(self):
        """Silencia o reactiva los efectos de sonido."""
        is_muted = self.audio.toggle_sfx_mute()
        icon_name = "volume-x" if is_muted else "volume"
        icon_color = TEXT_MUTED if is_muted else ACCENT_GREEN
        self.btn_sound.setIcon(get_icon(icon_name, icon_color, size=16))
        if not is_muted:
            self.audio.play_click()

