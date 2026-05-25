import customtkinter as ctk
from ui.styles import (
    BG_COLOR, BG1, BG2, BG3,
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED,
    BORDER, BORDER2,
    ACCENT_GREEN, ACCENT_HOVER, ACCENT_TEXT,
    ERROR_COLOR, ERROR_BG, ERROR_BORDER,
    RADIUS_MD,
)
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFilter
import os, base64, json
from io import BytesIO


def _make_circle(size, photo_path=None, initials="US", palette=None):
    if palette is None:
        palette = {"bg": "#101810", "fg": "#4ade80"}
    r = size * 2
    canvas = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    mask   = Image.new("L",    (r, r), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, r-1, r-1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path).convert("RGBA")
            w, h  = photo.size; s = min(w, h)
            photo = photo.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
            photo = photo.resize((r, r), Image.LANCZOS)
            canvas.paste(photo, (0, 0), mask)
        except Exception:
            _draw_initials(canvas, mask, r, initials, palette)
    else:
        _draw_initials(canvas, mask, r, initials, palette)

    brd = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(brd).ellipse((2, 2, r-3, r-3), outline=(255,255,255,40), width=3)
    canvas = Image.alpha_composite(canvas, brd)
    canvas = canvas.resize((size, size), Image.LANCZOS)
    return ctk.CTkImage(canvas, size=(size, size))


def _draw_initials(canvas, mask, r, initials, palette):
    from PIL import ImageFont
    bg = Image.new("RGBA", (r, r), palette["bg"])
    canvas.paste(bg, (0, 0), mask)
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", int(r * 0.38))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((r-tw)/2 - bbox[0], (r-th)/2 - bbox[1]),
              initials, fill=palette["fg"], font=font)
    canvas.putalpha(mask)


class ConfiguracionFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller   = controller
        self._new_img_path = None
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

        # Cargar datos actuales
        self._user_data = self._load_user()

        self._build_perfil(cnt)
        self._build_cuenta(cnt)
        self._build_peligro(cnt)

    # ── Sección: Perfil ───────────────────────────────────────────────────────
    def _build_perfil(self, parent):
        self._section_title(parent, "PERFIL")

        sec = ctk.CTkFrame(parent, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=9)
        sec.pack(fill="x", pady=(0, 14))

        inner = ctk.CTkFrame(sec, fg_color=BG2)
        inner.pack(fill="x", padx=16, pady=16)

        # Avatar + cambiar foto
        av_row = ctk.CTkFrame(inner, fg_color=BG2)
        av_row.pack(fill="x", pady=(0, 14))

        nombre   = self._user_data.get("nombre", "Usuario")
        initials = "".join(p[0].upper() for p in nombre.split()[:2]) or "US"

        self._av_img = _make_circle(52, initials=initials)
        self._lbl_av = ctk.CTkLabel(av_row, image=self._av_img, text="")
        self._lbl_av.pack(side="left", padx=(0, 12))

        av_info = ctk.CTkFrame(av_row, fg_color=BG2)
        av_info.pack(side="left")
        ctk.CTkLabel(av_info, text="Foto de perfil",
                     font=("DM Sans", 11, "bold"),
                     text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(av_info, text="JPG o PNG, máx. 2MB",
                     font=("DM Sans", 9),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(1, 6))
        ctk.CTkButton(av_info, text="⬆  Cambiar foto",
                      font=("DM Sans", 10),
                      fg_color=BG3, hover_color=BG2,
                      text_color=ACCENT_TEXT,
                      border_width=1, border_color=ACCENT_GREEN,
                      corner_radius=5, height=26, width=130,
                      command=self._change_photo).pack(anchor="w")

        # Campo nombre
        self._field_label(inner, "Nombre completo")
        self._ent_name = self._entry(inner, nombre)

        # Botón guardar perfil
        ctk.CTkButton(inner, text="Guardar cambios",
                      font=("DM Sans", 11, "bold"),
                      fg_color=ACCENT_GREEN, hover_color=ACCENT_HOVER,
                      text_color="#071a0e",
                      corner_radius=RADIUS_MD, height=32,
                      command=self._save_perfil).pack(anchor="w", pady=(10, 0))

        self._lbl_perfil_status = ctk.CTkLabel(inner, text="",
                                                font=("DM Sans", 10),
                                                text_color=ACCENT_TEXT)
        self._lbl_perfil_status.pack(anchor="w")

    # ── Sección: Cuenta ───────────────────────────────────────────────────────
    def _build_cuenta(self, parent):
        self._section_title(parent, "CUENTA")

        sec = ctk.CTkFrame(parent, fg_color=BG2,
                            border_width=1, border_color=BORDER,
                            corner_radius=9)
        sec.pack(fill="x", pady=(0, 14))
        inner = ctk.CTkFrame(sec, fg_color=BG2)
        inner.pack(fill="x", padx=16, pady=16)

        # Email (solo lectura si es Google)
        email    = self._user_data.get("email", "")
        provider = self._user_data.get("auth_provider", "manual")

        self._field_label(inner, "Correo electrónico")
        self._ent_email = self._entry(inner, email or "Sin correo")
        if provider == "google":
            self._ent_email.configure(state="disabled",
                                       text_color=TEXT_MUTED)
            ctk.CTkLabel(inner, text="Cuenta vinculada con Google — no editable",
                          font=("DM Sans", 9),
                          text_color=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        # Cambiar contraseña (solo manual)
        if provider in ("manual", "email"):
            ctk.CTkFrame(inner, fg_color=BORDER, height=1).pack(
                fill="x", pady=(12, 12))

            self._field_label(inner, "Nueva contraseña")
            self._ent_pass = self._entry(inner, "Dejar vacío para no cambiar",
                                          is_password=True)
            self._field_label(inner, "Confirmar nueva contraseña")
            self._ent_pass2 = self._entry(inner, "Repite la nueva contraseña",
                                           is_password=True)

            ctk.CTkButton(inner, text="Actualizar contraseña",
                          font=("DM Sans", 11, "bold"),
                          fg_color=BG3, hover_color=BG2,
                          text_color=TEXT_WHITE,
                          border_width=1, border_color=BORDER2,
                          corner_radius=RADIUS_MD, height=32,
                          command=self._update_password).pack(
                              anchor="w", pady=(10, 0))

            self._lbl_pass_status = ctk.CTkLabel(inner, text="",
                                                  font=("DM Sans", 10),
                                                  text_color=ACCENT_TEXT)
            self._lbl_pass_status.pack(anchor="w")

    # ── Sección: Zona de peligro ──────────────────────────────────────────────
    def _build_peligro(self, parent):
        self._section_title(parent, "ZONA DE PELIGRO")

        sec = ctk.CTkFrame(parent, fg_color=ERROR_BG,
                            border_width=1, border_color=ERROR_BORDER,
                            corner_radius=9)
        sec.pack(fill="x", pady=(0, 20))
        inner = ctk.CTkFrame(sec, fg_color=ERROR_BG)
        inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(inner, text="Eliminar cuenta",
                     font=("Syne", 11, "bold"),
                     text_color=ERROR_COLOR).pack(anchor="w")
        ctk.CTkLabel(inner,
                     text="Esta acción es irreversible. Se eliminarán todos tus datos.",
                     font=("DM Sans", 10),
                     text_color=TEXT_GRAY).pack(anchor="w", pady=(2, 10))

        ctk.CTkButton(inner, text="Eliminar mi cuenta",
                      font=("DM Sans", 11),
                      fg_color=ERROR_BG, hover_color="#2a1010",
                      text_color=ERROR_COLOR,
                      border_width=1, border_color=ERROR_BORDER,
                      corner_radius=RADIUS_MD, height=32,
                      command=self._confirm_delete).pack(anchor="w")

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    def _section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=("DM Sans", 8),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

    def _field_label(self, parent, text):
        ctk.CTkLabel(parent, text=text.upper(),
                     font=("DM Sans", 8),
                     text_color=TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(8, 2))

    def _entry(self, parent, value="", is_password=False):
        wrap = ctk.CTkFrame(parent, fg_color="#2a2a2e",
                            border_width=1, border_color=BORDER,
                            corner_radius=7, height=32)
        wrap.pack(fill="x")
        wrap.pack_propagate(False)
        e = ctk.CTkEntry(wrap,
                          show="*" if is_password else "",
                          font=("DM Sans", 11),
                          fg_color="#2a2a2e", border_width=0,
                          text_color=TEXT_WHITE,
                          placeholder_text_color=TEXT_MUTED,
                          height=32)
        e.pack(fill="x", padx=10, expand=True)
        if value:
            e.insert(0, value)
        e.bind("<FocusIn>",  lambda ev: wrap.configure(border_color=BORDER2))
        e.bind("<FocusOut>", lambda ev: wrap.configure(border_color=BORDER))
        return e

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _change_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.png")])
        if path:
            self._new_img_path = path
            self._av_img = _make_circle(52, photo_path=path)
            self._lbl_av.configure(image=self._av_img)
            self._lbl_perfil_status.configure(
                text="Foto lista — guarda los cambios para aplicar.")

    def _save_perfil(self):
        nombre = self._ent_name.get().strip()
        if not nombre:
            self._lbl_perfil_status.configure(
                text="❌ El nombre no puede estar vacío.", text_color=ERROR_COLOR)
            return
        try:
            uid    = self.controller.current_user_id
            update = {"nombre": nombre}

            if self._new_img_path:
                with Image.open(self._new_img_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((150, 150))
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    update["imagen_data"] = base64.b64encode(
                        buf.getvalue()).decode()

            self.controller.fb_db.update_record(f"users/{uid}", update)
            self._lbl_perfil_status.configure(
                text="✓ Perfil actualizado.", text_color=ACCENT_TEXT)
        except Exception as e:
            self._lbl_perfil_status.configure(
                text=f"Error: {e}", text_color=ERROR_COLOR)

    def _update_password(self):
        pw  = self._ent_pass.get()
        pw2 = self._ent_pass2.get()
        if not pw:
            return
        if pw != pw2:
            self._lbl_pass_status.configure(
                text="❌ Las contraseñas no coinciden.", text_color=ERROR_COLOR)
            return
        try:
            import bcrypt
            hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            uid    = self.controller.current_user_id
            self.controller.fb_db.update_record(
                f"users/{uid}", {"password": hashed})
            self._lbl_pass_status.configure(
                text="✓ Contraseña actualizada.", text_color=ACCENT_TEXT)
            self._ent_pass.delete(0, "end")
            self._ent_pass2.delete(0, "end")
        except Exception as e:
            self._lbl_pass_status.configure(
                text=f"Error: {e}", text_color=ERROR_COLOR)

    def _confirm_delete(self):
        win = ctk.CTkToplevel(self)
        win.title("Confirmar eliminación")
        win.geometry("360x200")
        win.configure(fg_color=BG1)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.grab_set()

        # Centrar
        win.update_idletasks()
        p = self.winfo_toplevel()
        px = p.winfo_x() + p.winfo_width()  // 2
        py = p.winfo_y() + p.winfo_height() // 2
        win.geometry(f"360x200+{px-180}+{py-100}")

        outer = ctk.CTkFrame(win, fg_color=BG1,
                              border_width=1, border_color=ERROR_BORDER,
                              corner_radius=RADIUS_MD)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(outer, text="¿Eliminar cuenta?",
                     font=("Syne", 13, "bold"),
                     text_color=ERROR_COLOR).pack(pady=(20, 4))
        ctk.CTkLabel(outer,
                     text="Se eliminarán todos tus datos.\nEsta acción no se puede deshacer.",
                     font=("DM Sans", 10),
                     text_color=TEXT_GRAY,
                     justify="center").pack(pady=(0, 16))

        btns = ctk.CTkFrame(outer, fg_color=BG1)
        btns.pack(fill="x", padx=20)

        ctk.CTkButton(btns, text="Cancelar",
                      font=("DM Sans", 11),
                      fg_color=BG2, hover_color=BG3,
                      text_color=TEXT_GRAY,
                      border_width=1, border_color=BORDER,
                      corner_radius=RADIUS_MD, height=32,
                      command=win.destroy).pack(
                          side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(btns, text="Sí, eliminar",
                      font=("DM Sans", 11, "bold"),
                      fg_color=ERROR_BG, hover_color="#2a1010",
                      text_color=ERROR_COLOR,
                      border_width=1, border_color=ERROR_BORDER,
                      corner_radius=RADIUS_MD, height=32,
                      command=lambda: self._delete_account(win)).pack(
                          side="left", fill="x", expand=True)

    def _delete_account(self, win):
        try:
            uid = self.controller.current_user_id
            self.controller.fb_db.delete_record(f"users/{uid}")
            # Eliminar perfil local
            if os.path.exists("local_profiles.json"):
                with open("local_profiles.json", "r") as f:
                    import json
                    profiles = json.load(f)
                profiles.pop(uid, None)
                with open("local_profiles.json", "w") as f:
                    json.dump(profiles, f)
        except Exception:
            pass
        win.destroy()
        from ui.frames.login import LoginFrame
        self.controller.show_frame(LoginFrame)

    # ── Datos ─────────────────────────────────────────────────────────────────

    def _load_user(self):
        try:
            uid = self.controller.current_user_id
            return self.controller.fb_db.read_record(f"users/{uid}") or {}
        except Exception:
            return {}