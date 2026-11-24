import time
import numpy as np

class ExerciseCounter:
    """
    Evaluador y contador de repeticiones multi-ángulo (de frente, de lado y en diagonal).
    """
    def __init__(self, exercise_type="knee_raise", target_reps=0):
        self.exercise_type = exercise_type
        self.counter = 0
        self.target_reps = target_reps
        self.stage = None  # "up", "down"
        self.feedback = "¡Ponte en posición!"
        self.feedback_type = "info"  # "good", "warning", "info"
        self.progress = 0  # 0 a 100%
        self.start_time = time.time()
        self.last_rep_time = 0.0
        self.session_accumulated_calories = 0.0
        self.session_accumulated_reps = 0
        self.reps_by_exercise = {}
        self.active_side = None
        self.last_counted_leg = None
        self.calories_per_rep = {
            "squat": 0.32,
            "pushup": 0.45,
            "knee_raise": 0.22,
            "rodillas": 0.22,
            "jumping_jacks": 0.22
        }

    def set_exercise(self, exercise_type, target_reps=0, preserve_session_totals=False):
        """Cambia el tipo de ejercicio a evaluar."""
        if preserve_session_totals:
            self.session_accumulated_calories += self.get_current_exercise_calories()
            self.session_accumulated_reps += self.counter
            if self.exercise_type and self.counter > 0:
                self.reps_by_exercise[self.exercise_type] = self.reps_by_exercise.get(self.exercise_type, 0) + self.counter

        self.exercise_type = exercise_type
        self.target_reps = target_reps
        self.counter = 0
        self.stage = None
        self.active_side = None
        self.last_counted_leg = None
        self.last_rep_time = 0.0
        self.feedback = "¡Ponte en posición!"
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

    def get_reps_by_exercise(self):
        """Calcula el desglose de repeticiones acumuladas por ejercicio en la sesión."""
        breakdown = dict(self.reps_by_exercise)
        if self.exercise_type and self.counter > 0:
            breakdown[self.exercise_type] = breakdown.get(self.exercise_type, 0) + self.counter
        return breakdown

    def process(self, detector, img):
        """
        Procesa la pose actual según el tipo de ejercicio seleccionado.
        Funciona tanto de frente como de lado usando ángulos 2D visuales y medidor de flexión.
        """
        lm_list = detector.lm_list
        if not lm_list or len(lm_list) < 33:
            self.feedback = "Buscando cuerpo..."
            self.feedback_type = "warning"
            self.progress = 0
            return self.counter, self.feedback, self.progress

        if self.exercise_type == "squat":
            self._evaluate_squat(detector, img)
        elif self.exercise_type == "pushup":
            self._evaluate_pushup(detector, img)
        elif self.exercise_type in ["knee_raise", "rodillas", "jumping_jacks"]:
            self._evaluate_knee_raise(detector, img)
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
            self.feedback = "Aléjate un poco"
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
            self.feedback = "Buscando piernas..."
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
                self.feedback = "Haz la sentadilla"
                self.feedback_type = "info"
            elif is_squatting_down:
                self.stage = "down"

        if is_standing_up:
            if self.stage == "down":
                self.counter += 1
                self.last_rep_time = time.time()
                self.feedback = f"¡Excelente #{self.counter}!"
                self.feedback_type = "good"
                self.stage = "up"
            else:
                self.feedback = "Haz la sentadilla"
                self.feedback_type = "info"
                self.stage = "up"

        elif is_squatting_down:
            if self.stage == "up":
                self.stage = "down"
                self.feedback = "¡Sube!"
                self.feedback_type = "good"

        elif 105 <= knee_angle <= 135 and self.stage == "up":
            self.feedback = "¡Baja más!"
            self.feedback_type = "warning"

    def _evaluate_pushup(self, detector, img):
        """
        Lagartijas: Evalúa flexión y extensión de codos en 2D con medidor gráfico.
        """
        lm = detector.lm_list
        shoulder_y = (lm[11][5] + lm[12][5]) / 2.0

        if shoulder_y > 0.80:
            self.feedback = "Aléjate un poco"
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
            self.feedback = "Buscando brazos..."
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
                self.feedback = f"¡Excelente #{self.counter}!"
                self.feedback_type = "good"
                self.stage = "up"
            else:
                self.feedback = "Baja el pecho"
                self.feedback_type = "info"
                self.stage = "up"

        elif is_flexed:
            if self.stage == "up":
                self.stage = "down"
                self.feedback = "¡Empuja!"
                self.feedback_type = "good"

        elif 100 <= elbow_angle <= 135 and self.stage == "up":
            self.feedback = "¡Baja más el pecho!"
            self.feedback_type = "warning"

    def _evaluate_knee_raise(self, detector, img):
        """
        Levantamiento de rodillas (High Knees / Marcha de rodillas altas):
        Evalúa la flexión de cadera y elevación de cada rodilla hacia el pecho.
        - Corregido para vista espejo: derecha en pantalla = derecha del usuario.
        - Exige alternancia estricta de piernas (no permite repetir la misma pierna consecutivamente).
        - Mensajes concisos, rápidos y de alta legibilidad a distancia.
        """
        lm = detector.lm_list

        # 1. Protección de proximidad
        hip_y = (lm[23][5] + lm[24][5]) / 2.0
        knee_y = (lm[25][5] + lm[26][5]) / 2.0
        if hip_y > 0.82 or knee_y > 0.94:
            self.feedback = "Aléjate un poco"
            self.feedback_type = "warning"
            return

        # 2. Altura de referencia del torso
        shoulder_y = (lm[11][5] + lm[12][5]) / 2.0
        torso_h = max(abs(hip_y - shoulder_y), 0.15)

        # En cámara volteada horizontalmente (efecto espejo):
        # Lado derecho de la pantalla (MediaPipe Left: 11, 23, 25) = pierna DERECHA real del usuario.
        # Lado izquierdo de la pantalla (MediaPipe Right: 12, 24, 26) = pierna IZQUIERDA real del usuario.
        rel_knee_derecha = (lm[25][5] - lm[23][5]) / torso_h
        rel_knee_izquierda = (lm[26][5] - lm[24][5]) / torso_h

        angle_derecha_3d = detector.find_angle_3d(img, 11, 23, 25, draw=False)
        angle_izquierda_3d = detector.find_angle_3d(img, 12, 24, 26, draw=False)

        # 3. Determinar cuál pierna del usuario está más elevada
        if rel_knee_derecha < rel_knee_izquierda:
            active_leg = "derecha"
            active_rel = rel_knee_derecha
            active_angle = angle_derecha_3d
            _ = detector.find_angle_3d(img, 11, 23, 25, draw=True)
        else:
            active_leg = "izquierda"
            active_rel = rel_knee_izquierda
            active_angle = angle_izquierda_3d
            _ = detector.find_angle_3d(img, 12, 24, 26, draw=True)

        if active_angle <= 0:
            self.feedback = "Buscando cuerpo..."
            self.feedback_type = "info"
            return

        # 4. Progreso continuo visual (0% a 100%)
        prog_angle = np.interp(active_angle, [95, 160], [100, 0])
        prog_rel = np.interp(active_rel, [0.20, 0.70], [100, 0])
        self.progress = int(max(0, min(100, max(prog_angle, prog_rel))))

        # 5. Criterios biomecánicos de activación y retorno:
        is_derecha_high = (rel_knee_derecha < 0.38) or (angle_derecha_3d < 118 and rel_knee_derecha < 0.50)
        is_izquierda_high = (rel_knee_izquierda < 0.38) or (angle_izquierda_3d < 118 and rel_knee_izquierda < 0.50)

        is_derecha_down = (rel_knee_derecha > 0.52) or (angle_derecha_3d > 135)
        is_izquierda_down = (rel_knee_izquierda > 0.52) or (angle_izquierda_3d > 135)

        # Inicialización de estado
        if self.stage is None:
            self.stage = "down"
            self.active_side = None

        # 6. Máquina de estados FSM con alternancia estricta y respuestas rápidas:
        if self.stage == "down":
            if is_derecha_high and not is_izquierda_high:
                if self.last_counted_leg == "derecha":
                    self.feedback = "¡Toca IZQUIERDA!"
                    self.feedback_type = "warning"
                else:
                    self.stage = "up"
                    self.active_side = "derecha"
                    self.feedback = "¡Baja el pie!"
                    self.feedback_type = "good"

            elif is_izquierda_high and not is_derecha_high:
                if self.last_counted_leg == "izquierda":
                    self.feedback = "¡Toca DERECHA!"
                    self.feedback_type = "warning"
                else:
                    self.stage = "up"
                    self.active_side = "izquierda"
                    self.feedback = "¡Baja el pie!"
                    self.feedback_type = "good"

            elif 0.38 <= active_rel <= 0.60:
                self.feedback = "¡Sube más la rodilla!"
                self.feedback_type = "warning"
            else:
                if self.last_counted_leg == "derecha":
                    self.feedback = "Sube rodilla IZQUIERDA"
                elif self.last_counted_leg == "izquierda":
                    self.feedback = "Sube rodilla DERECHA"
                else:
                    self.feedback = "Sube una rodilla"
                self.feedback_type = "info"

        elif self.stage == "up":
            # PROTECCIÓN: Si la rodilla se mantiene arriba, no suma repeticiones hasta descender
            if self.active_side == "derecha":
                if is_derecha_down:
                    self.counter += 1
                    self.last_counted_leg = "derecha"
                    self.last_rep_time = time.time()
                    self.stage = "down"
                    self.active_side = None

                    # Enlace continuo veloz: si la otra pierna ya viene subiendo
                    if is_izquierda_high and not is_derecha_high:
                        self.stage = "up"
                        self.active_side = "izquierda"
                        self.feedback = "¡Excelente! ¡Sigue!"
                    else:
                        self.feedback = "¡Bien! Toca IZQUIERDA"
                    self.feedback_type = "good"
                else:
                    self.feedback = "Baja el pie"
                    self.feedback_type = "good"

            elif self.active_side == "izquierda":
                if is_izquierda_down:
                    self.counter += 1
                    self.last_counted_leg = "izquierda"
                    self.last_rep_time = time.time()
                    self.stage = "down"
                    self.active_side = None

                    # Enlace continuo veloz: si la otra pierna ya viene subiendo
                    if is_derecha_high and not is_izquierda_high:
                        self.stage = "up"
                        self.active_side = "derecha"
                        self.feedback = "¡Excelente! ¡Sigue!"
                    else:
                        self.feedback = "¡Bien! Toca DERECHA"
                    self.feedback_type = "good"
                else:
                    self.feedback = "Baja el pie"
                    self.feedback_type = "good"

            else:
                if is_derecha_down and is_izquierda_down:
                    self.stage = "down"
