import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QDialog, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QImage, QPixmap

from ui.styles import (
    BG_MAIN, BG_CARD, BG_SIDEBAR, BORDER_DARK, BORDER_LIGHT, TEXT_WHITE, 
    TEXT_GRAY, TEXT_MUTED, ACCENT_GREEN, ACCENT_GREEN_BG, HARD_TX, HARD_BG,
    FONT_TITLE, EASY_BG, EASY_TX, NORM_BG, NORM_TX, FREE_BG, FREE_TX
)
from ui.icons import get_icon, get_icon_pixmap
from core.camera_worker import CameraThread
from core.analyzer import SessionAnalyzer

class WorkoutSummaryModal(QDialog):
    """Modal emergente al finalizar el entrenamiento con resumen de estadísticas."""
    def __init__(self, parent, session_summary):
        super().__init__(parent)
        self.setWindowTitle("Resumen de Entrenamiento")
        self.setFixedSize(450, 380)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.summary = session_summary
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
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("streak", ACCENT_GREEN, size=32))
        
        title_lbl = QLabel("¡Entrenamiento Completado!")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 18px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        card_layout.addLayout(header)

        # Nombre del Reto
        reto_name = self.summary.get("reto_nombre", "Entrenamiento Libre")
        sub_lbl = QLabel(f"Resultados de {reto_name}")
        sub_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 12px; border: none; background: transparent;")
        card_layout.addWidget(sub_lbl)

        # Rejilla de Métricas 2x2
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        metrics_layout = QVBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(16, 16, 16, 16)
        metrics_layout.setSpacing(12)

        def add_metric(label, value, icon_name, color):
            row = QHBoxLayout()
            ic = QLabel()
            ic.setPixmap(get_icon_pixmap(icon_name, color, size=16))
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {TEXT_WHITE}; font-weight: bold; font-size: 12px; border: none; background: transparent;")
            
            row.addWidget(ic)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            metrics_layout.addLayout(row)

        add_metric("Repeticiones Totales", f"{self.summary.get('repeticiones_totales', 0)} reps", "squat", ACCENT_GREEN)
        add_metric("Duración Total", f"{self.summary.get('duracion_minutos', 0)} min", "clock", "#3B82F6")
        add_metric("Calorías Quemadas", f"{self.summary.get('calorias_estimadas', 0)} kcal", "streak", "#F59E0B")
        add_metric("Precisión Postural", f"{self.summary.get('precision_postural', 0)}%", "stats", "#8B5CF6")

        card_layout.addWidget(metrics_frame)

        # Botón Aceptar
        btn_accept = QPushButton("Guardar y Volver a Ejercicios")
        btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_accept.setFixedHeight(38)
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


