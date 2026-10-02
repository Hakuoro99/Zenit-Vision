import time
import numpy as np

class ExerciseCounter:
    """
    Evaluador y contador de repeticiones multi-ángulo (de frente, de lado y en diagonal).
    """
    def __init__(self, exercise_type="squat", target_reps=0):
        self.exercise_type = exercise_type
        self.counter = 0
        self.target_reps = target_reps
        self.stage = None  # "up", "down"
        self.feedback = "Ponte en posicion frente a la camara"
        self.feedback_type = "info"  # "good", "warning", "info"
        self.progress = 0  # 0 a 100%
        self.start_time = time.time()
        self.last_rep_time = time.time()
        self.session_accumulated_calories = 0.0
        self.session_accumulated_reps = 0
        self.calories_per_rep = {
            "squat": 0.32,
            "pushup": 0.45,
            "jumping_jacks": 0.20
        }

    def set_exercise(self, exercise_type, target_reps=0, preserve_session_totals=False):
        """Cambia el tipo de ejercicio a evaluar."""
        if preserve_session_totals:
            self.session_accumulated_calories += self.get_current_exercise_calories()
            self.session_accumulated_reps += self.counter

        self.exercise_type = exercise_type
        self.target_reps = target_reps
        self.counter = 0
        self.stage = None
        self.feedback = f"Iniciando {exercise_type}"
        self.feedback_type = "info"
        self.progress = 0

    def get_elapsed_time(self):
        """Retorna el tiempo transcurrido en segundos."""
        return int(time.time() - self.start_time)

    def get_current_exercise_calories(self):
        """Calcula calorías quemadas estimadas del ejercicio actual."""
        rate = self.calories_per_rep.get(self.exercise_type, 0.3)
        return round(self.counter * rate, 1)

    def get_calories(self):
        """Calcula calorías quemadas estimadas totales de la sesión."""
        return round(self.session_accumulated_calories + self.get_current_exercise_calories(), 1)

    def get_total_reps(self):
        """Calcula las repeticiones totales acumuladas de la sesión."""
        return self.session_accumulated_reps + self.counter

    def process(self, detector, img):
        """
        Procesa la pose actual según el tipo de ejercicio seleccionado.
        Funciona tanto de frente como de lado usando ángulos 2D visuales y medidor de flexión.
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
        Sentadillas: Evaluación precisa por ángulo articulado de rodillas (2D).
        Dibuja el medidor de grados en tiempo real e impide falsos conteos al acercarse a la cámara.
        """
        lm = detector.lm_list

        # 1. Protección de proximidad excesiva (si cadera o rodillas están cortadas cerca del borde inferior)
        hip_y = (lm[23][5] + lm[24][5]) / 2.0
        knee_y = (lm[25][5] + lm[26][5]) / 2.0

        if hip_y > 0.82 or knee_y > 0.92:
            self.feedback = "Alejate a 1.5m - 2.5m para encuadrar las piernas"
            self.feedback_type = "warning"
            return

        # 2. Determinar lado con mayor visibilidad de articulaciones (izquierdo o derecho)
        vis_left = (lm[23][3] + lm[25][3] + lm[27][3]) / 3.0
        vis_right = (lm[24][3] + lm[26][3] + lm[28][3]) / 3.0

        use_left = vis_left >= vis_right

        if use_left:
            knee_angle = detector.find_angle(img, 23, 25, 27, draw=True)
            _ = detector.find_angle(img, 24, 26, 28, draw=False)
        else:
            knee_angle = detector.find_angle(img, 24, 26, 28, draw=True)
            _ = detector.find_angle(img, 23, 25, 27, draw=False)

        if knee_angle <= 0:
            self.feedback = "Buscando articulaciones de rodillas..."
            self.feedback_type = "info"
            return

        # 3. Mapeo de porcentaje de progreso (165° -> 0%, 95° -> 100%)
        self.progress = int(np.interp(knee_angle, [95, 165], [100, 0]))

        # 4. Evaluación de posturas basada en ángulos biomecánicos
        is_squatting_down = (knee_angle < 105)
        is_standing_up = (knee_angle > 150)

        # Inicializar estado al detectar postura erguida
        if self.stage is None:
            if is_standing_up:
                self.stage = "up"
                self.feedback = "Baja flexionando las rodillas"
                self.feedback_type = "info"
            elif is_squatting_down:
                self.stage = "down"

        if is_standing_up:
            if self.stage == "down":
                self.counter += 1
                self.last_rep_time = time.time()
                self.feedback = f"¡Excelente sentadilla #{self.counter}!"
                self.feedback_type = "good"
                self.stage = "up"
            else:
                self.feedback = "Baja flexionando las rodillas"
                self.feedback_type = "info"
                self.stage = "up"

        elif is_squatting_down:
            if self.stage == "up":
                self.stage = "down"
                self.feedback = "¡Bien! Ahora sube lentamente"
                self.feedback_type = "good"

        elif 105 <= knee_angle <= 135 and self.stage == "up":
            self.feedback = "Baja un poco mas la cadera"
            self.feedback_type = "warning"

    def _evaluate_pushup(self, detector, img):
        """
        Lagartijas: Evalúa flexión y extensión de codos en 2D con medidor gráfico.
        """
        lm = detector.lm_list
        shoulder_y = (lm[11][5] + lm[12][5]) / 2.0

        if shoulder_y > 0.80:
            self.feedback = "Alejate un poco para encuadrar los brazos"
            self.feedback_type = "warning"
            return

        vis_left = (lm[11][3] + lm[13][3] + lm[15][3]) / 3.0
        vis_right = (lm[12][3] + lm[14][3] + lm[16][3]) / 3.0

        use_left = vis_left >= vis_right

        if use_left:
            elbow_angle = detector.find_angle(img, 11, 13, 15, draw=True)
            _ = detector.find_angle(img, 12, 14, 16, draw=False)
        else:
            elbow_angle = detector.find_angle(img, 12, 14, 16, draw=True)
            _ = detector.find_angle(img, 11, 13, 15, draw=False)

        if elbow_angle <= 0:
            self.feedback = "Buscando codos..."
            self.feedback_type = "info"
            return

        self.progress = int(np.interp(elbow_angle, [95, 160], [100, 0]))

        is_extended = (elbow_angle > 150)
        is_flexed = (elbow_angle < 100)

        if self.stage is None:
            self.stage = "up" if is_extended else "down"

        if is_extended:
            if self.stage == "down":
                self.counter += 1
                self.last_rep_time = time.time()
                self.feedback = f"¡Excelente flexión #{self.counter}!"
                self.feedback_type = "good"
                self.stage = "up"
            else:
                self.feedback = "Flexiona los codos bajando el pecho"
                self.feedback_type = "info"
                self.stage = "up"

        elif is_flexed:
            if self.stage == "up":
                self.stage = "down"
                self.feedback = "¡Bien! Empuja hacia arriba"
                self.feedback_type = "good"

        elif 100 <= elbow_angle <= 135 and self.stage == "up":
            self.feedback = "Baja el pecho mas cerca del suelo"
            self.feedback_type = "warning"

    def _evaluate_jumping_jacks(self, detector, img):
        """
        Jumping Jacks: Evalúa apertura de brazos y piernas en 2D con medidores gráficos.
        """
        lm = detector.lm_list

        vis_left = (lm[23][3] + lm[11][3] + lm[15][3]) / 3.0
        vis_right = (lm[24][3] + lm[12][3] + lm[16][3]) / 3.0

        if vis_left >= vis_right:
            arm_angle = detector.find_angle(img, 23, 11, 15, draw=True)
            _ = detector.find_angle(img, 24, 12, 16, draw=False)
        else:
            arm_angle = detector.find_angle(img, 24, 12, 16, draw=True)
            _ = detector.find_angle(img, 23, 11, 15, draw=False)

        wrist_l_y = lm[15][5]
        wrist_r_y = lm[16][5]
        shoulder_l_y = lm[11][5]
        shoulder_r_y = lm[12][5]

        arms_raised = (wrist_l_y < shoulder_l_y) or (wrist_r_y < shoulder_r_y) or (arm_angle > 110)
        arms_lowered = (wrist_l_y > (shoulder_l_y + 0.05)) and (wrist_r_y > (shoulder_r_y + 0.05)) or (arm_angle < 50)

        ankle_l_x = lm[27][4]
        ankle_r_x = lm[28][4]
        shoulder_l_x = lm[11][4]
        shoulder_r_x = lm[12][4]

        ankle_dist = abs(ankle_l_x - ankle_r_x)
        shoulder_dist = max(abs(shoulder_l_x - shoulder_r_x), 0.05)
        leg_ratio = ankle_dist / shoulder_dist

        self.progress = int(np.interp(arm_angle, [30, 140], [0, 100]))

        is_jack_open = arms_raised or (arm_angle > 115 and leg_ratio > 1.25)
        is_jack_closed = arms_lowered and (leg_ratio < 1.25)

        if self.stage is None:
            self.stage = "down" if is_jack_closed else "up"

        if is_jack_closed:
            if self.stage == "up":
                self.counter += 1
                self.last_rep_time = time.time()
                self.feedback = f"¡Excelente Jack #{self.counter}!"
                self.feedback_type = "good"
                self.stage = "down"
            else:
                self.feedback = "Salta y abre brazos y piernas"
                self.feedback_type = "info"
                self.stage = "down"

        elif is_jack_open:
            if self.stage == "down":
                self.stage = "up"
                self.feedback = "¡Bien! Vuelve a la posición inicial"
                self.feedback_type = "good"
