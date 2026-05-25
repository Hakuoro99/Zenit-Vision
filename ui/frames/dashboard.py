import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR, ERROR_BG, ERROR_BORDER,
    AVATAR_PALETTE,
    FONT_LOGO, FONT_TITLE, FONT_SUBTITLE, FONT_LABEL, FONT_REGULAR, FONT_INPUT, FONT_SMALL, FONT_TINY,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, RADIUS_PILL,
    BTN_HEIGHT, INPUT_H, TOPBAR_H, SIDEBAR_W
)
import os, base64, requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO

# ── Colores de las tarjetas de actividad mapeados al Modo Mineral ─────────────
TAG_GREEN  = {"fg": "#2BB371", "bg": "#102118"}
TAG_BLUE   = {"fg": "#4F93E6", "bg": "#101626"}
TAG_YELLOW = {"fg": "#A3E635", "bg": "#1A2110"}
TAG_RED    = {"fg": "#E05A5A", "bg": "#211010"}


def _make_avatar(size, initials, palette):
    """Avatar circular con iniciales para el sidebar."""
    r = size * 2
    img  = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    mask = Image.new("L",    (r, r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r-1, r-1), fill=255)
    bg = Image.new("RGBA", (r, r), palette["bg"])
    img.paste(bg, (0, 0), mask)
    from PIL import ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(r * 0.38))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox-bbox, bbox-bbox
    draw.text(((r-tw)/2 - bbox, (r-th)/2 - bbox),
              initials, fill=palette["fg"], font=font)
    img.putalpha(mask)
    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(img, size=(size, size))


def _make_icon_bg(size, color_hex, alpha=18):
    """Fondo circular/cuadrado semitransparente para iconos."""
    r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
    img = Image.new("RGBA", (size, size), (r, g, b, alpha))
    return ctk.CTkImage(img, size=(size, size))


