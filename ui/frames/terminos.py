import customtkinter as ctk

# ─────────────────────────────────────────────────────────────────────────────
#  TEXTO DE LOS TÉRMINOS Y CONDICIONES
#  Edita este string cuando necesites actualizar el contenido.
# ─────────────────────────────────────────────────────────────────────────────

TERMINOS_TEXTO = """
TÉRMINOS Y CONDICIONES DE USO
Zenit Vision — Sistema Gamificado para Ejercicio Físico
Versión 1.0  ·  2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Antes de crear tu cuenta, lee este documento completo.
Al presionar "Acepto", confirmas que entendiste y estás
de acuerdo con todas las condiciones aquí descritas.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ¿QUÉ ES ZENIT VISION?

Zenit Vision es una aplicación de escritorio desarrollada 
para ayudarte a hacer ejercicio desde casa. 
Usa tu cámara web para detectar tu postura en tiempo real,
contar repeticiones y mantenerte motivado mediante un sistema 
de puntos, niveles y rachas diarias.
 
La aplicación es gratuita y no requiere equipos especiales,
solo una computadora con cámara web.
 
Importante: Zenit Vision NO es un dispositivo médico ni
reemplaza la orientación de un profesional de la salud o
entrenador certificado. Si tienes alguna condición física,
consulta a tu médico antes de comenzar cualquier rutina.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. TU CÁMARA Y TU PRIVACIDAD

⚠ Tu video NUNCA sale de tu computadora.

La cámara se usa únicamente para analizar tu postura en tiempo real. Ningún
video ni imagen es enviado, guardado ni transmitido a servidores externos.
Todo el procesamiento ocurre dentro de tu propio equipo.

Lo que SÍ guardamos en la nube:
  • Tu correo electrónico y nombre de usuario.
  • Historial de sesiones: fecha, tipo de ejercicio, repeticiones y puntos.
  • Tu nivel actual, puntos acumulados y racha de actividad.

Lo que NUNCA guardamos:
  • No grabamos ningún video ni tomamos fotos tuyas.
  • No enviamos imágenes a ningún servidor externo.
  • No almacenamos ningún fotograma de la cámara.
  • No accedemos a la cámara fuera de una sesión activa.
 
Todo el procesamiento de video ocurre únicamente dentro
de tu computadora. Una vez que cierras la sesión, el
acceso a la cámara se detiene completamente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. TU CUENTA

Para usar Zenit Vision necesitas registrarte con correo y contraseña. Tu
contraseña se almacena cifrada mediante Firebase Authentication; ni el
desarrollador ni nadie más puede verla.

Tienes derecho a:
  • Saber qué datos tuyos están guardados.
  • Corregir datos incorrectos.
  • Eliminar tu cuenta y todos tus datos en cualquier momento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. USO CORRECTO DE LA APP

Al usar Zenit Vision, aceptas:
  • Usar la app únicamente para ejercicio personal, no con fines comerciales.
  • No intentar modificar, copiar ni distribuir el software.
  • Asegurarte de tener espacio libre y seguro antes de ejercitarte.
  • Consultar a un médico antes de comenzar si tienes alguna condición de salud.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. LIMITACIONES IMPORTANTES

⚠ Zenit Vision NO es un dispositivo médico.

La retroalimentación de postura es una guía técnica basada en ángulos de
movimiento. No diagnostica lesiones ni condiciones médicas. Ante cualquier
dolor o molestia, detén el ejercicio y consulta a un profesional.

La precisión puede verse afectada por:
  • Iluminación insuficiente en tu entorno.
  • Distancia inadecuada a la cámara.
  • Ropa muy holgada o colores similares al fondo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. ALMACENAMIENTO EN LA NUBE

Tus datos se guardan en Firebase Cloud Firestore (Google LLC), protegidos con
reglas de seguridad que impiden el acceso de otros usuarios. Google procesa
estos datos conforme a su política: policies.google.com/privacy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. PROPIEDAD INTELECTUAL

Zenit Vision, incluyendo su código fuente, diseño visual,
interfaz, logotipos y documentación, es propiedad del
Equipo Zenit Vision, protegido por la Ley Federal del
Derecho de Autor de México.
 
Queda prohibido sin autorización expresa:
  × Copiar o reproducir el software.
  × Modificar o crear versiones derivadas.
  × Distribuir o vender la aplicación.
  × Realizar ingeniería inversa sobre el código.
 
La app utiliza las siguientes tecnologías de código
abierto bajo sus respectivas licencias:
 
  • MediaPipe / BlazePose — Google LLC  (Apache 2.0)
  • OpenCV                — OpenCV.org  (Apache 2.0)
  • CustomTkinter         — Tom Sch.    (MIT)
  • Firebase SDK          — Google LLC  (Términos Google)
  • Python                — PSF         (PSF License)
 
El uso de estas tecnologías no implica que sus creadores
respalden o estén asociados a Zenit Vision.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. CAMBIOS EN ESTOS TÉRMINOS

Si actualizamos estos Términos y Condiciones, te lo avisaremos dentro de la
app la próxima vez que inicies sesión.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. CONTACTO

¿Dudas, quieres eliminar tu cuenta o reportar un problema?

  ✉  Correo:      luisangelazm@gmail.com
  👤  Desarrollador: Equipo de Zenit Vision
  🏫  Institución:  Facultad de Ingeniería Electromecánica — U. de Colima

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Al presionar "Acepto" confirmas que:

  ✅ Leíste y entendiste estos Términos y Condiciones.
  ✅ Tienes 15 años o más (o cuentas con permiso de un adulto).
  ✅ Aceptas el uso local de tu cámara para análisis de postura.
  ✅ Aceptas que se guarden tus datos de sesión en la nube.

© 2026 Equipo Zenit Vision — Todos los derechos reservados.
"""


