import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    # Inicialización del motor de la aplicación Qt
    app = QApplication(sys.argv)
    
    # Instanciamos la ventana maestra
    window = MainWindow()
    
    # Iniciamos la aplicación mostrando el LoginView de PyQt6
    window.show_login()
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
