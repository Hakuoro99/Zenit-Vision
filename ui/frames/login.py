import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR, ERROR_BG, ERROR_BORDER,
    AVATAR_PALETTE,
    FONT_LOGO, FONT_SLOGAN, FONT_LABEL, FONT_REGULAR,
    FONT_INPUT, FONT_SMALL, FONT_TINY,
    RADIUS_MD, RADIUS_LG, RADIUS_PILL,
    BTN_HEIGHT, INPUT_H,
)
import json, os, base64, requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AVATAR_SIZE   = 86
AVATAR_RENDER = AVATAR_SIZE * 3


def _make_circle_avatar(size, bg, fg, initials, photo=None):
    r = AVATAR_RENDER
    base = Image.new("RGBA", (r, r), (0, 0, 0, 0))

    if photo:
        w, h = photo.size
        s = min(w, h)
        photo = photo.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
        photo = photo.convert("RGBA").resize((r, r), Image.LANCZOS)
        img_layer = photo
    else:
        img_layer = Image.new("RGBA", (r, r), bg)
        draw = ImageDraw.Draw(img_layer)
        try:
            font = ImageFont.truetype("arial.ttf", int(r * 0.32))
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), initials, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((r-tw)/2 - bbox[0], (r-th)/2 - bbox[1]),
                  initials, fill=fg, font=font)

    mask = Image.new("L", (r, r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r-1, r-1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.5))
    base.paste(img_layer, (0, 0), mask)

    border_layer = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(border_layer).ellipse(
        (2, 2, r-3, r-3), outline=(255, 255, 255, 50), width=4)
    base = Image.alpha_composite(base, border_layer)
    base = base.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(base, size=(size, size))


