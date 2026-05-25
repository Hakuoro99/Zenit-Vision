import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR,
    RADIUS_MD,
)
from datetime import datetime, timedelta


class EstadisticasFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Contenido scrollable ──────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR,
                                         scrollbar_button_color=BG3,
                                         scrollbar_button_hover_color=BORDER2)
        scroll.pack(fill="both", expand=True)

        cnt = ctk.CTkFrame(scroll, fg_color=BG_COLOR)
        cnt.pack(fill="both", expand=True, padx=18, pady=16)

        # Cargar datos
        stats = self._load_stats()

        self._build_resumen_cards(cnt, stats)
        self._build_grafico_semanal(cnt, stats)
        self._build_historial(cnt, stats)

    # ── Tarjetas de resumen ───────────────────────────────────────────────────
    def _build_resumen_cards(self, parent, stats):
        ctk.CTkLabel(parent, text="RESUMEN GENERAL",
                     font=("DM Sans", 8),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 7))

        grid = ctk.CTkFrame(parent, fg_color=BG_COLOR)
        grid.pack(fill="x", pady=(0, 16))

        cards = [
            {"label": "Total sesiones",   "value": str(stats["total_sesiones"]),  "unit": "sesiones", "color": "#4ade80", "icon": "📋"},
            {"label": "Puntos acumulados","value": f"{stats['total_puntos']:,}",   "unit": "pts",      "color": "#fbbf24", "icon": "⭐"},
            {"label": "Tiempo total",     "value": str(stats["total_minutos"]),    "unit": "min",      "color": "#60a5fa", "icon": "⏱"},
            {"label": "Reps totales",     "value": f"{stats['total_reps']:,}",     "unit": "reps",     "color": "#f87171", "icon": "🔁"},
        ]

        for col, card in enumerate(cards):
            grid.grid_columnconfigure(col, weight=1)
            self._mini_card(grid, card, col)

    def _mini_card(self, parent, data, col):
        frame = ctk.CTkFrame(parent, fg_color=BG2,
                              border_width=1, border_color=BORDER,
                              corner_radius=9)
        frame.grid(row=0, column=col,
                   padx=(0 if col == 0 else 8, 0),
                   sticky="nsew")

        inner = ctk.CTkFrame(frame, fg_color=BG2)
        inner.pack(padx=12, pady=12, fill="x")

        ctk.CTkLabel(inner, text=data["icon"],
                     font=("DM Sans", 13)).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(inner, text=data["label"].upper(),
                     font=("DM Sans", 7),
                     text_color=TEXT_MUTED).pack(anchor="w")

        row = ctk.CTkFrame(inner, fg_color=BG2)
        row.pack(anchor="w")
        ctk.CTkLabel(row, text=data["value"],
                     font=("Syne", 18, "bold"),
                     text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(row, text=f" {data['unit']}",
                     font=("DM Sans", 9),
                     text_color=TEXT_MUTED).pack(side="left")

    # ── Gráfico de barras semanal ─────────────────────────────────────────────
    def _build_grafico_semanal(self, parent, stats):
        sec = ctk.CTkFrame(parent, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=9)
        sec.pack(fill="x", pady=(0, 14))

        head = ctk.CTkFrame(sec, fg_color=BG2)
        head.pack(fill="x", padx=14, pady=(12, 0))

        ctk.CTkLabel(head, text="Actividad semanal",
                     font=("Syne", 11, "bold"),
                     text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(head, text="últimos 7 días",
                     font=("DM Sans", 9),
                     text_color=TEXT_MUTED).pack(side="right")

        # Barras manuales con CTkFrame
        bar_area = ctk.CTkFrame(sec, fg_color=BG2)
        bar_area.pack(fill="x", padx=14, pady=12)

        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        semana = stats.get("semana", [0]*7)
        max_val = max(semana) if max(semana) > 0 else 1
        MAX_H = 60

        for i, (dia, val) in enumerate(zip(dias, semana)):
            col_frame = ctk.CTkFrame(bar_area, fg_color=BG2)
            col_frame.pack(side="left", expand=True, fill="x", padx=3)

            bar_h = max(4, int(val / max_val * MAX_H))
            is_today = (i == datetime.now().weekday())

            # Spacer arriba
            ctk.CTkFrame(col_frame, fg_color=BG2,
                          height=MAX_H - bar_h).pack(fill="x")

            # Barra
            ctk.CTkFrame(col_frame,
                          fg_color=ACCENT_GREEN if is_today else BG3,
                          height=bar_h,
                          corner_radius=3).pack(fill="x")

            # Valor
            ctk.CTkLabel(col_frame,
                          text=str(val) if val > 0 else "",
                          font=("DM Sans", 7),
                          text_color=ACCENT_TEXT if is_today else TEXT_MUTED).pack()

            # Día
            ctk.CTkLabel(col_frame, text=dia,
                          font=("DM Sans", 8),
                          text_color=ACCENT_TEXT if is_today else TEXT_MUTED).pack()

    # ── Historial de sesiones ─────────────────────────────────────────────────
    def _build_historial(self, parent, stats):
        ctk.CTkLabel(parent, text="HISTORIAL DE SESIONES",
                     font=("DM Sans", 8),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 7))

        historial = stats.get("historial", [])
        if not historial:
            ctk.CTkLabel(parent,
                          text="Aún no hay sesiones registradas.\n¡Empieza tu primer ejercicio!",
                          font=("DM Sans", 11),
                          text_color=TEXT_MUTED,
                          justify="center").pack(pady=30)
            return

        for ses in historial:
            row = ctk.CTkFrame(parent, fg_color=BG2,
                                border_width=1, border_color=BORDER,
                                corner_radius=8)
            row.pack(fill="x", pady=2)

            inner = ctk.CTkFrame(row, fg_color=BG2)
            inner.pack(fill="x", padx=12, pady=8)

            ctk.CTkLabel(inner, text=ses.get("nombre", "Ejercicio"),
                          font=("DM Sans", 11, "bold"),
                          text_color=TEXT_WHITE).pack(side="left")

            right = ctk.CTkFrame(inner, fg_color=BG2)
            right.pack(side="right")

            ctk.CTkLabel(right, text=ses.get("pts", "+0 pts"),
                          font=("Syne", 10, "bold"),
                          text_color=ACCENT_TEXT).pack(side="right", padx=(8, 0))
            ctk.CTkLabel(right, text=ses.get("fecha", ""),
                          font=("DM Sans", 8),
                          text_color=TEXT_MUTED).pack(side="right")

    # ── Datos ─────────────────────────────────────────────────────────────────
    def _load_stats(self):
        try:
            uid  = self.controller.current_user_id
            data = self.controller.fb_db.read_record(f"actividades/{uid}")
            if data and isinstance(data, list):
                total_sesiones = len(data)
                total_puntos   = sum(int(a.get("puntos", 0)) for a in data)
                total_minutos  = sum(int(a.get("tiempo",  0)) for a in data)
                total_reps     = sum(int(a.get("reps",    0)) for a in data)
                return {
                    "total_sesiones": total_sesiones,
                    "total_puntos":   total_puntos,
                    "total_minutos":  total_minutos,
                    "total_reps":     total_reps,
                    "semana":         [0]*7,
                    "historial":      data[-10:],
                }
        except Exception:
            pass

        # Fallback de ejemplo
        return {
            "total_sesiones": 12,
            "total_puntos":   840,
            "total_minutos":  145,
            "total_reps":     320,
            "semana":         [2, 0, 3, 1, 2, 0, 1],
            "historial": [
                {"nombre": "Sentadillas",    "pts": "+45 pts", "fecha": "Hoy"},
                {"nombre": "Lagartijas",     "pts": "+80 pts", "fecha": "Ayer"},
                {"nombre": "Jumping Jacks",  "pts": "+80 pts", "fecha": "Ayer"},
                {"nombre": "Reto Avanzado",  "pts": "+200 pts","fecha": "Dom"},
            ],
        }