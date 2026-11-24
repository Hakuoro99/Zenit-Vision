"""
Script de Benchmark Automatizado para Zenit-Visión
Mide FPS, latencia por fotograma de PoseDetector, y tiempos de respuesta.
"""
import time
import os
import sys
import numpy as np
import cv2

# Añadir raíz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pose_detector import PoseDetector
from core.exercise_counter import ExerciseCounter
from core.gamification import GamificationEngine

def run_benchmark(num_frames=100):
    print("="*60)
    print(" INICIANDO BENCHMARK DE RENDIMIENTO - ZENIT-VISIÓN")
    print("="*60)
    
    print("\n[1/3] Inicializando detector MediaPipe PoseLandmarker...")
    t0 = time.time()
    detector = PoseDetector(min_detection_con=0.5)
    counter = ExerciseCounter(exercise_type="squat")
    init_time = (time.time() - t0) * 1000
    print(f" -> Tiempo de carga e inicialización del modelo: {init_time:.2f} ms")

    # Sintetizar fotograma de prueba HD (1280x720)
    test_img = np.zeros((720, 1280, 3), dtype=np.uint8)
    # Dibujar figura humana esquemática básica
    cv2.circle(test_img, (640, 200), 50, (200, 200, 200), -1) # Cabeza
    cv2.line(test_img, (640, 250), (640, 500), (200, 200, 200), 10) # Torso
    cv2.line(test_img, (640, 500), (580, 680), (200, 200, 200), 8) # Pierna Izq
    cv2.line(test_img, (640, 500), (700, 680), (200, 200, 200), 8) # Pierna Der

    print(f"\n[2/3] Procesando {num_frames} fotogramas a resolución 1280x720...")
    latencies = []
    
    for i in range(num_frames):
        t_start = time.perf_counter()
        
        # Pipeline: inferencia + extracción de landmarks + procesamiento cinemático
        processed = detector.find_pose(test_img.copy(), draw=True)
        detector.find_positions(processed, draw=False)
        counter.process(detector, processed)
        
        t_end = time.perf_counter()
        latencies.append((t_end - t_start) * 1000)

    avg_latency = np.mean(latencies)
    std_latency = np.std(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    estimated_fps = 1000.0 / avg_latency

    print("\n--- RESULTADOS DE VISIÓN ARTIFICIAL ---")
    print(f" • Latencia Media por fotograma : {avg_latency:.2f} ms (± {std_latency:.2f} ms)")
    print(f" • Latencia Mínima             : {min_latency:.2f} ms")
    print(f" • Latencia Máxima             : {max_latency:.2f} ms")
    print(f" • Tasa de Procesamiento (FPS) : {estimated_fps:.1f} FPS")

    print("\n[3/3] Midiendo Motor de Gamificación (1,000 transacciones)...")
    t_gam_start = time.perf_counter()
    for _ in range(1000):
        GamificationEngine.calculate_session_points("AVANZADO", 35, 95)
        GamificationEngine.get_level_data(15400)
    t_gam_end = time.perf_counter()
    gam_avg_us = ((t_gam_end - t_gam_start) / 1000) * 1000000
    print(f" • Tiempo promedio GamificationEngine: {gam_avg_us:.2f} microsegundos por cálculo")

    print("\n" + "="*60)
    print(" BENCHMARK COMPLETADO EXITOSAMENTE")
    print(" Usa estos datos exactos para rellenar la tabla 6.4 en tu tesis.")
    print("="*60)

if __name__ == "__main__":
    run_benchmark(50)
