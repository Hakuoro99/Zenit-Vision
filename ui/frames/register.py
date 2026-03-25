import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR,
    FONT_INPUT,
    RADIUS_MD, RADIUS_PILL,
    BTN_HEIGHT, INPUT_H,
) 
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter
import os, bcrypt, base64, json, threading
from io import BytesIO
from database.google_auth import GoogleAuth
from ui.frames.terminos import TerminosModal

FIELD_W  = 340   # ancho de campos/botones (evita amontonamiento)
AVATAR_S = 56    # tamaño del avatar (más compacto)


def _make_preview_circle(size, photo_path=None):
    r = size * 2
    canvas = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    mask   = Image.new("L",    (r, r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r-1, r-1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path).convert("RGBA")
            w, h = photo.size
            s = min(w, h)
            photo = photo.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
            photo = photo.resize((r, r), Image.LANCZOS)
            canvas.paste(photo, (0, 0), mask)
        except Exception:
            _draw_placeholder(canvas, mask, r)
    else:
        _draw_placeholder(canvas, mask, r)

    border = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(border).ellipse(
        (2, 2, r-3, r-3), outline=(63, 63, 70, 200), width=3)
    canvas = Image.alpha_composite(canvas, border)
    return ctk.CTkImage(canvas.resize((size, size), Image.LANCZOS), size=(size, size))


def _draw_placeholder(canvas, mask, r):
    bg = Image.new("RGBA", (r, r), "#1f1f23")
    canvas.paste(bg, (0, 0), mask)
    draw = ImageDraw.Draw(canvas)
    cx, cy = r // 2, int(r * 0.38)
    rad = int(r * 0.20)
    draw.ellipse((cx-rad, cy-rad, cx+rad, cy+rad), fill=(80, 80, 90, 255))
    bx = int(r * 0.24)
    by = int(r * 0.60)
    draw.ellipse((bx, by, r-bx, r-bx + int(r*0.12)), fill=(80, 80, 90, 255))
    canvas.putalpha(mask)


class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller
        self.user_image_path = None
        # Estado para registro con email (para no navegar a login
        # hasta que el correo sea verificado).
        self.pending_email = None
        self.pending_user_id = None
        self.pending_user_name = None
        self.pending_remember_local = False
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Wrapper con padding — igual que login ────────────────────────────
        wrapper = ctk.CTkFrame(self, fg_color=BG_COLOR)
        wrapper.pack(fill="both", expand=True, padx=30, pady=18)

        # ── Card centrado con place — sin scroll ──────────────────────────────
        card = ctk.CTkFrame(
            wrapper,
            fg_color=BG1,
            border_width=1,
            border_color="#ffffff",
            corner_radius=20,
        )
        card.place(relx=0.5, rely=0.46, anchor="center")
        # Asegura ancho mínimo para que los widgets no se compriman.
        try:
            card.configure(width=FIELD_W + 120)
        except Exception:
            pass

        self.main_card = ctk.CTkFrame(card, fg_color="transparent")
        self.main_card.pack(padx=28, pady=(14, 16))

        # ── Título ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(self.main_card,
                     text="Crear cuenta",
                     font=("Arial Black", 20),
                     text_color=TEXT_WHITE).pack(pady=(0, 2))

        ctk.CTkLabel(self.main_card,
                     text="Únete a la comunidad de Zenit Vision",
                     font=("DM Sans", 12),
                     text_color=TEXT_GRAY).pack(pady=(0, 8))

        # ── Avatar ────────────────────────────────────────────────────────────
        av_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        av_frame.pack(pady=(0, 8))

        self.av_img = _make_preview_circle(AVATAR_S)
        self.lbl_avatar = ctk.CTkLabel(av_frame, image=self.av_img, text="")
        self.lbl_avatar.pack(pady=(0, 4))

        self.btn_photo = ctk.CTkButton(
            av_frame,
            text="⬆  Subir imagen de perfil",
            font=("DM Sans", 11),
            fg_color=BG2,
            hover_color=BG3,
            text_color=ACCENT_TEXT,
            border_width=1,
            border_color=ACCENT_GREEN,
            corner_radius=6,
            height=28,
            width=FIELD_W,
            command=self.select_image,
        )
        self.btn_photo.pack()

        # ── Nombre completo ────────────────────────────────────────────────────
        self._field_label("Nombre completo")
        self.ent_name = self._entry("Tu nombre")

        # ── Correo electrónico (nuevo) ─────────────────────────────────────────
        self._field_label("Correo electrónico")
        self.ent_email = self._entry("tucorreo@ejemplo.com")

        # ── Contraseña ────────────────────────────────────────────────────────
        self._field_label("Contraseña")
        self.f_pass1, self.ent_pass = self._password_field("Crea una contraseña")
        self.btn_eye1 = self._eye_btn(
            self.f_pass1, self.ent_pass,
            lambda: self.toggle_p(self.ent_pass, self.btn_eye1))

        # ── Confirmar contraseña ──────────────────────────────────────────────
        self._field_label("Confirmar contraseña")
        self.f_pass2, self.ent_pass_conf = self._password_field("Repite tu contraseña")
        self.btn_eye2 = self._eye_btn(
            self.f_pass2, self.ent_pass_conf,
            lambda: self.toggle_p(self.ent_pass_conf, self.btn_eye2))

        # ── Checkboxes ────────────────────────────────────────────────────────
        ck_wrap = ctk.CTkFrame(self.main_card, fg_color="transparent")
        ck_wrap.pack(fill="x", pady=(8, 0))

        # Términos y condiciones
        terms_row = ctk.CTkFrame(ck_wrap, fg_color="transparent")
        terms_row.pack(anchor="w", pady=(0, 4))

        self.check_terms = ctk.CTkCheckBox(
            terms_row, text="",
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            border_color=BORDER2, checkmark_color="#071a0e",
            corner_radius=3, width=20, height=20,
        )
        self.check_terms.pack(side="left")
        # Bloqueamos el checkbox para que solo pueda marcarse
        # al aceptar los términos desde el modal.
        try:
            self.check_terms.configure(state="disabled")
        except Exception:
            pass

        ctk.CTkLabel(terms_row,
                     text="Aceptar ",
                     font=("DM Sans", 12),
                     text_color=TEXT_GRAY).pack(side="left")

        ctk.CTkButton(
            terms_row,
            text="términos y condiciones",
            font=("DM Sans", 12, "bold"),
            fg_color=BG1, hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=0, height=20,
            cursor="hand2",
            command=self.abrir_terminos,
        ).pack(side="left")

        # Mantener sesión
        self.check_remember = ctk.CTkCheckBox(
            ck_wrap,
            text="Mantener sesión iniciada",
            font=("DM Sans", 12),
            text_color=TEXT_GRAY,
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            border_color=BORDER2, checkmark_color="#071a0e",
            corner_radius=3, height=20,
        )
        self.check_remember.pack(anchor="w", pady=(0, 4))

        # ── Error label ───────────────────────────────────────────────────────
        self.lbl_error = ctk.CTkLabel(
            self.main_card, text="",
            font=("DM Sans", 12),
            text_color=ERROR_COLOR,
            wraplength=FIELD_W)
        self.lbl_error.pack(pady=(4, 0))

        # ── Botón Crear cuenta ────────────────────────────────────────────────
        ctk.CTkButton(
            self.main_card,
            text="→  Crear cuenta",
            font=("Arial Black", 12),
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            text_color="#071a0e",
            corner_radius=RADIUS_MD,
            height=36, width=FIELD_W,
            command=self.register_user,
        ).pack(pady=(8, 4))

        # Botón de verificación de correo (solo se muestra si registras con email).
        self.btn_verify_email = ctk.CTkButton(
            self.main_card,
            text="✓ Verificar correo",
            font=("DM Sans", 12, "bold"),
            fg_color=BG1, hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_MD,
            height=34, width=FIELD_W,
            command=self.verify_email_now,
        )

        # ── Divisor ───────────────────────────────────────────────────────────
        div = ctk.CTkFrame(self.main_card, fg_color="transparent")
        div.pack(fill="x", pady=(3, 4))
        ctk.CTkFrame(div, fg_color=BORDER2, height=1).pack(
            side="left", fill="x", expand=True)
        ctk.CTkLabel(div, text="  o continúa con  ",
                     font=("DM Sans", 11), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkFrame(div, fg_color=BORDER2, height=1).pack(
            side="left", fill="x", expand=True)

        # ── Botón Google ──────────────────────────────────────────────────────
        self.btn_google = ctk.CTkButton(
            self.main_card,
            text="G   Iniciar sesión con Google",
            font=("DM Sans", 12, "bold"),
            fg_color=BG2, hover_color=BG3,
            text_color=TEXT_WHITE,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_MD,
            height=36, width=FIELD_W,
            command=self.start_google_thread,
        )
        self.btn_google.pack(pady=(4, 8))

        # ── ¿Ya tienes cuenta? ────────────────────────────────────────────────
        back_row = ctk.CTkFrame(self.main_card, fg_color="transparent")
        back_row.pack(pady=(0, 0))

        ctk.CTkLabel(back_row, text="¿Ya tienes cuenta? ",
                     font=("DM Sans", 12),
                     text_color=TEXT_MUTED).pack(side="left")

        ctk.CTkButton(
            back_row,
            text="Iniciar sesión",
            font=("DM Sans", 12, "bold"),
            fg_color=BG1, hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=0, height=24,
            command=self.go_back_login,
        ).pack(side="left")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _field_label(self, text):
        ctk.CTkLabel(
            self.main_card, text=text.upper(),
            font=("DM Sans", 9), text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(5, 1))

    def _entry(self, placeholder):
        wrap = ctk.CTkFrame(self.main_card, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=7, height=32)
        wrap.pack(fill="x")
        wrap.pack_propagate(False)
        entry = ctk.CTkEntry(
            wrap, placeholder_text=placeholder,
            font=("DM Sans", 11), fg_color="transparent",
            border_width=0, text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED, height=32)
        entry.pack(fill="x", padx=10, expand=True)
        entry.bind("<FocusIn>",  lambda e: wrap.configure(border_color=BORDER2))
        entry.bind("<FocusOut>", lambda e: wrap.configure(border_color=BORDER))
        return entry

    def _password_field(self, placeholder):
        wrap = ctk.CTkFrame(self.main_card, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=7, height=32)
        wrap.pack(fill="x")
        wrap.pack_propagate(False)
        entry = ctk.CTkEntry(
            wrap, placeholder_text=placeholder, show="*",
            font=("DM Sans", 11), fg_color="transparent",
            border_width=0, text_color=TEXT_WHITE,
            placeholder_text_color=TEXT_MUTED, height=32)
        entry.pack(side="left", fill="x", padx=(10, 0), expand=True)
        entry.bind("<FocusIn>",  lambda e: wrap.configure(border_color=BORDER2))
        entry.bind("<FocusOut>", lambda e: wrap.configure(border_color=BORDER))
        return wrap, entry

    def _eye_btn(self, parent, entry, command):
        btn = ctk.CTkButton(
            parent, text="👁", font=("DM Sans", 13),
            width=28, height=32,
            fg_color=BG2, hover_color=BG3,
            text_color=TEXT_MUTED, border_width=0,
            command=command)
        btn.pack(side="right", padx=4)
        return btn

    # ── Términos y condiciones — listo para conectar ───────────────────────────
    def abrir_terminos(self):
        TerminosModal(
            parent=self.winfo_toplevel(),
            callback_aceptar=self.on_terminos_aceptados
        )

    def on_terminos_aceptados(self):
        self.terminos_aceptados = True
        try:
            # Permite marcarlo aunque esté deshabilitado en la UI.
            self.check_terms.configure(state="normal")
        except Exception:
            pass
        self.check_terms.select()
        try:
            self.check_terms.configure(state="disabled")
        except Exception:
            pass
        
    # ── Lógica original sin cambios ────────────────────────────────────────────

    def clean_form(self):
        self.ent_name.delete(0, 'end')
        self.ent_email.delete(0, 'end')
        self.ent_pass.delete(0, 'end')
        self.ent_pass_conf.delete(0, 'end')
        self.ent_pass.configure(show="*")
        self.ent_pass_conf.configure(show="*")
        self.btn_eye1.configure(text="👁")
        self.btn_eye2.configure(text="👁")
        self.user_image_path = None
        self.lbl_avatar.configure(image=_make_preview_circle(AVATAR_S))
        self.check_remember.deselect()
        self.check_terms.deselect()
        self.lbl_error.configure(text="")
        self.btn_google.configure(state="normal", text="G   Iniciar sesión con Google")
        # Ocultar botón de verificación si estaba visible.
        try:
            self.btn_verify_email.pack_forget()
        except Exception:
            pass
        self.pending_email = None
        self.pending_user_id = None
        self.pending_user_name = None
        self.pending_remember_local = False

    def tkraise(self, *args, **kwargs):
        self.clean_form()
        super().tkraise(*args, **kwargs)

    def go_back_login(self):
        from ui.frames.login import LoginFrame
        self.controller.show_frame(LoginFrame)

    def register_user(self):
        # ── LÓGICA ORIGINAL (manual) + flujo nuevo (email verificación) ─────
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        pw   = self.ent_pass.get()
        pw_c = self.ent_pass_conf.get()

        # Validación de términos (bloquea la creación si no se aceptan).
        if self.check_terms.get() != 1:
            self.lbl_error.configure(
                text="❌ Debes aceptar los términos y condiciones para continuar.",
                text_color=ERROR_COLOR,
            )
            return

        # Si ya hay un registro con email en espera, evita duplicarlo.
        if self.pending_email and self.pending_user_id:
            if email:
                self.lbl_error.configure(
                    text="❌ Ya existe un registro pendiente. Verifica tu correo antes de crear otra cuenta.",
                    text_color=ERROR_COLOR)
                return
            # Si el usuario decide hacer registro manual, limpiamos el estado
            # previo del flujo de email.
            try:
                self.btn_verify_email.pack_forget()
            except Exception:
                pass
            self.pending_email = None
            self.pending_user_id = None
            self.pending_user_name = None
            self.pending_remember_local = False

        # Validación básica de campos
        if not name or not pw or not pw_c:
            self.lbl_error.configure(
                text="❌ Por favor llena todos los campos",
                text_color=ERROR_COLOR)
            return
        if pw != pw_c:
            self.lbl_error.configure(
                text="❌ Las contraseñas no coinciden",
                text_color=ERROR_COLOR)
            return

        if email and ("@" not in email or "." not in email):
            self.lbl_error.configure(
                text="❌ Ingresa un correo válido",
                text_color=ERROR_COLOR)
            return

        img_b64 = ""
        try:
            if self.user_image_path:
                with Image.open(self.user_image_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((150, 150))
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            import bcrypt
            hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = name.lower().replace(" ", "_")

            # ---------------------- Flujo nuevo: email + verificación ----------------------
            if email:
                from database import firebase_auth as fb_auth

                # 1) Crear en Firebase Auth (si ya existe el usuario, no fallamos:
                # solo reenviamos el correo de verificación).
                fb_uid = None
                try:
                    fb_uid = fb_auth.create_user_with_email_and_password(email, pw)
                except Exception:
                    fb_uid = None

                # 2) Enviar el correo de verificación a la bandeja del usuario
                fb_auth.send_verification_email(email, pw)

                # 3) Guardar usuario en Realtime DB (igual que antes, pero con email).
                # Si el registro ya existía, no sobrescribimos la contraseña hasheada.
                existing = self.controller.fb_db.read_record(f"users/{user_id}")
                if existing:
                    update_data = {
                        "email": email,
                        "auth_provider": "email",
                        "email_verified": False,
                    }
                    if fb_uid:
                        update_data["firebase_uid"] = fb_uid
                    if img_b64:
                        update_data["imagen_data"] = img_b64
                    self.controller.fb_db.update_record(f"users/{user_id}", update_data)
                else:
                    data = {
                        "nombre": name,
                        "email": email,
                        "password": hashed_pw,
                        "imagen_data": img_b64,
                        "auth_provider": "email",
                        "email_verified": False,
                        "firebase_uid": fb_uid or "",
                        "puntos": 0,
                        "nivel": 1,
                    }
                    self.controller.fb_db.write_record(f"users/{user_id}", data)

                # 4) No guardamos el perfil local ni llevamos a login hasta que
                # el usuario verifique el correo desde su bandeja.
                valor_remember = True if self.check_remember.get() == 1 else False
                self.pending_email = email
                self.pending_user_id = user_id
                self.pending_user_name = name
                self.pending_remember_local = valor_remember

                self.lbl_error.configure(
                    text=f"✅ Correo enviado a {email}. "
                         "Abre el correo y confirma tu cuenta. "
                         "Luego vuelve a esta pantalla y presiona \"Verificar correo\".",
                    text_color=ACCENT_TEXT,
                )
                self.btn_verify_email.pack(pady=(0, 4))
                return

            # ---------------------- Flujo original: manual ----------------------
            data = {
                "nombre": name, "password": hashed_pw,
                "imagen_data": img_b64, "auth_provider": "manual",
                "puntos": 0, "nivel": 1,
            }
            self.controller.fb_db.write_record(f"users/{user_id}", data)

            valor_remember = True if self.check_remember.get() == 1 else False
            self.save_local_profile(user_id, name, valor_remember)

            from ui.frames.login import LoginFrame
            self.lbl_error.configure(
                text="✅ Perfil creado correctamente. Inicia sesión.",
                text_color=ACCENT_TEXT,
            )
            self.controller.frames[LoginFrame].necesita_actualizar = True
            self.after(800, lambda: self.controller.show_frame(LoginFrame))

        except Exception as e:
            self.lbl_error.configure(text=f"Error técnico: {e}", text_color=ERROR_COLOR)

    def verify_email_now(self):
        """Comprueba si el email ya fue verificado en Firebase Auth."""
        if not self.pending_email or not self.pending_user_id:
            self.lbl_error.configure(
                text="❌ No hay un registro pendiente para verificar.",
                text_color=ERROR_COLOR)
            return

        self.lbl_error.configure(text="Verificando correo...", text_color=TEXT_GRAY)
        pending_email = self.pending_email
        pending_user_id = self.pending_user_id
        pending_user_name = self.pending_user_name
        pending_remember = self.pending_remember_local

        def worker():
            try:
                from database import firebase_auth as fb_auth
                verified = fb_auth.is_email_verified(pending_email)
                if verified:
                    # Actualizamos el estado en la nube para futuras validaciones.
                    try:
                        self.controller.fb_db.update_record(
                            f"users/{pending_user_id}",
                            {"email_verified": True},
                        )
                    except Exception:
                        pass
                self.after(0, lambda: self._on_email_verified_result(
                    verified=verified,
                    pending_user_id=pending_user_id,
                    pending_user_name=pending_user_name,
                    pending_remember=pending_remember,
                ))
            except Exception as e:
                self.after(0, lambda: self.lbl_error.configure(
                    text=f"Error al verificar correo: {e}",
                    text_color=ERROR_COLOR))

        threading.Thread(target=worker, daemon=True).start()

    def _on_email_verified_result(self, verified: bool, pending_user_id: str,
                                    pending_user_name: str, pending_remember: bool):
        if not verified:
            self.lbl_error.configure(
                text="Aún no aparece verificado. "
                     "Verifica tu correo y vuelve a intentarlo.",
                text_color=ERROR_COLOR)
            return

        self.lbl_error.configure(
            text="✓ Correo verificado correctamente. Iniciando sesión...",
            text_color=ACCENT_TEXT)

        # Ahora sí guardamos el perfil local y llevamos al login.
        try:
            self.save_local_profile(pending_user_id, pending_user_name, pending_remember)
        except Exception:
            # Si falla guardar local, igual enviamos al login.
            pass

        from ui.frames.login import LoginFrame
        self.controller.frames[LoginFrame].necesita_actualizar = True
        self.controller.show_frame(LoginFrame)

    def start_google_thread(self):
        # ── Validación de términos (antes de iniciar Google) ───────────────────
        if self.check_terms.get() != 1:
            self.lbl_error.configure(
                text="❌ Debes aceptar los términos y condiciones para continuar.",
                text_color=ERROR_COLOR,
            )
            return

        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        self.btn_google.configure(state="disabled", text="Revisa tu navegador...")
        threading.Thread(target=self._google_logic, daemon=True).start()

    def _google_logic(self):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        auth = GoogleAuth("google_secrets.json")
        user_info = auth.login()
        if user_info:
            self.after(0, lambda: self._finalize_google(user_info))
        else:
            self.after(0, lambda: self.btn_google.configure(
                state="normal", text="G   Iniciar sesión con Google"))

    def _finalize_google(self, user_info):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        try:
            user_id = user_info['email'].replace(".", "_").replace("@", "_")
            data = {
                "nombre": user_info['name'], "email": user_info['email'],
                "imagen_url": user_info.get('picture', ""),
                "auth_provider": "google", "puntos": 0, "nivel": 1,
            }
            self.controller.fb_db.write_record(f"users/{user_id}", data)
            self.save_local_profile(user_id, user_info['name'], True)

            from ui.frames.login import LoginFrame
            self.controller.frames[LoginFrame].necesita_actualizar = True

            from ui.frames.dashboard import DashboardFrame
            self.lbl_error.configure(
                text="✅ Perfil creado correctamente con Google.",
                text_color=ACCENT_TEXT,
            )
            self.after(800, lambda: self.controller.show_frame(DashboardFrame))

        except Exception as e:
            self.lbl_error.configure(
                text=f"Error al finalizar sesión Google: {e}",
                text_color=ERROR_COLOR)
            self.btn_google.configure(state="normal", text="G   Iniciar sesión con Google")

    def toggle_p(self, entry, button):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        if entry.cget("show") == "*":
            entry.configure(show="")
            button.configure(text="🔒")
        else:
            entry.configure(show="*")
            button.configure(text="👁")

    def select_image(self):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png")])
        if path:
            self.user_image_path = path
            self.lbl_avatar.configure(image=_make_preview_circle(AVATAR_S, path))
            self.lbl_error.configure(
                text="✅ Imagen seleccionada correctamente",
                text_color=ACCENT_TEXT)

    def save_local_profile(self, user_id, name, valor_remember):
        # ── LÓGICA ORIGINAL SIN CAMBIOS ───────────────────────────────────────
        profiles = {}
        if os.path.exists("local_profiles.json"):
            with open("local_profiles.json", "r") as f:
                try:    profiles = json.load(f)
                except: profiles = {}

        profiles[user_id] = {"nombre": name, "remember": valor_remember}

        with open("local_profiles.json", "w") as f:
            json.dump(profiles, f)

        from ui.frames.login import LoginFrame
        self.controller.frames[LoginFrame].necesita_actualizar = True