from datetime import datetime, date

class GamificationEngine:
    """
    Motor central de Gamificación para Zenit-Visión.
    Maneja 50 niveles, 5 rangos de jerarquía, cálculo de puntos por ejercicio,
    bonos fijos de racha diaria y misiones diarias.
    """

    # Definición de Rangos (Cada 10 niveles)
    RANKS = [
        (1, 10, "Novato Explorador", "#10B981", "bronze"),
        (11, 20, "Atleta Promesa", "#3B82F6", "silver"),
        (21, 30, "Guerrero de Elite", "#8B5CF6", "purple"),
        (31, 40, "Maestro de la Postura", "#F59E0B", "gold"),
        (41, 50, "Titán Legendario", "#EF4444", "crimson"),
    ]

    # Recompensas fijas por racha diaria (Día 1 a Día 7+)
    STREAK_BONUSES = {
        1: 20,
        2: 30,
        3: 50,
        4: 70,
        5: 90,
        6: 120,
        7: 150  # 150 pts a partir del día 7
    }

    @staticmethod
    def points_needed_for_level(level: int) -> int:
        """Puntos requeridos para avanzar del nivel N al nivel N+1 (100 * N)."""
        return 100 * level

    @classmethod
    def get_level_data(cls, total_points: int) -> dict:
        """
        Calcula el nivel actual (1 a 50), título de rango, avance dentro del nivel
        y puntos necesarios para el siguiente nivel.
        """
        pts = max(0, total_points)
        level = 1
        
        while level < 50:
            req = cls.points_needed_for_level(level)
            if pts >= req:
                pts -= req
                level += 1
            else:
                break

        pts_in_current_level = pts
        pts_for_next = cls.points_needed_for_level(level) if level < 50 else cls.points_needed_for_level(49)
        progress_pct = min(100.0, (pts_in_current_level / max(1, pts_for_next)) * 100.0)

        # Buscar Título y Color según el nivel actual
        title = "Novato Explorador"
        color = "#10B981"
        badge_style = "bronze"

        for min_lvl, max_lvl, rank_title, rank_color, style in cls.RANKS:
            if min_lvl <= level <= max_lvl:
                title = rank_title
                color = rank_color
                badge_style = style
                break

        return {
            "level": level,
            "title": title,
            "color": color,
            "badge_style": badge_style,
            "current_level_pts": pts_in_current_level,
            "next_level_req": pts_for_next,
            "progress_pct": round(progress_pct, 1),
            "total_points": total_points
        }

    @classmethod
    def calculate_session_points(cls, difficulty: str, reps: int, precision_score: int) -> dict:
        """
        Calcula los puntos ganados en una sesión según la dificultad y la precisión postural.
        - Fácil/Libre: 10 pts/rep
        - Estándar: 15 pts/rep
        - Avanzado: 20 pts/rep
        - Bono Precisión: +50 pts (>=90%), +25 pts (75-89%)
        """
        diff_str = str(difficulty).upper()
        if "AVANZAD" in diff_str or "HARD" in diff_str or "DIFICIL" in diff_str:
            pts_per_rep = 20
        elif "ESTANDAR" in diff_str or "NORM" in diff_str or "INTERMEDIO" in diff_str:
            pts_per_rep = 15
        else:
            pts_per_rep = 10

        rep_points = reps * pts_per_rep

        precision_bonus = 0
        if precision_score >= 90:
            precision_bonus = 50
        elif precision_score >= 75:
            precision_bonus = 25

        total_pts = rep_points + precision_bonus

        return {
            "total_points": total_pts,
            "rep_points": rep_points,
            "precision_bonus": precision_bonus,
            "pts_per_rep": pts_per_rep
        }

    @classmethod
    def check_daily_streak_bonus(cls, last_workout_date_str: str, current_streak: int) -> dict:
        """
        Verifica si el usuario ingresa en un nuevo día consecutivo.
        Retorna la nueva racha y los puntos otorgados por bono diario.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        if not last_workout_date_str:
            # Primer día de uso
            streak = 1
            bonus = cls.STREAK_BONUSES[1]
            return {"streak": streak, "bonus_pts": bonus, "updated": True, "date": today_str}

        if last_workout_date_str == today_str:
            # Mismo día, no vuelve a otorgar bono diario
            return {"streak": max(1, current_streak), "bonus_pts": 0, "updated": False, "date": today_str}

        try:
            last_date = datetime.strptime(last_workout_date_str, "%Y-%m-%d").date()
            today_date = date.today()
            diff_days = (today_date - last_date).days

            if diff_days == 1:
                # Día consecutivo
                new_streak = current_streak + 1
            else:
                # Se rompió la racha (pasó más de 1 día)
                new_streak = 1

            streak_key = min(new_streak, 7)
            bonus = cls.STREAK_BONUSES.get(streak_key, 150)
            return {"streak": new_streak, "bonus_pts": bonus, "updated": True, "date": today_str}

        except Exception as e:
            print(f"[GamificationEngine] Error analizando fecha de racha: {e}")
            return {"streak": 1, "bonus_pts": cls.STREAK_BONUSES[1], "updated": True, "date": today_str}

    @classmethod
    def check_and_reset_daily_quests(cls, user_data: dict, fb_db=None, user_id=None, controller=None) -> dict:
        """
        Verifica si ha pasado un nuevo día (24 horas / cambio de fecha) y reinicia las misiones diarias si es necesario.
        """
        if user_data is None:
            return {}

        today_str = datetime.now().strftime("%Y-%m-%d")
        last_quest_date = user_data.get("last_quest_date", "")

        if not last_quest_date or last_quest_date != today_str:
            user_data["today_reps"] = 0
            user_data["today_sessions"] = 0
            user_data["best_precision_today"] = 0
            user_data["last_quest_date"] = today_str

            if user_id == "invitado" or (controller and hasattr(controller, 'guest_data')):
                if controller and hasattr(controller, 'guest_data') and isinstance(controller.guest_data, dict):
                    controller.guest_data["today_reps"] = 0
                    controller.guest_data["today_sessions"] = 0
                    controller.guest_data["best_precision_today"] = 0
                    controller.guest_data["last_quest_date"] = today_str
            elif fb_db and user_id and user_id != "invitado":
                try:
                    user_node = f"users/{user_id}"
                    fb_db.update_record("", {
                        f"{user_node}/today_reps": 0,
                        f"{user_node}/today_sessions": 0,
                        f"{user_node}/best_precision_today": 0,
                        f"{user_node}/last_quest_date": today_str
                    })
                    print(f"[GamificationEngine] Misiones diarias reiniciadas para {user_id} el {today_str}")
                except Exception as e:
                    print(f"[GamificationEngine] Error reiniciando misiones en Firebase: {e}")

        return user_data

    @classmethod
    def get_daily_quests(cls, user_data: dict, fb_db=None, user_id=None, controller=None) -> list:
        """
        Retorna las 3 misiones diarias con su estado de avance, garantizando el reinicio de 24 horas.
        """
        if user_data is not None:
            cls.check_and_reset_daily_quests(user_data, fb_db=fb_db, user_id=user_id, controller=controller)
        else:
            user_data = {}

        today_reps = user_data.get("today_reps", 0)
        today_sessions = user_data.get("today_sessions", 0)
        best_precision = user_data.get("best_precision_today", 0)

        quests = [
            {
                "id": "q_reps",
                "title": "Atleta Constante",
                "desc": "Completa 30 repeticiones hoy",
                "current": min(30, today_reps),
                "target": 30,
                "reward_pts": 50,
                "completed": today_reps >= 30
            },
            {
                "id": "q_precision",
                "title": "Técnica Fina",
                "desc": "Alcanza 80%+ de precisión postural",
                "current": min(80, best_precision),
                "target": 80,
                "reward_pts": 40,
                "completed": best_precision >= 80
            },
            {
                "id": "q_session",
                "title": "Rutina Activa",
                "desc": "Completa al menos 1 rutina de ejercicio",
                "current": min(1, today_sessions),
                "target": 1,
                "reward_pts": 30,
                "completed": today_sessions >= 1
            }
        ]
        return quests
