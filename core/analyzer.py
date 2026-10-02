from datetime import datetime
from core.gamification import GamificationEngine

class SessionAnalyzer:
    """
    Analizador de sesiones de entrenamiento para calcular métricas de rendimiento y guardado en Firebase / Sesión Local.
    Integrado con GamificationEngine (50 Niveles, 5 Rangos, Puntos por Ejercicio y Misiones Diarias).
    """
    @staticmethod
    def calculate_session_stats(exercise_data, total_reps, elapsed_seconds, total_calories):
        """
        Genera un resumen analítico de la sesión finalizada con desglose de Gamificación.
        """
        minutes = round(elapsed_seconds / 60.0, 1)
        reps_per_minute = round(total_reps / max(minutes, 0.1), 1)
        precision_score = min(100, max(60, int(70 + (total_reps * 2)))) if total_reps > 0 else 0
        
        difficulty = exercise_data.get("badge", exercise_data.get("dificultad", "LIBRE"))
        
        # Cálculo de puntos mediante el motor de gamificación
        pts_info = GamificationEngine.calculate_session_points(difficulty, total_reps, precision_score)
        puntos_ganados = pts_info["total_points"]

        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timestamp": int(datetime.now().timestamp()),
            "reto_id": exercise_data.get("id", "libre"),
            "reto_nombre": exercise_data.get("nombre", "Entrenamiento Libre"),
            "dificultad": difficulty,
            "repeticiones_totales": total_reps,
            "duracion_segundos": elapsed_seconds,
            "duracion_minutos": minutes,
            "calorias_estimadas": round(total_calories, 1),
            "puntos": puntos_ganados,
            "rep_points": pts_info["rep_points"],
            "precision_bonus": pts_info["precision_bonus"],
            "ritmo_reps_min": reps_per_minute,
            "precision_postural": precision_score
        }

    @staticmethod
    def save_session_to_firebase(fb_db, user_id, session_summary, controller=None):
        """
        Persiste los resultados de la sesión en Firebase o en el almacenamiento temporal de invitado.
        Actualiza el Nivel (1-50), Rango y Misiones Diarias.
        """
        if not user_id or user_id == "invitado":
            print("[SessionAnalyzer] Guardando en sesión temporal de Invitado...")
            if controller:
                if not hasattr(controller, 'guest_data') or not isinstance(controller.guest_data, dict):
                    controller.guest_data = {}
                
                gd = controller.guest_data
                puntos_prev = gd.get("puntos", 0)
                nuevos_puntos = puntos_prev + session_summary.get("puntos", 0)
                
                lvl_info = GamificationEngine.get_level_data(nuevos_puntos)
                
                gd["puntos"] = nuevos_puntos
                gd["nivel"] = lvl_info["level"]
                gd["rango_titulo"] = lvl_info["title"]
                gd["rango_color"] = lvl_info["color"]
                gd["racha"] = gd.get("racha", 1)
                gd["total_reps"] = gd.get("total_reps", 0) + session_summary.get("repeticiones_totales", 0)
                gd["total_calorias"] = round(gd.get("total_calorias", 0.0) + session_summary.get("calorias_estimadas", 0.0), 1)
                gd["total_minutos"] = round(gd.get("total_minutos", 0.0) + session_summary.get("duracion_minutos", 0.0), 1)
                gd["total_sesiones"] = gd.get("total_sesiones", 0) + 1
                
                # Misiones diarias en modo invitado
                gd["today_reps"] = gd.get("today_reps", 0) + session_summary.get("repeticiones_totales", 0)
                gd["today_sessions"] = gd.get("today_sessions", 0) + 1
                gd["best_precision_today"] = max(gd.get("best_precision_today", 0), session_summary.get("precision_postural", 0))

                if "historial" not in gd:
                    gd["historial"] = []
                gd["historial"].insert(0, session_summary)
            return True

        if not fb_db:
            print("[SessionAnalyzer] Error: FirebaseDB no disponible.")
            return False

        try:
            timestamp_key = str(session_summary.get("timestamp", int(datetime.now().timestamp())))
            endpoint = f"users/{user_id}/historial/{timestamp_key}"
            
            # 1. Leer datos actuales del usuario para actualizar totales acumulados
            user_node = f"users/{user_id}"
            user_data = fb_db.read_record(user_node) or {}

            puntos_prev = user_data.get("puntos", 0)
            nuevos_puntos = puntos_prev + session_summary.get("puntos", 0)
            lvl_info = GamificationEngine.get_level_data(nuevos_puntos)

            total_reps_prev = user_data.get("total_reps", 0)
            nuevas_reps = total_reps_prev + session_summary.get("repeticiones_totales", 0)

            cal_prev = user_data.get("total_calorias", 0.0)
            nuevas_cal = round(cal_prev + session_summary.get("calorias_estimadas", 0), 1)

            min_prev = user_data.get("total_minutos", 0.0)
            nuevos_min = round(min_prev + session_summary.get("duracion_minutos", 0), 1)

            sesiones_prev = user_data.get("total_sesiones", 0)
            nuevas_sesiones = sesiones_prev + 1

            today_reps = user_data.get("today_reps", 0) + session_summary.get("repeticiones_totales", 0)
            today_sessions = user_data.get("today_sessions", 0) + 1
            best_precision = max(user_data.get("best_precision_today", 0), session_summary.get("precision_postural", 0))

            # 2. Guardar la sesión individual en el historial
            fb_db.write_record(endpoint, session_summary)

            # 3. Actualizar nodo principal del usuario
            updates = {
                f"{user_node}/puntos": nuevos_puntos,
                f"{user_node}/nivel": lvl_info["level"],
                f"{user_node}/rango_titulo": lvl_info["title"],
                f"{user_node}/rango_color": lvl_info["color"],
                f"{user_node}/total_reps": nuevas_reps,
                f"{user_node}/total_calorias": nuevas_cal,
                f"{user_node}/total_minutos": nuevos_min,
                f"{user_node}/total_sesiones": nuevas_sesiones,
                f"{user_node}/today_reps": today_reps,
                f"{user_node}/today_sessions": today_sessions,
                f"{user_node}/best_precision_today": best_precision
            }
            
            fb_db.update_record("", updates)
            print(f"[SessionAnalyzer] Sesión y gamificación guardadas con éxito en Firebase para {user_id}")
            return True
        except Exception as e:
            print(f"[SessionAnalyzer] Error al guardar datos en Firebase: {e}")
            return False
