"""
Helpers de Firebase Authentication (email verificado).

La app utiliza `firebase_admin` para Realtime Database (ver `database/firebase_database.py`).
Aquí usamos el SDK de Admin para crear usuarios/consultar verificación, y usamos
la API REST de Firebase Auth para enviar el correo de verificación a la bandeja.
"""

from __future__ import annotations

import requests


firebaseConfig = {
    "apiKey": "AIzaSyC8cI1UIORjSfsq3znieazIoNVrLvg5HHQ",
    "authDomain": "zenit-vision.firebaseapp.com",
    "databaseURL": "https://zenit-vision-default-rtdb.firebaseio.com",
    "projectId": "zenit-vision",
    "storageBucket": "zenit-vision.firebasestorage.app",
    "messagingSenderId": "1076934438956",
    "appId": "1:1076934438956:web:13df276dba621d2894e189",
    "measurementId": "G-C6E5KGMFKC",
}


def _get_auth():
    try:
        from firebase_admin import auth as fb_auth  # type: ignore
        return fb_auth
    except Exception as e:
        raise RuntimeError(
            "Firebase Admin Auth no está disponible. "
            "Asegúrate de instalar `firebase-admin` en tu entorno."
        ) from e


def create_user_with_email_and_password(email: str, password: str) -> str:
    """Crea un usuario en Firebase Auth y devuelve su UID."""
    fb_auth = _get_auth()
    user = fb_auth.create_user(email=email, password=password)
    return user.uid


def generate_email_verification_link(email: str) -> str:
    """Genera un link de verificación (uso opcional)."""
    fb_auth = _get_auth()
    try:
        return fb_auth.generate_email_verification_link(email)
    except TypeError:
        # Algunas versiones pueden requerir `action_code_settings`.
        return fb_auth.generate_email_verification_link(email, action_code_settings=None)


def _sign_in_with_email_and_password(email: str, password: str) -> str:
    """Devuelve el `idToken` para el usuario (Identity Toolkit REST)."""
    api_key = firebaseConfig.get("apiKey")
    if not api_key:
        raise RuntimeError("Falta `apiKey` en firebaseConfig.")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=payload, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"Error al iniciar sesión para verificación: {resp.text}")

    data = resp.json()
    id_token = data.get("idToken")
    if not id_token:
        raise RuntimeError(f"No se recibió idToken: {data}")
    return id_token


def send_verification_email(email: str, password: str, name: str = "Usuario") -> tuple[bool, str]:
    """
    Envía el correo de verificación.
    Intenta enviar un correo HTML con diseño premium vía SMTP y, si falla o no está
    configurado en smtp_config.json, realiza un fallback al correo estándar de Firebase.
    Retorna una tupla (enviado_exitosamente, link_de_verificacion).
    """
    link = ""
    try:
        link = generate_email_verification_link(email)
        sent = send_custom_html_email(email, name, link)
        if sent:
            return True, link
    except Exception as e:
        print(f"[SMTP] No se pudo enviar correo personalizado: {e}. Usando fallback...")

    # Fallback estándar
    try:
        api_key = firebaseConfig.get("apiKey")
        if not api_key:
            raise RuntimeError("Falta `apiKey` en firebaseConfig.")

        id_token = _sign_in_with_email_and_password(email, password)

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
            "email": email,
            "clientType": "CLIENT_TYPE_WEB",
        }
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"No se pudo enviar verificación: {resp.text}")
        return True, link
    except Exception as e:
        print(f"[Auth] Fallback estándar falló debido a límites o error: {e}")
        # Si ambos fallaron pero generamos el link con éxito, retornamos False con el link
        # para que la UI pueda abrirlo automáticamente o mostrarlo sin bloquear el registro.
        if link:
            return False, link
        raise e


