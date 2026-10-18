import os
import json
import base64
import time
import random
import bcrypt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, QFileDialog, QDialog, QStackedWidget
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
        def _on_ok():
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
            self.accept()
        btn_ok.clicked.connect(_on_ok)
        
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


def _actualizar_password_en_sistema(user_id, shell, new_password):
    """
    Sincroniza la nueva contraseña de forma segura en:
    1. Firebase Realtime Database (con hash bcrypt)
    2. local_profiles.json (con hash bcrypt)
    3. Firebase Authentication (directamente con el cliente de auth)
    """
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode()

    # 1. Actualizar en Firebase RTDB
    if shell and hasattr(shell, 'controller') and shell.controller and shell.controller.fb_db:
        try:
            shell.controller.fb_db.update_record(f"users/{user_id}", {"password": hashed})
        except Exception as e:
            print(f"[PasswordSync] Error actualizando en Firebase RTDB: {e}")

    # 2. Actualizar en local_profiles.json
    if os.path.exists("local_profiles.json"):
        try:
            with open("local_profiles.json", "r") as f:
                profs = json.load(f)
            if user_id in profs:
                profs[user_id]["password"] = hashed
                with open("local_profiles.json", "w") as f:
                    json.dump(profs, f)
        except Exception as e:
            print(f"[PasswordSync] Error actualizando local_profiles: {e}")

    # 3. Actualizar en Firebase Auth si la cuenta existe
    try:
        from database import firebase_auth as fb_auth
        auth_client = fb_auth._get_auth()
        auth_client.update_user(user_id, password=new_password)
    except Exception as e:
        print(f"[PasswordSync] Error actualizando Firebase Auth: {e}")


def _build_modal_field(label_text, is_pw=False, placeholder=""):
    frame = QFrame()
    frame.setStyleSheet("background: transparent; border: none;")
    v = QVBoxLayout(frame)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)
    lbl = QLabel(label_text.upper())
    lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")
    ent = QLineEdit()
    ent.setPlaceholderText(placeholder)
    if is_pw:
        ent.setEchoMode(QLineEdit.EchoMode.Password)
    ent.setFixedHeight(34)
    ent.setStyleSheet(f"""
        QLineEdit {{
            background-color: #22252A;
            border: 1px solid #2A2D34;
            border-radius: 8px;
            color: {TEXT_WHITE};
            font-size: 11.5px;
            padding: 6px 10px;
        }}
        QLineEdit:hover {{
            border: 1px solid #3E4456;
        }}
        QLineEdit:focus {{
            border: 1.5px solid {ACCENT_GREEN};
            background-color: #121316;
        }}
    """)
    v.addWidget(lbl)
    v.addWidget(ent)
    return frame, ent