def _make_green_hover(size):
    r = size * 2
    img = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse((0, 0, r-1, r-1), fill=(45, 106, 74, 90))
    img = img.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(img, size=(size, size))


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller
        self.local_users_file = "local_profiles.json"
        self.necesita_actualizar = True
        self._hover_imgs = {}
        self.render_ui()

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        if self.necesita_actualizar:
            self.render_ui()
            self.necesita_actualizar = False

    def render_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._hover_imgs.clear()

        # ── Wrapper con padding en los 4 lados → card nunca toca el borde ─────
        wrapper = ctk.CTkFrame(self, fg_color=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=30, pady=30)

        # ── Card con borde BLANCO redondeado ──────────────────────────────────
        border_card = ctk.CTkFrame(
            wrapper,
            fg_color=BG1,
            border_width=1,
            border_color="#ffffff",   # borde blanco
            corner_radius=20,
        )
        border_card.place(relx=0.5, rely=0.5, anchor="center")

        # Contenido del card — padding compacto para que todo quepa
        self.main_card = ctk.CTkFrame(border_card, fg_color="transparent")
        self.main_card.pack(padx=40, pady=(24, 28))

        # ── Logo proporcional ─────────────────────────────────────────────────
        logo_path = os.path.join("assets", "icon", "Zenit_Vision_Logo.png")
        if os.path.exists(logo_path):
            try:
                pil_logo = Image.open(logo_path).convert("RGBA")
                ow, oh = pil_logo.size
                tw = 130          # ancho fijo — más compacto
                th = int(oh * tw / ow)
                logo_ctk = ctk.CTkImage(pil_logo, size=(tw, th))
                ctk.CTkLabel(
                    self.main_card, image=logo_ctk, text=""
                ).pack(pady=(0, 6))
            except Exception:
                pass

        # ── Título ────────────────────────────────────────────────────────────
        logo_row = ctk.CTkFrame(self.main_card, fg_color="transparent")
        logo_row.pack(pady=(0, 4))
        ctk.CTkLabel(logo_row, text="ZENIT ",
                     font=("Arial Black", 28),
                     text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(logo_row, text="VISION",
                     font=("Arial Black", 28),
                     text_color=ACCENT_TEXT).pack(side="left")

        # ── Subtítulo ─────────────────────────────────────────────────────────
        ctk.CTkLabel(self.main_card,
                     text="¿Quién está entrenando hoy?",
                     font=("DM Sans", 13),
                     text_color=TEXT_GRAY).pack(pady=(0, 14))

        # ── Grid de perfiles ──────────────────────────────────────────────────
        self.profiles_container = ctk.CTkFrame(
            self.main_card, fg_color="transparent")
        self.profiles_container.pack()
        self.load_local_profiles()

        # ── Divisor ───────────────────────────────────────────────────────────
        div_row = ctk.CTkFrame(self.main_card, fg_color="transparent")
        div_row.pack(pady=(18, 8))
        ctk.CTkFrame(div_row, fg_color=BORDER2,
                     height=1, width=90).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(div_row,
                     text="¿No tienes cuenta?",
                     font=("DM Sans", 12),
                     text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkFrame(div_row, fg_color=BORDER2,
                     height=1, width=90).pack(side="left", padx=(8, 0))

        # ── Botón registro ────────────────────────────────────────────────────
        reg_btn = ctk.CTkButton(
            self.main_card,
            text="Registrarse ahora",
            fg_color="transparent",
            hover_color=ACCENT_GREEN,
            text_color=TEXT_WHITE,
            font=("DM Sans", 13, "bold"),
            border_width=2,
            border_color=ACCENT_TEXT,
            corner_radius=RADIUS_PILL,
            width=230, height=38,
            command=self.go_to_register,
        )
        reg_btn.pack()
        reg_btn.bind("<Enter>", lambda e: reg_btn.configure(
            fg_color=ACCENT_GREEN, text_color="#071a0e"))
        reg_btn.bind("<Leave>", lambda e: reg_btn.configure(
            fg_color="transparent", text_color=TEXT_WHITE))

    # ── Cargar perfiles ────────────────────────────────────────────────────────
    def load_local_profiles(self):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        if os.path.exists(self.local_users_file):
            with open(self.local_users_file, "r") as f:
                try:
                    users = json.load(f)
                except Exception:
                    users = {}

                for c in range(3):
                    self.profiles_container.grid_columnconfigure(c, weight=1)

                i = 0
                for user_id, local_info in users.items():
                    cloud_data = self.controller.fb_db.read_record(
                        f"users/{user_id}")
                    if cloud_data:
                        row = i // 3
                        col = i % 3
                        self.create_profile_card(
                            user_id, cloud_data,
                            local_info.get("remember", False),
                            row, col, i)
                        i += 1

    def create_profile_card(self, user_id, data, remember, row, col, idx=0):
        # ── LÓGICA ORIGINAL + estilo ──────────────────────────────────────────
        CELL_W, CELL_H = 120, 136   # más compacto
        container = ctk.CTkFrame(
            self.profiles_container,
            fg_color="transparent",
            width=CELL_W, height=CELL_H)
        container.grid(row=row, column=col, padx=10, pady=8)
        container.grid_propagate(False)

        palette  = AVATAR_PALETTE[idx % len(AVATAR_PALETTE)]
        nombre   = data.get("nombre", user_id)
        initials = ("".join(p[0].upper() for p in nombre.split()[:2])
                    or nombre[:2].upper())

        photo_pil = None
        if data.get("imagen_url"):
            try:
                res = requests.get(data["imagen_url"], timeout=3)
                photo_pil = Image.open(BytesIO(res.content))
            except Exception:
                pass
        elif data.get("imagen_data"):
            try:
                photo_pil = Image.open(
                    BytesIO(base64.b64decode(data["imagen_data"])))
            except Exception:
                pass

        img_normal = _make_circle_avatar(
            AVATAR_SIZE, palette["bg"], palette["fg"], initials, photo_pil)
        img_hover  = _make_green_hover(AVATAR_SIZE)
        self._hover_imgs[user_id] = (img_normal, img_hover)

        btn = ctk.CTkButton(
            container,
            text="", image=img_normal,
            width=AVATAR_SIZE, height=AVATAR_SIZE,
            corner_radius=AVATAR_SIZE // 2,
            fg_color="transparent",
            hover_color=BG1,
            border_width=0,
            command=lambda: self.access(user_id, remember),
        )
        btn.place(relx=0.5, rely=0.35, anchor="center")

        lbl = ctk.CTkLabel(
            container, text=nombre,
            font=("DM Sans", 11), text_color=TEXT_GRAY,
            wraplength=CELL_W - 8, justify="center")
        lbl.place(relx=0.5, rely=0.83, anchor="center")

        def on_enter(e, b=btn, uid=user_id):
            imgs = self._hover_imgs.get(uid)
            if not imgs:
                return
            combined = Image.alpha_composite(
                imgs[0]._light_image.copy(),
                imgs[1]._light_image.copy())
            b.configure(image=ctk.CTkImage(
                combined, size=(AVATAR_SIZE, AVATAR_SIZE)))

        def on_leave(e, b=btn, uid=user_id):
            imgs = self._hover_imgs.get(uid)
            if imgs:
                b.configure(image=imgs[0])

        for w in (btn, container, lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    # ── Lógica original ────────────────────────────────────────────────────────
    def access(self, user_id, remember_local):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        user_data = self.controller.fb_db.read_record(f"users/{user_id}")
        if not user_data:
            return
        if user_data.get("auth_provider") == "google":
            self.go_to_dashboard()
            return
        # Para cuentas registradas con email/contraseña:
        # si el correo no está verificado, forzamos validación de contraseña
        # y bloqueamos el acceso hasta que `email_verified` sea True.
        if user_data.get("auth_provider") == "email":
            email = user_data.get("email")
            from database import firebase_auth as fb_auth
            try:
                if not email or not fb_auth.is_email_verified(email):
                    self.ask_password(user_id)
                    return
            except Exception:
                # Si no podemos comprobar la verificación, NO dejamos entrar.
                self.ask_password(user_id)
                return
        if remember_local == True:
            print(f"Entrando directo a {user_id} por sesión recordada.")
            self.go_to_dashboard()
        else:
            print(f"Solicitando contraseña para {user_id}.")
            self.ask_password(user_id)

    def _center_window(self, win, w, h):
        """Centra una ventana hija sobre la ventana principal."""
        win.update_idletasks()
        parent = self.winfo_toplevel()
        px = parent.winfo_x() + parent.winfo_width()  // 2
        py = parent.winfo_y() + parent.winfo_height() // 2
        win.geometry(f"{w}x{h}+{px - w//2}+{py - h//2}")

    def ask_password(self, user_id):
        # ── LÓGICA ORIGINAL + estilo ──────────────────────────────────────────
        self.pw_window = ctk.CTkToplevel(self)
        self.pw_window.title("Seguridad Zenit")
        self.pw_window.configure(fg_color=BG1)
        self.pw_window.resizable(False, False)
        self.pw_window.attributes("-topmost", True)
        self.pw_window.grab_set()
        self._center_window(self.pw_window, 380, 310)

        outer = ctk.CTkFrame(
            self.pw_window, fg_color=BG1,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_LG)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(outer, text="VALIDACIÓN DE IDENTIDAD",
                     font=("Arial Black", 13),
                     text_color=TEXT_WHITE).pack(pady=(24, 4))
        ctk.CTkLabel(outer, text="Introduce tu contraseña para continuar",
                     font=("DM Sans", 11),
                     text_color=TEXT_GRAY).pack(pady=(0, 14))

        pw_wrap = ctk.CTkFrame(
            outer, fg_color=BG2,
            corner_radius=RADIUS_MD,
            border_width=1, border_color=BORDER2)
        pw_wrap.pack(padx=28, fill="x")

        self.entry_pw = ctk.CTkEntry(
            pw_wrap, show="*",
            placeholder_text="Tu contraseña",
            font=FONT_INPUT,
            fg_color="transparent", border_width=0,
            text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED,
            height=INPUT_H)
        self.entry_pw.pack(fill="x", padx=8)
        self.entry_pw.focus()

        self.lbl_pw_error = ctk.CTkLabel(
            outer, text="",
            text_color=ERROR_COLOR,
            font=("DM Sans", 11))
        self.lbl_pw_error.pack(pady=(6, 0))

        def verify():
            # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────
            pw_input = self.entry_pw.get()
            user_data = self.controller.fb_db.read_record(f"users/{user_id}")
            import bcrypt
            try:
                stored_hash = user_data['password'].encode('utf-8')
                if bcrypt.checkpw(pw_input.encode('utf-8'), stored_hash):
                    print("Contraseña correcta.")
                    # Bloqueo hasta verificación de email
                    if user_data.get("auth_provider") == "email":
                        try:
                            email = user_data.get("email")
                            from database import firebase_auth as fb_auth
                            if email and not fb_auth.is_email_verified(email):
                                self.lbl_pw_error.configure(
                                    text="Verifica tu correo desde el email para poder entrar."
                                )
                                pw_wrap.configure(border_color=ERROR_COLOR)
                                return
                        except Exception:
                            self.lbl_pw_error.configure(
                                text="No se pudo confirmar la verificación del correo."
                            )
                            pw_wrap.configure(border_color=ERROR_COLOR)
                            return
                    self.pw_window.destroy()
                    self.go_to_dashboard()
                else:
                    self.lbl_pw_error.configure(text="Contraseña incorrecta")
                    pw_wrap.configure(border_color=ERROR_COLOR)
            except Exception as e:
                print(f"Error al validar contraseña: {e}")
                self.lbl_pw_error.configure(text="Error técnico de validación")

        ctk.CTkButton(
            outer, text="Entrar",
            font=("DM Sans", 13, "bold"),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            text_color="#071a0e",
            corner_radius=RADIUS_MD, height=BTN_HEIGHT,
            command=verify,
        ).pack(padx=28, pady=(12, 6), fill="x")

        self.entry_pw.bind("<Return>", lambda e: verify())

        # Recuperar contraseña
        rec_btn = ctk.CTkButton(
            outer,
            text="¿Olvidaste tu contraseña?",
            font=("DM Sans", 11),
            fg_color="transparent",
            hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=0,
            height=28,
            command=lambda: self._recover_password(user_id),
        )
        rec_btn.pack(pady=(0, 16))

    def _recover_password(self, user_id):
        """Ventana para recuperar contraseña vía correo."""
        try:
            self.pw_window.destroy()
        except Exception:
            pass

        rec_win = ctk.CTkToplevel(self)
        rec_win.title("Recuperar contraseña")
        rec_win.configure(fg_color=BG1)
        rec_win.resizable(False, False)
        rec_win.attributes("-topmost", True)
        rec_win.grab_set()
        self._center_window(rec_win, 400, 280)

        outer = ctk.CTkFrame(
            rec_win, fg_color=BG1,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_LG)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(outer, text="RECUPERAR CONTRASEÑA",
                     font=("Arial Black", 13),
                     text_color=TEXT_WHITE).pack(pady=(24, 4))
        ctk.CTkLabel(outer,
                     text="Ingresa el correo asociado a tu cuenta.\nTe enviaremos instrucciones para restablecerla.",
                     font=("DM Sans", 11),
                     text_color=TEXT_GRAY,
                     justify="center").pack(pady=(0, 16))

        email_wrap = ctk.CTkFrame(
            outer, fg_color=BG2,
            corner_radius=RADIUS_MD,
            border_width=1, border_color=BORDER2)
        email_wrap.pack(padx=28, fill="x")

        entry_email = ctk.CTkEntry(
            email_wrap,
            placeholder_text="tucorreo@ejemplo.com",
            font=FONT_INPUT,
            fg_color="transparent", border_width=0,
            text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED,
            height=INPUT_H)
        entry_email.pack(fill="x", padx=8)
        entry_email.focus()

        # Pre-rellenar con email si existe
        user_data = self.controller.fb_db.read_record(f"users/{user_id}")
        if user_data and user_data.get("email"):
            entry_email.insert(0, user_data["email"])

        lbl_status = ctk.CTkLabel(
            outer, text="",
            font=("DM Sans", 11),
            text_color=ACCENT_TEXT)
        lbl_status.pack(pady=(8, 0))

        def send_recovery():
            email = entry_email.get().strip()
            if not email:
                lbl_status.configure(
                    text="Ingresa un correo válido",
                    text_color=ERROR_COLOR)
                return
            try:
                self.controller.fb_db.send_password_reset(email)
                lbl_status.configure(
                    text=f"✓ Correo enviado a {email}",
                    text_color=ACCENT_TEXT)
                rec_win.after(2500, rec_win.destroy)
            except Exception as e:
                print(f"Error al enviar recuperación: {e}")
                lbl_status.configure(
                    text="Error al enviar. Verifica el correo.",
                    text_color=ERROR_COLOR)

        ctk.CTkButton(
            outer,
            text="Enviar instrucciones",
            font=("DM Sans", 13, "bold"),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            text_color="#071a0e",
            corner_radius=RADIUS_MD, height=BTN_HEIGHT,
            command=send_recovery,
        ).pack(padx=28, pady=(10, 20), fill="x")

        entry_email.bind("<Return>", lambda e: send_recovery())

    def go_to_dashboard(self):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        from ui.frames.dashboard import DashboardFrame
        self.controller.show_frame(DashboardFrame)

    def go_to_register(self):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        from ui.frames.register import RegisterFrame
        self.controller.show_frame(RegisterFrame)