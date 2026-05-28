import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QPushButton, QLabel, QSpacerItem, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap

from database.firebase_database import FirebaseDB
from ui.styles import (
    GLOBAL_STYLESHEET, BG_MAIN, BORDER_DARK, TEXT_WHITE, TEXT_GRAY, 
    ACCENT_GREEN, HARD_TX, BG_SIDEBAR, TEXT_MUTED, FONT_TITLE
)
from ui.icons import get_icon, get_state_icon, get_icon_pixmap

class LogoutConfirmModal(QDialog):
    def __init__(self, parent, is_guest=False):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Salida")
        self.setFixedSize(400, 240)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._init_ui(is_guest)

    def _init_ui(self, is_guest):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        accent_color = HARD_TX if is_guest else ACCENT_GREEN
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
                border: 2px solid {accent_color};
                border-radius: 14px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        # Icono y Título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon_pixmap("logout", accent_color, size=32))
        
        title_lbl = QLabel("Cerrar Sesión")
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

        # Mensaje adaptativo
        if is_guest:
            msg_text = (
                "⚠️ ATENCIÓN: Estás en una sesión de Invitado.\n\n"
                "Al cerrar la sesión, todos tus entrenamientos libres, estadísticas temporales y progresos se BORRARÁN por completo de forma irreversible."
            )
        else:
            msg_text = "¿Estás seguro de que deseas cerrar tu sesión en Zenit-Visión?"

        msg_lbl = QLabel(msg_text)
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
        
        btn_ok = QPushButton("Cerrar sesión")
        btn_ok.setFixedSize(110, 34)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: {"#FFFFFF" if is_guest else "#000000"};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {"#DC2626" if is_guest else "#34D399"};
            }}
        """)
        btn_ok.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(card)

class AppShell(QWidget):
    """
    Contenedor principal para la parte autenticada de la aplicación.
    Estructura: Sidebar (Izquierda) + QStackedWidget para contenido (Derecha).
    """
    def __init__(self, parent_window):
        super().__init__()
        self.controller = parent_window
        self._content_widgets = {}
        self._active_key = "dashboard"
        self._init_ui()

    def _init_ui(self):
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 1. Sidebar (Panel Izquierdo) ─────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(200)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(14, 20, 14, 20)
        sidebar_layout.setSpacing(10)

        # Logo / Marca
        self.logo_label = QLabel()
        self.logo_label.setObjectName("SidebarLogo")
        logo_path = os.path.join("assets", "icon", "Zenit_Vision_Logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        
        brand_title = QLabel("ZENIT ")
        brand_title.setStyleSheet(f"font-family: 'Arial Black'; font-size: 13px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        brand_title_accent = QLabel("VISION")
        brand_title_accent.setStyleSheet(f"font-family: 'Arial Black'; font-size: 13px; color: {ACCENT_GREEN}; font-weight: bold; border: none; background: transparent;")

        title_row = QFrame()
        title_row.setStyleSheet("background: transparent; border: none;")
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(0)
        title_row_layout.addWidget(brand_title)
        title_row_layout.addWidget(brand_title_accent)

        brand_subtitle = QLabel("MODO EXPLORADOR")
        brand_subtitle.setStyleSheet("font-size: 7px; color: #626A7A; font-weight: bold; border: none; background: transparent;")

        text_container = QFrame()
        text_container.setStyleSheet("background: transparent; border: none;")
        text_container_layout = QVBoxLayout(text_container)
        text_container_layout.setContentsMargins(0, 0, 0, 0)
        text_container_layout.setSpacing(0)
        text_container_layout.addWidget(title_row)
        text_container_layout.addWidget(brand_subtitle)

        logo_container = QFrame()
        logo_container.setStyleSheet("background: transparent; border: none;")
        logo_container_layout = QHBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(0, 0, 0, 10)
        logo_container_layout.setSpacing(8)
        logo_container_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        logo_container_layout.addWidget(text_container, alignment=Qt.AlignmentFlag.AlignVCenter)
        sidebar_layout.addWidget(logo_container)

        # Divisor sutil
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px;")
        sidebar_layout.addWidget(sep)

        # Botones de navegación
        self.nav_buttons = {}
        items = [
            ("dashboard", "home", " Inicio"),
            ("ejercicios", "exercises", " Ejercicios"),
            ("estadisticas", "stats", " Estadísticas"),
            ("configuracion", "settings", " Configuración"),
        ]

        for key, icon_name, label in items:
            btn = QPushButton(label)
            btn.setProperty("class", "NavButton")
            btn.setCheckable(True)
            btn.setFixedHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Asignar icono vectorial interactivo
            icon = get_state_icon(icon_name, TEXT_GRAY, TEXT_WHITE, ACCENT_GREEN, size=18)
            btn.setIcon(icon)
            btn.setIconSize(QSize(18, 18))
            
            btn.clicked.connect(lambda checked, k=key: self.navigate(k))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        # Espaciador para empujar elementos al final
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Divisor inferior
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px;")
        sidebar_layout.addWidget(sep2)

        # Fila de Usuario
        self.user_card = QFrame()
        self.user_card.setObjectName("UserCard")
        user_layout = QVBoxLayout(self.user_card)
        user_layout.setContentsMargins(10, 10, 10, 10)

        self.username_label = QLabel("Usuario")
        self.username_label.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold;")
        self.user_level_label = QLabel("Nivel 1 · Explorador")
        self.user_level_label.setStyleSheet("color: #626A7A; font-size: 9px;")
        
        user_layout.addWidget(self.username_label)
        user_layout.addWidget(self.user_level_label)
        sidebar_layout.addWidget(self.user_card)

        # Botón de Cerrar Sesión
        self.logout_btn = QPushButton(" Cerrar sesión")
        self.logout_btn.setProperty("class", "DangerButton")
        self.logout_btn.setFixedHeight(30)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setIcon(get_icon("logout", HARD_TX, size=14))
        self.logout_btn.setIconSize(QSize(14, 14))
        self.logout_btn.clicked.connect(self._logout)
        sidebar_layout.addWidget(self.logout_btn)

        main_layout.addWidget(self.sidebar)

        # ── 2. Área de Contenido (Stacked Widget Derecho) ──────────────────────
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("MainContent")
        main_layout.addWidget(self.content_stack)

    def navigate(self, key):
        self._active_key = key

        # Actualizar estado Checked de los botones
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)

        # Cargar de forma perezosa (lazy) la vista correspondiente
        widget = self._get_or_create(key)
        self.content_stack.setCurrentWidget(widget)

    def _get_or_create(self, key):
        if key not in self._content_widgets:
            widget = None
            if key == "dashboard":
                # importación diferida
                from ui.views.dashboard_view import DashboardView
                widget = DashboardView(self)
            elif key == "ejercicios":
                from ui.views.ejercicios_view import EjerciciosView
                widget = EjerciciosView(self)
            elif key == "estadisticas":
                from ui.views.estadisticas_view import EstadisticasView
                widget = EstadisticasView(self)
            elif key == "configuracion":
                from ui.views.configuracion_view import ConfiguracionView
                widget = ConfiguracionView(self)
            
            if widget:
                self._content_widgets[key] = widget
                self.content_stack.addWidget(widget)
        return self._content_widgets[key]

    def refresh_user(self):
        """Actualiza la tarjeta de usuario en el sidebar."""
        uid = self.controller.current_user_id
        if uid == "invitado":
            self.username_label.setText("Invitado")
            self.user_level_label.setText("Entrenamiento Libre")
            return
        if uid:
            try:
                data = self.controller.fb_db.read_record(f"users/{uid}")
                if data:
                    nombre = data.get("nombre", "Usuario")
                    nivel = data.get("nivel", 1)
                    self.username_label.setText(nombre[:15])
                    self.user_level_label.setText(f"Nivel {nivel} · Explorador")
            except Exception:
                pass

    def _logout(self):
        uid = self.controller.current_user_id
        is_guest = (uid == "invitado")
        
        dlg = LogoutConfirmModal(self, is_guest=is_guest)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        self.controller.current_user_id = None
        # Limpiar widgets cargados para forzar recreación
        for w in list(self._content_widgets.values()):
            self.content_stack.removeWidget(w)
            w.deleteLater()
        self._content_widgets.clear()
        
        # Redirigir a login
        self.controller.show_login()


class MainWindow(QMainWindow):
    """
    Controlador maestro de la ventana principal de la aplicación.
    Maneja el ruteo general usando QStackedWidget y la conexión a Firebase.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Zenit Vision — PyQt6 Premium")
        self.setMinimumSize(1180, 750)
        self.resize(1180, 750)

        # Aplicar hoja de estilos global
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # Configuración de base de datos
        self.fb_db = FirebaseDB("firebase.json", "https://zenit-vision-default-rtdb.firebaseio.com/")
        
        # Estado Global de la Sesión
        self.current_user_id = None
        self.ejercicio_actual = None

        # Contenedor central apilado
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # App Shell Autenticado
        self.shell = AppShell(self)
        self.central_stack.addWidget(self.shell)

        # Iniciar mostrando el login
        self.show_login()

    def show_login(self):
        # Mostraremos la vista del login en PyQt6 (se creará a continuación)
        try:
            from ui.views.login_view import LoginView
            if not hasattr(self, 'login_view'):
                self.login_view = LoginView(self)
                self.central_stack.addWidget(self.login_view)
            self.central_stack.setCurrentWidget(self.login_view)
        except ImportError:
            print("[Zenit-Vision] LoginView aún no implementado en ui/views/")

    def show_register(self):
        try:
            from ui.views.register_view import RegisterView
            if not hasattr(self, 'register_view'):
                self.register_view = RegisterView(self)
                self.central_stack.addWidget(self.register_view)
            else:
                self.register_view.clear_form()
            self.central_stack.setCurrentWidget(self.register_view)
        except ImportError:
            print("[Zenit-Vision] RegisterView aún no implementado en ui/views/")

    def login_success(self, user_id):
        self.current_user_id = user_id
        self.shell.refresh_user()
        self.central_stack.setCurrentWidget(self.shell)
        self.shell.navigate("dashboard")
