import cv2
import math
import os
import urllib.request
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Conexiones principales de articulaciones para renderizado gráfico
POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Brazos y hombros
    (11, 23), (12, 24), (23, 24),                      # Torso
    (23, 25), (25, 27), (24, 26), (26, 28)             # Piernas
]

class PoseDetector:
    """
    Clase para la detección de la postura corporal y cálculo de ángulos en 2D y 3D usando MediaPipe PoseLandmarker.
    """
    def __init__(self, model_path="assets/pose_landmarker.task", min_detection_con=0.5):
        self.model_path = model_path
        self._ensure_model_exists()
        
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_poses=1,
            min_pose_detection_confidence=min_detection_con
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)
        self.results = None
        self.lm_list = []

    def _ensure_model_exists(self):
        """Descarga el modelo de MediaPipe PoseLandmarker si no existe localmente."""
        if not os.path.exists(self.model_path):
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
            print(f"[PoseDetector] Descargando modelo MediaPipe desde {url}...")
            try:
                urllib.request.urlretrieve(url, self.model_path)
                print("[PoseDetector] Modelo descargado con éxito.")
            except Exception as e:
                print(f"[PoseDetector] Error descargando el modelo: {e}")

    def find_pose(self, img, draw=True):
        """
        Procesa una imagen BGR de OpenCV y dibuja las conexiones posturales.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.results = self.landmarker.detect(mp_image)
        
        if draw and self.results and self.results.pose_landmarks:
            h, w, _ = img.shape
            pose_lms = self.results.pose_landmarks[0]
            
            # Dibujar líneas de conexión entre articulaciones
            for p1_id, p2_id in POSE_CONNECTIONS:
                if p1_id < len(pose_lms) and p2_id < len(pose_lms):
                    lm1 = pose_lms[p1_id]
                    lm2 = pose_lms[p2_id]
                    if getattr(lm1, 'visibility', 1.0) > 0.3 and getattr(lm2, 'visibility', 1.0) > 0.3:
                        x1, y1 = int(lm1.x * w), int(lm1.y * h)
                        x2, y2 = int(lm2.x * w), int(lm2.y * h)
                        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            
            # Dibujar puntos de articulación
            for idx, lm in enumerate(pose_lms):
                if getattr(lm, 'visibility', 1.0) > 0.3:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (0, 255, 200), cv2.FILLED, cv2.LINE_AA)
                    cv2.circle(img, (cx, cy), 7, (255, 255, 255), 1, cv2.LINE_AA)

        return img

    def find_positions(self, img, draw=False):
        """
        Devuelve una lista con las coordenadas de cada landmark.
        Estructura: [[id, cx, cy, visibility, nx, ny, nz], ...]
        donde (cx, cy) son en píxeles y (nx, ny, nz) son normalizadas 3D.
        """
        self.lm_list = []
        if self.results and self.results.pose_landmarks and len(self.results.pose_landmarks) > 0:
            h, w, _ = img.shape
            for lm_id, lm in enumerate(self.results.pose_landmarks[0]):
                cx, cy = int(lm.x * w), int(lm.y * h)
                vis = getattr(lm, 'visibility', 1.0)
                self.lm_list.append([lm_id, cx, cy, vis, lm.x, lm.y, lm.z])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return self.lm_list

    def find_angle_3d(self, img, p1, p2, p3, draw=True):
        """
        Calcula el ángulo en 3D en grados formado por tres puntos (p2 es el vértice).
        Invariante a la perspectiva de la cámara (vista de frente, de lado o diagonal).
        """
        if len(self.lm_list) <= max(p1, p2, p3):
            return 0.0

        # Coordenadas normalizadas 3D
        p1_3d = np.array(self.lm_list[p1][4:7])
        p2_3d = np.array(self.lm_list[p2][4:7])
        p3_3d = np.array(self.lm_list[p3][4:7])

        v1 = p1_3d - p2_3d
        v2 = p3_3d - p2_3d

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 < 1e-6 or norm2 < 1e-6:
            return 0.0

        cosine = np.dot(v1, v2) / (norm1 * norm2)
        cosine = np.clip(cosine, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine))

        if draw and img is not None:
            x1, y1 = self.lm_list[p1][1:3]
            x2, y2 = self.lm_list[p2][1:3]
            x3, y3 = self.lm_list[p3][1:3]

            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(img, (x1, y1), 5, (0, 220, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (0, 255, 100), cv2.FILLED)
            cv2.circle(img, (x3, y3), 5, (0, 220, 255), cv2.FILLED)
            cv2.putText(img, f"{int(angle)}°", (x2 - 30, y2 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        return angle

    def find_angle(self, img, p1, p2, p3, draw=True):
        """
        Calcula el ángulo 2D tradicional en grados en el plano de la imagen.
        """
        if len(self.lm_list) <= max(p1, p2, p3):
            return 0.0

        x1, y1 = self.lm_list[p1][1:3]
        x2, y2 = self.lm_list[p2][1:3]
        x3, y3 = self.lm_list[p3][1:3]

        radians = math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
        angle = abs(radians * 180.0 / math.pi)

        if angle > 180.0:
            angle = 360.0 - angle

        if draw and img is not None:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            cv2.circle(img, (x1, y1), 5, (0, 220, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 7, (0, 255, 100), cv2.FILLED)
            cv2.circle(img, (x3, y3), 5, (0, 220, 255), cv2.FILLED)
            cv2.putText(img, f"{int(angle)}°", (x2 - 30, y2 - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        return angle

    def close(self):
        """Cierra el reconocedor de MediaPipe."""
        if hasattr(self, 'landmarker') and self.landmarker:
            self.landmarker.close()
