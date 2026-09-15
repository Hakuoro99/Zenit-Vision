import time
import numpy as np

class ExerciseCounter:
    """
    Evaluador y contador de repeticiones multi-ángulo (de frente, de lado y en diagonal).
    """
    def __init__(self, exercise_type="squat"):
        self.exercise_type = exercise_type
        self.counter = 0
        self.stage = None  # "up", "down"
        self.feedback = "Pónte en posición frente a la cámara"
        self.feedback_type = "info"  # "good", "warning", "info"
        self.progress = 0  # 0 a 100%
        self.start_time = time.time()
        self.last_rep_time = time.time()
        self.calories_per_rep = {
            "squat": 0.32,
            "pushup": 0.45,
            "jumping_jacks": 0.20
        }

    def set_exercise(self, exercise_type):
        """Cambia el tipo de ejercicio a evaluar."""
        self.exercise_type = exercise_type
        self.counter = 0
        self.stage = None
        self.feedback = f"Iniciando {exercise_type}"
        self.progress = 0
        self.start_time = time.time()

    def get_elapsed_time(self):
        """Retorna el tiempo transcurrido en segundos."""
        return int(time.time() - self.start_time)

    def get_calories(self):
        """Calcula calorías quemadas estimadas."""
        rate = self.calories_per_rep.get(self.exercise_type, 0.3)
        return round(self.counter * rate, 1)

    def process(self, detector, img):
        """
        Procesa la pose actual según el tipo de ejercicio seleccionado.
        Funciona tanto de frente como de lado usando ángulos 3D y desplazamientos coordinados.
        """
        lm_list = detector.lm_list
        if not lm_list or len(lm_list) < 33:
            self.feedback = "Buscando cuerpo entero..."
            self.feedback_type = "warning"
            self.progress = 0
            return self.counter, self.feedback, self.progress

        if self.exercise_type == "squat":
            self._evaluate_squat(detector, img)
        elif self.exercise_type == "pushup":
            self._evaluate_pushup(detector, img)
        elif self.exercise_type == "jumping_jacks":
            self._evaluate_jumping_jacks(detector, img)
        else:
            self._evaluate_squat(detector, img)

        return self.counter, self.feedback, self.progress

    def _evaluate_squat(self, detector, img):
        """
        Sentadillas: Funciona perfectamente de FRENTE, DE LADO y DIAGONAL.
        Combina el ángulo 3D de rodilla con el descenso relativo de la cadera.
        """
        # Calcular ángulos 3D para ambos lados
        angle_l_3d = detector.find_angle_3d(img, 23, 25, 27, draw=False)
        angle_r_3d = detector.find_angle_3d(img, 24, 26, 28, draw=False)
        
        # Calcular ángulos 2D para renderizado visual
        angle_l_2d = detector.find_angle(img, 23, 25, 27, draw=True)
        angle_r_2d = detector.find_angle(img, 24, 26, 28, draw=True)

        # Usar el ángulo más pronunciado (mínimo) entre ambos lados
        angles_valid = [a for a in [angle_l_3d, angle_r_3d, angle_l_2d, angle_r_2d] if a > 0]
        if not angles_valid:
            return

        knee_angle = min(angles_valid)

        # Altura vertical normalizada (Y de cadera vs Y de rodilla)
        lm = detector.lm_list
        hip_y = (lm[23][5] + lm[24][5]) / 2.0
        knee_y = (lm[25][5] + lm[26][5]) / 2.0
        ankle_y = (lm[27][5] + lm[28][5]) / 2.0

        thigh_height = knee_y - hip_y
        shin_height = max(ankle_y - knee_y, 0.05)
        height_ratio = thigh_height / shin_height

        # Mapeo de porcentaje de progreso (160° -> 0%, 95° -> 100%)
        self.progress = int(np.interp(knee_angle, [95, 160], [100, 0]))

        # Detección de estados (Frecuente de frente y de lado)
        is_squatting_down = (knee_angle < 105) or (height_ratio < 0.5)
        is_standing_up = (knee_angle > 155) and (height_ratio > 0.75)

        if is_standing_up:
            if self.stage == "down":
                self.feedback = "¡Buena repetición!"
                self.feedback_type = "good"
            else:
                self.feedback = "Baja flexionando las rodillas"
                self.feedback_type = "info"
            self.stage = "up"

        if is_squatting_down and self.stage == "up":
            self.stage = "down"
            self.counter += 1
            self.last_rep_time = time.time()
            self.feedback = f"¡Excelente sentadilla #{self.counter}!"
            self.feedback_type = "good"
        elif (105 <= knee_angle <= 135) and self.stage == "up":
            self.feedback = "¡Baja un poco más!"
            self.feedback_type = "warning"

    def _evaluate_pushup(self, detector, img):
        """
        Lagartijas: Evalúa codos tanto de FRENTE como de LADO.
        """
        angle_l_3d = detector.find_angle_3d(img, 11, 13, 15, draw=False)
        angle_r_3d = detector.find_angle_3d(img, 12, 14, 16, draw=False)
        
        angle_l_2d = detector.find_angle(img, 11, 13, 15, draw=True)
        angle_r_2d = detector.find_angle(img, 12, 14, 16, draw=True)

        angles_valid = [a for a in [angle_l_3d, angle_r_3d, angle_l_2d, angle_r_2d] if a > 0]
        if not angles_valid:
            return

        elbow_angle = min(angles_valid)

        # Mapeo de progreso
        self.progress = int(np.interp(elbow_angle, [95, 160], [100, 0]))

        is_extended = (elbow_angle > 150)
        is_flexed = (elbow_angle < 100)

        if is_extended:
            self.stage = "up"
            self.feedback = "Flexiona los codos hacia abajo"
            self.feedback_type = "info"

        if is_flexed and self.stage == "up":
            self.stage = "down"
            self.counter += 1
            self.last_rep_time = time.time()
            self.feedback = f"¡Buena flexión #{self.counter}!"
            self.feedback_type = "good"
        elif (100 <= elbow_angle <= 135) and self.stage == "up":
            self.feedback = "¡Baja el pecho más cerca del suelo!"
            self.feedback_type = "warning"

    def _evaluate_jumping_jacks(self, detector, img):
        """
        Jumping Jacks: Optimizado para orientación frontal de cámara.
        Combina elevación de brazos (Muñecas por encima de hombros/cabeza) y apertura de piernas.
        """
        lm = detector.lm_list

        # Ángulo de brazos 3D
        arm_l_3d = detector.find_angle_3d(img, 23, 11, 15, draw=False)
        arm_r_3d = detector.find_angle_3d(img, 24, 12, 16, draw=False)

        arm_l_2d = detector.find_angle(img, 23, 11, 15, draw=True)
        arm_r_2d = detector.find_angle(img, 24, 12, 16, draw=True)

        avg_arm_angle = (max(arm_l_3d, arm_l_2d) + max(arm_r_3d, arm_r_2d)) / 2.0

        # Verificación directa de elevación de muñecas en Y (menor Y = más alto en imagen)
        wrist_l_y = lm[15][5]
        wrist_r_y = lm[16][5]
        shoulder_l_y = lm[11][5]
        shoulder_r_y = lm[12][5]
        hip_l_y = lm[23][5]
        hip_r_y = lm[24][5]

        arms_raised = (wrist_l_y < shoulder_l_y) or (wrist_r_y < shoulder_r_y) or (avg_arm_angle > 110)
        arms_lowered = (wrist_l_y > (shoulder_l_y + 0.1)) and (wrist_r_y > (shoulder_r_y + 0.1)) or (avg_arm_angle < 50)

        # Distancia entre tobillos vs distancia entre hombros (apertura de piernas)
        ankle_l_x = lm[27][4]
        ankle_r_x = lm[28][4]
        shoulder_l_x = lm[11][4]
        shoulder_r_x = lm[12][4]

        ankle_dist = abs(ankle_l_x - ankle_r_x)
        shoulder_dist = max(abs(shoulder_l_x - shoulder_r_x), 0.05)
        leg_ratio = ankle_dist / shoulder_dist

        self.progress = int(np.interp(avg_arm_angle, [30, 140], [0, 100]))

        # Criterios de apertura y cierre
        is_jack_open = arms_raised or (avg_arm_angle > 115 and leg_ratio > 1.2)
        is_jack_closed = arms_lowered and (leg_ratio < 1.3)

        if is_jack_closed:
            self.stage = "down"
            self.feedback = "¡Salta y abre brazos y piernas!"
            self.feedback_type = "info"

        if is_jack_open and self.stage == "down":
            self.stage = "up"
            self.counter += 1
            self.last_rep_time = time.time()
            self.feedback = f"¡Jumping Jack #{self.counter}!"
            self.feedback_type = "good"
