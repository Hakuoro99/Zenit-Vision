import os
import sys

# Añadir el directorio raíz al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.gamification import GamificationEngine

def test_gamification():
    print("=== TEST 1: Niveles y Rangos (50 Niveles) ===")
    
    # Test level 1 (0 pts)
    lvl_info = GamificationEngine.get_level_data(0)
    print(f"0 pts -> Nivel {lvl_info['level']} ({lvl_info['title']}), req: {lvl_info['next_level_req']} pts, progreso: {lvl_info['progress_pct']}%")
    assert lvl_info['level'] == 1
    assert lvl_info['title'] == "Novato Explorador"

    # Test level 11 (req sum = 100+200+300+400+500+600+700+800+900+1000 = 5500 pts)
    pts_for_lvl_11 = sum(100 * i for i in range(1, 11))
    lvl_info_11 = GamificationEngine.get_level_data(pts_for_lvl_11)
    print(f"{pts_for_lvl_11} pts -> Nivel {lvl_info_11['level']} ({lvl_info_11['title']})")
    assert lvl_info_11['level'] == 11
    assert lvl_info_11['title'] == "Atleta Promesa"

    # Test level 41
    pts_for_lvl_41 = sum(100 * i for i in range(1, 41))
    lvl_info_41 = GamificationEngine.get_level_data(pts_for_lvl_41)
    print(f"{pts_for_lvl_41} pts -> Nivel {lvl_info_41['level']} ({lvl_info_41['title']})")
    assert lvl_info_41['level'] == 41
    assert lvl_info_41['title'] == "Titán Legendario"

    print("\n=== TEST 2: Puntos por Ejercicio y Precisión ===")
    session_pts = GamificationEngine.calculate_session_points("FACIL", 10, 92)
    print(f"Fácil, 10 reps, 92% precisión -> {session_pts}")
    assert session_pts["rep_points"] == 100
    assert session_pts["precision_bonus"] == 50
    assert session_pts["total_points"] == 150

    session_pts_hard = GamificationEngine.calculate_session_points("AVANZADO", 20, 80)
    print(f"Avanzado, 20 reps, 80% precisión -> {session_pts_hard}")
    assert session_pts_hard["rep_points"] == 400
    assert session_pts_hard["precision_bonus"] == 25
    assert session_pts_hard["total_points"] == 425

    print("\n=== TEST 3: Bono Fijo por Racha Diaria ===")
    res1 = GamificationEngine.check_daily_streak_bonus("", 0)
    print(f"Primer día -> Racha: {res1['streak']}, Bono: {res1['bonus_pts']} pts")
    assert res1["bonus_pts"] == 20

    res_consec = GamificationEngine.check_daily_streak_bonus("2026-09-14", 3)
    print(f"Día consecutivo después de racha 3 -> Racha: {res_consec['streak']}, Bono: {res_consec['bonus_pts']} pts")
    assert res_consec["streak"] == 4
    assert res_consec["bonus_pts"] == 70

    print("\n¡TODOS LOS TESTS PASARON EXITOSAMENTE!")

if __name__ == "__main__":
    test_gamification()
