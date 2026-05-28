from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from datetime import datetime

from ui.styles import (
    TEXT_WHITE, TEXT_GRAY, TEXT_MUTED, BORDER_DARK, BG_CARD, FONT_TITLE,
    EASY_BG, EASY_BRD, EASY_TX,
    NORM_BG, NORM_BRD, NORM_TX,
    HARD_BG, HARD_BRD, HARD_TX,
    FREE_BG, FREE_BRD, FREE_TX, BG_MAIN
)
from ui.icons import get_icon, get_icon_pixmap

def get_current_date_spanish():
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    now = datetime.now()
    return f"{now.day} {months[now.month]} {now.year}"

# ── Catálogo de Datos de Retos en PyQt6 ───────────────────────────────────────
RETOS_DATA = [
    {
        "id": "reto_principiante",
        "nombre": "Reto Principiante",
        "dificultad": "facil",
        "descripcion": "Ejercicios básicos con tiempo suficiente para aprender la técnica correcta.",
        "tiempo": "10 minutos",
        "tiempo_lbl": "tiempo total",
        "ejercicios": [
            ("Sentadillas", "15 reps", "squat"),
            ("Lagartijas", "10 reps", "pushup"),
            ("Jumping Jacks", "20 reps", "jumping_jacks")
        ],
        "btn_text": "Comenzar reto",
        "color_bg": EASY_BG,
        "color_brd": EASY_BRD,
        "color_tx": EASY_TX,
        "badge": "FÁCIL"
    },
    {
        "id": "reto_estandar",
        "nombre": "Reto Estándar",
        "dificultad": "normal",
        "descripcion": "Nivel intermedio con intensidad moderada. Ideal para una rutina activa diaria.",
        "tiempo": "20 minutos",
        "tiempo_lbl": "tiempo total",
        "ejercicios": [
            ("Sentadillas", "30 reps", "squat"),
            ("Lagartijas", "20 reps", "pushup"),
            ("Jumping Jacks", "40 reps", "jumping_jacks")
        ],
        "btn_text": "Comenzar reto",
        "color_bg": NORM_BG,
        "color_brd": NORM_BRD,
        "color_tx": NORM_TX,
        "badge": "NORMAL"
    },
    {
        "id": "reto_avanzado",
        "nombre": "Reto Avanzado",
        "dificultad": "dificil",
        "descripcion": "Alta intensidad para usuarios experimentados. Lleva tu cuerpo al límite.",
        "tiempo": "35 minutos",
        "tiempo_lbl": "tiempo total",
        "ejercicios": [
            ("Sentadillas", "60 reps", "squat"),
            ("Lagartijas", "40 reps", "pushup"),
            ("Jumping Jacks", "80 reps", "jumping_jacks")
        ],
        "btn_text": "Comenzar reto",
        "color_bg": HARD_BG,
        "color_brd": HARD_BRD,
        "color_tx": HARD_TX,
        "badge": "DIFÍCIL"
    },
    {
        "id": "ejercicio_libre",
        "nombre": "Ejercicio Libre",
        "dificultad": "libre",
        "descripcion": "Sin metas fijas. Entrena a tu ritmo. La cámara registra todo el movimiento.",
        "tiempo": "Sin límite",
        "tiempo_lbl": "a tu ritmo",
        "ejercicios": [
            ("Sentadillas", "Libre", "squat"),
            ("Lagartijas", "Libre", "pushup"),
            ("Jumping Jacks", "Libre", "jumping_jacks")
        ],
        "btn_text": "Comenzar sesión",
        "color_bg": FREE_BG,
        "color_brd": FREE_BRD,
        "color_tx": FREE_TX,
        "badge": "LIBRE"
    }
]

