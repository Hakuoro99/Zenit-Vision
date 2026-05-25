import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR, ERROR_BG, ERROR_BORDER,
    RADIUS_MD, RADIUS_LG,
)

# ── Paleta de dificultades (igual que HTML) ───────────────────────────────────
DIFF = {
    "facil":  {"bg": "#0d1a10", "brd": "#163022", "tx": "#4ade80", "label": "Fácil"},
    "normal": {"bg": "#141a0d", "brd": "#243018", "tx": "#a3e635", "label": "Normal"},
    "dificil":{"bg": "#1a0d0d", "brd": "#301616", "tx": "#f87171", "label": "Difícil"},
    "libre":  {"bg": "#0d1020", "brd": "#162040", "tx": "#60a5fa", "label": "Libre"},
}

EJERCICIOS_DATA = [
    {
        "id": "sentadillas",
        "nombre": "Sentadillas",
        "descripcion": "Fortalece cuádriceps, glúteos y core con el movimiento básico.",
        "dificultad": "facil",
        "reps": 15,
        "tiempo": 10,
        "pts": 45,
        "icon": "⬇",
    },
    {
        "id": "lagartijas",
        "nombre": "Lagartijas",
        "descripcion": "Trabaja pectoral, tríceps y hombros con postura correcta.",
        "dificultad": "normal",
        "reps": 30,
        "tiempo": 20,
        "pts": 80,
        "icon": "➡",
    },
    {
        "id": "jumping_jacks",
        "nombre": "Jumping Jacks",
        "descripcion": "Cardio de cuerpo completo para mejorar resistencia.",
        "dificultad": "normal",
        "reps": 40,
        "tiempo": 20,
        "pts": 80,
        "icon": "⚡",
    },
    {
        "id": "burpees",
        "nombre": "Burpees",
        "descripcion": "Ejercicio de alta intensidad que trabaja todo el cuerpo.",
        "dificultad": "dificil",
        "reps": 20,
        "tiempo": 30,
        "pts": 150,
        "icon": "🔥",
    },
    {
        "id": "plancha",
        "nombre": "Plancha Isométrica",
        "descripcion": "Fortalece el core y mejora la estabilidad postural.",
        "dificultad": "normal",
        "reps": 1,
        "tiempo": 60,
        "pts": 70,
        "icon": "▬",
    },
    {
        "id": "libre",
        "nombre": "Ejercicio Libre",
        "descripcion": "Entrena a tu ritmo sin guía — registra tus propios datos.",
        "dificultad": "libre",
        "reps": 0,
        "tiempo": 0,
        "pts": 60,
        "icon": "🕐",
    },
]


class EjerciciosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller    = controller
        self.filtro_activo = "todos"
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Filtros de dificultad ─────────────────────────────────────────────
        filter_bar = ctk.CTkFrame(self, fg_color=BG1,
                                   border_width=1, border_color=BORDER)
        filter_bar.pack(fill="x")

        self._filter_btns = {}
        filtros = [("todos", "Todos"), ("facil", "Fácil"),
                   ("normal", "Normal"), ("dificil", "Difícil"),
                   ("libre", "Libre")]

        for key, label in filtros:
            btn = ctk.CTkButton(
                filter_bar,
                text=label,
                font=("DM Sans", 10),
                fg_color=BG2 if key == "todos" else BG1,
                hover_color=BG2,
                text_color=ACCENT_TEXT if key == "todos" else TEXT_MUTED,
                border_width=1,
                border_color=BORDER2 if key == "todos" else BORDER,
                corner_radius=5,
                height=24, width=72,
                command=lambda k=key: self._apply_filter(k),
            )
            btn.pack(side="left", padx=5, pady=8)
            self._filter_btns[key] = btn

        # ── Grid de ejercicios (scrollable) ───────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR,
                                         scrollbar_button_color=BG3,
                                         scrollbar_button_hover_color=BORDER2)
        scroll.pack(fill="both", expand=True)
        self._scroll = scroll
        self._render_cards(EJERCICIOS_DATA)

    def _apply_filter(self, key):
        self.filtro_activo = key
        for k, btn in self._filter_btns.items():
            if k == key:
                btn.configure(fg_color=BG2, text_color=ACCENT_TEXT,
                               border_color=BORDER2)
            else:
                btn.configure(fg_color=BG1, text_color=TEXT_MUTED,
                               border_color=BORDER)
        filtrados = (EJERCICIOS_DATA if key == "todos"
                     else [e for e in EJERCICIOS_DATA if e["dificultad"] == key])
        self._render_cards(filtrados)

    def _render_cards(self, ejercicios):
        # Limpiar cards anteriores
        for w in self._scroll.winfo_children():
            w.destroy()

        grid = ctk.CTkFrame(self._scroll, fg_color=BG_COLOR)
        grid.pack(fill="both", expand=True, padx=18, pady=16)

        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)

        for idx, ej in enumerate(ejercicios):
            row = idx // 3
            col = idx % 3
            self._ejercicio_card(grid, ej, row, col)

    def _ejercicio_card(self, parent, ej, row, col):
        d = DIFF[ej["dificultad"]]

        card = ctk.CTkFrame(parent, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=9)
        card.grid(row=row, column=col,
                  padx=(0 if col == 0 else 9, 0),
                  pady=(0 if row == 0 else 9, 0),
                  sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color=BG2)
        inner.pack(fill="both", padx=14, pady=14)

        # Cabecera: icono + badge dificultad
        head = ctk.CTkFrame(inner, fg_color=BG2)
        head.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(head, text=ej["icon"],
                     font=("DM Sans", 16),
                     fg_color=d["bg"],
                     corner_radius=6,
                     width=32, height=32,
                     text_color=d["tx"]).pack(side="left")

        ctk.CTkLabel(head,
                     text=d["label"],
                     font=("DM Sans", 8),
                     fg_color=d["bg"],
                     corner_radius=4,
                     text_color=d["tx"],
                     padx=7, pady=2).pack(side="right")

        # Nombre
        ctk.CTkLabel(inner, text=ej["nombre"],
                     font=("Syne", 12, "bold"),
                     text_color=TEXT_WHITE,
                     anchor="w").pack(fill="x")

        # Descripción
        ctk.CTkLabel(inner, text=ej["descripcion"],
                     font=("DM Sans", 10),
                     text_color=TEXT_GRAY,
                     wraplength=180,
                     justify="left",
                     anchor="w").pack(fill="x", pady=(3, 10))

        # Stats: reps / tiempo / pts
        stats = ctk.CTkFrame(inner, fg_color=BG2)
        stats.pack(fill="x", pady=(0, 10))

        if ej["reps"] > 0:
            self._stat_pill(stats, f"{ej['reps']} reps", "#4ade80")
        if ej["tiempo"] > 0:
            self._stat_pill(stats, f"{ej['tiempo']} min", "#60a5fa")
        self._stat_pill(stats, f"+{ej['pts']} pts", "#fbbf24")

        # Separador
        ctk.CTkFrame(inner, fg_color=BORDER, height=1).pack(fill="x", pady=(0, 10))

        # Botón iniciar
        ctk.CTkButton(
            inner,
            text="▶  Iniciar reto",
            font=("DM Sans", 11, "bold"),
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_HOVER,
            text_color="#071a0e",
            corner_radius=7,
            height=32,
            command=lambda e=ej: self._iniciar(e),
        ).pack(fill="x")

    def _stat_pill(self, parent, text, color):
        ctk.CTkLabel(parent, text=text,
                     font=("DM Sans", 8),
                     fg_color=BG3,
                     corner_radius=4,
                     text_color=color,
                     padx=6, pady=2).pack(side="left", padx=(0, 4))

    def _iniciar(self, ejercicio):
        """Navega a la pantalla de ejercicio activo."""
        try:
            from ui.frames.ejercicio_activo import EjercicioActivoFrame
            self.controller.ejercicio_actual = ejercicio
            self.controller.show_frame(EjercicioActivoFrame)
        except Exception:
            # Si no existe el frame todavía, mostrar info en consola
            print(f"Iniciando: {ejercicio['nombre']}")