# ─────────────────────────────────────────────────────────────────────────────
#  MODAL DE TÉRMINOS Y CONDICIONES
# ─────────────────────────────────────────────────────────────────────────────

class TerminosModal(ctk.CTkToplevel):
    """
    Ventana modal que muestra los Términos y Condiciones.

    Uso:
        modal = TerminosModal(parent=self, callback_aceptar=mi_funcion)

    Si el usuario presiona "Acepto", se llama a callback_aceptar().
    Si cierra la ventana o presiona "Cancelar", no se llama nada.
    """

    def __init__(self, parent, callback_aceptar=None):
        super().__init__(parent)

        self.callback_aceptar = callback_aceptar

        # ── Configuración de la ventana ──────────────────────────────────────
        self.title("Términos y Condiciones — Zenit Vision")
        self.geometry("680x560")
        self.resizable(False, False)
        self.grab_set()          # Bloquea la ventana principal mientras está abierta
        self.focus_force()       # Trae el modal al frente

        # Centrar en pantalla
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  // 2) - 340
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 280
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # ── Contenedor principal ─────────────────────────────────────────────
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Encabezado ───────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#1F4E79", corner_radius=0, height=56)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="  📋  Términos y Condiciones de Uso",
            font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
            text_color="white",
            anchor="w"
        ).pack(side="left", padx=20, pady=12)

        # ── Área de texto con scroll ─────────────────────────────────────────
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(12, 0))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            activate_scrollbars=True,
            corner_radius=8,
            border_width=1,
            border_color="#CCCCCC",
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("1.0", TERMINOS_TEXTO.strip())
        self.textbox.configure(state="disabled")   # Solo lectura

        # ── Checkbox de aceptación ────────────────────────────────────────────
        self.aceptado_var = ctk.BooleanVar(value=False)

        check_frame = ctk.CTkFrame(self, fg_color="transparent")
        check_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(10, 4))

        self.checkbox = ctk.CTkCheckBox(
            check_frame,
            text="He leído y acepto los Términos y Condiciones de Zenit Vision",
            variable=self.aceptado_var,
            font=ctk.CTkFont(family="Arial", size=12),
            command=self._toggle_boton_aceptar
        )
        self.checkbox.pack(side="left")

        # ── Botones ───────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(6, 14))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=160,
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color="#AAAAAA",
            text_color=("black", "white"),
            font=ctk.CTkFont(family="Arial", size=13),
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 8), sticky="e")

        self.btn_aceptar = ctk.CTkButton(
            btn_frame,
            text="✅  Acepto los Términos y Condiciones",
            width=260,
            height=38,
            fg_color="#2E75B6",
            hover_color="#1F4E79",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            state="disabled",            # Se activa solo al marcar el checkbox
            command=self._on_aceptar
        )
        self.btn_aceptar.grid(row=0, column=1, padx=(8, 0), sticky="w")

    def _toggle_boton_aceptar(self):
        """Activa o desactiva el botón Acepto según el estado del checkbox."""
        if self.aceptado_var.get():
            self.btn_aceptar.configure(state="normal")
        else:
            self.btn_aceptar.configure(state="disabled")

    def _on_aceptar(self):
        """Llama al callback y cierra el modal."""
        self.destroy()
        if self.callback_aceptar:
            self.callback_aceptar()


