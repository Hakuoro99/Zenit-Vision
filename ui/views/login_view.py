import os
import json
import base64
import bcrypt
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QGridLayout, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor, QFont, QIcon

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BORDER_LIGHT, BG_CARD, FONT_TITLE,
    ACCENT_GREEN, BG_SIDEBAR, BG_MAIN, AVATAR_PALETTE, ACCENT_GREEN_BG, BG_INPUT
)
from ui.icons import get_icon, get_icon_pixmap, get_state_icon

# ── Generador Nativo de Avatares Circulares con QPainter ──────────────────────
def get_circular_avatar(size, initials, palette_idx, photo_data=None, photo_url=None):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Ruta circular para recorte
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    
    loaded_photo = False
    if photo_data:
        try:
            img_bytes = base64.b64decode(photo_data)
            qimg = QImage.fromData(img_bytes)
            if not qimg.isNull():
                pix = QPixmap.fromImage(qimg).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                cx = (pix.width() - size) // 2
                cy = (pix.height() - size) // 2
                painter.drawPixmap(0, 0, pix, cx, cy, size, size)
                loaded_photo = True
        except Exception:
            pass
            
    if not loaded_photo and photo_url:
        try:
            resp = requests.get(photo_url, timeout=2)
            if resp.status_code == 200:
                qimg = QImage.fromData(resp.content)
                if not qimg.isNull():
                    pix = QPixmap.fromImage(qimg).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    cx = (pix.width() - size) // 2
                    cy = (pix.height() - size) // 2
                    painter.drawPixmap(0, 0, pix, cx, cy, size, size)
                    loaded_photo = True
        except Exception:
            pass
            
    if not loaded_photo:
        palette = AVATAR_PALETTE[palette_idx % len(AVATAR_PALETTE)]
        # Relleno de color deportivo
        bg_color = QColor(palette["bg"])
        painter.fillPath(path, bg_color)
        
        # Iniciales centradass
        fg_color = QColor(palette["fg"])
        painter.setPen(fg_color)
        font = QFont("Arial", int(size * 0.35), QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, initials)
        
    # Borde traslúcido
    painter.setClipping(False)
    painter.setPen(QColor(255, 255, 255, 30))
    painter.drawEllipse(1, 1, size - 2, size - 2)
    
    painter.end()
    return pixmap


# ── Diálogo Modal de Validación de Contraseña ──────────────────────────────────
class PasswordDialog(QDialog):
    def __init__(self, parent_view, user_id, user_name, stored_hash):
        super().__init__(parent_view)
        self.parent_view = parent_view
        self.user_id = user_id
        self.stored_hash = stored_hash
        self.success = False

        self.setWindowTitle("Seguridad Zenit")
        self.setFixedSize(380, 270)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui(user_name)

    def _init_ui(self, user_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Contenedor con borde y fondo oscuro
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 1px solid {BORDER_DARK};
                border-radius: 12px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        title = QLabel("VALIDACIÓN DE IDENTIDAD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 13px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        
        subtitle = QLabel(f"Hola {user_name}, ingresa tu contraseña:")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")

        # Campo contraseña
        self.entry_pw = QLineEdit()
        self.entry_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_pw.setPlaceholderText("Tu contraseña")
        self.entry_pw.setPlaceholderText("Tu contraseña")

        # Etiqueta de error
        self.err_lbl = QLabel("")
        self.err_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.err_lbl.setStyleSheet("color: #E05A5A; font-size: 10px; font-weight: bold; border: none; background: transparent;")

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(34)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setProperty("class", "SecondaryButton")
        btn_cancel.clicked.connect(self.reject)

        btn_entrar = QPushButton("Entrar")
        btn_entrar.setFixedHeight(34)
        btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_entrar.setProperty("class", "PrimaryButton")
        btn_entrar.clicked.connect(self._verify_password)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_entrar)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.entry_pw)
        card_layout.addWidget(self.err_lbl)
        card_layout.addLayout(btn_layout)

        layout.addWidget(card)

    def _verify_password(self):
        pw_input = self.entry_pw.text().strip()
        if not pw_input:
            self.err_lbl.setText("Ingresa una contraseña")
            return
        
        try:
            # Validar usando bcrypt
            stored_bytes = self.stored_hash.encode('utf-8')
            if bcrypt.checkpw(pw_input.encode('utf-8'), stored_bytes):
                self.success = True
                self.accept()
            else:
                self.err_lbl.setText("Contraseña incorrecta")
                self.entry_pw.setStyleSheet(f"border: 1px solid #E05A5A; background-color: {BG_MAIN}; color: {TEXT_WHITE}; padding: 8px; border-radius: 7px;")
        except Exception as e:
            print(f"Error bcrypt: {e}")
            self.err_lbl.setText("Error técnico de validación")


