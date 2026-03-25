import customtkinter as ctk
from ui.main_window import MainWindow

def main():
    # Configuración global de la interfaz
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Iniciamos la ventana principal (MainWindow)
    # Ella será la encargada de llamar a Firebase cuando sea necesario
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
    main()