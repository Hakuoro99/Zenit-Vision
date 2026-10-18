import os
import sys
import time
from PyQt6.QtCore import QObject

# En Windows utilizamos winsound nativo (sub-milisegundo, 0% CPU, 0 cuelgues, sin FFmpeg)
if sys.platform == 'win32':
    import winsound

class AudioManager(QObject):
    """
    Gestor optimizado de Audio y Efectos de Sonido (SFX) para Zenit-Visión.
    Diseñado para respuesta instantánea, sin fugas de memoria y sin bloqueos de interfaz.
    """
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.sounds_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
        self.music_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "music"))
        
        self.sfx_volume = 0.75
        self.is_sfx_muted = False
        self._sound_paths = {}
        self._last_played_times = {}
        
        # Reproductor de música perezoso (solo se inicializa cuando se use música de fondo)
        self._music_player = None
        self._audio_output = None
        self.is_music_muted = False
        
        self._index_sound_files()

    def _index_sound_files(self):
        """Indexa las rutas absolutas de los efectos de sonido para acceso inmediato."""
        sound_names = [
            "click", "select", "countdown_tick", "countdown_go",
            "rep_ding", "warning", "transition", "victory", "logout"
        ]
        for name in sound_names:
            file_path = os.path.join(self.sounds_dir, f"{name}.wav")
            if os.path.exists(file_path):
                self._sound_paths[name] = file_path

    def play_sfx(self, sound_name, min_interval=0.0):
        """
        Reproduce un efecto de sonido de forma 100% asíncrona y no bloqueante.
        Incluye protección de intervalo mínimo para evitar saturación de la tarjeta de sonido.
        """
        if self.is_sfx_muted:
            return

        now = time.time()
        if min_interval > 0.0:
            last_time = self._last_played_times.get(sound_name, 0.0)
            if now - last_time < min_interval:
                return

        file_path = self._sound_paths.get(sound_name)
        if not file_path:
            return

        try:
            if sys.platform == 'win32':
                # SND_ASYNC ejecuta en segundo plano sin congelar la GUI
                # SND_NODEFAULT evita emitir el beep por defecto de Windows si no está disponible
                winsound.PlaySound(
                    file_path, 
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                )
                self._last_played_times[sound_name] = now
            else:
                # Fallback multiplataforma en caso de no ser Windows
                self._play_fallback(file_path)
                self._last_played_times[sound_name] = now
        except Exception as e:
            # En caso de error de hardware de audio, nunca tumbar la aplicación
            print(f"[AudioManager] Error reproduciendo {sound_name}: {e}")

    def _play_fallback(self, file_path):
        """Fallback seguro para entornos no Windows."""
        try:
            from PyQt6.QtCore import QUrl
            from PyQt6.QtMultimedia import QSoundEffect
            effect = QSoundEffect(self)
            effect.setSource(QUrl.fromLocalFile(file_path))
            effect.setVolume(self.sfx_volume)
            effect.play()
        except Exception:
            pass

    # Métodos directos de alta usabilidad
    def play_click(self):
        """Click digital sutil para botones y controles generales."""
        self.play_sfx("click", min_interval=0.05)

    def play_select(self):
        """Efecto al seleccionar una opción o iniciar un reto de ejercicio."""
        self.play_sfx("select", min_interval=0.1)

    def play_countdown_tick(self):
        """Beep de preparación para cada segundo de conteo regresivo."""
        self.play_sfx("countdown_tick", min_interval=0.25)

    def play_countdown_go(self):
        """Tono enérgico para el inicio del entrenamiento (¡Ya!)."""
        self.play_sfx("countdown_go", min_interval=0.35)

    def play_rep(self):
        """Campana brillante que premia cada repetición válida."""
        self.play_sfx("rep_ding", min_interval=0.15)

    def play_warning(self):
        """Alerta suave de corrección de postura."""
        self.play_sfx("warning", min_interval=2.0)

    def play_transition(self):
        """Arpegio alegre cuando se completa un ejercicio y se pasa al siguiente."""
        self.play_sfx("transition", min_interval=0.5)

    def play_victory(self):
        """Fanfarria triunfal al terminar toda la rutina de entrenamiento."""
        self.play_sfx("victory", min_interval=0.8)

    def play_logout(self):
        """Tono de cierre de sesión / desconexión."""
        self.play_sfx("logout", min_interval=0.4)

    # Control de estado y silenciado
    def set_sfx_volume(self, volume):
        """Ajusta el volumen de los efectos entre 0.0 y 1.0."""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle_sfx_mute(self):
        """Alterna el estado de silenciado de los efectos de sonido."""
        self.is_sfx_muted = not self.is_sfx_muted
        if self.is_sfx_muted and sys.platform == 'win32':
            try:
                # Detener cualquier sonido en curso
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        return self.is_sfx_muted