# ══════════════════════════════════════════════════════════════════════════════

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller
        self._build_layout()

    def _build_layout(self):
        """Construye topbar + contenido."""
        for w in self.winfo_children():
            w.destroy()
        self._build_topbar(self)
        self._build_content(self)

    def _nav_btn(self, parent, label, icon_text, active=False, cmd=None):
        fg   = "#102118" if active else BG1
        tc   = ACCENT_TEXT if active else TEXT_MUTED
        brd  = "#163827" if active else BG1
        btn = ctk.CTkButton(
            parent,
            text=f"  {icon_text}  {label}",
            font=ctk.CTkFont(family=FONT_LABEL, size=FONT_LABEL, weight="bold" if active else "normal"),
            fg_color=fg,
            hover_color="#102118" if active else BG3,
            text_color=tc,
            border_width=1,
            border_color=brd,
            corner_radius=RADIUS_MD,
            height=32,
            anchor="w",
            command=cmd,
        )
        return btn

    def _nav_click(self, key):
        for k, btn in self._nav_items.items():
            if k == key:
                btn.configure(fg_color="#102118", text_color=ACCENT_TEXT,
                               border_color="#163827", hover_color="#102118")
            else:
                btn.configure(fg_color=BG1, text_color=TEXT_MUTED,
                               border_color=BG1, hover_color=BG3)

        if key == "inicio":
            self.controller.show_frame(DashboardFrame)
        elif key == "ejercicios":
            from ui.frames.ejercicios import EjerciciosFrame
            self.controller.show_frame(EjerciciosFrame)
        elif key == "estadisticas":
            from ui.frames.estadisticas import EstadisticasFrame
            self.controller.show_frame(EstadisticasFrame)
        elif key == "configuracion":
            from ui.frames.configuracion import ConfiguracionFrame
            self.controller.show_frame(ConfiguracionFrame)

    def _build_user_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color=BG2,
                           border_width=1, border_color=BORDER,
                           corner_radius=RADIUS_MD)
        row.pack(fill="x", pady=(0, 5))

        nombre  = "Usuario"
        nivel   = 1
        initials = "US"
        palette  = AVATAR_PALETTE

        try:
            uid  = self.controller.current_user_id
            data = self.controller.fb_db.read_record(f"users/{uid}")
            if data:
                nombre   = data.get("nombre", "Usuario")
                nivel    = data.get("nivel", 1)
                initials = "".join(p.upper() for p in nombre.split()[:2]) or nombre[:2].upper()
        except Exception:
            pass

        av_img = _make_avatar(24, initials, palette)
        ctk.CTkLabel(row, image=av_img, text="").pack(
            side="left", padx=(8, 6), pady=6)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", pady=4)
        ctk.CTkLabel(info, text=nombre[:14],
                     font=ctk.CTkFont(family=FONT_LABEL, size=FONT_LABEL, weight="bold"),
                     text_color=TEXT_WHITE,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=f"Nivel {nivel} · Explorador",
                     font=ctk.CTkFont(family=FONT_TINY, size=FONT_TINY),
                     text_color=TEXT_MUTED,
                     anchor="w").pack(anchor="w")

    def _build_logout_btn(self, parent):
        btn = ctk.CTkButton(
            parent,
            text="  ⎋  Cerrar sesión",
            font=ctk.CTkFont(family=FONT_LABEL, size=FONT_LABEL),
            fg_color=ERROR_BG,
            hover_color="#2B1414",
            text_color=ERROR_COLOR,
            border_width=1,
            border_color=ERROR_BORDER,
            corner_radius=RADIUS_MD,
            height=30,
            anchor="w",
            command=self._logout,
        )
        btn.pack(fill="x")

    # ── TOPBAR ────────────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        tb = ctk.CTkFrame(parent, fg_color=BG1, height=TOPBAR_H,
                          corner_radius=0,
                          border_width=1, border_color=BORDER)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        left = ctk.CTkFrame(tb, fg_color="transparent")
        left.pack(side="left", padx=18)

        ctk.CTkLabel(left, text="Panel de Control",
                     font=ctk.CTkFont(family=FONT_TITLE, size=16, weight="bold"),
                     text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(left, text="Actividades de la semana",
                     font=ctk.CTkFont(family=FONT_REGULAR, size=10),
                     text_color=TEXT_MUTED).pack(anchor="w")

        right = ctk.CTkFrame(tb, fg_color="transparent")
        right.pack(side="right", padx=18)

        fecha = datetime.now().strftime("%d %B %Y")
        ctk.CTkLabel(right,
                     text=fecha,
                     font=ctk.CTkFont(family=FONT_SMALL, size=10),
                     fg_color=BG2,
                     corner_radius=RADIUS_SM,
                     text_color=TEXT_GRAY,
                     padx=10, pady=4).pack(side="left", padx=(0, 6))

        ctk.CTkButton(right, text="🔔",
                      font=ctk.CTkFont(family=FONT_REGULAR, size=12),
                      fg_color=BG2, hover_color=BG3,
                      text_color=TEXT_GRAY,
                      border_width=1, border_color=BORDER,
                      corner_radius=RADIUS_SM,
                      width=28, height=28,
                      command=lambda: None).pack(side="left")

    # ── CONTENIDO PRINCIPAL ───────────────────────────────────────────────────
    def _build_content(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color=BG_COLOR,
                                         scrollbar_button_color=BG2,
                                         scrollbar_button_hover_color=BG3)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        cnt = ctk.CTkFrame(scroll, fg_color="transparent")
        cnt.pack(fill="both", expand=True, padx=20, pady=18)

        self._build_stat_cards(cnt)
        self._build_action_buttons(cnt)
        self._build_activity_header(cnt)
        self._build_activity_list(cnt)

    # ── TARJETAS DE ESTADÍSTICAS ──────────────────────────────────────────────
    def _build_stat_cards(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 16))

        puntos = 0
        nivel  = 1
        racha  = 15

        try:
            uid  = self.controller.current_user_id
            data = self.controller.fb_db.read_record(f"users/{uid}")
            if data:
                puntos = data.get("puntos", 0)
                nivel  = data.get("nivel", 1)
                racha  = data.get("racha", 0)
        except Exception:
            pass

        cards = [
            {"label": "Total de Puntos", "value": f"{puntos:,}", "unit": "pts",
             "tag": "+45 hoy", "color": TAG_GREEN,  "icon": "⭐"},
            {"label": "Nivel Actual",    "value": str(nivel),   "unit": "Explorador",
             "tag": "3 ejercicios hoy", "color": TAG_BLUE,   "icon": "📈"},
            {"label": "Mejor Racha",     "value": str(racha),   "unit": "días",
             "tag": "Activa",           "color": TAG_YELLOW, "icon": "⚡"},
        ]

        for col, card in enumerate(cards):
            grid.grid_columnconfigure(col, weight=1)
            self._stat_card(grid, card, col)

    def _stat_card(self, parent, data, col):
        c = data["color"]
        frame = ctk.CTkFrame(parent, fg_color=BG2,
                              border_width=1, border_color=BORDER,
                              corner_radius=RADIUS_LG)
        frame.grid(row=0, column=col, padx=(0 if col == 0 else 10, 0), sticky="nsew")

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(padx=16, pady=16, fill="x")

        ic = ctk.CTkLabel(inner, text=data["icon"],
                          font=ctk.CTkFont(family=FONT_REGULAR, size=13),
                          fg_color=c["bg"],
                          corner_radius=RADIUS_MD,
                          width=30, height=30,
                          text_color=c["fg"])
        ic.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(inner, text=data["label"].upper(),
                     font=ctk.CTkFont(family=FONT_TINY, size=8, weight="bold"),
                     text_color=TEXT_MUTED,
                     anchor="w").pack(anchor="w")

        val_row = ctk.CTkFrame(inner, fg_color="transparent")
        val_row.pack(anchor="w")
        ctk.CTkLabel(val_row, text=data["value"],
                     font=ctk.CTkFont(family=FONT_TITLE, size=24, weight="bold"),
                     text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(val_row, text=f" {data['unit']}",
                     font=ctk.CTkFont(family=FONT_REGULAR, size=11),
                     text_color=TEXT_MUTED).pack(side="left", pady=(6, 0))

        ctk.CTkLabel(inner, text=data["tag"],
                     font=ctk.CTkFont(family=FONT_TINY, size=8, weight="bold"),
                     fg_color=c["bg"],
                     corner_radius=RADIUS_SM,
                     text_color=c["fg"],
                     padx=8, pady=2).pack(anchor="w", pady=(6, 0))

    # ── BOTONES DE ACCIÓN ─────────────────────────────────────────────────────
    def _build_action_buttons(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        btn_p = ctk.CTkButton(
            grid,
            text="▶   Iniciar ejercicio\n      Nueva sesión de entrenamiento",
            font=ctk.CTkFont(family=FONT_SUBTITLE, size=13, weight="bold"),
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_HOVER,
            text_color="#070809",  # Texto oscuro premium
            corner_radius=RADIUS_LG,
            height=60,
            anchor="w",
            command=lambda: self._nav_click("ejercicios"),
        )
        btn_p.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        btn_s = ctk.CTkButton(
            grid,
            text="📊   Ver estadísticas\n       Revisa tu progreso semanal",
            font=ctk.CTkFont(family=FONT_SUBTITLE, size=13, weight="bold"),
            fg_color=BG2,
            hover_color=BG3,
            text_color=TEXT_WHITE,
            border_width=1,
            border_color=BORDER,
            corner_radius=RADIUS_LG,
            height=60,
            anchor="w",
            command=lambda: self._nav_click("estadisticas"),
        )
        btn_s.grid(row=0, column=1, sticky="nsew")

    # ── CABECERA ACTIVIDADES ──────────────────────────────────────────────────
    def _build_activity_header(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(row, text="Actividades de esta semana",
                     font=ctk.CTkFont(family=FONT_SUBTITLE, size=14, weight="bold"),
                     text_color=TEXT_WHITE).pack(side="left")

        ctk.CTkButton(row, text="Ver todo →",
                      font=ctk.CTkFont(family=FONT_SMALL, size=10, weight="bold"),
                      fg_color=BG_COLOR,
                      hover_color=BG2,
                      text_color=ACCENT_TEXT,
                      border_width=0,
                      height=22,
                      command=lambda: self._nav_click("estadisticas")).pack(side="right")

    # ── LISTA DE ACTIVIDADES ──────────────────────────────────────────────────
    def _build_activity_list(self, parent):
        activities = self._load_activities()

        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x")

        last_day = None
        for act in activities:
            day = act.get("day", "")
            if day != last_day:
                sep_frame = ctk.CTkFrame(container, fg_color="transparent")
                sep_frame.pack(fill="x", pady=(10 if last_day else 0, 4))
                if last_day:
                    ctk.CTkFrame(sep_frame, fg_color=BORDER, height=1).pack(fill="x", pady=(0, 4))
                ctk.CTkLabel(sep_frame,
                             text=day.upper(),
                             font=ctk.CTkFont(family=FONT_TINY, size=8, weight="bold"),
                             text_color=TEXT_MUTED).pack(anchor="w")
                last_day = day

            self._activity_item(container, act)

    def _activity_item(self, parent, data):
        c = data.get("color", TAG_GREEN)

        row = ctk.CTkFrame(parent, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=RADIUS_MD)
        row.pack(fill="x", pady=3)
        row.bind("<Enter>", lambda e: row.configure(border_color=BORDER2))
        row.bind("<Leave>", lambda e: row.configure(border_color=BORDER))

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(inner, text=data.get("icon", "•"),
                      font=ctk.CTkFont(family=FONT_REGULAR, size=14),
                      fg_color=c["bg"],
                      corner_radius=RADIUS_SM,
                      width=32, height=32,
                      text_color=c["fg"]).pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=data.get("nombre", "Ejercicio"),
                     font=ctk.CTkFont(family=FONT_LABEL, size=12, weight="bold"),
                     text_color=TEXT_WHITE,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(info,
                     text=data.get("hora", "").upper(),
                     font=ctk.CTkFont(family=FONT_TINY, size=9),
                     text_color=TEXT_MUTED,
                     anchor="w").pack(anchor="w")

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")
        ctk.CTkLabel(right, text=data.get("pts", "+0 pts"),
                     font=ctk.CTkFont(family=FONT_SUBTITLE, size=12, weight="bold"),
                     text_color=ACCENT_TEXT,
                     anchor="e").pack(anchor="e")
        ctk.CTkLabel(right, text=data.get("detalle", ""),
                     font=ctk.CTkFont(family=FONT_TINY, size=9),
                     text_color=TEXT_MUTED,
                     anchor="e").pack(anchor="e")

        ctk.CTkLabel(inner, text="›",
                     font=ctk.CTkFont(family=FONT_REGULAR, size=18),
                     text_color=TEXT_MUTED).pack(side="right", padx=(6, 0))

    def _load_activities(self):
        try:
            uid  = self.controller.current_user_id
            data = self.controller.fb_db.read_record(f"actividades/{uid}")
            if data and isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass

        return [
            {"day": "Hoy — " + datetime.now().strftime("%A %d %b"),
             "nombre": "Sentadillas · Reto Fácil",
             "hora": "08:30 am", "pts": "+45 pts",
             "detalle": "15 reps · 10 min",
             "icon": "⬇", "color": TAG_GREEN},
            {"day": "Ayer",
             "nombre": "Lagartijas · Reto Normal",
             "hora": "07:15 am", "pts": "+80 pts",
             "detalle": "30 reps · 20 min",
             "icon": "➡", "color": TAG_BLUE},
            {"day": "Ayer",
             "nombre": "Jumping Jacks · Reto Normal",
             "hora": "07:50 am", "pts": "+80 pts",
             "detalle": "40 reps · 20 min",
             "icon": "⚡", "color": TAG_YELLOW},
            {"day": "Domingo",
             "nombre": "Reto Avanzado completo",
             "hora": "06:00 am", "pts": "+200 pts",
             "detalle": "180 reps · 35 min",
             "icon": "🔥", "color": TAG_RED},
            {"day": "Sábado",
             "nombre": "Ejercicio Libre",
             "hora": "10:20 am", "pts": "+60 pts",
             "detalle": "Libre · 18 min",
             "icon": "🕐", "color": TAG_GREEN},
        ]

    def _icon_grid(self):     return "⊞"
    def _icon_clock(self):    return "◷"
    def _icon_bars(self):     return "▐"
    def _icon_settings(self): return "⚙"

    def _logout(self):
        try:
            self.controller.current_user_id = None
        except Exception:
            pass
        from ui.frames.login import LoginFrame
        self.controller.show_frame(LoginFrame)