import customtkinter as ctk
from database.firebase_database import FirebaseDB
from ui.styles import BG_COLOR, BG1, BG2, BG3, BORDER, BORDER2
from ui.styles import TEXT_WHITE, TEXT_GRAY, TEXT_MUTED
from ui.styles import ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT
from ui.styles import ERROR_COLOR, ERROR_BG, ERROR_BORDER
from ui.styles import AVATAR_PALETTE
from ui.frames.login import LoginFrame
from ui.frames.register import RegisterFrame

import os
from PIL import Image


# ── Páginas autenticadas (importación lazy para evitar errores) ────────────────
def _get_frame(name):
    if name == "dashboard":
        from ui.frames.dashboard import DashboardFrame
        return DashboardFrame
    elif name == "ejercicios":
        from ui.frames.ejercicios import EjerciciosFrame
        return EjerciciosFrame
    elif name == "estadisticas":
        from ui.frames.estadisticas import EstadisticasFrame
        return EstadisticasFrame
    elif name == "configuracion":
        from ui.frames.configuracion import ConfiguracionFrame
        return ConfiguracionFrame


# ══════════════════════════════════════════════════════════════════════════════
# AppShell — layout con sidebar permanente para todas las pantallas autenticadas
# ══════════════════════════════════════════════════════════════════════════════

class AppShell(ctk.CTkFrame):
    """
    Frame contenedor para las pantallas autenticadas.
    Sidebar permanente a la izquierda + área de contenido intercambiable.
    """
    SB_W = 190

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller   = controller
        self._nav_btns    = {}
        self._content_frames = {}
        self._active_key  = "dashboard"

        # Layout horizontal: sidebar | contenido
        self._build_sidebar()
        self._build_content_area()

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self._sb = ctk.CTkFrame(self, fg_color=BG1, width=self.SB_W,
                                 corner_radius=0,
                                 border_width=1, border_color=BORDER)
        self._sb.pack(side="left", fill="y")
        self._sb.pack_propagate(False)

        # Logo
        logo_f = ctk.CTkFrame(self._sb, fg_color=BG1)
        logo_f.pack(fill="x", padx=14, pady=(14, 10))

        logo_path = os.path.join("assets", "icon", "Zenit_Vision_Logo.png")
        if os.path.exists(logo_path):
            try:
                pil = Image.open(logo_path).convert("RGBA")
                ow, oh = pil.size
                tw = 28
                img = ctk.CTkImage(pil, size=(tw, int(oh*tw/ow)))
                ctk.CTkLabel(logo_f, image=img, text="").pack(side="left", padx=(0,8))
            except Exception:
                pass

        txt = ctk.CTkFrame(logo_f, fg_color=BG1)
        txt.pack(side="left")
        row = ctk.CTkFrame(txt, fg_color=BG1)
        row.pack(anchor="w")
        ctk.CTkLabel(row, text="ZENIT ",  font=("Syne",12,"bold"), text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(row, text="VISION",  font=("Syne",12,"bold"), text_color=ACCENT_TEXT).pack(side="left")
        ctk.CTkLabel(txt, text="MODO EXPLORADOR", font=("DM Sans",7), text_color=TEXT_MUTED).pack(anchor="w")

        # Separador
        ctk.CTkFrame(self._sb, fg_color=BORDER, height=1).pack(fill="x")

        # Navegación
        nav = ctk.CTkFrame(self._sb, fg_color=BG1)
        nav.pack(fill="x", padx=7, pady=10)

        items = [
            ("dashboard",    "⊞  Inicio"),
            ("ejercicios",   "◷  Ejercicios"),
            ("estadisticas", "▐  Estadísticas"),
            ("configuracion","⚙  Configuración"),
        ]
        for key, label in items:
            btn = ctk.CTkButton(
                nav,
                text=label,
                font=("DM Sans", 11),
                fg_color=BG1,
                hover_color=BG3,
                text_color=TEXT_MUTED,
                border_width=1,
                border_color=BG1,
                corner_radius=7,
                height=30,
                anchor="w",
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", pady=1)
            self._nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(self._sb, fg_color=BG1).pack(fill="both", expand=True)

        # Separador inferior
        ctk.CTkFrame(self._sb, fg_color=BORDER, height=1).pack(fill="x")

        # Fila de usuario + logout
        bot = ctk.CTkFrame(self._sb, fg_color=BG1)
        bot.pack(fill="x", padx=7, pady=9)
        self._user_row_frame = bot
        self._build_user_row()
        self._build_logout_btn()

    def _build_user_row(self):
        # Limpiar fila anterior si existe
        for w in self._user_row_frame.winfo_children():
            if hasattr(w, '_is_user_row'):
                w.destroy()

        nombre   = "Usuario"
        nivel    = 1
        initials = "US"
        palette  = AVATAR_PALETTE[1]

        try:
            uid  = self.controller.current_user_id
            data = self.controller.fb_db.read_record(f"users/{uid}")
            if data:
                nombre   = data.get("nombre", "Usuario")
                nivel    = data.get("nivel", 1)
                initials = "".join(p[0].upper() for p in nombre.split()[:2]) or nombre[:2].upper()
        except Exception:
            pass

        from PIL import ImageDraw, ImageFont
        r   = 48
        img = Image.new("RGBA", (r, r), (0, 0, 0, 0))
        msk = Image.new("L",    (r, r), 0)
        ImageDraw.Draw(msk).ellipse((0, 0, r-1, r-1), fill=255)
        bg  = Image.new("RGBA", (r, r), palette["bg"])
        img.paste(bg, (0, 0), msk)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(r * 0.38))
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), initials, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((r-tw)/2 - bbox[0], (r-th)/2 - bbox[1]),
                  initials, fill=palette["fg"], font=font)
        img.putalpha(msk)
        img = img.resize((24, 24), Image.LANCZOS)
        av_ctk = ctk.CTkImage(img, size=(24, 24))

        row = ctk.CTkFrame(self._user_row_frame, fg_color=BG3,
                            border_width=1, border_color=BORDER,
                            corner_radius=7)
        row._is_user_row = True
        row.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(row, image=av_ctk, text="").pack(
            side="left", padx=(8, 6), pady=6)

        info = ctk.CTkFrame(row, fg_color=BG3)
        info.pack(side="left", pady=4)
        ctk.CTkLabel(info, text=nombre[:14],
                     font=("DM Sans", 10, "bold"),
                     text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Nivel {nivel}",
                     font=("DM Sans", 8),
                     text_color=TEXT_MUTED).pack(anchor="w")

    def _build_logout_btn(self):
        ctk.CTkButton(
            self._user_row_frame,
            text="  ⎋  Cerrar sesión",
            font=("DM Sans", 11),
            fg_color=ERROR_BG,
            hover_color="#2a1010",
            text_color=ERROR_COLOR,
            border_width=1,
            border_color=ERROR_BORDER,
            corner_radius=7,
            height=28,
            anchor="w",
            command=self._logout,
        ).pack(fill="x")

    # ── Área de contenido ─────────────────────────────────────────────────────

    def _build_content_area(self):
        self._content = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self._content.pack(side="left", fill="both", expand=True)
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

    def _get_or_create(self, key):
        if key not in self._content_frames:
            cls = _get_frame(key)
            frame = cls(parent=self._content, controller=self.controller)
            self._content_frames[key] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        return self._content_frames[key]

    # ── Navegación ────────────────────────────────────────────────────────────

    def navigate(self, key):
        self._active_key = key

        # Actualizar estilos del nav
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color="#0d2010", text_color=ACCENT_TEXT,
                               border_color="#132416", hover_color="#0d2010")
            else:
                btn.configure(fg_color=BG1, text_color=TEXT_MUTED,
                               border_color=BG1, hover_color=BG3)

        # Mostrar el frame — solo construye la primera vez (sin reconstruir)
        frame = self._get_or_create(key)
        frame.tkraise()

    def navigate_refresh(self, key):
        """Igual que navigate pero fuerza reconstrucción (usar tras guardar datos)."""
        if key in self._content_frames:
            self._content_frames[key].destroy()
            del self._content_frames[key]
        self.navigate(key)

    def refresh_user(self):
        """Llamar tras login para actualizar el sidebar con el usuario real."""
        self._build_user_row()
        self._build_logout_btn()

    def _logout(self):
        self.controller.current_user_id = None
        # Destruir frames de contenido para forzar recreación en próximo login
        for f in self._content_frames.values():
            f.destroy()
        self._content_frames.clear()
        self.controller.show_frame(LoginFrame)


# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zenit Vision")
        self.app_width  = 1180
        self.app_height = 750

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (self.app_width  // 2)
        y = (screen_h // 2) - (self.app_height // 2)
        self.geometry(f"{self.app_width}x{self.app_height}+{x}+{y}")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        # Firebase
        self.fb_db = FirebaseDB("firebase.json",
                                "https://zenit-vision-default-rtdb.firebaseio.com/")

        # Estado global
        self.current_user_id  = None
        self.ejercicio_actual = None

        # Contenedor maestro
        self.container = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Frames de autenticación (sin sidebar)
        for F in (LoginFrame, RegisterFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # AppShell — contiene sidebar + contenido autenticado
        self._shell = AppShell(parent=self.container, controller=self)
        self.frames[AppShell] = self._shell
        self._shell.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, page_class):
        """
        Para LoginFrame / RegisterFrame → muestra directamente.
        Para DashboardFrame / EjerciciosFrame / etc → activa AppShell
        y navega internamente.
        """
        from ui.frames.login import LoginFrame as LF
        from ui.frames.register import RegisterFrame as RF

        if page_class in (LF, RF):
            frame = self.frames[page_class]
            self.update_idletasks()
            frame.tkraise()
        else:
            # Determinar la clave de navegación
            name = page_class.__name__
            key_map = {
                "DashboardFrame":    "dashboard",
                "EjerciciosFrame":   "ejercicios",
                "EstadisticasFrame": "estadisticas",
                "ConfiguracionFrame":"configuracion",
            }
            key = key_map.get(name, "dashboard")
            self.update_idletasks()
            self._shell.tkraise()
            self._shell.navigate(key)