class EjerciciosView(QWidget):
    def __init__(self, shell_parent):
        super().__init__()
        self.shell = shell_parent
        self._init_ui()

    def _init_ui(self):
        # Layout vertical principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(14)

        # ── 1. Cabecera (Header) ─────────────────────────────────────────────
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Título y Subtítulo
        title_container = QFrame()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)

        title_lbl = QLabel("Selecciona tu reto")
        title_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 22px; color: {TEXT_WHITE}; font-weight: bold;")
        sub_lbl = QLabel("Elige la dificultad y comienza")
        sub_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_GRAY};")

        title_layout.addWidget(title_lbl)
        title_layout.addWidget(sub_lbl)
        header_layout.addWidget(title_container)

        # Widget de fecha derecha
        date_card = QFrame()
        date_card.setStyleSheet(f"background-color: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 5px;")
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(14, 6, 14, 6)

        date_lbl = QLabel(get_current_date_spanish())
        date_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        date_layout.addWidget(date_lbl)
        
        header_layout.addWidget(date_card, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(header_frame)

        # ── 2. Cuadrícula de Desafíos (2x2 Grid) ─────────────────────────────
        grid_widget = QFrame()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)

        for idx, data in enumerate(RETOS_DATA):
            row = idx // 2
            col = idx % 2
            card = self._build_challenge_card(data)
            grid_layout.addWidget(card, row, col)

        main_layout.addWidget(grid_widget)

    def _build_challenge_card(self, data):
        card = QFrame()
        card.setProperty("class", "Card")
        # Aplicamos el borde y fondo de la tarjeta de acuerdo al mockup
        card.setStyleSheet(f"""
            QFrame.Card {{
                background-color: {BG_CARD};
                border: 1px solid {data['color_brd']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Badge e Icono de dificultad arriba a la derecha
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        
        badge_lbl = QLabel(data["badge"])
        badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_lbl.setFixedSize(64, 20)
        badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {data['color_bg']};
                color: {data['color_tx']};
                border-radius: 4px;
                font-size: 9px;
                font-weight: bold;
                border: none;
            }}
        """)
        badge_row.addWidget(badge_lbl)
        badge_row.addStretch()
        
        tr_icon = QLabel()
        tr_icon.setFixedSize(14, 14)
        icon_name = "streak"
        if data["id"] == "reto_estandar":
            icon_name = "stats"
        elif data["id"] == "ejercicio_libre":
            icon_name = "clock"
            
        tr_icon.setPixmap(get_icon_pixmap(icon_name, data["color_tx"], size=14))
        tr_icon.setStyleSheet("border: none; background: transparent;")
        badge_row.addWidget(tr_icon)
        
        layout.addLayout(badge_row)

        # Nombre / Título
        name_lbl = QLabel(data["nombre"])
        name_lbl.setStyleSheet(f"font-family: '{FONT_TITLE}'; font-size: 19px; color: {TEXT_WHITE}; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(name_lbl)

        # La descripción se ha eliminado por completo para evitar espacios vacíos y mantener las tarjetas compactas

        # Barra de Tiempo
        time_bar = QFrame()
        time_bar.setFixedHeight(34)
        time_bar.setStyleSheet(f"background-color: {data['color_bg']}; border: none; border-radius: 5px;")
        time_layout = QHBoxLayout(time_bar)
        time_layout.setContentsMargins(12, 0, 12, 0)
        time_layout.setSpacing(6)

        time_icon = QLabel()
        time_icon.setPixmap(get_icon_pixmap("clock", data["color_tx"], size=12))
        time_icon.setStyleSheet("border: none; background: transparent;")

        time_left = QLabel(data['tiempo'])
        time_left.setStyleSheet(f"color: {data['color_tx']}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        time_right = QLabel(data["tiempo_lbl"])
        time_right.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; border: none; background: transparent;")

        time_layout.addWidget(time_icon)
        time_layout.addWidget(time_left)
        time_layout.addWidget(time_right, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(time_bar)

        # Lista de Ejercicios
        exercises_container = QFrame()
        exercises_container.setStyleSheet("background: transparent; border: none;")
        ex_layout = QVBoxLayout(exercises_container)
        ex_layout.setContentsMargins(0, 4, 0, 4)
        ex_layout.setSpacing(8)

        for name, reps, icon in data["ejercicios"]:
            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            left_layout = QHBoxLayout()
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(6)
            
            icon_lbl = QLabel()
            icon_lbl.setPixmap(get_icon_pixmap(icon, data["color_tx"], size=12))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(f"color: {TEXT_GRAY}; font-size: 11px; border: none; background: transparent;")
            
            left_layout.addWidget(icon_lbl)
            left_layout.addWidget(name_lbl)
            
            # Repeticiones a la derecha formateadas (número en negrita, "reps" en gris)
            if " " in reps:
                num_part, unit_part = reps.split(" ", 1)
                
                rf = QFrame()
                rf.setStyleSheet("background: transparent; border: none;")
                rf_layout = QHBoxLayout(rf)
                rf_layout.setContentsMargins(0, 0, 0, 0)
                rf_layout.setSpacing(3)
                
                n_lbl = QLabel(num_part)
                n_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
                u_lbl = QLabel(unit_part)
                u_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none; background: transparent;")
                
                rf_layout.addWidget(n_lbl)
                rf_layout.addWidget(u_lbl)
                
                row_layout.addLayout(left_layout)
                row_layout.addWidget(rf, alignment=Qt.AlignmentFlag.AlignRight)
            else:
                right_lbl = QLabel(reps)
                right_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 11px; font-weight: bold; border: none; background: transparent;")
                row_layout.addLayout(left_layout)
                row_layout.addWidget(right_lbl, alignment=Qt.AlignmentFlag.AlignRight)
                
            ex_layout.addWidget(row)

        layout.addWidget(exercises_container)

        # Separador sutil
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {BORDER_DARK}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # Botón de Acción con estilo personalizado por dificultad del mockup
        btn_text_str = data["btn_text"]
        if data["id"] != "ejercicio_libre":
            btn_text_str += "  ▷"
            
        btn = QPushButton(btn_text_str)
        btn.setFixedHeight(38)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if data["id"] == "reto_principiante":
            btn_style = f"""
                QPushButton {{
                    background-color: {data['color_tx']};
                    color: {BG_MAIN};
                    border: none;
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #34D399;
                }}
            """
        elif data["id"] == "reto_estandar":
            btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {data['color_tx']};
                    border: 1.5px solid {data['color_tx']};
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {data['color_tx']};
                    color: {BG_MAIN};
                }}
            """
        elif data["id"] == "reto_avanzado":
            btn_style = f"""
                QPushButton {{
                    background-color: {data['color_tx']};
                    color: {TEXT_WHITE};
                    border: none;
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
            """
        else:
            btn_style = f"""
                QPushButton {{
                    background-color: #D1D5DB;
                    color: #1F2937;
                    border: none;
                    border-radius: 8px;
                    font-family: '{FONT_TITLE}';
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #E5E7EB;
                }}
            """
            btn.setIcon(get_icon("camera", "#1F2937", size=12))
            btn.setIconSize(QSize(12, 12))
            
        btn.setStyleSheet(btn_style)
        btn.clicked.connect(lambda: self._iniciar(data))
        layout.addWidget(btn)

        return card

    def _iniciar(self, data):
        """Navega a la pantalla del ejercicio activo guardando el reto actual."""
        try:
            self.shell.controller.ejercicio_actual = data
            # Simula navegación o abre vista
            print(f"[Zenit-Vision QTs] Iniciando reto: {data['nombre']} (Dificultad: {data['badge']})")
        except Exception as e:
            print(f"Error al iniciar reto: {e}")
