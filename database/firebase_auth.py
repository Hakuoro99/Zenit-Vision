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


def send_verification_email(email: str, password: str) -> None:
    """
    Envía el correo de verificación a la bandeja del usuario.

    Importante: con esto el usuario debe abrir el correo y pulsar el botón/link
    de verificación para que `email_verified` se vuelva True.
    """
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


def is_email_verified(email: str) -> bool:
    """Devuelve True si Firebase Auth marca el email como verificado."""
    fb_auth = _get_auth()
    user = fb_auth.get_user_by_email(email)
    return bool(getattr(user, "email_verified", False))