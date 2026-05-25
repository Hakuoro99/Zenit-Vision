import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR, RADIUS_MD,
)
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter
import os, base64, json, threading
from io import BytesIO
from database.google_auth import GoogleAuth
from ui.frames.terminos import TerminosModal

FIELD_W  = 310
AVATAR_S = 64


# ── Helpers de imagen ─────────────────────────────────────────────────────────

def _make_preview_circle(size, photo_path=None):
    r = size * 2
    canvas = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    mask   = Image.new("L",    (r, r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r-1, r-1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path).convert("RGBA")
            w, h  = photo.size
            s     = min(w, h)
            photo = photo.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
            photo = photo.resize((r, r), Image.LANCZOS)
            canvas.paste(photo, (0, 0), mask)
        except Exception:
            _placeholder(canvas, mask, r)
    else:
        _placeholder(canvas, mask, r)

    brd = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(brd).ellipse((2, 2, r-3, r-3), outline=(63,63,70,200), width=3)
    canvas = Image.alpha_composite(canvas, brd)
    return ctk.CTkImage(canvas.resize((size, size), Image.LANCZOS), size=(size, size))


def _placeholder(canvas, mask, r):
    bg = Image.new("RGBA", (r, r), "#1f1f23")
    canvas.paste(bg, (0, 0), mask)
    d  = ImageDraw.Draw(canvas)
    cx, cy, rad = r//2, int(r*.38), int(r*.20)
    d.ellipse((cx-rad, cy-rad, cx+rad, cy+rad), fill=(80,80,90,255))
    bx = int(r*.24)
    d.ellipse((bx, int(r*.60), r-bx, r-bx+int(r*.12)), fill=(80,80,90,255))
    canvas.putalpha(mask)


# ══════════════════════════════════════════════════════════════════════════════

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller          = controller
        self.user_image_path     = None
        self.terminos_aceptados  = False
        self.pending_email       = None
        self.pending_user_id     = None
        self.pending_user_name   = None
        self.pending_remember    = False
        self._build_ui()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # ── Misma estructura que el login ────────────────────────────────────
        # Mismo patrón que login — fondo ocupa todo, card flotante centrado
        self.configure(fg_color=BG_COLOR)

        card = ctk.CTkFrame(
            self,
            fg_color=BG1,
            border_width=1,
            border_color="#ffffff",
            corner_radius=20,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        m = ctk.CTkFrame(card, fg_color="transparent")
        m.pack(padx=26, pady=(16, 18))
        self.m = m

        # ── Título ────────────────────────────────────────────────────────────
        ctk.CTkLabel(m, text="Crear cuenta",
                     font=("Arial Black", 20), text_color=TEXT_WHITE).pack(pady=(0,2))
        ctk.CTkLabel(m, text="Únete a la comunidad de Zenit Vision",
                     font=("DM Sans", 12), text_color=TEXT_GRAY).pack(pady=(0,10))

        # ── Avatar centrado con botón pequeño superpuesto ────────────────────
        av_wrap = ctk.CTkFrame(m, fg_color="transparent")
        av_wrap.pack(pady=(0, 10))

        # Icono centrado
        self.av_img = _make_preview_circle(AVATAR_S)
        self.lbl_av = ctk.CTkLabel(av_wrap, image=self.av_img, text="",
                                    cursor="hand2")
        self.lbl_av.pack(anchor="center")
        self.lbl_av.bind("<Button-1>", lambda e: self.select_image())

        # Botón pequeño debajo del icono, centrado
        self.btn_photo = ctk.CTkButton(
            av_wrap, text="⬆  Subir foto",
            font=("DM Sans", 10),
            fg_color=BG2, hover_color=BG3,
            text_color=ACCENT_TEXT,
            border_width=1, border_color=ACCENT_GREEN,
            corner_radius=5, height=22, width=100,
            command=self.select_image)
        self.btn_photo.pack(anchor="center", pady=(4, 0))

        # ── Campos ────────────────────────────────────────────────────────────
        self._label("Nombre completo")
        self.ent_name  = self._entry("Tu nombre completo")

        self._label("Correo electrónico")
        self.ent_email = self._entry("tucorreo@ejemplo.com")

        self._label("Contraseña")
        self.fw1, self.ent_pass = self._pw_field("Crea una contraseña")
        self.eye1 = self._eye(self.fw1, self.ent_pass,
                               lambda: self.toggle_p(self.ent_pass, self.eye1))

        self._label("Confirmar contraseña")
        self.fw2, self.ent_conf = self._pw_field("Repite tu contraseña")
        self.eye2 = self._eye(self.fw2, self.ent_conf,
                               lambda: self.toggle_p(self.ent_conf, self.eye2))

        # ── Checkboxes compactos ──────────────────────────────────────────────
        ck = ctk.CTkFrame(m, fg_color="transparent")
        ck.pack(fill="x", pady=(8, 0))

        # Términos
        tr = ctk.CTkFrame(ck, fg_color="transparent")
        tr.pack(anchor="w", pady=(0, 2))

        self.chk_terms = ctk.CTkCheckBox(
            tr, text="", fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            border_color=BORDER2, checkmark_color="#071a0e",
            corner_radius=3, width=16, height=16)
        self.chk_terms.pack(side="left")
        try:
            self.chk_terms.configure(state="disabled")
        except Exception:
            pass

        ctk.CTkLabel(tr, text=" Aceptar ",
                     font=("DM Sans", 10), text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkButton(
            tr, text="términos y condiciones",
            font=("DM Sans", 10, "bold"),
            fg_color=BG1, hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=0, height=16,
            cursor="hand2", command=self.abrir_terminos
        ).pack(side="left")

        # Mantener sesión
        self.chk_remember = ctk.CTkCheckBox(
            ck, text="Mantener sesión iniciada",
            font=("DM Sans", 10), text_color=TEXT_GRAY,
            fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
            border_color=BORDER2, checkmark_color="#071a0e",
            corner_radius=3, width=16, height=16)
        self.chk_remember.pack(anchor="w", pady=(0, 2))

        # ── Error / estado ────────────────────────────────────────────────────
        self.lbl_err = ctk.CTkLabel(m, text="",
                                    font=("DM Sans", 11), text_color=ERROR_COLOR,
                                    wraplength=FIELD_W)
        self.lbl_err.pack(pady=(4, 0))

        # ── Botón Crear cuenta ────────────────────────────────────────────────
        ctk.CTkButton(m, text="→  Crear cuenta",
                      font=("Arial Black", 12),
                      fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
                      text_color="#071a0e",
                      corner_radius=RADIUS_MD,
                      height=36, width=FIELD_W,
                      command=self.register_user).pack(pady=(6, 3))

        # Botón verificar correo (oculto hasta registrar con email)
        self.btn_verify = ctk.CTkButton(
            m, text="✓ Verificar correo",
            font=("DM Sans", 11, "bold"),
            fg_color=BG1, hover_color=BG2,
            text_color=ACCENT_TEXT,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_MD,
            height=30, width=FIELD_W,
            command=self.verify_email_now)

        # ── Divisor ───────────────────────────────────────────────────────────
        dv = ctk.CTkFrame(m, fg_color="transparent")
        dv.pack(fill="x", pady=(3, 3))
        ctk.CTkFrame(dv, fg_color=BORDER2, height=1).pack(
            side="left", fill="x", expand=True)
        ctk.CTkLabel(dv, text="  o continúa con  ",
                     font=("DM Sans", 10), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkFrame(dv, fg_color=BORDER2, height=1).pack(
            side="left", fill="x", expand=True)

        # ── Botón Google ──────────────────────────────────────────────────────
        self.btn_google = ctk.CTkButton(
            m, text="G   Iniciar sesión con Google",
            font=("DM Sans", 12, "bold"),
            fg_color=BG2, hover_color=BG3,
            text_color=TEXT_WHITE,
            border_width=1, border_color=BORDER2,
            corner_radius=RADIUS_MD,
            height=36, width=FIELD_W,
            command=self.start_google_thread)
        self.btn_google.pack(pady=(0, 5))

        # ── ¿Ya tienes cuenta? ────────────────────────────────────────────────
        br = ctk.CTkFrame(m, fg_color="transparent")
        br.pack()
        ctk.CTkLabel(br, text="¿Ya tienes cuenta? ",
                     font=("DM Sans", 11), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(br, text="Iniciar sesión",
                      font=("DM Sans", 11, "bold"),
                      fg_color=BG1, hover_color=BG2,
                      text_color=ACCENT_TEXT,
                      border_width=0, height=22,
                      command=self.go_back_login).pack(side="left")


    # ── Widget helpers ────────────────────────────────────────────────────────

    def _label(self, text):
        ctk.CTkLabel(self.m, text=text.upper(),
                     font=("DM Sans", 9), text_color=TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(5, 1))

    def _entry(self, placeholder):
        wrap = ctk.CTkFrame(self.m, fg_color="#2a2a2e",
                            border_width=1, border_color="#3f3f46",
                            corner_radius=7, height=34)
        wrap.pack(fill="x")
        wrap.pack_propagate(False)
        e = ctk.CTkEntry(wrap, placeholder_text=placeholder,
                         font=("DM Sans", 12), fg_color="transparent",
                         border_width=0, text_color=TEXT_WHITE,
                         placeholder_text_color="#9ca3af", height=34)
        e.pack(fill="x", padx=10, expand=True)
        # Insertar placeholder visible desde el inicio
        e.insert(0, placeholder)
        e.configure(text_color="#9ca3af")
        def _focus_in(ev, entry=e, ph=placeholder):
            if entry.get() == ph:
                entry.delete(0, "end")
                entry.configure(text_color=TEXT_WHITE)
            wrap.configure(border_color=ACCENT_GREEN)
        def _focus_out(ev, entry=e, ph=placeholder):
            if entry.get() == "":
                entry.insert(0, ph)
                entry.configure(text_color="#9ca3af")
            wrap.configure(border_color="#3f3f46")
        e.bind("<FocusIn>",  _focus_in)
        e.bind("<FocusOut>", _focus_out)
        return e

    def _pw_field(self, placeholder):
        wrap = ctk.CTkFrame(self.m, fg_color="#2a2a2e",
                            border_width=1, border_color="#3f3f46",
                            corner_radius=7, height=34)
        wrap.pack(fill="x")
        wrap.pack_propagate(False)
        # Sin show="*" al inicio para que el placeholder sea legible
        e = ctk.CTkEntry(wrap, placeholder_text=placeholder,
                         font=("DM Sans", 12), fg_color="transparent",
                         border_width=0, text_color="#9ca3af",
                         placeholder_text_color="#9ca3af", height=34)
        e.pack(side="left", fill="x", padx=(10, 0), expand=True)
        # Insertar placeholder visible
        e.insert(0, placeholder)
        def _focus_in(ev, entry=e, ph=placeholder):
            if entry.get() == ph:
                entry.delete(0, "end")
                entry.configure(show="*", text_color=TEXT_WHITE)
            wrap.configure(border_color=ACCENT_GREEN)
        def _focus_out(ev, entry=e, ph=placeholder):
            if entry.get() == "":
                entry.configure(show="")
                entry.insert(0, ph)
                entry.configure(text_color="#9ca3af")
            wrap.configure(border_color="#3f3f46")
        e.bind("<FocusIn>",  _focus_in)
        e.bind("<FocusOut>", _focus_out)
        return wrap, e

    def _eye(self, parent, entry, cmd):
        btn = ctk.CTkButton(parent, text="👁", font=("DM Sans", 13),
                            width=28, height=32,
                            fg_color="#2a2a2e",   # mismo color que el wrap
                            hover_color="#3a3a3e",
                            text_color=TEXT_MUTED, border_width=0,
                            command=cmd)
        btn.pack(side="right", padx=(0, 6))
        return btn

    # ── Términos ──────────────────────────────────────────────────────────────

    def abrir_terminos(self):
        TerminosModal(parent=self.winfo_toplevel(),
                      callback_aceptar=self.on_terminos_aceptados)

    def on_terminos_aceptados(self):
        self.terminos_aceptados = True
        try:
            self.chk_terms.configure(state="normal")
        except Exception:
            pass
        self.chk_terms.select()
        try:
            self.chk_terms.configure(state="disabled")
        except Exception:
            pass

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def _restore_placeholder(self, entry, placeholder, is_password=False):
        """Restaura el placeholder visible en un entry."""
        entry.delete(0, "end")
        if is_password:
            entry.configure(show="", text_color="#9ca3af")
        else:
            entry.configure(text_color="#9ca3af")
        entry.insert(0, placeholder)

    def clean_form(self):
        self._restore_placeholder(self.ent_name,  "Tu nombre completo")
        self._restore_placeholder(self.ent_email, "tucorreo@ejemplo.com")
        self._restore_placeholder(self.ent_pass,  "Crea una contraseña",  is_password=True)
        self._restore_placeholder(self.ent_conf,  "Repite tu contraseña", is_password=True)
        self.eye1.configure(text="👁")
        self.eye2.configure(text="👁")
        self.user_image_path    = None
        self.terminos_aceptados = False
        self.lbl_av.configure(image=_make_preview_circle(AVATAR_S))
        self.chk_remember.deselect()
        self.chk_terms.deselect()
        self.lbl_err.configure(text="")
        self.btn_google.configure(state="normal", text="G   Iniciar sesión con Google")
        try:
            self.btn_verify.pack_forget()
        except Exception:
            pass
        self.pending_email    = None
        self.pending_user_id  = None
        self.pending_user_name= None
        self.pending_remember = False

    def tkraise(self, *args, **kwargs):
        self.clean_form()
        super().tkraise(*args, **kwargs)

    # ── Navegación ────────────────────────────────────────────────────────────

    def go_back_login(self):
        from ui.frames.login import LoginFrame
        self.controller.show_frame(LoginFrame)

    # ── Registro manual ───────────────────────────────────────────────────────

    def register_user(self):
        _ph = lambda e, ph: "" if e.get() == ph else e.get()
        name  = _ph(self.ent_name,  "Tu nombre completo").strip()
        email = _ph(self.ent_email, "tucorreo@ejemplo.com").strip()
        pw    = _ph(self.ent_pass,  "Crea una contraseña")
        pw_c  = _ph(self.ent_conf,  "Repite tu contraseña")

        if not self.terminos_aceptados:
            self.lbl_err.configure(
                text="❌ Debes aceptar los términos y condiciones.",
                text_color=ERROR_COLOR)
            return

        if self.pending_email and self.pending_user_id:
            self.lbl_err.configure(
                text="❌ Ya hay un registro pendiente. Verifica tu correo primero.",
                text_color=ERROR_COLOR)
            return

        if not name or not pw or not pw_c:
            self.lbl_err.configure(text="❌ Llena todos los campos.", text_color=ERROR_COLOR)
            return
        if pw != pw_c:
            self.lbl_err.configure(text="❌ Las contraseñas no coinciden.", text_color=ERROR_COLOR)
            return
        if email and ("@" not in email or "." not in email):
            self.lbl_err.configure(text="❌ Ingresa un correo válido.", text_color=ERROR_COLOR)
            return

        img_b64 = ""
        try:
            if self.user_image_path:
                with Image.open(self.user_image_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((150, 150))
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode()

            import bcrypt
            hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            uid    = name.lower().replace(" ", "_")

            # Flujo con email → verificación
            if email:
                from database import firebase_auth as fb_auth
                fb_uid = None
                try:
                    fb_uid = fb_auth.create_user_with_email_and_password(email, pw)
                except Exception:
                    pass
                fb_auth.send_verification_email(email, pw)

                existing = self.controller.fb_db.read_record(f"users/{uid}")
                if existing:
                    upd = {"email": email, "auth_provider": "email", "email_verified": False}
                    if fb_uid:  upd["firebase_uid"] = fb_uid
                    if img_b64: upd["imagen_data"]  = img_b64
                    self.controller.fb_db.update_record(f"users/{uid}", upd)
                else:
                    self.controller.fb_db.write_record(f"users/{uid}", {
                        "nombre": name, "email": email, "password": hashed,
                        "imagen_data": img_b64, "auth_provider": "email",
                        "email_verified": False, "firebase_uid": fb_uid or "",
                        "puntos": 0, "nivel": 1,
                    })

                self.pending_email     = email
                self.pending_user_id   = uid
                self.pending_user_name = name
                self.pending_remember  = self.chk_remember.get() == 1

                self.lbl_err.configure(
                    text=f"✅ Correo enviado a {email}. Confírmalo y presiona «Verificar correo».",
                    text_color=ACCENT_TEXT)
                self.btn_verify.pack(pady=(0, 3))
                return

            # Flujo manual (sin email)
            self.controller.fb_db.write_record(f"users/{uid}", {
                "nombre": name, "password": hashed,
                "imagen_data": img_b64, "auth_provider": "manual",
                "puntos": 0, "nivel": 1,
            })
            self.save_local(uid, name, self.chk_remember.get() == 1)
            self.lbl_err.configure(text="✅ Perfil creado. Iniciando sesión...", text_color=ACCENT_TEXT)
            from ui.frames.login import LoginFrame
            self.controller.frames[LoginFrame].necesita_actualizar = True
            self.after(800, lambda: self.controller.show_frame(LoginFrame))

        except Exception as e:
            self.lbl_err.configure(text=f"Error técnico: {e}", text_color=ERROR_COLOR)

    # ── Verificar email ───────────────────────────────────────────────────────

    def verify_email_now(self):
        if not self.pending_email:
            self.lbl_err.configure(text="❌ No hay registro pendiente.", text_color=ERROR_COLOR)
            return
        self.lbl_err.configure(text="Verificando...", text_color=TEXT_GRAY)

        pe, pu, pn, pr = (self.pending_email, self.pending_user_id,
                          self.pending_user_name, self.pending_remember)

        def worker():
            try:
                from database import firebase_auth as fb_auth
                ok = fb_auth.is_email_verified(pe)
                if ok:
                    try:
                        self.controller.fb_db.update_record(
                            f"users/{pu}", {"email_verified": True})
                    except Exception:
                        pass
                self.after(0, lambda: self._verified(ok, pu, pn, pr))
            except Exception as ex:
                self.after(0, lambda: self.lbl_err.configure(
                    text=f"Error: {ex}", text_color=ERROR_COLOR))

        threading.Thread(target=worker, daemon=True).start()

    def _verified(self, ok, uid, name, remember):
        if not ok:
            self.lbl_err.configure(
                text="Aún no verificado. Revisa tu correo e intenta de nuevo.",
                text_color=ERROR_COLOR)
            return
        self.lbl_err.configure(text="✓ Verificado. Iniciando sesión...", text_color=ACCENT_TEXT)
        try:
            self.save_local(uid, name, remember)
        except Exception:
            pass
        from ui.frames.login import LoginFrame
        self.controller.frames[LoginFrame].necesita_actualizar = True
        self.controller.show_frame(LoginFrame)

    # ── Google ────────────────────────────────────────────────────────────────

    def start_google_thread(self):
        if not self.terminos_aceptados:
            self.lbl_err.configure(
                text="❌ Debes aceptar los términos y condiciones.",
                text_color=ERROR_COLOR)
            return
        self.btn_google.configure(state="disabled", text="Revisa tu navegador...")
        threading.Thread(target=self._google_worker, daemon=True).start()

    def _google_worker(self):
        auth = GoogleAuth("google_secrets.json")
        info = auth.login()
        if info:
            self.after(0, lambda: self._finalize_google(info))
        else:
            self.after(0, lambda: self.btn_google.configure(
                state="normal", text="G   Iniciar sesión con Google"))

    def _finalize_google(self, info):
        try:
            uid = info["email"].replace(".", "_").replace("@", "_")
            self.controller.fb_db.write_record(f"users/{uid}", {
                "nombre": info["name"], "email": info["email"],
                "imagen_url": info.get("picture", ""),
                "auth_provider": "google", "puntos": 0, "nivel": 1,
            })
            self.save_local(uid, info["name"], True)
            from ui.frames.login import LoginFrame
            self.controller.frames[LoginFrame].necesita_actualizar = True
            from ui.frames.dashboard import DashboardFrame
            self.lbl_err.configure(text="✅ Cuenta creada con Google.", text_color=ACCENT_TEXT)
            self.after(800, lambda: self.controller.show_frame(DashboardFrame))
        except Exception as e:
            self.lbl_err.configure(
                text=f"Error Google: {e}", text_color=ERROR_COLOR)
            self.btn_google.configure(state="normal", text="G   Iniciar sesión con Google")

    # ── Utilidades ────────────────────────────────────────────────────────────

    def toggle_p(self, entry, btn):
        if entry.cget("show") == "*":
            entry.configure(show="")
            btn.configure(text="🔒")
        else:
            entry.configure(show="*")
            btn.configure(text="👁")

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png")])
        if path:
            self.user_image_path = path
            self.lbl_av.configure(image=_make_preview_circle(AVATAR_S, path))
            self.lbl_err.configure(text="✅ Imagen seleccionada.", text_color=ACCENT_TEXT)

    def save_local(self, uid, name, remember):
        profiles = {}
        if os.path.exists("local_profiles.json"):
            with open("local_profiles.json", "r") as f:
                try:    profiles = json.load(f)
                except: profiles = {}
        profiles[uid] = {"nombre": name, "remember": remember}
        with open("local_profiles.json", "w") as f:
            json.dump(profiles, f)
        from ui.frames.login import LoginFrame
        self.controller.frames[LoginFrame].necesita_actualizar = True