class GuestWarningModal(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Acceso como Invitado")
        self.setFixedSize(420, 270)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 2px solid {ACCENT_GREEN};
                border-radius: 14px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        # Icono y Título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("info", ACCENT_GREEN, size=32))
        
        title_lbl = QLabel("Acceso como Invitado")
        title_lbl.setStyleSheet(f"""
            font-family: '{FONT_TITLE}';
            font-size: 16px;
            color: {TEXT_WHITE};
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)

        # Mensaje
        msg_lbl = QLabel(
            "Al entrar como invitado, podrás realizar entrenamientos libres y explorar las funciones esenciales de la aplicación.\n\n"
            "⚠️ IMPORTANTE: Tus avances, estadísticas y puntos NO quedarán registrados en la base de datos y se borrarán por completo al cerrar la sesión."
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"""
            color: {TEXT_GRAY};
            font-size: 11.5px;
            line-height: 1.4;
            border: none;
            background: transparent;
        """)
        card_layout.addWidget(msg_lbl)

        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedSize(100, 34)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_WHITE};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #25282E;
                border: 1px solid #3E4456;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_ok = QPushButton("Entrar")
        btn_ok.setFixedSize(100, 34)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: #000000;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        btn_ok.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(card)


# ── Vista Principal de Login en PyQt6 ──────────────────────────────────────────
class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.controller = main_window
        self.local_users_file = "local_profiles.json"
        self._init_ui()

    def _init_ui(self):
        # Layout principal de centrado
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tarjeta centradora de Login (Ampliada para evitar ensimados)
        self.login_card = QFrame()
        self.login_card.setFixedSize(480, 560)
        self.login_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 1px solid {BORDER_DARK};
                border-radius: 20px;
            }}
        """)
        
        self.card_layout = QVBoxLayout(self.login_card)
        self.card_layout.setContentsMargins(40, 30, 40, 30)
        self.card_layout.setSpacing(10)

        # Logo
        logo_lbl = QLabel()
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("border: none; background: transparent;")
        logo_path = os.path.join("assets", "icon", "Zenit_Vision_Logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
        self.card_layout.addWidget(logo_lbl)

        # Título
        title_lbl = QLabel("ZENIT VISION")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 24px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        self.card_layout.addWidget(title_lbl)

        # Subtítulo
        self.sub_lbl = QLabel("¿Quién está entrenando hoy?")
        self.sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 12px; border: none; background: transparent;")
        self.card_layout.addWidget(self.sub_lbl)

        # Grid de Perfiles Locales
        self.profiles_container = QFrame()
        self.profiles_container.setStyleSheet("border: none; background: transparent;")
        self.grid_layout = QGridLayout(self.profiles_container)
        self.grid_layout.setContentsMargins(0, 10, 0, 10)
        self.grid_layout.setSpacing(14)
        
        self.card_layout.addWidget(self.profiles_container)

        # Cargar perfiles reales
        self.load_local_profiles()

        # Divisor
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px; border: none; background: transparent;")
        self.card_layout.addWidget(sep)

        # Pregunta
        no_acct = QLabel("¿No tienes cuenta?")
        no_acct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_acct.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
        self.card_layout.addWidget(no_acct)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(10, 0, 10, 0)
        
        button_style = f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {ACCENT_GREEN};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding-left: 12px;
                padding-right: 12px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_GREEN_BG};
                color: {TEXT_WHITE};
                border: 1px solid {ACCENT_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {BG_INPUT};
            }}
        """
        
        btn_reg = QPushButton(" Registrarse ahora")
        btn_reg.setFixedHeight(36)
        btn_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reg.setIcon(get_state_icon("user", ACCENT_GREEN, TEXT_WHITE, ACCENT_GREEN, size=16))
        btn_reg.setIconSize(QSize(16, 16))
        btn_reg.setStyleSheet(button_style)
        btn_reg.clicked.connect(self.controller.show_register)
        
        btn_guest = QPushButton(" Entrar como Invitado")
        btn_guest.setFixedHeight(36)
        btn_guest.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guest.setIcon(get_state_icon("play", ACCENT_GREEN, TEXT_WHITE, ACCENT_GREEN, size=16))
        btn_guest.setIconSize(QSize(16, 16))
        btn_guest.setStyleSheet(button_style)
        btn_guest.clicked.connect(self._login_as_guest)
        
        btn_layout.addWidget(btn_reg)
        btn_layout.addWidget(btn_guest)
        self.card_layout.addLayout(btn_layout)

        main_layout.addWidget(self.login_card, alignment=Qt.AlignmentFlag.AlignCenter)

    def load_local_profiles(self):
        # Limpiar perfiles anteriores
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Intentar conectar a Firebase para obtener todos los usuarios registrados
        users = None
        try:
            users = self.controller.fb_db.read_record("users")
            if not users:
                users = {}
        except Exception as e:
            print(f"[Zenit-Vision] Error al conectar con la base de datos de Firebase: {e}")
            users = None

        # Si Firebase falló o no devolvió datos, cargamos de local_profiles.json como fallback offline
        if users is None:
            print("[Zenit-Vision] Usando perfiles locales almacenados temporalmente (Modo Offline)...")
            if os.path.exists(self.local_users_file):
                try:
                    with open(self.local_users_file, "r") as f:
                        local_users = json.load(f)
                    users = {}
                    for uid, info in local_users.items():
                        users[uid] = {
                            "nombre": info.get("nombre", uid),
                            "auth_provider": "manual"
                        }
                except Exception:
                    users = {}
            else:
                users = {}

        # Sincronizar local_profiles.json local con los usuarios obtenidos de Firebase
        if users:
            try:
                local_profiles = {}
                if os.path.exists(self.local_users_file):
                    try:
                        with open(self.local_users_file, "r") as f:
                            local_profiles = json.load(f)
                    except Exception:
                        pass
                
                updated = False
                for uid, data in users.items():
                    if uid not in local_profiles:
                        local_profiles[uid] = {
                            "nombre": data.get("nombre", uid),
                            "remember": False
                        }
                        updated = True
                if updated:
                    with open(self.local_users_file, "w") as f:
                        json.dump(local_profiles, f)
            except Exception as e:
                print(f"Error sincronizando local_profiles: {e}")

        # Renderizar cada perfil en el grid de la interfaz
        idx = 0
        for user_id, cloud_data in users.items():
            if not cloud_data:
                continue

            # Obtener si tiene activado "remember" del archivo local
            remember = False
            if os.path.exists(self.local_users_file):
                try:
                    with open(self.local_users_file, "r") as f:
                        local_p = json.load(f)
                        remember = local_p.get(user_id, {}).get("remember", False)
                except Exception:
                    pass

            try:
                self._create_profile_card(user_id, cloud_data, remember, idx)
                idx += 1
            except Exception as e:
                print(f"Error creando perfil {user_id}: {e}")

    def _create_profile_card(self, user_id, data, remember, idx):
        row = idx // 3
        col = idx % 3

        nombre = data.get("nombre", user_id)
        initials = "".join(p[0].upper() for p in nombre.split()[:2]) or nombre[:2].upper()
        photo_data = data.get("imagen_data")
        photo_url = data.get("imagen_url")

        # Dibujar avatar circular
        avatar_pixmap = get_circular_avatar(72, initials, idx, photo_data, photo_url)

        # Crear contenedor del perfil
        profile_frame = QFrame()
        profile_frame.setStyleSheet("background: transparent; border: none;")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(4)

        # Botón con el avatar
        btn = QPushButton()
        btn.setIcon(QIcon(avatar_pixmap))
        btn.setIconSize(QSize(72, 72))
        btn.setFixedSize(76, 76)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 2px solid {BORDER_DARK};
                border-radius: 38px;
            }}
            QPushButton:hover {{
                border: 2px solid {ACCENT_GREEN};
            }}
        """)
        btn.clicked.connect(lambda: self._access_profile(user_id, remember, data))

        # Nombre del perfil
        lbl = QLabel(nombre[:12])
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; font-weight: bold; border: none;")

        profile_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        profile_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        self.grid_layout.addWidget(profile_frame, row, col, alignment=Qt.AlignmentFlag.AlignCenter)

    def _access_profile(self, user_id, remember, data):
        # Si es login con Google o tiene recordar sesión activado, entra directo
        if data.get("auth_provider") == "google" or remember:
            self.controller.login_success(user_id)
            return

        # Si no, solicita contraseña en un diálogo modal estilizado
        stored_hash = data.get("password")
        if not stored_hash:
            return

        dlg = PasswordDialog(self, user_id, data.get("nombre", "Usuario"), stored_hash)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.success:
            self.controller.login_success(user_id)

    def _login_as_guest(self):
        modal = GuestWarningModal(self)
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.controller.login_success("invitado")
