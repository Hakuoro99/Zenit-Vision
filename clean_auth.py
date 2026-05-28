import firebase_admin
from firebase_admin import credentials, auth

def clean_all_users():
    # Inicializar firebase_admin si no ha sido inicializado
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate("firebase.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://zenit-vision-default-rtdb.firebaseio.com/"
            })
        except Exception as e:
            print(f"Error al inicializar Firebase Admin: {e}")
            return
        
    print("Conectando con Firebase Authentication...")
    try:
        page = auth.list_users()
        deleted_count = 0
        
        # Iterar sobre todos los usuarios registrados en Firebase Auth
        while page:
            for user in page.users:
                try:
                    auth.delete_user(user.uid)
                    print(f"[+] Eliminado de Auth: {user.email or user.uid}")
                    deleted_count += 1
                except Exception as e:
                    print(f"[X] Error al eliminar {user.email}: {e}")
            page = page.get_next_page()
            
        print(f"\n[Zenit-Vision] Limpieza completada con éxito. Se eliminaron {deleted_count} usuarios de Firebase Auth.")
    except Exception as e:
        print(f"Error al listar usuarios de Firebase Auth: {e}")

if __name__ == "__main__":
    clean_all_users()