def send_custom_html_email(email: str, name: str, link: str) -> bool:
    import os
    import json
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    config_path = "smtp_config.json"
    if not os.path.exists(config_path):
        # Crear plantilla de configuración vacía
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "tu_correo@gmail.com",
            "sender_password": "tu_app_password_de_google_16_caracteres"
        }
        try:
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=4)
            print(f"[SMTP] Creado '{config_path}' de ejemplo. Llena tus datos para activar correos premium.")
        except Exception:
            pass
        return False

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        smtp_server = config.get("smtp_server", "smtp.gmail.com")
        smtp_port = config.get("smtp_port", 587)
        sender_email = config.get("sender_email")
        sender_password = config.get("sender_password")
        
        # Validar si el usuario no ha configurado sus credenciales reales en smtp_config.json
        if (not sender_email or 
            "tu_correo" in sender_email or 
            "correo@ejemplo" in sender_email or
            not sender_password or 
            "tu_contrase" in sender_password or 
            "tu_app_password" in sender_password):
            return False

        # Construir correo con diseño Premium Cyberpunk Esmeralda
        from email.header import Header
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header("Activa tu cuenta en Zenit-Visión", "utf-8")
        msg["From"] = f"Zenit-Vision <{sender_email}>"
        msg["To"] = email

        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    background-color: #08090C;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #C5C7CA;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 500px;
                    margin: 30px auto;
                    background-color: #0F1115;
                    border: 1px solid #262A34;
                    border-radius: 12px;
                    padding: 30px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 25px;
                    border-bottom: 1px solid #262A34;
                    padding-bottom: 15px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: 800;
                    color: #FFFFFF;
                    letter-spacing: 1px;
                }}
                .accent {{
                    color: #10B981;
                }}
                .title {{
                    font-size: 18px;
                    color: #FFFFFF;
                    margin-bottom: 15px;
                    font-weight: bold;
                    text-align: center;
                }}
                .text {{
                    font-size: 13px;
                    line-height: 1.5;
                    color: #C5C7CA;
                }}
                .btn-row {{
                    text-align: center;
                    margin: 25px 0;
                }}
                .btn {{
                    background: linear-gradient(90deg, #10B981 0%, #059669 100%);
                    color: #08090C !important;
                    text-decoration: none;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 10px 30px;
                    border-radius: 6px;
                    display: inline-block;
                }}
                .link-box {{
                    font-size: 11px;
                    color: #8A8E98;
                    background-color: #08090C;
                    padding: 10px;
                    border-radius: 6px;
                    border: 1px solid #262A34;
                    word-break: break-all;
                }}
                .footer {{
                    text-align: center;
                    font-size: 10px;
                    color: #8A8E98;
                    border-top: 1px solid #262A34;
                    padding-top: 15px;
                    margin-top: 25px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 8px;">
                        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                        <polyline points="2 17 12 22 22 17"></polyline>
                        <polyline points="2 12 12 17 22 12"></polyline>
                    </svg>
                    <div class="logo">ZENIT <span class="accent">VISION</span></div>
                </div>
                <div class="title">¡Hola, {name}!</div>
                <p class="text">
                    Te damos la bienvenida a Zenit-Visión. Estamos muy emocionados de que formes parte de nuestra plataforma de entrenamiento inteligente.
                </p>
                <p class="text">
                    Para activar tu perfil, guardar tu historial y comenzar a acumular puntos, confirma tu correo electrónico presionando el siguiente botón:
                </p>
                <div class="btn-row">
                    <a href="{link}" class="btn">Confirmar mi Cuenta</a>
                </div>
                <div class="link-box">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                    <a href="{link}" style="color: #10B981;">{link}</a>
                </div>
                <div class="footer">
                    Este correo se envió de forma automática por seguridad.<br>
                    Si no te registraste en Zenit-Visión, puedes ignorar este mensaje.
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        # Conectar y enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP] Error en envío SMTP: {e}")
        return False


def is_email_verified(email: str) -> bool:
    """Devuelve True si Firebase Auth marca el email como verificado."""
    fb_auth = _get_auth()
    user = fb_auth.get_user_by_email(email)
    return bool(getattr(user, "email_verified", False))


def delete_user_by_email(email: str) -> None:
    """Elimina al usuario de Firebase Authentication por su correo."""
    fb_auth = _get_auth()
    try:
        user = fb_auth.get_user_by_email(email)
        fb_auth.delete_user(user.uid)
        print(f"[Auth] Usuario {email} ({user.uid}) eliminado de Firebase Auth.")
    except Exception as e:
        print(f"[Auth] Error al eliminar usuario por email de Firebase Auth: {e}")