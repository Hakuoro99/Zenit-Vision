import os
import json
import base64
import bcrypt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BORDER_LIGHT, BG_CARD, BG_CARD_HOVER, BG_INPUT, FONT_TITLE,
    HARD_BG, HARD_BRD, HARD_TX, ACCENT_GREEN, BG_MAIN, AVATAR_PALETTE
)
from ui.icons import get_icon, get_icon_pixmap
from ui.views.login_view import get_circular_avatar

# ── 1. DIÁLOGOS Y MODALES PERSONALIZADOS DE ZENIT ─────────────────────────────

class ZenitInfoDialog(QDialog):
    """
    Modal de información/alerta estilo dark premium, sin bordes nativos.
    """
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        card = QFrame()
        card.setFixedSize(360, 180)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 2px solid {ACCENT_GREEN};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent; line-height: 15px;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_ok = QPushButton("Entendido")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedHeight(30)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
                color: {BG_MAIN};
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        btn_ok.clicked.connect(self.accept)
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_msg)
        card_layout.addStretch()
        card_layout.addWidget(btn_ok)
        
        layout.addWidget(card)


class ZenitConfirmDialog(QDialog):
    """
    Modal crítico de confirmación para la eliminación de cuenta, replicando el mockup exacto.
    """
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        card = QFrame()
        card.setFixedSize(400, 440)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 2px solid {HARD_TX};
                border-radius: 16px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)
        
        # Círculo de advertencia rojo
        warn_row = QHBoxLayout()
        warn_circle = QFrame()
        warn_circle.setFixedSize(64, 64)
        warn_circle.setStyleSheet(f"""
            QFrame {{
                background-color: #240E0E;
                border: 2px solid {HARD_TX};
                border-radius: 32px;
            }}
        """)
        circle_layout = QHBoxLayout(warn_circle)
        circle_layout.setContentsMargins(0, 0, 0, 0)
        
        warn_lbl = QLabel("⚠️")
        warn_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_lbl.setStyleSheet("font-size: 26px; border: none; background: transparent;")
        circle_layout.addWidget(warn_lbl)
        
        warn_row.addWidget(warn_circle, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(warn_row)
        
        # Título
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 18px; font-weight: bold; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_title)
        
        # Mensaje descriptivo
        lbl_msg = QLabel(message)
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent; line-height: 16px;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(lbl_msg)
        
        # Tarjeta informativa interna
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: #0D1F17;
                border: 1px solid #143D2A;
                border-radius: 8px;
            }}
        """)
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(8)
        
        info_icon = QLabel()
        info_icon.setFixedSize(14, 14)
        info_icon.setPixmap(get_icon_pixmap("info", ACCENT_GREEN, 14))
        info_icon.setStyleSheet("border: none; background: transparent;")
        
        info_txt = QLabel("Tu suscripción activa también será cancelada de inmediato.")
        info_txt.setWordWrap(True)
        info_txt.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10px; border: none; background: transparent;")
        
        info_layout.addWidget(info_icon, alignment=Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(info_txt)
        card_layout.addWidget(info_card)
        
        # Botones de Acción Horizontales
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedHeight(36)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: #1F222A;
                color: {TEXT_WHITE};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2D313C;
            }}
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("Eliminar permanentemente")
        btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirm.setFixedHeight(36)
        btn_confirm.setStyleSheet(f"""
            QPushButton {{
                background-color: {HARD_TX};
                color: {TEXT_WHITE};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        btn_confirm.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(card)


# ── 2. VISTA PRINCIPAL DE CONFIGURACIÓN ───────────────────────────────────────

class ConfiguracionView(QWidget):
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self.uploaded_image_b64 = None
        self._init_ui()

    def _init_ui(self):
        # Layout maestro principal (Vertical) sin scrollbars, espacio óptimo
        master_layout = QVBoxLayout(self)
        master_layout.setContentsMargins(28, 20, 28, 20)
        master_layout.setSpacing(14)

        # ── 1. Cabecera (Header con Buscador e Iconos idéntico al mockup) ──────
        header_frame = QFrame()
        header_frame.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_container = QFrame()
        title_container.setStyleSheet("background: transparent; border: none;")
        title_v_layout = QVBoxLayout(title_container)
        title_v_layout.setContentsMargins(0, 0, 0, 0)
        title_v_layout.setSpacing(2)

        title_lbl = QLabel("Configuración")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 22px; color: {ACCENT_GREEN}; font-weight: bold; border: none; background: transparent;")
        sub_lbl = QLabel("Modifica tu perfil, seguridad y preferencias del sistema")
        sub_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; border: none; background: transparent;")

        title_v_layout.addWidget(title_lbl)
        title_v_layout.addWidget(sub_lbl)
        header_layout.addWidget(title_container)
        header_layout.addStretch()

        # Contenedor de acciones del header
        actions_container = QFrame()
        actions_container.setStyleSheet("background: transparent; border: none;")
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        # Campo de Búsqueda
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar ajustes...")
        search_input.setFixedSize(180, 28)
        search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER_DARK};
                border-radius: 14px;
                color: {TEXT_WHITE};
                font-size: 11px;
                padding: 4px 10px 4px 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_GREEN};
            }}
        """)
        actions_layout.addWidget(search_input)

        # Iconos de Notificaciones y Calendario
        btn_bell = QPushButton()
        btn_bell.setFixedSize(28, 28)
        btn_bell.setIcon(get_icon("info", TEXT_GRAY, 14))
        btn_bell.setStyleSheet("QPushButton { border: none; background: transparent; }")

        btn_cal = QPushButton()
        btn_cal.setFixedSize(28, 28)
        btn_cal.setIcon(get_icon("clock", TEXT_GRAY, 14))
        btn_cal.setStyleSheet("QPushButton { border: none; background: transparent; }")

        actions_layout.addWidget(btn_bell)
        actions_layout.addWidget(btn_cal)
        header_layout.addWidget(actions_container)
        master_layout.addWidget(header_frame)

        # Cargar datos de usuario
        self.nombre_val = "Usuario"
        self.email_val = "correo@ejemplo.com"
        self.provider = "manual"
        self.photo_data = None
        self.photo_url = None

        uid = self.shell.controller.current_user_id
        if uid == "invitado":
            self.nombre_val = "Invitado"
            self.email_val = "invitado@zenitvision.com"
            self.provider = "guest"
            self.photo_data = None
            self.photo_url = None
        elif uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    self.nombre_val = data.get("nombre", "Usuario")
                    self.email_val = data.get("email", "correo@ejemplo.com")
                    self.provider = data.get("auth_provider", "manual")
                    self.photo_data = data.get("imagen_data")
                    self.photo_url = data.get("imagen_url")
            except Exception:
                pass

        # ── 2. Panel Horizontal de dos columnas (Todo cabe sin scroll) ────────
        body_frame = QFrame()
        body_frame.setStyleSheet("background: transparent; border: none;")
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(24)

        # ── 2.1 COLUMNA IZQUIERDA (Perfil de Usuario y Zona de Peligro) ──────────
        left_column = QFrame()
        left_column.setStyleSheet("background: transparent; border: none;")
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(14)

        # Encabezado "PERFIL" con divisor de línea
        left_layout.addWidget(self._create_section_title("Perfil", "user"))

        perfil_card = QFrame()
        perfil_card.setStyleSheet("QFrame { background-color: #1E1F22; border: 1px solid #2E3035; border-radius: 12px; }")
        perfil_layout = QVBoxLayout(perfil_card)
        perfil_layout.setContentsMargins(20, 20, 20, 20)
        perfil_layout.setSpacing(14)

        # Avatar Circular Interactivo (100x100px) con Badge Flotante de Cámara
        avatar_container = QFrame()
        avatar_container.setFixedSize(110, 110)
        avatar_container.setStyleSheet("background: transparent; border: none;")

        self.av_avatar = QPushButton(avatar_container)
        self.av_avatar.setFixedSize(100, 100)
        self.av_avatar.setGeometry(0, 0, 100, 100)
        self.av_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.av_avatar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_MAIN};
                border: 2px solid #2E3035;
                border-radius: 50px;
            }}
            QPushButton:hover {{
                border: 2px solid #4ADE80;
            }}
        """)
        self.av_avatar.clicked.connect(self._select_image)

        # Botón Badge de Cámara superpuesto a la derecha
        self.badge_camera = QPushButton(avatar_container)
        self.badge_camera.setFixedSize(26, 26)
        self.badge_camera.setGeometry(72, 72, 26, 26)
        self.badge_camera.setCursor(Qt.CursorShape.PointingHandCursor)
        self.badge_camera.setIcon(get_icon("camera", "#121316", 12))
        self.badge_camera.setIconSize(QSize(12, 12))
        self.badge_camera.setStyleSheet("""
            QPushButton {
                background-color: #4ADE80;
                border: 2.5px solid #1E1F22;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: #34D399;
            }
        """)
        self.badge_camera.clicked.connect(self._select_image)

        avatar_row = QHBoxLayout()
        avatar_row.addWidget(avatar_container, alignment=Qt.AlignmentFlag.AlignCenter)
        perfil_layout.addLayout(avatar_row)

        self._load_avatar_preview()

        # Textos de Avatar
        photo_txt_layout = QVBoxLayout()
        photo_txt_layout.setSpacing(2)
        lbl_foto = QLabel("Foto de perfil")
        lbl_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_foto.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        lbl_foto_sub = QLabel("Haz clic en el avatar para cambiar")
        lbl_foto_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_foto_sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none; background: transparent;")
        photo_txt_layout.addWidget(lbl_foto)
        photo_txt_layout.addWidget(lbl_foto_sub)
        perfil_layout.addLayout(photo_txt_layout)

        # Input: Nombre Completo (Alta visibilidad y contraste)
        self.frame_nombre = self._build_field(perfil_layout, "Nombre completo", self.nombre_val, placeholder="Tu nombre completo")

        # Botones de Acción
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        btn_save_p = QPushButton("Guardar cambios")
        btn_save_p.setFixedHeight(34)
        btn_save_p.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_p.setStyleSheet(f"""
            QPushButton {{
                background-color: #4ADE80;
                color: #0B0C0E;
                border: none;
                border-radius: 8px;
                font-family: '{FONT_TITLE}';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
            QPushButton:pressed {{
                background-color: #10B981;
            }}
        """)
        btn_save_p.clicked.connect(self._guardar_perfil)

        btn_cancel = QPushButton("Descartar")
        btn_cancel.setFixedHeight(34)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: #FFFFFF;
                border: 1px solid #2E323A;
                border-radius: 8px;
                font-family: '{FONT_TITLE}';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #25282E;
                border: 1px solid #3E4456;
            }}
            QPushButton:pressed {{
                background-color: #1C1E22;
            }}
        """)
        btn_cancel.clicked.connect(self._revertir_cambios)

        btn_row.addWidget(btn_save_p, stretch=1)
        btn_row.addWidget(btn_cancel, stretch=1)
        perfil_layout.addLayout(btn_row)

        left_layout.addWidget(perfil_card)

        # Encabezado "ZONA DE PELIGRO"
        left_layout.addWidget(self._create_section_title("Zona de peligro", None))

        danger_card = QFrame()
        danger_card.setStyleSheet("QFrame { background-color: #1A0D0E; border: 1px solid #4F1B1B; border-radius: 12px; }")
        danger_layout = QVBoxLayout(danger_card)
        danger_layout.setContentsMargins(16, 12, 16, 12)
        danger_layout.setSpacing(10)

        lbl_del_sub = QLabel("Esta acción es irreversible y borrará todo tu historial.")
        lbl_del_sub.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
        
        btn_del = QPushButton("Eliminar mi cuenta")
        btn_del.setFixedHeight(30)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: #240E0E;
                color: #F87171;
                border: 1px solid #4F1B1B;
                border-radius: 8px;
                font-family: '{FONT_TITLE}';
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #3B1414;
                color: #FFFFFF;
                border: 1px solid #EF4444;
            }}
            QPushButton:pressed {{
                background-color: #4F1B1B;
            }}
        """)
        btn_del.clicked.connect(self._eliminar_cuenta)

        danger_layout.addWidget(lbl_del_sub)
        danger_layout.addWidget(btn_del)
        left_layout.addWidget(danger_card)

        # ── 2.2 COLUMNA DERECHA (Cuenta y Seguridad) ─────────────────────────────
        right_column = QFrame()
        right_column.setStyleSheet("background: transparent; border: none;")
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        # Encabezado "CUENTA Y SEGURIDAD"
        right_layout.addWidget(self._create_section_title("Cuenta y seguridad", "shield"))

        cuenta_card = QFrame()
        cuenta_card.setStyleSheet("QFrame { background-color: #1E1F22; border: 1px solid #2E3035; border-radius: 12px; }")
        cuenta_layout = QVBoxLayout(cuenta_card)
        cuenta_layout.setContentsMargins(20, 20, 20, 20)
        cuenta_layout.setSpacing(14)

        # Campo: Correo Electrónico (Con icono interno a la izquierda)
        self.frame_email, self.ent_email = self._build_icon_field("Correo electrónico", self.email_val, disabled=True, icon_name="at")
        cuenta_layout.addWidget(self.frame_email)

        if self.provider in ("google", "guest"):
            if self.provider == "guest":
                info_text_guest = "Perfil de Invitado activo. Regístrate para personalizar tu perfil, guardar tu historial de entrenamientos, competir en la tabla de clasificación y sincronizar tu progreso en la nube de Zenit-Visión."
                cuenta_layout.addWidget(self._build_info_card(info_text_guest))
            else:
                lbl_goog = QLabel("Cuenta vinculada con Google — seguridad delegada")
                lbl_goog.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none; background: transparent; font-style: italic; margin-top: 6px;")
                cuenta_layout.addWidget(lbl_goog)
        else:
            # Campo: Contraseña Actual (Con icono interno a la izquierda)
            self.frame_current_pw, self.ent_current_pw = self._build_icon_field("Contraseña actual", is_pw=True, placeholder="Tu contraseña actual obligatoria", icon_name="lock")
            cuenta_layout.addWidget(self.frame_current_pw)

            # Fila Horizontal para Nueva Contraseña y Confirmar Nueva Contraseña (Side-by-side)
            pw_row = QHBoxLayout()
            pw_row.setSpacing(12)

            new_pw_v = QVBoxLayout()
            new_pw_v.setContentsMargins(0, 0, 0, 0)
            self.frame_new_pw, self.ent_new_pw = self._build_icon_field("Nueva contraseña", is_pw=True, placeholder="Dejar vacío para no cambiar")
            new_pw_v.addWidget(self.frame_new_pw)

            conf_pw_v = QVBoxLayout()
            conf_pw_v.setContentsMargins(0, 0, 0, 0)
            self.frame_conf_pw, self.ent_conf_pw = self._build_icon_field("Confirmar nueva contraseña", is_pw=True, placeholder="Repite tu nueva contraseña")
            conf_pw_v.addWidget(self.frame_conf_pw)

            pw_row.addLayout(new_pw_v, stretch=1)
            pw_row.addLayout(conf_pw_v, stretch=1)
            cuenta_layout.addLayout(pw_row)

            # Tarjeta de Información Estilo Mockup (Subtle Green)
            info_text = "Tu contraseña debe tener al menos 8 caracteres, incluyendo una letra mayúscula y un número para mayor seguridad en el acceso a tus datos de rendimiento."
            cuenta_layout.addWidget(self._build_info_card(info_text))

            # Botón Actualizar Contraseña
            btn_save_c = QPushButton("Actualizar contraseña")
            btn_save_c.setFixedHeight(34)
            btn_save_c.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_save_c.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2C2F36;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px 24px;
                }}
                QPushButton:hover {{
                    background-color: #3E4456;
                }}
                QPushButton:pressed {{
                    background-color: #1E2127;
                }}
            """)
            btn_save_c.clicked.connect(self._actualizar_contrasena)
            cuenta_layout.addWidget(btn_save_c, alignment=Qt.AlignmentFlag.AlignLeft)

        cuenta_layout.addStretch() # Push inputs to top inside the card
        right_layout.addWidget(cuenta_card, stretch=1) # Stretch the card to fill the column height

        # Unir Columnas al Body
        body_layout.addWidget(left_column, stretch=1)
        body_layout.addWidget(right_column, stretch=1)

        master_layout.addWidget(body_frame)
        master_layout.addStretch()

    def _create_section_title(self, text, icon_name=None):
        """
        Crea encabezados de sección estilizados con icono guía y línea divisoria.
        """
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        
        if icon_name:
            icon_lbl = QLabel()
            icon_lbl.setFixedSize(14, 14)
            icon_lbl.setPixmap(get_icon_pixmap(icon_name, ACCENT_GREEN, 14))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            row_layout.addWidget(icon_lbl)
            
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        row_layout.addWidget(lbl)
        row_layout.addStretch()
        
        layout.addLayout(row_layout)
        
        # Divisor horizontal
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px; border: none;")
        layout.addWidget(line)
        
        return container

    def _build_field(self, parent_layout, label_text, value="", is_pw=False, disabled=False, placeholder=""):
        """
        Construye campos estándar de altísimo contraste con bordes definidos.
        """
        field_frame = QFrame()
        field_frame.setStyleSheet("background: transparent; border: none;")
        field_layout = QVBoxLayout(field_frame)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(4)

        lbl = QLabel(label_text.upper())
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold; border: none; background: transparent;")
        
        ent = QLineEdit()
        ent.setPlaceholderText(placeholder)
        if value:
            ent.setText(value)
        if is_pw:
            ent.setEchoMode(QLineEdit.EchoMode.Password)
        if disabled:
            ent.setDisabled(True)

        ent.setStyleSheet(f"""
            QLineEdit {{
                background-color: #22252A;
                border: 1px solid #2A2D34;
                border-radius: 8px;
                color: {TEXT_WHITE};
                font-size: 12px;
                padding: 8px 12px;
            }}
            QLineEdit:hover {{
                border: 1px solid #3E4456;
            }}
            QLineEdit:focus {{
                border: 1px solid #4ADE80;
                background-color: #121316;
            }}
            QLineEdit:disabled {{
                background-color: #1E1F22;
                color: {TEXT_MUTED};
                border: 1px solid #2E3035;
            }}
        """)

        field_layout.addWidget(lbl)
        field_layout.addWidget(ent)
        parent_layout.addWidget(field_frame)
        return field_frame

    def _build_icon_field(self, label_text, value="", is_pw=False, disabled=False, placeholder="", icon_name=None):
        """
        Construye campos de entrada de altísima fidelidad con icono a la izquierda interno.
        """
        container = QFrame()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        lbl = QLabel(label_text.upper())
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold; border: none; background: transparent;")
        
        input_wrapper = QFrame()
        if disabled:
            input_wrapper.setStyleSheet("""
                QFrame {
                    background-color: #22252A;
                    border: 1px solid #2A2D34;
                    border-radius: 8px;
                }
            """)
        else:
            input_wrapper.setStyleSheet("""
                QFrame {
                    background-color: #22252A;
                    border: 1px solid #2A2D34;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border: 1px solid #3E4456;
                }
                QFrame:focus-within {
                    border: 1px solid #4ADE80;
                    background-color: #121316;
                }
            """)
            
        wrapper_layout = QHBoxLayout(input_wrapper)
        wrapper_layout.setContentsMargins(10, 4, 10, 4)
        wrapper_layout.setSpacing(8)
        
        # Icono a la izquierda
        if icon_name:
            icon_lbl = QLabel()
            icon_lbl.setFixedSize(14, 14)
            icon_lbl.setPixmap(get_icon_pixmap(icon_name, TEXT_MUTED, 14))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            wrapper_layout.addWidget(icon_lbl)
            
        ent = QLineEdit()
        ent.setPlaceholderText(placeholder)
        if value:
            ent.setText(value)
        if is_pw:
            ent.setEchoMode(QLineEdit.EchoMode.Password)
        if disabled:
            ent.setDisabled(True)
            
        ent.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {TEXT_WHITE};
                font-size: 12px;
                padding: 6px 0px;
            }}
            QLineEdit:disabled {{
                color: {TEXT_MUTED};
            }}
        """)
        wrapper_layout.addWidget(ent)
        
        layout.addWidget(lbl)
        layout.addWidget(input_wrapper)
        return container, ent

    def _build_info_card(self, text):
        """
        Construye tarjetas informativas estilo Cyberpunk sutiles con borde de aviso.
        """
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #0D1F17;
                border: 1px solid #143D2A;
                border-radius: 8px;
            }
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(16, 16)
        icon_lbl.setPixmap(get_icon_pixmap("info", "#4ADE80", 16))
        icon_lbl.setStyleSheet("border: none; background: transparent;")
        
        txt_lbl = QLabel(text)
        txt_lbl.setWordWrap(True)
        txt_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10px; border: none; background: transparent; line-height: 14px;")
        
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(txt_lbl)
        return card

    def _load_avatar_preview(self):
        initials = "".join(p[0].upper() for p in self.nombre_val.split()[:2]) or self.nombre_val[:2].upper()
        avatar_pixmap = get_circular_avatar(96, initials, 0, self.photo_data, self.photo_url)
        self.av_avatar.setIcon(QIcon(avatar_pixmap))
        self.av_avatar.setIconSize(QSize(96, 96))

    def _select_image(self):
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no puedes modificar la foto de perfil.")
            dialog.exec()
            return
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar foto de perfil", "", "Imágenes (*.jpg *.png)")
        if path:
            try:
                from PIL import Image
                from io import BytesIO
                with Image.open(path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((150, 150))
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    self.uploaded_image_b64 = base64.b64encode(buf.getvalue()).decode()
                
                self.photo_data = self.uploaded_image_b64
                self._load_avatar_preview()
            except Exception as e:
                dialog = ZenitInfoDialog(self, "Error", f"No se pudo cargar la imagen: {e}")
                dialog.exec()

    def _guardar_perfil(self):
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no puedes modificar el perfil.")
            dialog.exec()
            return
        # Para acceder al QLineEdit de self.frame_nombre, buscamos el hijo
        ent_nombre = self.frame_nombre.findChild(QLineEdit)
        nombre = ent_nombre.text().strip() if ent_nombre else ""
        if not nombre:
            dialog = ZenitInfoDialog(self, "Error", "El nombre completo no puede estar vacío.")
            dialog.exec()
            return

        uid = self.shell.controller.current_user_id
        if uid:
            try:
                upd = {"nombre": nombre}
                if self.uploaded_image_b64:
                    upd["imagen_data"] = self.uploaded_image_b64

                self.shell.controller.fb_db.update_record(f"users/{uid}", upd)
                
                # Sincronización local
                profiles = {}
                if os.path.exists("local_profiles.json"):
                    try:
                        with open("local_profiles.json", "r") as f:
                            profiles = json.load(f)
                    except Exception:
                        pass
                if uid in profiles:
                    profiles[uid]["nombre"] = nombre
                    if self.uploaded_image_b64:
                        profiles[uid]["imagen_data"] = self.uploaded_image_b64
                    with open("local_profiles.json", "w") as f:
                        json.dump(profiles, f)

                self.nombre_val = nombre
                self.shell.refresh_user()
                self.shell.controller.login_view.load_local_profiles()
                
                dialog = ZenitInfoDialog(self, "Perfil Actualizado", "✓ Tu perfil ha sido actualizado con éxito.")
                dialog.exec()
            except Exception as e:
                dialog = ZenitInfoDialog(self, "Error", f"No se pudieron guardar los cambios: {e}")
                dialog.exec()

    def _revertir_cambios(self):
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no tienes cambios que revertir.")
            dialog.exec()
            return
        ent_nombre = self.frame_nombre.findChild(QLineEdit)
        if ent_nombre:
            ent_nombre.setText(self.nombre_val)
        self.uploaded_image_b64 = None
        
        uid = self.shell.controller.current_user_id
        if uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    self.nombre_val = data.get("nombre", "Usuario")
                    self.photo_data = data.get("imagen_data")
                    self.photo_url = data.get("imagen_url")
            except Exception:
                pass
        
        self._load_avatar_preview()
        
        dialog = ZenitInfoDialog(self, "Cambios Descartados", "Se han restablecido los valores originales de tu perfil.")
        dialog.exec()

    def _actualizar_contrasena(self):
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no puedes modificar contraseñas.")
            dialog.exec()
            return
        current_pw = self.ent_current_pw.text().strip()
        new_pw = self.ent_new_pw.text().strip()
        conf_pw = self.ent_conf_pw.text().strip()

        if not current_pw or not new_pw or not conf_pw:
            dialog = ZenitInfoDialog(self, "Campos Vacíos", "Por favor, completa todos los campos de contraseña.")
            dialog.exec()
            return

        if new_pw != conf_pw:
            dialog = ZenitInfoDialog(self, "Error de Coincidencia", "Las nuevas contraseñas no coinciden.")
            dialog.exec()
            return

        if len(new_pw) < 6:
            dialog = ZenitInfoDialog(self, "Contraseña Corta", "La nueva contraseña debe tener al menos 6 caracteres.")
            dialog.exec()
            return

        uid = self.shell.controller.current_user_id
        if uid:
            try:
                user_data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if not user_data:
                    dialog = ZenitInfoDialog(self, "Error", "No se encontró información del usuario.")
                    dialog.exec()
                    return

                stored_hash = user_data.get("password")
                if not stored_hash:
                    dialog = ZenitInfoDialog(self, "Error", "Esta cuenta no utiliza contraseña (Google Auth).")
                    dialog.exec()
                    return

                # Validar contraseña actual con bcrypt
                if bcrypt.checkpw(current_pw.encode('utf-8'), stored_hash.encode('utf-8')):
                    hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode()
                    self.shell.controller.fb_db.update_record(f"users/{uid}", {"password": hashed})
                    
                    self.ent_current_pw.clear()
                    self.ent_new_pw.clear()
                    self.ent_conf_pw.clear()

                    dialog = ZenitInfoDialog(self, "Contraseña Cambiada", "✓ Tu contraseña ha sido actualizada con éxito.")
                    dialog.exec()
                else:
                    dialog = ZenitInfoDialog(self, "Validación Fallida", "La contraseña actual ingresada es incorrecta.")
                    dialog.exec()
            except Exception as e:
                dialog = ZenitInfoDialog(self, "Error Técnico", f"No se pudo cambiar la contraseña: {e}")
                dialog.exec()

    def _eliminar_cuenta(self):
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no puedes eliminar una cuenta.")
            dialog.exec()
            return
        dialog = ZenitConfirmDialog(
            self,
            "¿Eliminar cuenta?",
            "Esta acción es IRREVERSIBLE. Al confirmar, perderás acceso a todo tu historial de entrenamiento, métricas de precisión y logros obtenidos en Zenit Vision. Todos tus datos personales serán borrados de nuestros servidores."
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            uid = self.shell.controller.current_user_id
            if uid:
                try:
                    # Obtener email para borrar también de Firebase Auth
                    email = None
                    user_data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                    if user_data:
                        email = user_data.get("email")

                    # Borrar registro de Realtime Database
                    self.shell.controller.fb_db.delete_record(f"users/{uid}")
                    
                    # Borrar de Firebase Auth si tiene correo
                    if email:
                        try:
                            from database import firebase_auth as fb_auth
                            fb_auth.delete_user_by_email(email)
                        except Exception as auth_err:
                            print(f"[Config] Error al eliminar de Firebase Auth: {auth_err}")
                    
                    # Eliminar de local JSON
                    if os.path.exists("local_profiles.json"):
                        try:
                            with open("local_profiles.json", "r") as f:
                                profiles = json.load(f)
                            if uid in profiles:
                                del profiles[uid]
                                with open("local_profiles.json", "w") as f:
                                    json.dump(profiles, f)
                        except Exception:
                            pass

                    self.shell.controller.login_view.load_local_profiles()
                    
                    info = ZenitInfoDialog(self, "Cuenta Eliminada", "Tu cuenta ha sido eliminada con éxito. Serás redirigido.")
                    info.exec()
                    
                    self.shell._logout()
                except Exception as e:
                    info = ZenitInfoDialog(self, "Error", f"No se pudo eliminar la cuenta: {e}")
                    info.exec()
