import os
import json
import base64
# pyrefly: ignore [missing-import]
import bcrypt
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QDialog, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QRectF, QRegularExpression, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QPen, QRegularExpressionValidator, QAction

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BORDER_LIGHT, BG_CARD, FONT_TITLE,
    FREE_TX, BG_SIDEBAR, BG_MAIN, EASY_TX, ACCENT_GREEN, BG_INPUT
)
from ui.icons import get_icon, get_icon_pixmap
from database.google_auth import GoogleAuth
from ui.views.login_view import get_circular_avatar

# ── Generador vectorial de icono de Google a color ───────────────────────────
def get_google_colored_icon(size=18):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    scale = size / 24.0
    painter.scale(scale, scale)
    
    rect = QRectF(4, 4, 16, 16)
    
    # Red (Top)
    pen_red = QPen(QColor("#EA4335"))
    pen_red.setWidthF(3.0)
    painter.setPen(pen_red)
    painter.drawArc(rect, 45 * 16, 90 * 16)
    
    # Yellow (Left)
    pen_yellow = QPen(QColor("#FBBC05"))
    pen_yellow.setWidthF(3.0)
    painter.setPen(pen_yellow)
    painter.drawArc(rect, 135 * 16, 90 * 16)
    
    # Green (Bottom)
    pen_green = QPen(QColor("#34A853"))
    pen_green.setWidthF(3.0)
    painter.setPen(pen_green)
    painter.drawArc(rect, 225 * 16, 90 * 16)
    
    # Blue (Right & Bar)
    pen_blue = QPen(QColor("#4285F4"))
    pen_blue.setWidthF(3.0)
    painter.setPen(pen_blue)
    painter.drawArc(rect, 315 * 16, 45 * 16)
    painter.drawLine(12, 12, 19, 12)
    
    painter.end()
    return QIcon(pixmap)

# ── Modal de Confirmación Custom Premium ─────────────────────────────────────
class ConfirmacionModal(QDialog):
    def __init__(self, parent, title, message, is_success=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(420, 240)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._init_ui(title, message, is_success)

    def _init_ui(self, title, message, is_success):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        accent_color = "#10B981" if is_success else "#EF4444"
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 2px solid {accent_color};
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
        icon_name = "check" if is_success else "info"
        icon_lbl.setPixmap(get_icon_pixmap(icon_name, accent_color, size=32))
        
        title_lbl = QLabel(title)
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
        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"""
            color: {TEXT_GRAY};
            font-size: 12px;
            line-height: 1.4;
            border: none;
            background: transparent;
        """)
        card_layout.addWidget(msg_lbl)

        # Botón Aceptar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_ok = QPushButton("Entendido")
        btn_ok.setFixedSize(120, 36)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #34D399;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        
        card_layout.addLayout(btn_layout)
        layout.addWidget(card)


# ── Texto de Términos y Condiciones ──────────────────────────────────────────
# pyrefly: ignore [missing-import]
from ui.views.terminos import TERMINOS_TEXTO  # Reutilizamos el texto ya redactado