# ─────────────────────────────────────────────────────────────────────────────
#  EJEMPLO DE USO EN TU PANTALLA DE REGISTRO
#  Copia este patrón en tu clase de registro.
# ─────────────────────────────────────────────────────────────────────────────

class PantallaRegistro(ctk.CTkFrame):
    """Ejemplo mínimo de cómo integrar el modal en tu pantalla de registro."""

    def __init__(self, master):
        super().__init__(master)
        self.terminos_aceptados = False  # Estado interno

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Crear cuenta",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold")
        ).grid(row=0, column=0, pady=(30, 20))

        # … tus campos de correo, contraseña, etc. …

        # ── Fila del checkbox + enlace de T&C ────────────────────────────────
        tyc_frame = ctk.CTkFrame(self, fg_color="transparent")
        tyc_frame.grid(row=5, column=0, pady=(10, 4))

        self.check_tyc_var = ctk.BooleanVar(value=False)
        self.check_tyc = ctk.CTkCheckBox(
            tyc_frame,
            text="Acepto los",
            variable=self.check_tyc_var,
            font=ctk.CTkFont(family="Arial", size=12),
            state="disabled",   # Se activa solo después de abrir y aceptar el modal
        )
        self.check_tyc.pack(side="left")

        # Botón-enlace que abre el modal
        ctk.CTkButton(
            tyc_frame,
            text="Términos y Condiciones",
            font=ctk.CTkFont(family="Arial", size=12, underline=True),
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            text_color="#2E75B6",
            width=0,
            cursor="hand2",
            command=self.abrir_terminos   # ← Aquí conectas el botón
        ).pack(side="left", padx=(4, 0))

        # ── Botón de registro ─────────────────────────────────────────────────
        self.btn_registrar = ctk.CTkButton(
            self,
            text="Crear cuenta",
            width=240,
            height=42,
            state="disabled",   # Se activa solo después de aceptar T&C
            fg_color="#1F4E79",
            font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
            command=self.registrar
        )
        self.btn_registrar.grid(row=6, column=0, pady=16)

    # ─────────────────────────────────────────────────────────────────────────
    def abrir_terminos(self):
        """Abre el modal de T&C. Al aceptar, activa el checkbox y el botón."""
        TerminosModal(
            parent=self.winfo_toplevel(),
            callback_aceptar=self.on_terminos_aceptados
        )

    def on_terminos_aceptados(self):
        """Se ejecuta automáticamente cuando el usuario presiona 'Acepto'."""
        self.terminos_aceptados = True
        self.check_tyc_var.set(True)
        self.btn_registrar.configure(state="normal")  # Desbloquea el botón de registro

    def registrar(self):
        if not self.terminos_aceptados:
            return
        # Aquí va tu lógica de registro con Firebase
        print("Registrando usuario...")


# ─────────────────────────────────────────────────────────────────────────────
#  EJECUCIÓN DE PRUEBA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Zenit Vision — Prueba T&C")
    app.geometry("500x420")

    pantalla = PantallaRegistro(app)
    pantalla.pack(fill="both", expand=True)

    app.mainloop()