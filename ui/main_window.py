import customtkinter as ctk
from database.firebase_database import FirebaseDB
from ui.styles import BG_COLOR
from ui.frames.login import LoginFrame
from ui.frames.register import RegisterFrame
from ui.frames.dashboard import DashboardFrame

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Zenit Vision")
        # Establecemos el tamaño fijo de 1180x750
        self.app_width = 1180
        self.app_height = 750
        
        # Centrado en la pantalla del monitor
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (self.app_width // 2)
        y = (screen_h // 2) - (self.app_height // 2)
        self.geometry(f"{self.app_width}x{self.app_height}+{x}+{y}")
        
        # Bloqueamos el tamaño para evitar lag visual
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        # Configuración de Firebase
        path_json = "firebase.json"
        url_db = "https://zenit-vision-default-rtdb.firebaseio.com/"
        self.fb_db = FirebaseDB(path_json, url_db)

        # CONTENEDOR MAESTRO: Debe llenar TODO el espacio
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Configuración de pesos para que los frames internos se estiren (Fundamental)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame):
            # 'sticky="nsew"' obliga al frame a medir lo mismo que el container
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, page_class):
        frame = self.frames.get(page_class)
        if frame:
            self.update_idletasks() # Evita parpadeos
            frame.tkraise()