import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from PyQt6.QtGui import QImage

from core.pose_detector import PoseDetector
from core.exercise_counter import ExerciseCounter

def clean_cv2_text(text):
    """Sanea caracteres especiales y acentuados para compatibilidad total con cv2.putText sin mostrar '??'."""
    if not text:
        return ""
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', '¿': '', '¡': '', 'ü': 'u', 'Ü': 'U'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

class CameraThread(QThread):
    """
    Hilo secundario PyQt6 para capturar video de la cámara web sin bloquear la interfaz gráfica.
    Realiza la detección de la postura en tiempo real y emite la imagen procesada y las estadísticas.
    """
    frame_processed = pyqtSignal(QImage)
    stats_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0, exercise_type="squat", target_reps=0):
        super().__init__()
        self.camera_index = camera_index
        self.exercise_type = exercise_type
        self.target_reps = target_reps
        self.running = False
        self.paused = False
        self.mutex = QMutex()
        self.cap = None

        self.in_prep_mode = True
        self.prep_seconds = 5
        self.prep_start_time = time.time()

        self.detector = PoseDetector(min_detection_con=0.6)
        self.counter = ExerciseCounter(exercise_type=self.exercise_type, target_reps=self.target_reps)

    def start_prep(self, duration=5):
        """Inicia el temporizador de preparación de N segundos."""
        self.mutex.lock()
        self.prep_seconds = duration
        self.prep_start_time = time.time()
        self.in_prep_mode = True
        self.mutex.unlock()

    def set_exercise(self, exercise_type, target_reps=0, preserve_session_totals=False, start_prep=True):
        """Cambia el tipo de ejercicio activo y su meta."""
        self.mutex.lock()
        self.exercise_type = exercise_type
        self.target_reps = target_reps
        self.counter.set_exercise(exercise_type, target_reps=target_reps, preserve_session_totals=preserve_session_totals)
        if start_prep:
            self.in_prep_mode = True
            self.prep_seconds = 5
            self.prep_start_time = time.time()
        self.mutex.unlock()

    def run(self):
        """Bucle principal de lectura y procesamiento de frames de cámara."""
        self.running = True
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        
        # Si la cámara por defecto falla con DSHOW, intentar abrir en modo normal
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            self.error_occurred.emit("No se pudo acceder a la cámara web.")
            self.running = False
            return

        # Ajustar resolución deseada a HD Panorámico
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Iniciar tiempo de preparación
        self.prep_start_time = time.time()

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret or not self.running:
                time.sleep(0.03)
                continue

            # Voltear horizontalmente para efecto espejo natural
            frame = cv2.flip(frame, 1)

            self.mutex.lock()
            ex_type = self.exercise_type
            t_reps = self.target_reps
            is_prep = self.in_prep_mode
            p_seconds = self.prep_seconds
            p_start = self.prep_start_time
            self.mutex.unlock()

            now = time.time()
            remaining_prep = 0

            if is_prep:
                elapsed_prep = now - p_start
                remaining_prep = int(np.ceil(p_seconds - elapsed_prep))
                if remaining_prep <= 0:
                    self.mutex.lock()
                    self.in_prep_mode = False
                    is_prep = False
                    self.counter.start_time = time.time()
                    self.mutex.unlock()

            # 1. Detectar postura y calcular landmarks
            frame = self.detector.find_pose(frame, draw=True)
            self.detector.find_positions(frame, draw=False)

            # 2. Procesar contador y retroalimentación
            if is_prep:
                reps = self.counter.counter
                feedback = "Acomodate a 1.5m - 2.5m de la camara"
                progress = 0
            else:
                reps, feedback, progress = self.counter.process(self.detector, frame)

            # 3. Dibujar silueta de posicionamiento durante la preparación
            if is_prep:
                self._draw_body_silhouette_overlay(frame)
                self._draw_prep_countdown_overlay(frame, remaining_prep)

            # 4. Dibujar overlay visual en el frame (HUD)
            self._draw_hud_overlay(frame, reps, t_reps, feedback, self.counter.feedback_type, progress)

            # 5. Convertir BGR a QImage para PyQt6
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # 6. Emitir señales hacia la vista de la UI sólo si sigue en ejecución
            if self.running:
                self.frame_processed.emit(qt_img)
                display_feedback = "Preparando posicion..." if is_prep else feedback
                self.stats_updated.emit({
                    "reps": reps,
                    "target_reps": t_reps,
                    "total_session_reps": self.counter.get_total_reps(),
                    "feedback": display_feedback,
                    "feedback_type": "info" if is_prep else self.counter.feedback_type,
                    "progress": progress,
                    "elapsed": self.counter.get_elapsed_time() if not is_prep else 0,
                    "calories": self.counter.get_calories(),
                    "exercise_type": ex_type,
                    "in_prep": is_prep
                })

            time.sleep(0.02)  # Aprox 45-50 FPS máximo

        # Liberar cámara al salir del bucle
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def pause(self):
        """Pausa el procesamiento de video."""
        self.paused = True

    def resume(self):
        """Reanuda el procesamiento de video."""
        self.paused = False

    def stop(self):
        """Detiene la captura de cámara de forma segura sin bloquear el hilo GUI principal."""
        self.running = False
        try:
            self.frame_processed.disconnect()
        except Exception:
            pass
        try:
            self.stats_updated.disconnect()
        except Exception:
            pass
        
        if not self.wait(1000):
            try:
                self.terminate()
            except Exception:
                pass

    def _draw_body_silhouette_overlay(self, frame):
        """Dibuja una silueta guía sombreada y semitransparente perfectamente centrada."""
        h, w, _ = frame.shape
        overlay = frame.copy()

        center_x = w // 2
        center_y = h // 2

        # Dimensiones proporcionales centradas (Guía de Encuadre 1.5m - 2.5m)
        head_cy = center_y - int(h * 0.28)
        head_r = int(h * 0.065)
        
        shoulder_y = center_y - int(h * 0.18)
        shoulder_w = int(w * 0.22)
        
        hip_y = center_y + int(h * 0.05)
        hip_w = int(w * 0.16)
        
        feet_y = center_y + int(h * 0.34)
        foot_w = int(w * 0.20)

        color_sil = (0, 230, 180)    # Verde esmeralda suave

        # 1. Marco de encuadre externo centrado con esquinas orientativas
        box_w = int(w * 0.44)
        box_h = int(h * 0.78)
        box_left = center_x - box_w // 2
        box_right = center_x + box_w // 2
        box_top = center_y - box_h // 2
        box_bottom = center_y + box_h // 2

        corner_len = 25
        thickness = 2
        # Esquina superior izquierda
        cv2.line(overlay, (box_left, box_top), (box_left + corner_len, box_top), color_sil, thickness)
        cv2.line(overlay, (box_left, box_top), (box_left, box_top + corner_len), color_sil, thickness)
        # Esquina superior derecha
        cv2.line(overlay, (box_right, box_top), (box_right - corner_len, box_top), color_sil, thickness)
        cv2.line(overlay, (box_right, box_top), (box_right, box_top + corner_len), color_sil, thickness)
        # Esquina inferior izquierda
        cv2.line(overlay, (box_left, box_bottom), (box_left + corner_len, box_bottom), color_sil, thickness)
        cv2.line(overlay, (box_left, box_bottom), (box_left, box_bottom - corner_len), color_sil, thickness)
        # Esquina inferior derecha
        cv2.line(overlay, (box_right, box_bottom), (box_right - corner_len, box_bottom), color_sil, thickness)
        cv2.line(overlay, (box_right, box_bottom), (box_right, box_bottom - corner_len), color_sil, thickness)

        # 2. Cabeza centrada
        cv2.circle(overlay, (center_x, head_cy), head_r, color_sil, 2, cv2.LINE_AA)
        
        # 3. Torso estético
        torso_pts = np.array([
            [center_x - shoulder_w // 2, shoulder_y],
            [center_x + shoulder_w // 2, shoulder_y],
            [center_x + hip_w // 2, hip_y],
            [center_x - hip_w // 2, hip_y]
        ], np.int32)
        cv2.polylines(overlay, [torso_pts], isClosed=True, color=color_sil, thickness=2, lineType=cv2.LINE_AA)
        cv2.fillPoly(overlay, [torso_pts], (30, 45, 40))

        # 4. Brazos centrados
        cv2.line(overlay, (center_x - shoulder_w // 2, shoulder_y), (center_x - shoulder_w // 2 - 20, hip_y), color_sil, 2, cv2.LINE_AA)
        cv2.line(overlay, (center_x + shoulder_w // 2, shoulder_y), (center_x + shoulder_w // 2 + 20, hip_y), color_sil, 2, cv2.LINE_AA)

        # 5. Piernas centradas
        cv2.line(overlay, (center_x - hip_w // 3, hip_y), (center_x - foot_w // 2, feet_y), color_sil, 2, cv2.LINE_AA)
        cv2.line(overlay, (center_x + hip_w // 3, hip_y), (center_x + foot_w // 2, feet_y), color_sil, 2, cv2.LINE_AA)

        # Mezclar transparencia sutil (alpha blending 25%)
        alpha = 0.25
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Etiqueta indicadora centrada sobre el marco
        tag_text = clean_cv2_text("ALINEA TU CUERPO AQUI (1.5m - 2.5m)")
        (tw, th), _ = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(frame, (center_x - tw // 2 - 10, box_bottom + 8), (center_x + tw // 2 + 10, box_bottom + 32), (20, 20, 20), -1)
        cv2.putText(frame, tag_text, (center_x - tw // 2, box_bottom + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 200), 1, cv2.LINE_AA)

    def _draw_prep_countdown_overlay(self, frame, remaining_seconds):
        """Dibuja la cuenta regresiva gigante central de 5s."""
        h, w, _ = frame.shape
        center_x = w // 2
        center_y = h // 2

        # Cuadro translúcido central
        card_w, card_h = 420, 160
        x1 = center_x - card_w // 2
        y1 = center_y - card_h // 2
        x2 = center_x + card_w // 2
        y2 = center_y + card_h // 2

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (15, 15, 15), -1)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 200), 2)
        cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

        txt1 = clean_cv2_text("PREPARATE PARA EMPEZAR")
        txt2 = f"{remaining_seconds}" if remaining_seconds > 0 else "¡YA!"

        (w1, h1), _ = cv2.getTextSize(txt1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, txt1, (center_x - w1 // 2, y1 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2, cv2.LINE_AA)

        (w2, h2), _ = cv2.getTextSize(txt2, cv2.FONT_HERSHEY_SIMPLEX, 2.2, 4)
        cv2.putText(frame, txt2, (center_x - w2 // 2, y1 + 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 255, 200), 4, cv2.LINE_AA)

    def _draw_hud_overlay(self, frame, reps, target_reps, feedback, feedback_type, progress):
        """Dibuja elementos gráficos sobre el frame de la cámara."""
        h, w, _ = frame.shape

        # Banner superior de retroalimentación
        banner_bg = (30, 30, 30)
        if feedback_type == "good":
            banner_bg = (34, 150, 60)  # Verde
        elif feedback_type == "warning":
            banner_bg = (20, 100, 220)  # Naranja/Rojo

        cv2.rectangle(frame, (20, 20), (w - 20, 70), banner_bg, -1)
        cv2.rectangle(frame, (20, 20), (w - 20, 70), (255, 255, 255), 1)
        
        # Limpiar texto para evitar '??' en OpenCV putText
        safe_feedback = clean_cv2_text(feedback)
        cv2.putText(frame, safe_feedback, (35, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # Guía de distancia sutil en parte superior izquierda
        dist_lbl = clean_cv2_text("Distancia ideal: 1.5m - 2.5m")
        cv2.putText(frame, dist_lbl, (30, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

        # Barra lateral de progreso de repetición
        bar_x = w - 40
        bar_y1 = 110
        bar_y2 = h - 60
        bar_h = bar_y2 - bar_y1

        # Fondo barra
        cv2.rectangle(frame, (bar_x, bar_y1), (bar_x + 20, bar_y2), (50, 50, 50), -1)
        # Relleno barra
        fill_h = int((progress / 100.0) * bar_h)
        cv2.rectangle(frame, (bar_x, bar_y2 - fill_h), (bar_x + 20, bar_y2), (0, 255, 200), -1)
        cv2.rectangle(frame, (bar_x, bar_y1), (bar_x + 20, bar_y2), (255, 255, 255), 1)

        # Marcador de repeticiones en esquina inferior izquierda (ampliado para meta)
        box_w = 230 if target_reps > 0 else 160
        cv2.rectangle(frame, (20, h - 90), (20 + box_w, h - 20), (20, 20, 20), -1)
        cv2.rectangle(frame, (20, h - 90), (20 + box_w, h - 20), (0, 255, 200), 2)
        
        rep_label = "REPS / META" if target_reps > 0 else "REPS"
        cv2.putText(frame, rep_label, (35, h - 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        
        reps_text = f"{reps} / {target_reps}" if target_reps > 0 else str(reps)
        cv2.putText(frame, reps_text, (35, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3, cv2.LINE_AA)