class PasswordSettingsModal(QDialog):
    """
    Modal minimalista y estético para cambiar la contraseña usando la clave actual.
    Incluye la pregunta '¿Olvidaste tu contraseña? Haz clic aquí' directamente debajo
    del botón de guardar, que abre el modal de restablecimiento por correo.
    """
    def __init__(self, parent, user_id, user_email, user_name):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.parent_view = parent
        self.user_id = user_id
        self.user_email = user_email or "correo@ejemplo.com"
        self.user_name = user_name or "Usuario"
        self.shell = parent.shell if hasattr(parent, 'shell') else None

        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(410, 375)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedSize(410, 375)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1.5px solid #2E323A;
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 18)
        card_layout.setSpacing(10)

        # 1. Cabecera minimalista
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("lock", ACCENT_GREEN, size=20))
        header.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        title_lbl = QLabel("Seguridad de Contraseña")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14.5px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        sub_lbl = QLabel("Actualiza tu clave de acceso")
        sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10.5px; border: none; background: transparent;")
        title_v.addWidget(title_lbl)
        title_v.addWidget(sub_lbl)
        header.addLayout(title_v)

        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 13px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2E323A;
                color: {TEXT_WHITE};
            }}
        """)
        btn_close.clicked.connect(self._cerrar)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # 2. Campos de contraseña
        f_cur, self.ent_cur_pw = _build_modal_field("Contraseña actual", is_pw=True, placeholder="Tu contraseña actual obligatoria")
        f_new, self.ent_new_pw = _build_modal_field("Nueva contraseña", is_pw=True, placeholder="Mínimo 6 caracteres")
        f_conf, self.ent_conf_pw = _build_modal_field("Confirmar nueva contraseña", is_pw=True, placeholder="Repite tu nueva contraseña")

        card_layout.addWidget(f_cur)
        card_layout.addWidget(f_new)
        card_layout.addWidget(f_conf)

        # 3. Botón Guardar nueva contraseña
        btn_save = QPushButton("Guardar nueva contraseña")
        btn_save.setFixedHeight(35)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
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
        btn_save.clicked.connect(self._cambiar_con_actual)
        card_layout.addWidget(btn_save)

        # 4. Enlace directo bajo el botón: "¿Olvidaste tu contraseña? Haz clic aquí"
        btn_forgot = QPushButton("¿Olvidaste tu contraseña? Haz clic aquí")
        btn_forgot.setFixedHeight(22)
        btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_forgot.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
                padding-top: 2px;
            }}
            QPushButton:hover {{
                color: {ACCENT_GREEN};
                text-decoration: underline;
            }}
        """)
        btn_forgot.clicked.connect(self._abrir_recuperacion)
        card_layout.addWidget(btn_forgot)

        layout.addWidget(card)

    def _abrir_recuperacion(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        parent = self.parent_view
        user_id = self.user_id
        user_email = self.user_email
        user_name = self.user_name
        shell = self.shell
        self.reject()

        modal = PasswordResetCodeModal(parent, user_id, user_email, user_name, shell)
        modal.exec()

    def _cambiar_con_actual(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass

        cur_pw = self.ent_cur_pw.text().strip()
        new_pw = self.ent_new_pw.text().strip()
        conf_pw = self.ent_conf_pw.text().strip()

        if not cur_pw or not new_pw or not conf_pw:
            dialog = ZenitInfoDialog(self, "Campos Incompletos", "Por favor completa todos los campos de contraseña.")
            dialog.exec()
            return

        if new_pw != conf_pw:
            dialog = ZenitInfoDialog(self, "Error de Coincidencia", "Las nuevas contraseñas no coinciden.")
            dialog.exec()
            return

        if len(new_pw) < 6:
            dialog = ZenitInfoDialog(self, "Contraseña Muy Corta", "La nueva contraseña debe tener al menos 6 caracteres.")
            dialog.exec()
            return

        # Validar contraseña actual
        stored_hash = None
        if self.shell and self.shell.controller and self.shell.controller.fb_db:
            try:
                user_data = self.shell.controller.fb_db.read_record(f"users/{self.user_id}")
                if user_data:
                    stored_hash = user_data.get("password")
            except Exception:
                pass

        if not stored_hash and os.path.exists("local_profiles.json"):
            try:
                with open("local_profiles.json", "r") as f:
                    profs = json.load(f)
                    if self.user_id in profs:
                        stored_hash = profs[self.user_id].get("password")
            except Exception:
                pass

        if not stored_hash:
            dialog = ZenitInfoDialog(self, "Error", "No se encontró registro de contraseña para este usuario.")
            dialog.exec()
            return

        if not bcrypt.checkpw(cur_pw.encode('utf-8'), stored_hash.encode('utf-8')):
            dialog = ZenitInfoDialog(self, "Contraseña Incorrecta", "La contraseña actual no es correcta. Si la has olvidado, haz clic en '¿Olvidaste tu contraseña? Haz clic aquí'.")
            dialog.exec()
            return

        _actualizar_password_en_sistema(self.user_id, self.shell, new_pw)
        dialog = ZenitInfoDialog(self, "Contraseña Actualizada", "✓ Tu contraseña ha sido cambiada con éxito.")
        dialog.exec()
        self.accept()

    def _cerrar(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        self.reject()


class PasswordResetCodeModal(QDialog):
    """
    Modal minimalista y estético para verificar el código OTP de seguridad por correo.
    Muestra la fila del correo, el campo 'CÓDIGO' limpio y el botón 'Verificar código'.
    Al verificarse exitosamente, abre el modal de 'Nueva Contraseña'.
    """
    def __init__(self, parent, user_id, user_email, user_name, shell=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.parent_view = parent
        self.user_id = user_id
        self.user_email = user_email or "correo@ejemplo.com"
        self.user_name = user_name or "Usuario"
        self.shell = shell or (parent.shell if hasattr(parent, 'shell') else None)

        self.generated_code = None
        self.code_timestamp = 0

        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(410, 315)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedSize(410, 315)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1.5px solid #2E323A;
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 18)
        card_layout.setSpacing(10)

        # 1. Cabecera
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("at", ACCENT_GREEN, size=20))
        header.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        title_lbl = QLabel("Restablecer Contraseña")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14.5px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        sub_lbl = QLabel("Verificación de seguridad por correo")
        sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10.5px; border: none; background: transparent;")
        title_v.addWidget(title_lbl)
        title_v.addWidget(sub_lbl)
        header.addLayout(title_v)

        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 13px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2E323A;
                color: {TEXT_WHITE};
            }}
        """)
        btn_close.clicked.connect(self._cerrar)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # 2. Fila de Correo con Botón de Envío
        email_box = QFrame()
        email_box.setStyleSheet("QFrame { background-color: #181A1D; border: 1px solid #2A2D34; border-radius: 8px; }")
        eb_layout = QHBoxLayout(email_box)
        eb_layout.setContentsMargins(10, 6, 10, 6)
        eb_layout.setSpacing(8)

        ic_at = QLabel()
        ic_at.setPixmap(get_icon_pixmap("at", ACCENT_GREEN, size=14))
        lbl_em = QLabel(self.user_email)
        lbl_em.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none; background: transparent;")

        self.btn_send_code = QPushButton("Enviar código")
        self.btn_send_code.setFixedHeight(26)
        self.btn_send_code.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send_code.setStyleSheet(f"""
            QPushButton {{
                background-color: #2A2D34;
                color: {ACCENT_GREEN};
                border: 1px solid #3E4456;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0px 12px;
            }}
            QPushButton:hover {{
                background-color: #3E4456;
                color: #FFFFFF;
            }}
        """)
        self.btn_send_code.clicked.connect(self._enviar_codigo_correo)

        eb_layout.addWidget(ic_at)
        eb_layout.addWidget(lbl_em)
        eb_layout.addStretch()
        eb_layout.addWidget(self.btn_send_code)
        card_layout.addWidget(email_box)

        # Estado del envío
        self.lbl_reset_status = QLabel("Presiona 'Enviar código' para recibir la clave en tu correo.")
        self.lbl_reset_status.setWordWrap(True)
        self.lbl_reset_status.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none; background: transparent;")
        card_layout.addWidget(self.lbl_reset_status)

        # 3. Campo CÓDIGO (Limpio, sin 'Ejemplo: 742918')
        code_box = QFrame()
        code_box.setStyleSheet("background: transparent; border: none;")
        cb_layout = QVBoxLayout(code_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setSpacing(4)

        lbl_code = QLabel("CÓDIGO")
        lbl_code.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9.5px; font-weight: bold; border: none; background: transparent;")

        self.ent_reset_code = QLineEdit()
        self.ent_reset_code.setMaxLength(6)
        self.ent_reset_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ent_reset_code.setFixedHeight(34)
        self.ent_reset_code.setStyleSheet(f"""
            QLineEdit {{
                background-color: #121316;
                border: 1.5px solid #2A2D34;
                border-radius: 8px;
                color: {ACCENT_GREEN};
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 4px;
                padding: 4px 10px;
            }}
            QLineEdit:hover {{
                border: 1.5px solid #3E4456;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {ACCENT_GREEN};
            }}
        """)
        cb_layout.addWidget(lbl_code)
        cb_layout.addWidget(self.ent_reset_code)
        card_layout.addWidget(code_box)

        # 4. Botón Verificar código
        btn_verify = QPushButton("Verificar código")
        btn_verify.setFixedHeight(35)
        btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_verify.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
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
        btn_verify.clicked.connect(self._verificar_codigo)
        card_layout.addWidget(btn_verify)

        # 5. Volver a cambiar con contraseña actual
        btn_back = QPushButton("← Volver a cambiar con contraseña actual")
        btn_back.setFixedHeight(22)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 11px;
                font-weight: 500;
                text-align: center;
                padding-top: 2px;
            }}
            QPushButton:hover {{
                color: {TEXT_WHITE};
            }}
        """)
        btn_back.clicked.connect(self._volver_a_cambio)
        card_layout.addWidget(btn_back)

        layout.addWidget(card)

    def _volver_a_cambio(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        parent = self.parent_view
        user_id = self.user_id
        user_email = self.user_email
        user_name = self.user_name
        shell = self.shell
        self.reject()

        modal = PasswordSettingsModal(parent, user_id, user_email, user_name)
        modal.exec()

    def _enviar_codigo_correo(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass

        self.generated_code = f"{random.randint(100000, 999999)}"
        self.code_timestamp = time.time()

        self.btn_send_code.setEnabled(False)
        self.btn_send_code.setText("Enviando...")
        self.lbl_reset_status.setText(f"Enviando código de seguridad a {self.user_email}...")
        self.lbl_reset_status.setStyleSheet("color: #F59E0B; font-size: 10px; border: none; background: transparent;")

        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            from database.firebase_auth import send_password_reset_code_email
            sent = send_password_reset_code_email(self.user_email, self.user_name, self.generated_code)
            if sent:
                self.btn_send_code.setText("Reenviar código")
                self.btn_send_code.setEnabled(True)
                self.lbl_reset_status.setText(f"✓ Código enviado a {self.user_email}. Revisa tu bandeja de entrada o spam.")
                self.lbl_reset_status.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10.5px; font-weight: bold; border: none; background: transparent;")
                self.ent_reset_code.setFocus()
            else:
                self.btn_send_code.setText("Reintentar")
                self.btn_send_code.setEnabled(True)
                self.lbl_reset_status.setText("⚠️ No se pudo enviar el correo vía SMTP. Verifica smtp_config.json.")
                self.lbl_reset_status.setStyleSheet("color: #F87171; font-size: 10px; border: none; background: transparent;")
        except Exception as e:
            self.btn_send_code.setText("Reintentar")
            self.btn_send_code.setEnabled(True)
            self.lbl_reset_status.setText(f"Error al enviar: {e}")
            self.lbl_reset_status.setStyleSheet("color: #F87171; font-size: 10px; border: none; background: transparent;")

    def _verificar_codigo(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass

        if not self.generated_code:
            dialog = ZenitInfoDialog(self, "Código no Solicitado", "Primero debes presionar 'Enviar código' para recibir la clave por correo.")
            dialog.exec()
            return

        if time.time() - self.code_timestamp > 900:
            dialog = ZenitInfoDialog(self, "Código Expirado", "El código ha expirado (límite de 15 minutos). Por favor presiona 'Reenviar código'.")
            dialog.exec()
            return

        code_input = self.ent_reset_code.text().strip()
        if not code_input:
            dialog = ZenitInfoDialog(self, "Código Requerido", "Por favor ingresa el código recibido en tu correo.")
            dialog.exec()
            return

        if code_input != self.generated_code:
            dialog = ZenitInfoDialog(self, "Código Inválido", "El código ingresado no coincide con el enviado a tu correo.")
            dialog.exec()
            return

        # Código verificado exitosamente
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_select()
        except Exception:
            pass

        parent = self.parent_view
        user_id = self.user_id
        shell = self.shell
        self.accept()

        # Abrir modal para registrar la nueva contraseña
        new_pw_modal = SetNewPasswordModal(parent, user_id, shell)
        new_pw_modal.exec()

    def _cerrar(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        self.reject()


class SetNewPasswordModal(QDialog):
    """
    Modal minimalista y estético para agregar la nueva contraseña tras
    haber verificado el código por correo.
    """
    def __init__(self, parent, user_id, shell=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.parent_view = parent
        self.user_id = user_id
        self.shell = shell or (parent.shell if hasattr(parent, 'shell') else None)

        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(410, 295)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedSize(410, 295)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1.5px solid #2E323A;
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(10)

        # 1. Cabecera
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("lock", ACCENT_GREEN, size=20))
        header.addWidget(icon_lbl)

        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        title_lbl = QLabel("Nueva Contraseña")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 14.5px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        sub_lbl = QLabel("Ingresa y confirma tu nueva clave de acceso")
        sub_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10.5px; border: none; background: transparent;")
        title_v.addWidget(title_lbl)
        title_v.addWidget(sub_lbl)
        header.addLayout(title_v)

        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_MUTED};
                border: none;
                border-radius: 13px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2E323A;
                color: {TEXT_WHITE};
            }}
        """)
        btn_close.clicked.connect(self._cerrar)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # 2. Campos de nueva contraseña
        f_new, self.ent_new_pw = _build_modal_field("Nueva contraseña", is_pw=True, placeholder="Mínimo 6 caracteres")
        f_conf, self.ent_conf_pw = _build_modal_field("Confirmar nueva contraseña", is_pw=True, placeholder="Repite tu nueva contraseña")

        card_layout.addWidget(f_new)
        card_layout.addWidget(f_conf)

        # 3. Botón Guardar nueva contraseña
        btn_save = QPushButton("Guardar nueva contraseña")
        btn_save.setFixedHeight(35)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_GREEN};
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
        btn_save.clicked.connect(self._guardar_nueva_contrasena)
        card_layout.addWidget(btn_save)

        layout.addWidget(card)

    def _guardar_nueva_contrasena(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass

        new_pw = self.ent_new_pw.text().strip()
        conf_pw = self.ent_conf_pw.text().strip()

        if not new_pw or not conf_pw:
            dialog = ZenitInfoDialog(self, "Campos Incompletos", "Por favor completa ambos campos de contraseña.")
            dialog.exec()
            return

        if new_pw != conf_pw:
            dialog = ZenitInfoDialog(self, "Error de Coincidencia", "Las nuevas contraseñas no coinciden.")
            dialog.exec()
            return

        if len(new_pw) < 6:
            dialog = ZenitInfoDialog(self, "Contraseña Muy Corta", "La nueva contraseña debe tener al menos 6 caracteres.")
            dialog.exec()
            return

        _actualizar_password_en_sistema(self.user_id, self.shell, new_pw)
        dialog = ZenitInfoDialog(self, "Contraseña Restablecida", "✓ Tu contraseña ha sido actualizada y guardada exitosamente.")
        dialog.exec()
        self.accept()

    def _cerrar(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        self.reject()


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

        self.original_nombre = self.nombre_val
        self.original_photo_data = self.photo_data

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
        self.frame_nombre, self.ent_nombre = self._build_field(perfil_layout, "Nombre completo", self.nombre_val, placeholder="Tu nombre completo")

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
            # Tarjeta de Estado de Contraseña y Seguridad
            sec_card = QFrame()
            sec_card.setStyleSheet("QFrame { background-color: #22252A; border: 1px solid #2E323A; border-radius: 12px; }")
            sec_layout = QVBoxLayout(sec_card)
            sec_layout.setContentsMargins(16, 16, 16, 16)
            sec_layout.setSpacing(10)

            sec_header = QHBoxLayout()
            sec_ic = QLabel()
            sec_ic.setPixmap(get_icon_pixmap("lock", ACCENT_GREEN, size=18))
            sec_title = QLabel("Contraseña de Acceso")
            sec_title.setStyleSheet(f"color: {TEXT_WHITE}; font-family: '{FONT_TITLE}'; font-size: 13px; font-weight: bold; border: none; background: transparent;")
            sec_header.addWidget(sec_ic)
            sec_header.addWidget(sec_title)
            sec_header.addStretch()
            sec_layout.addLayout(sec_header)

            sec_desc = QLabel(
                "Tu contraseña está protegida con encriptación segura. Puedes actualizarla o restablecerla mediante verificación por correo electrónico si la has olvidado."
            )
            sec_desc.setWordWrap(True)
            sec_desc.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent; line-height: 16px;")
            sec_layout.addWidget(sec_desc)

            btn_open_pw_modal = QPushButton("  Configurar contraseña")
            btn_open_pw_modal.setFixedHeight(36)
            btn_open_pw_modal.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_open_pw_modal.setIcon(get_icon("lock", "#0B0C0E", size=14))
            btn_open_pw_modal.setIconSize(QSize(14, 14))
            btn_open_pw_modal.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ACCENT_GREEN};
                    color: #0B0C0E;
                    border: none;
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px 18px;
                }}
                QPushButton:hover {{
                    background-color: #34D399;
                }}
                QPushButton:pressed {{
                    background-color: #10B981;
                }}
            """)
            btn_open_pw_modal.clicked.connect(self._abrir_modal_contrasena)
            sec_layout.addWidget(btn_open_pw_modal, alignment=Qt.AlignmentFlag.AlignLeft)

            cuenta_layout.addWidget(sec_card)

            # Tarjeta de recomendación de seguridad
            info_text = "Te recomendamos utilizar contraseñas de al menos 8 caracteres con letras mayúsculas, minúsculas y números para mayor protección de tu cuenta."
            cuenta_layout.addWidget(self._build_info_card(info_text))

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
        return field_frame, ent

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
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no puedes modificar el perfil.")
            dialog.exec()
            return
        
        # Acceder directamente al QLineEdit de nombre
        if hasattr(self, 'ent_nombre') and self.ent_nombre:
            nombre = self.ent_nombre.text().strip()
        else:
            ent = self.frame_nombre.findChild(QLineEdit)
            nombre = ent.text().strip() if ent else ""

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
                self.original_nombre = nombre
                self.original_photo_data = self.photo_data
                self.shell.refresh_user()
                self.shell.controller.login_view.load_local_profiles()
                
                dialog = ZenitInfoDialog(self, "Perfil Actualizado", "✓ Tu perfil ha sido actualizado con éxito.")
                dialog.exec()
            except Exception as e:
                dialog = ZenitInfoDialog(self, "Error", f"No se pudieron guardar los cambios: {e}")
                dialog.exec()

    def _revertir_cambios(self):
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no tienes cambios que revertir.")
            dialog.exec()
            return

        uid = self.shell.controller.current_user_id
        original_name = getattr(self, "original_nombre", None)
        original_photo = getattr(self, "original_photo_data", None)

        if not original_name and uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    original_name = data.get("nombre")
                    original_photo = data.get("imagen_data")
                    self.photo_url = data.get("imagen_url")
            except Exception:
                pass

        if not original_name and os.path.exists("local_profiles.json"):
            try:
                with open("local_profiles.json", "r") as f:
                    profiles = json.load(f)
                    if uid in profiles:
                        original_name = profiles[uid].get("nombre")
                        original_photo = profiles[uid].get("imagen_data")
            except Exception:
                pass

        if not original_name:
            original_name = "Usuario"

        self.nombre_val = original_name
        self.photo_data = original_photo
        self.uploaded_image_b64 = None

        # Restaurar inmediatamente el texto en el QLineEdit
        if hasattr(self, 'ent_nombre') and self.ent_nombre:
            self.ent_nombre.setText(self.nombre_val)
        elif hasattr(self, 'frame_nombre') and self.frame_nombre:
            ent = self.frame_nombre.findChild(QLineEdit)
            if ent:
                ent.setText(self.nombre_val)

        self._load_avatar_preview()

        dialog = ZenitInfoDialog(self, "Cambios Descartados", "Se han restablecido los valores originales de tu perfil.")
        dialog.exec()

    def refresh_data(self):
        """Sincroniza y recarga los valores cuando el usuario abre la vista de configuración."""
        uid = self.shell.controller.current_user_id
        if uid == "invitado":
            self.nombre_val = "Invitado"
            self.email_val = "invitado@zenitvision.com"
            self.photo_data = None
        elif uid and uid != "demo_tesis":
            try:
                data = self.shell.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    self.nombre_val = data.get("nombre", "Usuario")
                    self.email_val = data.get("email", "correo@ejemplo.com")
                    self.photo_data = data.get("imagen_data")
                    self.photo_url = data.get("imagen_url")
            except Exception:
                pass

        self.original_nombre = self.nombre_val
        self.original_photo_data = self.photo_data
        self.uploaded_image_b64 = None

        if hasattr(self, 'ent_nombre') and self.ent_nombre:
            self.ent_nombre.setText(self.nombre_val)
        self._load_avatar_preview()

    def _abrir_modal_contrasena(self):
        """Abre el modal de configuración y restablecimiento de contraseña."""
        try:
            from core.audio_manager import AudioManager
            AudioManager.instance().play_click()
        except Exception:
            pass
        if self.shell.controller.current_user_id == "invitado":
            dialog = ZenitInfoDialog(self, "Acceso de Invitado", "Como invitado no tienes una contraseña registrada.")
            dialog.exec()
            return
        
        modal = PasswordSettingsModal(
            self,
            user_id=self.shell.controller.current_user_id,
            user_email=self.email_val,
            user_name=self.nombre_val
        )
        modal.exec()

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
