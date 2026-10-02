import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.gamification import GamificationEngine
from core.analyzer import SessionAnalyzer

def test_full_integration():
    print("=== TEST INTEGRACIÓN GAMIFICACIÓN LIMPIA ===")

    # 1. Simular resumen de workout
    ex_data = {"id": "squat_easy", "nombre": "Sentadilla Libre", "badge": "FACIL"}
    summary = SessionAnalyzer.calculate_session_stats(ex_data, total_reps=25, elapsed_seconds=120, total_calories=15.5)

    print(f"Resumen de sesión calculado:")
    print(f" - Repeticiones: {summary['repeticiones_totales']}")
    print(f" - Puntos ganados: {summary['puntos']} pts (Reps: {summary['rep_points']} pts, Precisión: {summary['precision_bonus']} pts)")

    # 2. Simular guardado en usuario invitado
    class DummyController:
        def __init__(self):
            self.guest_data = {}

    controller = DummyController()
    SessionAnalyzer.save_session_to_firebase(None, "invitado", summary, controller=controller)

    gd = controller.guest_data
    print(f"\nDatos de Invitado tras entrenamiento:")
    print(f" - Puntos acumulados: {gd['puntos']} pts")
    print(f" - Nivel actual: Nivel {gd['nivel']} ({gd['rango_titulo']})")

    assert gd['puntos'] == summary['puntos']
    assert gd['nivel'] == 3

    print("\n¡INTEGRACIÓN VERIFICADA CORRECTAMENTE SIN LOGROS!")

if __name__ == "__main__":
    test_full_integration()
