import customtkinter as ctk
from ui.styles import *

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        # --- CABECERA ---
        self.lbl_title = ctk.CTkLabel(self, text="PANEL DE CONTROL", font=FONT_LOGO, text_color=ACCENT_GREEN)
        self.lbl_title.pack(pady=(50, 10))
        
        self.lbl_welcome = ctk.CTkLabel(self, text="¡Bienvenido a Zenit Vision!", font=FONT_SLOGAN, text_color=TEXT_WHITE)
        self.lbl_welcome.pack(pady=10)

        # --- TARJETA DE ESTADO (Placeholder para stats) ---
        self.info_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=15, width=400, height=150)
        self.info_card.pack(pady=30, padx=20)
        self.info_card.pack_propagate(False)

        ctk.CTkLabel(self.info_card, text="Sesión iniciada correctamente", font=FONT_LABEL, text_color=ACCENT_GREEN).pack(pady=20)
        
        # --- BOTÓN SALIR ---
        # Asegúrate de que este bloque esté INDENTADO dentro de __init__
        self.btn_logout = ctk.CTkButton(
            self, 
            text="Cerrar Sesión", 
            fg_color=ERROR_COLOR, 
            hover_color="#b91c1c", 
            text_color=TEXT_WHITE,
            width=200, 
            corner_radius=12,
            command=self.logout # Llama a la función de abajo
        )
        self.btn_logout.pack(pady=20)

    def logout(self):
        """Regresa al Login de perfiles"""
        from ui.frames.login import LoginFrame
        self.controller.show_frame(LoginFrame)