# ── Modal de Términos y Condiciones en PyQt6 ──────────────────────────────────
class TerminosModal(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.accepted_terms = False

        self.setWindowTitle("Términos y Condiciones — Zenit Vision")
        self.setFixedSize(620, 520)
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
                border: 1px solid {BORDER_DARK};
                border-radius: 14px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        header = QLabel("📋  Términos y Condiciones de Uso")
        header.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 15px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        card_layout.addWidget(header)

        # Caja de texto scrollable
        textbox = QTextEdit()
        textbox.setReadOnly(True)
        textbox.setPlainText(TERMINOS_TEXTO.strip())
        textbox.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG_MAIN};
                color: {TEXT_GRAY};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
                font-family: 'Consolas';
                font-size: 11px;
                padding: 10px;
            }}
        """)
        card_layout.addWidget(textbox)

        # Checkbox
        self.chk = QCheckBox("He leído y acepto los Términos y Condiciones de Zenit Vision")
        self.chk.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
        self.chk.stateChanged.connect(self._toggle_button)
        card_layout.addWidget(self.chk)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(36)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setProperty("class", "SecondaryButton")
        btn_cancel.clicked.connect(self.reject)

        self.btn_accept = QPushButton("Aceptar")
        self.btn_accept.setFixedHeight(36)
        self.btn_accept.setDisabled(True)
        self.btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_accept.setProperty("class", "SecondaryButton")
        self.btn_accept.clicked.connect(self._on_accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_accept)
        card_layout.addLayout(btn_layout)

        layout.addWidget(card)

    def _toggle_button(self, state):
        if state == 2:  # Checked
            self.btn_accept.setDisabled(False)
            self.btn_accept.setProperty("class", "PrimaryButton")
        else:
            self.btn_accept.setDisabled(True)
            self.btn_accept.setProperty("class", "SecondaryButton")
        self.btn_accept.style().unpolish(self.btn_accept)
        self.btn_accept.style().polish(self.btn_accept)

    def _on_accept(self):
        self.accepted_terms = True
        self.accept()


# ── Hilos Asíncronos para Google Auth y Email Verification ────────────────────
class GoogleAuthThread(QThread):
    success = pyqtSignal(dict)
    failed = pyqtSignal()

    def run(self):
        try:
            auth = GoogleAuth("google_secrets.json")
            info = auth.login()
            if info:
                self.success.emit(info)
            else:
                self.failed.emit()
        except Exception:
            self.failed.emit()

class VerifyEmailThread(QThread):
    success = pyqtSignal(bool)
    failed = pyqtSignal(str)

    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        try:
            from database import firebase_auth as fb_auth
            ok = fb_auth.is_email_verified(self.email)
            self.success.emit(ok)
        except Exception as e:
            self.failed.emit(str(e))


# ── Vista Principal de Registro en PyQt6 ───────────────────────────────────────
class RegisterView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.controller = main_window
        self.user_image_path = None
        self.terminos_aceptados = False
        
        # Parámetros de registro pendiente por email
        self.pending_email = None
        self.pending_user_id = None
        self.pending_user_name = None
        self.pending_remember = False

        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Tarjeta centradora de Registro (Más compacta para que sea 100% visible en cualquier pantalla)
        self.reg_card = QFrame()
        self.reg_card.setFixedSize(460, 680)  
        self.reg_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 1px solid {BORDER_DARK};
                border-radius: 20px;
            }}
        """)
        
        self.card_layout = QVBoxLayout(self.reg_card)
        self.card_layout.setContentsMargins(40, 15, 40, 15)
        self.card_layout.setSpacing(6)

        # Títulos
        title_lbl = QLabel("Crear cuenta")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 20px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        
        sub_lbl = QLabel("Únete a la comunidad de Zenit Vision")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10px; border: none; background: transparent;")

        self.card_layout.addWidget(title_lbl)
        self.card_layout.addWidget(sub_lbl)

        # Avatar Subir Foto Centrado e Interactivo con mensaje explicativo
        avatar_frame = QFrame()
        avatar_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        avatar_layout = QVBoxLayout(avatar_frame)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setSpacing(4)

        btn_av_container = QHBoxLayout()
        self.btn_av = QPushButton()
        self.btn_av.setFixedSize(60, 60)
        self.btn_av.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_av.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_MAIN};
                border: 2px solid {BORDER_DARK};
                border-radius: 30px;
            }}
            QPushButton:hover {{
                border: 2px solid {ACCENT_GREEN};
            }}
        """)
        self.btn_av.clicked.connect(self._select_image)
        
        btn_av_container.addStretch()
        btn_av_container.addWidget(self.btn_av)
        btn_av_container.addStretch()
        avatar_layout.addLayout(btn_av_container)

        self.lbl_av_prompt = QLabel("Seleccionar foto de perfil (Opcional)")
        self.lbl_av_prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_av_prompt.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        avatar_layout.addWidget(self.lbl_av_prompt)

        self.card_layout.addWidget(avatar_frame)
        self._update_avatar_preview()

        # Campos de Texto (incluyen etiquetas de error individuales en su interior)
        self.ent_name = self._build_input("name", "Nombre completo", "Tu nombre completo")
        self.ent_email = self._build_input("email", "Correo electrónico", "tucorreo@ejemplo.com")
        self.ent_pass = self._build_input("pass", "Contraseña", "Crea una contraseña", is_pw=True)
        self.ent_conf = self._build_input("conf", "Confirmar contraseña", "Repite tu contraseña", is_pw=True)

        # Restricciones físicas en campos de entrada
        self.ent_name.setMaxLength(20)
        self.ent_pass.setMaxLength(20)
        self.ent_conf.setMaxLength(20)

        # Restricción física en Nombre (Regex: solo letras y espacios)
        regex_name = QRegularExpression(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$")
        validator_name = QRegularExpressionValidator(regex_name, self.ent_name)
        self.ent_name.setValidator(validator_name)

        # Conectar validaciones en tiempo real
        self.ent_name.textChanged.connect(self._validate_name_field)
        self.ent_email.textChanged.connect(self._validate_email_field)
        self.ent_pass.textChanged.connect(self._validate_pass_field)
        self.ent_conf.textChanged.connect(self._validate_conf_field)

        # Fila de Checkboxes (Términos y Mantener Abierto)
        checkboxes_container = QFrame()
        checkboxes_container.setStyleSheet("QFrame { background: transparent; border: none; }")
        chk_layout = QVBoxLayout(checkboxes_container)
        chk_layout.setContentsMargins(2, 2, 2, 2)
        chk_layout.setSpacing(4)

        # 1. Fila de Términos (Habilitada directamente y con diseño premium)
        terms_frame = QFrame()
        terms_layout = QHBoxLayout(terms_frame)
        terms_layout.setContentsMargins(0, 0, 0, 0)
        terms_layout.setSpacing(6)

        self.chk_terms = QCheckBox("Leí y acepto los")
        self.chk_terms.setChecked(False)
        self.chk_terms.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_terms.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_GRAY};
                font-size: 11px;
                border: none;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
                background-color: {BG_MAIN};
            }}
            QCheckBox::indicator:checked {{
                border: 1px solid {ACCENT_GREEN};
                background-color: {ACCENT_GREEN};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {ACCENT_GREEN};
            }}
        """)
        self.chk_terms.stateChanged.connect(self._on_terms_checkbox_changed)
        
        btn_terms = QPushButton("términos y condiciones")
        btn_terms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_terms.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; text-decoration: underline; background: transparent; border: none;")
        btn_terms.clicked.connect(self._abrir_terminos)

        terms_layout.addWidget(self.chk_terms)
        terms_layout.addWidget(btn_terms)
        terms_layout.addStretch()

        # 2. Fila de Mantener Abierto (Recordar Sesión)
        remember_frame = QFrame()
        remember_layout = QHBoxLayout(remember_frame)
        remember_layout.setContentsMargins(0, 0, 0, 0)
        remember_layout.setSpacing(8)

        self.chk_remember = QCheckBox("Mantener perfil abierto")
        self.chk_remember.setChecked(True)
        self.chk_remember.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_remember.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_GRAY};
                font-size: 11px;
                border: none;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
                background-color: {BG_MAIN};
            }}
            QCheckBox::indicator:checked {{
                border: 1px solid {ACCENT_GREEN};
                background-color: {ACCENT_GREEN};
            }}
        """)
        remember_layout.addWidget(self.chk_remember)
        remember_layout.addStretch()

        chk_layout.addWidget(terms_frame)
        chk_layout.addWidget(remember_frame)
        self.card_layout.addWidget(checkboxes_container)

        # Etiqueta de Error/Estado Global (Mantenida por compatibilidad)
        self.lbl_err = QLabel("")
        self.lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_err.setWordWrap(True)
        self.lbl_err.setStyleSheet("color: #E05A5A; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        self.card_layout.addWidget(self.lbl_err)

        # Botón de Registrarse (Vibrante gradiente verde esmeralda con texto blanco)
        self.btn_register = QPushButton(" Crear cuenta")
        self.btn_register.setFixedHeight(36)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.setIcon(get_icon("profile", "#FFFFFF", size=16))
        self.btn_register.setIconSize(QSize(16, 16))
        self.btn_register.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_GREEN}, stop:1 #059669);
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 {ACCENT_GREEN});
                border: 1px solid #34D399;
            }}
            QPushButton:pressed {{
                background-color: #047857;
            }}
        """)
        self.btn_register.clicked.connect(self._register_user)
        self.card_layout.addWidget(self.btn_register)

        # Botón dinámico de Verificar Correo (Inicialmente oculto)
        self.btn_verify = QPushButton(" Verificar correo ahora")
        self.btn_verify.setFixedHeight(32)
        self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify.setProperty("class", "SecondaryButton")
        self.btn_verify.setIcon(get_icon("check", ACCENT_GREEN, size=14))
        self.btn_verify.setIconSize(QSize(14, 14))
        self.btn_verify.clicked.connect(lambda: self._verify_email_now(is_manual=True))
        self.btn_verify.hide()
        self.card_layout.addWidget(self.btn_verify)

        # Divisor (Línea sutil visible)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px; border: none; margin: 4px 0;")
        self.card_layout.addWidget(sep)

        # Botón Google (Estilo Oficial a color con logo vectorizado)
        self.btn_google = QPushButton(" Registrarse con Google")
        self.btn_google.setFixedHeight(36)
        self.btn_google.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_google.setIcon(get_google_colored_icon(size=18))
        self.btn_google.setIconSize(QSize(18, 18))
        self.btn_google.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #3C4043;
                border: 1px solid #DADCE0;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #F8F9FA;
                border: 1px solid #747775;
                color: #1F2937;
            }}
            QPushButton:pressed {{
                background-color: #F1F3F4;
            }}
            QPushButton:disabled {{
                background-color: #F5F5F5;
                color: #A0A0A0;
                border: 1px solid #E0E0E0;
            }}
        """)
        self.btn_google.clicked.connect(self._start_google_login)
        self.card_layout.addWidget(self.btn_google)

        # Iniciar sesión link
        login_row = QFrame()
        login_row.setStyleSheet("QFrame { background: transparent; border: none; }")
        login_row_layout = QHBoxLayout(login_row)
        login_row_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_acc = QLabel("¿Ya tienes cuenta?")
        lbl_acc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
        
        btn_log = QPushButton("Iniciar sesión")
        btn_log.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_log.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        btn_log.clicked.connect(self._on_iniciar_sesion_clicked)

        login_row_layout.addWidget(lbl_acc)
        login_row_layout.addWidget(btn_log)
        self.card_layout.addWidget(login_row, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.reg_card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_input(self, label_key, label_text, placeholder, is_pw=False):
        field = QFrame()
        field.setStyleSheet("QFrame { background: transparent; border: none; }")
        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        lbl = QLabel(label_text.upper())
        lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 9px; font-weight: bold; letter-spacing: 0.5px; border: none; background: transparent;")
        
        ent = QLineEdit()
        ent.setPlaceholderText(placeholder)
        
        ent.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER_DARK};
                border-radius: 8px;
                color: {TEXT_WHITE};
                font-size: 11px;
                padding: 7px 10px;
            }}
            QLineEdit:hover {{
                border: 1px solid {BORDER_LIGHT};
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_GREEN};
                background-color: {BG_MAIN};
            }}
        """)

        if is_pw:
            ent.setEchoMode(QLineEdit.EchoMode.Password)
            # Botón del ojo inline en QLineEdit
            eye_icon = get_icon("eye", TEXT_MUTED, size=16)
            action = ent.addAction(eye_icon, QLineEdit.ActionPosition.TrailingPosition)
            action.setData(ent)
            action.triggered.connect(self._on_toggle_password_visibility)

        err_lbl = QLabel("")
        err_lbl.setStyleSheet("color: #EF4444; font-size: 9px; border: none; background: transparent;")
        err_lbl.setWordWrap(True)
        err_lbl.hide()

        layout.addWidget(lbl)
        layout.addWidget(ent)
        layout.addWidget(err_lbl)
        self.card_layout.addWidget(field)

        setattr(self, f"err_{label_key}", err_lbl)

        return ent

    def _on_toggle_password_visibility(self):
        action = self.sender()
        if not action:
            return
        ent = action.data()
        if not ent:
            return
            
        if ent.echoMode() == QLineEdit.EchoMode.Password:
            ent.setEchoMode(QLineEdit.EchoMode.Normal)
            action.setIcon(get_icon("eye", ACCENT_GREEN, size=16))
        else:
            ent.setEchoMode(QLineEdit.EchoMode.Password)
            action.setIcon(get_icon("eye", TEXT_MUTED, size=16))

    def _set_field_error(self, key, message):
        err_lbl = getattr(self, f"err_{key}")
        err_lbl.setText(f"⚠ {message}")
        err_lbl.show()
        
        ent = getattr(self, f"ent_{key}")
        ent.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid #EF4444;
                border-radius: 8px;
                color: {TEXT_WHITE};
                font-size: 11px;
                padding: 7px 10px;
            }}
            QLineEdit:hover {{
                border: 1px solid #F87171;
            }}
            QLineEdit:focus {{
                border: 1px solid #EF4444;
                background-color: {BG_MAIN};
            }}
        """)

    def _set_field_success(self, key):
        err_lbl = getattr(self, f"err_{key}")
        err_lbl.setText("")
        err_lbl.hide()
        
        ent = getattr(self, f"ent_{key}")
        ent.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid #10B981;
                border-radius: 8px;
                color: {TEXT_WHITE};
                font-size: 11px;
                padding: 7px 10px;
            }}
            QLineEdit:hover {{
                border: 1px solid #34D399;
            }}
            QLineEdit:focus {{
                border: 1px solid #10B981;
                background-color: {BG_MAIN};
            }}
        """)

    # ── VALIDACIONES EN TIEMPO REAL ──────────────────────────────────────────
    def _validate_name_field(self):
        name = self.ent_name.text().strip()
        if not name:
            self._set_field_error("name", "El nombre es obligatorio")
            return False
        self._set_field_success("name")
        return True

    def _validate_email_field(self):
        email = self.ent_email.text().strip()
        if not email:
            self._set_field_success("email")
            return True
        if "@" not in email or "." not in email:
            self._set_field_error("email", "Formato de correo no válido")
            return False
        self._set_field_success("email")
        return True

    def _validate_pass_field(self):
        pw = self.ent_pass.text()
        if not pw:
            self._set_field_error("pass", "La contraseña es obligatoria")
            return False
        if len(pw) < 8:
            self._set_field_error("pass", "Mínimo 8 caracteres")
            return False
        if len(pw) > 20:
            self._set_field_error("pass", "Máximo 20 caracteres")
            return False
        self._set_field_success("pass")
        if self.ent_conf.text():
            self._validate_conf_field()
        return True

    def _validate_conf_field(self):
        pw = self.ent_pass.text()
        pw_conf = self.ent_conf.text()
        if not pw_conf:
            self._set_field_error("conf", "Confirma tu contraseña")
            return False
        if pw != pw_conf:
            self._set_field_error("conf", "Las contraseñas no coinciden")
            return False
        self._set_field_success("conf")
        return True

    def _on_terms_checkbox_changed(self, state):
        self.terminos_aceptados = (state == 2)

    def _update_avatar_preview(self):
        size = 56
        avatar_pixmap = get_circular_avatar(size, "US", 1, photo_data=None, photo_url=None) # Index 1 is emerald green
        if self.user_image_path:
            try:
                with open(self.user_image_path, "rb") as f:
                    data_b64 = base64.b64encode(f.read()).decode()
                avatar_pixmap = get_circular_avatar(size, "US", 1, photo_data=data_b64)
            except Exception:
                pass
        self.btn_av.setIcon(QIcon(avatar_pixmap))
        self.btn_av.setIconSize(QSize(size, size))

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar avatar", "", "Imágenes (*.jpg *.png)")
        if path:
            self.user_image_path = path
            self._update_avatar_preview()
            self.lbl_av_prompt.setText("✓ Foto de perfil cargada")
            self.lbl_av_prompt.setStyleSheet(f"color: {EASY_TX}; font-size: 10px; font-weight: bold; border: none; background: transparent;")

    def _abrir_terminos(self):
        dlg = TerminosModal(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.accepted_terms:
            self.chk_terms.setChecked(True)
            self.terminos_aceptados = True
            self.lbl_err.setText("")

    # ── LÓGICA DE REGISTRO MANUAL ─────────────────────────────────────────────
    def _register_user(self):
        name = self.ent_name.text().strip()
        email = self.ent_email.text().strip()
        pw = self.ent_pass.text()
        pw_c = self.ent_conf.text()

        # Ejecutar validaciones antes de procesar
        val_name = self._validate_name_field()
        val_email = self._validate_email_field()
        val_pass = self._validate_pass_field()
        val_conf = self._validate_conf_field()

        if not (val_name and val_email and val_pass and val_conf):
            self._error("Por favor, corrige los errores en el formulario.")
            return

        if not self.terminos_aceptados:
            self._error("Debes aceptar los términos y condiciones.")
            return

        img_b64 = ""
        if self.user_image_path:
            try:
                from PIL import Image
                from io import BytesIO
                with Image.open(self.user_image_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((150, 150))
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode()
            except Exception:
                pass

        try:
            # pyrefly: ignore [missing-import]
            import bcrypt
            hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            uid = name.lower().replace(" ", "_")

            # Flujo con Email (Requiere Verificación Firebase Auth)
            if email:
                from database import firebase_auth as fb_auth
                fb_uid = None
                try:
                    fb_uid = fb_auth.create_user_with_email_and_password(email, pw)
                except Exception as e:
                    err_str = str(e).lower()
                    if "already exists" in err_str or "email-already-exists" in err_str or "already in use" in err_str:
                        self._error("El correo electrónico ya está registrado por otro usuario.")
                        return
                    else:
                        self._error(f"Error al crear el usuario: {e}")
                        return
                
                email_sent = False
                verification_link = ""
                try:
                    email_sent, verification_link = fb_auth.send_verification_email(email, pw, name)
                except Exception as e:
                    self._error(f"Error al iniciar verificación: {e}")
                    return
                
                # Escribir registro inactivo en la nube
                existing = self.controller.fb_db.read_record(f"users/{uid}")
                if existing:
                    upd = {"email": email, "auth_provider": "email", "email_verified": False}
                    if fb_uid: upd["firebase_uid"] = fb_uid
                    if img_b64: upd["imagen_data"] = img_b64
                    self.controller.fb_db.update_record(f"users/{uid}", upd)
                else:
                    self.controller.fb_db.write_record(f"users/{uid}", {
                        "nombre": name, "email": email, "password": hashed,
                        "imagen_data": img_b64, "auth_provider": "email",
                        "email_verified": False, "firebase_uid": fb_uid or "",
                        "puntos": 0, "nivel": 1,
                    })

                self.pending_email = email
                self.pending_user_id = uid
                self.pending_user_name = name

                self.lbl_err.setText(f"Esperando verificación en tiempo real...")
                self.lbl_err.setStyleSheet(f"color: {ACCENT_GREEN}; font-size: 10px; font-weight: bold; border: none;")
                self.btn_verify.show()
                
                # Iniciar el temporizador de verificación automática (sondeo silencioso) ANTES de mostrar el modal
                if not hasattr(self, "verify_timer") or self.verify_timer is None:
                    self.verify_timer = QTimer(self)
                    self.verify_timer.timeout.connect(self._verify_email_now)
                self.verify_timer.start(2000) # Cada 2 segundos

                if email_sent:
                    self.active_confirm_modal = ConfirmacionModal(self, "Verificación de Correo", f"Hemos enviado un enlace de verificación a: {email}\n\nEl sistema activará tu cuenta en tiempo real de forma automática cuando hagas clic en el enlace del correo.", is_success=True)
                    self.active_confirm_modal.exec()
                    self.active_confirm_modal = None
                else:
                    import webbrowser
                    try:
                        webbrowser.open(verification_link)
                    except Exception:
                        pass
                    
                    print(f"\n[Auth] Límite de Google detectado. Enlace de activación directa:\n{verification_link}\n")
                    
                    self.active_confirm_modal = ConfirmacionModal(
                        self, 
                        "Activación de Cuenta Directa", 
                        f"⚠️ Límite de envíos de Google detectado para tu red.\n\nHemos abierto automáticamente el enlace de verificación en tu navegador web para que verifiques tu cuenta de inmediato y sin esperar.\n\nAl activarlo en tu navegador, la app se iniciará de forma automática en tiempo real.", 
                        is_success=True
                    )
                    self.active_confirm_modal.exec()
                    self.active_confirm_modal = None
                
                return

            # Flujo Manual (Sin Email)
            self.controller.fb_db.write_record(f"users/{uid}", {
                "nombre": name, "password": hashed,
                "imagen_data": img_b64, "auth_provider": "manual",
                "puntos": 0, "nivel": 1,
            })
            self._save_local(uid, name, self.chk_remember.isChecked())
            
            modal = ConfirmacionModal(self, "¡Registro Exitoso!", f"Tu perfil '{name}' ha sido creado correctamente en Zenit-Visión.", is_success=True)
            modal.exec()

            self.controller.login_view.load_local_profiles()
            self.controller.show_login()

        except Exception as e:
            self._error(f"Error técnico: {e}")

    # ── VALIDACIÓN ASÍNCRONA DE VERIFICACIÓN ──────────────────────────────────
    def _verify_email_now(self, is_manual=False):
        if not self.pending_email:
            return
        # Evitar duplicar hilos de sondeo si ya hay uno corriendo
        if hasattr(self, "verify_thread") and self.verify_thread.isRunning():
            return
            
        if is_manual:
            self.lbl_err.setText("Verificando...")
            self.lbl_err.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10px; border: none;")
        
        self.verify_thread = VerifyEmailThread(self.pending_email)
        self.verify_thread.success.connect(lambda ok, m=is_manual: self._on_email_verified(ok, m))
        self.verify_thread.failed.connect(lambda err: self._error(f"Error: {err}") if is_manual else None)
        self.verify_thread.start()

    def _on_email_verified(self, ok, is_manual=False):
        if not ok:
            if is_manual:
                self._error("Aún no verificado. Revisa tu bandeja de correo.")
            return
        
        # Detener el temporizador de sondeo de fondo al verificar con éxito
        if hasattr(self, "verify_timer") and self.verify_timer is not None:
            if self.verify_timer.isActive():
                self.verify_timer.stop()
            
        uid = self.pending_user_id
        name = self.pending_user_name
        
        try:
            self.controller.fb_db.update_record(f"users/{uid}", {"email_verified": True})
            self._save_local(uid, name, self.chk_remember.isChecked())
        except Exception:
            pass

        # Cerrar programáticamente el modal de espera activo si está abierto
        if hasattr(self, "active_confirm_modal") and self.active_confirm_modal is not None:
            try:
                self.active_confirm_modal.accept()
            except Exception:
                pass
            self.active_confirm_modal = None

        modal = ConfirmacionModal(self, "¡Cuenta Activada!", "Tu correo electrónico ha sido verificado con éxito y tu cuenta ya está lista para usarse.", is_success=True)
        modal.exec()

        self.controller.login_view.load_local_profiles()
        self.controller.show_login()

    # ── INICIO DE SESIÓN DE GOOGLE ASÍNCRONO ─────────────────────────────────
    def _start_google_login(self):
        if not self.terminos_aceptados:
            self._error("Debes aceptar los términos y condiciones.")
            return

        self.btn_google.setDisabled(True)
        self.btn_google.setText("Revisa tu navegador...")
        self.lbl_err.setText("Autenticando con Google...")
        self.lbl_err.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 10px; border: none;")

        self.google_thread = GoogleAuthThread()
        self.google_thread.success.connect(self._on_google_success)
        self.google_thread.failed.connect(self._on_google_failed)
        self.google_thread.start()

    def _on_google_success(self, info):
        try:
            uid = info["email"].replace(".", "_").replace("@", "_")
            self.controller.fb_db.write_record(f"users/{uid}", {
                "nombre": info["name"], "email": info["email"],
                "imagen_url": info.get("picture", ""),
                "auth_provider": "google", "puntos": 0, "nivel": 1,
            })
            self._save_local(uid, info["name"], self.chk_remember.isChecked())
            
            modal = ConfirmacionModal(self, "¡Sesión Iniciada con Google!", f"Bienvenido(a) a Zenit-Visión, {info['name']}.", is_success=True)
            modal.exec()
            
            # Recargar y login
            self.controller.login_view.load_local_profiles()
            self.controller.login_success(uid)
        except Exception as e:
            self._error(f"Error Google: {e}")
            self._on_google_failed()

    def _on_google_failed(self):
        self.btn_google.setDisabled(False)
        self.btn_google.setIcon(get_google_colored_icon(size=18))
        self.btn_google.setText(" Registrarse con Google")
        
        modal = ConfirmacionModal(self, "Autenticación Cancelada", "La conexión con Google fue cancelada o no se pudo completar.", is_success=False)
        modal.exec()
        
        self._error("Autenticación con Google cancelada o fallida.")

    # ── Métodos de Limpieza y Transición ──
    def clear_form(self):
        # Detener temporizador de sondeo si está activo
        if hasattr(self, "verify_timer") and self.verify_timer is not None:
            if self.verify_timer.isActive():
                self.verify_timer.stop()
        self.pending_email = None
        self.pending_user_id = None
        self.pending_user_name = None
        if hasattr(self, "btn_verify"):
            self.btn_verify.hide()
            
        # Limpiar inputs
        self.ent_name.clear()
        self.ent_email.clear()
        self.ent_pass.clear()
        self.ent_conf.clear()
        
        # Limpiar avatar y path
        self.user_image_path = None
        self._update_avatar_preview()
        self.lbl_av_prompt.setText("Seleccionar foto de perfil (Opcional)")
        self.lbl_av_prompt.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; border: none; background: transparent;")
        
        # Limpiar checkbox de términos
        self.chk_terms.setChecked(False)
        self.terminos_aceptados = False
        
        # Limpiar error global
        self.lbl_err.setText("")
        
        # Ocultar y restaurar estilos de campos individuales
        for key in ["name", "email", "pass", "conf"]:
            err_lbl = getattr(self, f"err_{key}")
            err_lbl.setText("")
            err_lbl.hide()
            
            ent = getattr(self, f"ent_{key}")
            ent.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {BG_INPUT};
                    border: 1px solid {BORDER_DARK};
                    border-radius: 8px;
                    color: {TEXT_WHITE};
                    font-size: 11px;
                    padding: 7px 10px;
                }}
                QLineEdit:hover {{
                    border: 1px solid {BORDER_LIGHT};
                }}
                QLineEdit:focus {{
                    border: 1px solid {ACCENT_GREEN};
                    background-color: {BG_MAIN};
                }}
            """)

    def _on_iniciar_sesion_clicked(self):
        self.clear_form()
        self.controller.show_login()

    # ── Utilidades ──
    def _error(self, text):
        self.lbl_err.setText(f"❌ {text}")
        self.lbl_err.setStyleSheet("color: #E05A5A; font-size: 10px; font-weight: bold; border: none; background: transparent;")

    def _save_local(self, uid, name, remember):
        profiles = {}
        if os.path.exists("local_profiles.json"):
            try:
                with open("local_profiles.json", "r") as f:
                    profiles = json.load(f)
            except Exception:
                profiles = {}
        profiles[uid] = {"nombre": name, "remember": remember}
        with open("local_profiles.json", "w") as f:
            json.dump(profiles, f)



