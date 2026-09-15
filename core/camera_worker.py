import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from PyQt6.QtGui import QImage

from core.pose_detector import PoseDetector
from core.exercise_counter import ExerciseCounter

class CameraThread(QThread):
    """
    Hilo secundario PyQt6 para capturar video de la cámara web sin bloquear la interfaz gráfica.
    Realiza la detección de la postura en tiempo real y emite la imagen procesada y las estadísticas.
    """
    frame_processed = pyqtSignal(QImage)
    stats_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0, exercise_type="squat"):
        super().__init__()
        self.camera_index = camera_index
        self.exercise_type = exercise_type
        self.running = False
        self.paused = False
        self.mutex = QMutex()
        self.cap = None

        self.detector = PoseDetector(min_detection_con=0.6)
        self.counter = ExerciseCounter(exercise_type=self.exercise_type)

    def set_exercise(self, exercise_type):
        """Cambia el tipo de ejercicio activo."""
        self.mutex.lock()
        self.exercise_type = exercise_type
        self.counter.set_exercise(exercise_type)
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

        # Ajustar resolución deseada
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            # Voltear horizontalmente para efecto espejo natural
            frame = cv2.flip(frame, 1)

            self.mutex.lock()
            ex_type = self.exercise_type
            self.mutex.unlock()

            # 1. Detectar postura y calcular landmarks
            frame = self.detector.find_pose(frame, draw=True)
            self.detector.find_positions(frame, draw=False)

            # 2. Procesar contador y retroalimentación
            reps, feedback, progress = self.counter.process(self.detector, frame)

            # 3. Dibujar overlay visual en el frame (HUD)
            self._draw_hud_overlay(frame, reps, feedback, self.counter.feedback_type, progress)

            # 4. Convertir BGR a QImage para PyQt6
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # 5. Emitir señales hacia la vista de la UI
            self.frame_processed.emit(qt_img)
            self.stats_updated.emit({
                "reps": reps,
                "feedback": feedback,
                "feedback_type": self.counter.feedback_type,
                "progress": progress,
                "elapsed": self.counter.get_elapsed_time(),
                "calories": self.counter.get_calories(),
                "exercise_type": ex_type
            })

            time.sleep(0.02)  # Aprox 45-50 FPS máximo

        # Liberar cámara al salir del bucle
        if self.cap:
            self.cap.release()
            self.cap = None

    def pause(self):
        """Pausa el procesamiento de video."""
        self.paused = True

    def resume(self):
        """Reanuda el procesamiento de video."""
        self.paused = False

    def stop(self):
        """Detiene la captura de cámara de forma segura."""
        self.running = False
        self.wait()

    def _draw_hud_overlay(self, frame, reps, feedback, feedback_type, progress):
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
        cv2.putText(frame, feedback, (35, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # Barra lateral de progreso de repetición
        bar_x = w - 40
        bar_y1 = 100
        bar_y2 = h - 60
        bar_h = bar_y2 - bar_y1

        # Fondo barra
        cv2.rectangle(frame, (bar_x, bar_y1), (bar_x + 20, bar_y2), (50, 50, 50), -1)
        # Relleno barra
        fill_h = int((progress / 100.0) * bar_h)
        cv2.rectangle(frame, (bar_x, bar_y2 - fill_h), (bar_x + 20, bar_y2), (0, 255, 200), -1)
        cv2.rectangle(frame, (bar_x, bar_y1), (bar_x + 20, bar_y2), (255, 255, 255), 1)

        # Marcador de repeticiones en esquina inferior izquierda
        cv2.rectangle(frame, (20, h - 90), (160, h - 20), (20, 20, 20), -1)
        cv2.rectangle(frame, (20, h - 90), (160, h - 20), (0, 255, 200), 2)
        cv2.putText(frame, "REPS", (35, h - 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, str(reps), (35, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)