class ActiveExerciseView(QWidget):
    """
    Vista de pantalla completa para el entrenamiento con visión por computadora en tiempo real.
    """
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self.camera_thread = None
        self.current_challenge = None
        self.latest_stats = {}
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
        self.live_badge = QLabel(" ● CÁMARA EN VIVO")
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

        main_layout.addWidget(top_bar)

        # ── 2. Zona de Contenido Principal (Video Feed + Panel Lateral) ────────
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Contenedor de Video (Izquierda)
        video_card = QFrame()
        video_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        video_card_layout = QVBoxLayout(video_card)
        video_card_layout.setContentsMargins(8, 8, 8, 8)

        self.video_feed_lbl = QLabel("Iniciando cámara web...")
        self.video_feed_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_feed_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px; background-color: #000000; border-radius: 8px;")
        self.video_feed_lbl.setMinimumSize(640, 480)
        
        video_card_layout.addWidget(self.video_feed_lbl)
        content_layout.addWidget(video_card, stretch=3)

        # Panel Control & Dashboard de Métricas (Derecha)
        panel_card = QFrame()
        panel_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 12px;")
        panel_layout = QVBoxLayout(panel_card)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(14)

        # Card Repeticiones
        reps_box = QFrame()
        reps_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        reps_layout = QVBoxLayout(reps_box)
        reps_layout.setContentsMargins(14, 12, 14, 12)
        
        reps_title = QLabel("REPETICIONES")
        reps_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        
        self.reps_val_lbl = QLabel("0")
        self.reps_val_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 38px; color: {ACCENT_GREEN}; font-weight: bold; border: none; background: transparent;")
        
        reps_layout.addWidget(reps_title)
        reps_layout.addWidget(self.reps_val_lbl)
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

        # Banner de Retroalimentación Postural
        feedback_box = QFrame()
        feedback_box.setStyleSheet(f"background-color: {BG_SIDEBAR}; border: 1px solid {BORDER_DARK}; border-radius: 10px;")
        f_layout = QVBoxLayout(feedback_box)
        f_layout.setContentsMargins(12, 10, 12, 10)

        f_title = QLabel("POSTURA Y RETROALIMENTACIÓN")
        f_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        self.feedback_val_lbl = QLabel("Posiciónate frente a la cámara")
        self.feedback_val_lbl.setWordWrap(True)
        self.feedback_val_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 12px; font-weight: bold;")

        f_layout.addWidget(f_title)
        f_layout.addWidget(self.feedback_val_lbl)
        panel_layout.addWidget(feedback_box)

        # Selector rápido de Ejercicio
        ex_select_lbl = QLabel("CAMBIAR EJERCICIO")
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

        self.btn_ex_squat.clicked.connect(lambda: self._switch_exercise("squat"))
        self.btn_ex_pushup.clicked.connect(lambda: self._switch_exercise("pushup"))
        self.btn_ex_jacks.clicked.connect(lambda: self._switch_exercise("jumping_jacks"))

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
        """Inicializa la captura de cámara con los parámetros del reto seleccionado."""
        self.current_challenge = challenge_data or {
            "id": "ejercicio_libre",
            "nombre": "Ejercicio Libre",
            "badge": "LIBRE"
        }

        self.title_lbl.setText(f"Entrenamiento: {self.current_challenge['nombre']}")

        # Determinar tipo de ejercicio inicial
        ex_type = "squat"
        if self.current_challenge.get("ejercicios"):
            first_ex = self.current_challenge["ejercicios"][0]
            ex_type = first_ex[2] if len(first_ex) > 2 else "squat"

        self._switch_exercise(ex_type)

        # Detener hilo previo si existe
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()

        # Iniciar nuevo hilo de cámara
        self.camera_thread = CameraThread(camera_index=0, exercise_type=ex_type)
        self.camera_thread.frame_processed.connect(self._on_frame_processed)
        self.camera_thread.stats_updated.connect(self._on_stats_updated)
        self.camera_thread.error_occurred.connect(self._on_camera_error)
        self.camera_thread.start()

    def _switch_exercise(self, ex_type):
        """Cambia el ejercicio activo y actualiza los estilos de los botones."""
        if self.camera_thread:
            self.camera_thread.set_exercise(ex_type)

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
        """Actualiza las tarjetas con información en tiempo real."""
        self.latest_stats = stats
        self.reps_val_lbl.setText(str(stats["reps"]))
        
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

    def _on_camera_error(self, err_msg):
        QMessageBox.warning(self, "Error de Cámara", err_msg)
        self._exit_view()

    def _toggle_pause(self):
        if not self.camera_thread:
            return
        if self.camera_thread.paused:
            self.camera_thread.resume()
            self.btn_pause.setText("Pausar Entrenamiento")
            self.live_badge.setText(" ● CÁMARA EN VIVO")
            self.live_badge.setStyleSheet(f"color: {ACCENT_GREEN}; background-color: {ACCENT_GREEN_BG}; border: 1px solid {ACCENT_GREEN}; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: bold;")
        else:
            self.camera_thread.pause()
            self.btn_pause.setText("Reanudar Entrenamiento")
            self.live_badge.setText(" ❚❚ PAUSADO")
            self.live_badge.setStyleSheet(f"color: #F59E0B; background-color: #1F170A; border: 1px solid #F59E0B; border-radius: 4px; padding: 4px 8px; font-size: 11px; font-weight: bold;")

    def _confirm_exit(self):
        reply = QMessageBox.question(
            self, "Confirmar Salida",
            "¿Deseas salir del entrenamiento actual? Se perderá el progreso sin guardar.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._exit_view()

    def _finish_workout(self):
        # Detener hilo de cámara
        if self.camera_thread:
            self.camera_thread.stop()

        # Calcular métricas finales
        reps = self.latest_stats.get("reps", 0)
        elapsed = self.latest_stats.get("elapsed", 0)
        calories = self.latest_stats.get("calories", 0.0)

        summary = SessionAnalyzer.calculate_session_stats(
            self.current_challenge, reps, elapsed, calories
        )

        # Guardar en Firebase si hay usuario
        controller = getattr(self.shell, 'controller', None)
        user_id = getattr(controller, 'current_user_id', None)
        fb_db = getattr(controller, 'fb_db', None)

        SessionAnalyzer.save_session_to_firebase(fb_db, user_id, summary, controller=controller)

        # Mostrar resumen modal
        dlg = WorkoutSummaryModal(self, summary)
        dlg.exec()

        self._exit_view()

    def _exit_view(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
        
        # Volver a la vista de ejercicios
        if hasattr(self.shell, 'navigate'):
            self.shell.navigate("ejercicios")
