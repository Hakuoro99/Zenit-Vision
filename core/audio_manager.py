import os
import sys
import time
import json
import random
from PyQt6.QtCore import QObject, QUrl

# En Windows utilizamos winsound nativo (sub-milisegundo, 0% CPU, 0 cuelgues, sin FFmpeg)
if sys.platform == 'win32':
    import winsound


class AudioManager(QObject):
    """
    Gestor de Audio de Zenit-Visión:
    - Efectos de sonido (SFX) cortos
    - Música de fondo (app) y música de ejercicio (sesión), aleatoria y continua
    """
    _instance = None

    MODE_FONDO = "fondo"
    MODE_EJERCICIO = "ejercicio"
    _AUDIO_EXTS = (".mp3", ".wav", ".ogg", ".m4a", ".flac")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AudioManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        self.sounds_dir = os.path.join(assets_root, "sounds")
        self.fondo_dir = os.path.join(assets_root, "musica_fondo")
        self.ejercicio_dir = os.path.join(assets_root, "musica_ejercicio")
        self.prefs_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "audio_prefs.json")
        )

        self.sfx_volume = 0.75
        self.is_sfx_muted = False
        self._sound_paths = {}
        self._last_played_times = {}

        # Preferencias de música (persistentes)
        self.music_enabled = True
        self.music_volume = 0.42
        self.is_music_muted = False  # alias lógico de not music_enabled
        self._load_music_prefs()

        # Reproductor de música (QMediaPlayer)
        self._music_player = None
        self._audio_output = None
        self._current_mode = None
        self._playlist = []
        self._playlist_index = 0
        self._current_track = None
        self._advancing = False
        # Pausas temporales (no cambian la preferencia global music_enabled)
        self._exercise_paused = False
        self._session_audio_muted = False

        self._index_sound_files()

    # ── Preferencias ──────────────────────────────────────────────────────────

    def _load_music_prefs(self):
        try:
            if os.path.exists(self.prefs_path):
                with open(self.prefs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.music_enabled = bool(data.get("music_enabled", True))
                self.music_volume = float(data.get("music_volume", 0.42))
                self.music_volume = max(0.0, min(1.0, self.music_volume))
                self.is_music_muted = not self.music_enabled
        except Exception as e:
            print(f"[AudioManager] No se pudieron cargar preferencias de música: {e}")

    def _save_music_prefs(self):
        try:
            with open(self.prefs_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "music_enabled": self.music_enabled,
                        "music_volume": self.music_volume,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"[AudioManager] No se pudieron guardar preferencias de música: {e}")

    def set_music_enabled(self, enabled, persist=True):
        """Activa o desactiva la música de fondo/ejercicio."""
        self.music_enabled = bool(enabled)
        self.is_music_muted = not self.music_enabled
        if persist:
            self._save_music_prefs()

        if not self.music_enabled:
            self._stop_player()
        elif self._current_mode:
            self._ensure_playing()

    def set_music_volume(self, volume, persist=True):
        """Ajusta el volumen de la música entre 0.0 y 1.0."""
        self.music_volume = max(0.0, min(1.0, float(volume)))
        if self._audio_output is not None:
            self._audio_output.setVolume(self.music_volume)
        if persist:
            self._save_music_prefs()

    def toggle_music_mute(self):
        """Alterna música on/off y persiste el cambio."""
        self.set_music_enabled(not self.music_enabled, persist=True)
        return not self.music_enabled

    # ── SFX ───────────────────────────────────────────────────────────────────

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
                winsound.PlaySound(
                    file_path,
                    winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
                )
                self._last_played_times[sound_name] = now
            else:
                self._play_fallback(file_path)
                self._last_played_times[sound_name] = now
        except Exception as e:
            print(f"[AudioManager] Error reproduciendo {sound_name}: {e}")

    def _play_fallback(self, file_path):
        """Fallback seguro para entornos no Windows."""
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            effect = QSoundEffect(self)
            effect.setSource(QUrl.fromLocalFile(file_path))
            effect.setVolume(self.sfx_volume)
            effect.play()
        except Exception:
            pass

    def play_click(self):
        self.play_sfx("click", min_interval=0.05)

    def play_select(self):
        self.play_sfx("select", min_interval=0.1)

    def play_countdown_tick(self):
        self.play_sfx("countdown_tick", min_interval=0.25)

    def play_countdown_go(self):
        self.play_sfx("countdown_go", min_interval=0.35)

    def play_rep(self):
        self.play_sfx("rep_ding", min_interval=0.15)

    def play_warning(self):
        self.play_sfx("warning", min_interval=2.0)

    def play_transition(self):
        self.play_sfx("transition", min_interval=0.5)

    def play_victory(self):
        self.play_sfx("victory", min_interval=0.8)

    def play_logout(self):
        self.play_sfx("logout", min_interval=0.4)

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle_sfx_mute(self):
        self.is_sfx_muted = not self.is_sfx_muted
        if self.is_sfx_muted and sys.platform == 'win32':
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        return self.is_sfx_muted

    # ── Música de fondo / ejercicio ───────────────────────────────────────────

    def start_background_music(self):
        """Inicia (o reanuda) la música ambiental de la app, aleatoria y continua."""
        self._exercise_paused = False
        self._session_audio_muted = False
        self.is_sfx_muted = False
        self._start_mode(self.MODE_FONDO)

    def start_exercise_music(self):
        """Inicia la música motivacional de la sesión de ejercicio."""
        self._exercise_paused = False
        self._session_audio_muted = False
        self.is_sfx_muted = False
        self._start_mode(self.MODE_EJERCICIO)

    def stop_music(self):
        """Detiene la música por completo y limpia el modo activo."""
        self._current_mode = None
        self._exercise_paused = False
        self._stop_player()

    def pause_music_for_exercise(self):
        """Pausa la música mientras el entrenamiento está en pausa."""
        self._exercise_paused = True
        self._pause_player()

    def resume_music_for_exercise(self):
        """Reanuda la música al continuar el entrenamiento (si no está silenciada)."""
        self._exercise_paused = False
        if self._can_play_music():
            self._resume_or_play()

    def toggle_session_audio_mute(self):
        """
        Silencia o reactiva SFX + música de forma temporal (botón de volumen en entrenamiento).
        No modifica la preferencia global 'Activar música' de Configuración.
        """
        self._session_audio_muted = not self._session_audio_muted
        self.is_sfx_muted = self._session_audio_muted

        if self._session_audio_muted:
            if sys.platform == 'win32':
                try:
                    winsound.PlaySound(None, winsound.SND_PURGE)
                except Exception:
                    pass
            self._pause_player()
        else:
            if self._can_play_music():
                self._resume_or_play()

        return self._session_audio_muted

    def _can_play_music(self):
        return (
            self.music_enabled
            and not self._session_audio_muted
            and not self._exercise_paused
            and self._current_mode is not None
        )

    def _pause_player(self):
        if self._music_player is not None:
            try:
                self._music_player.pause()
            except Exception:
                pass

    def _resume_or_play(self):
        """Reanuda la pista actual o la inicia si el reproductor estaba detenido."""
        self._ensure_player()
        if self._music_player is None:
            return
        try:
            state = self._music_player.playbackState()
            if state == self._music_player.PlaybackState.PausedState:
                self._audio_output.setVolume(self.music_volume)
                self._music_player.play()
            elif state == self._music_player.PlaybackState.StoppedState:
                self._play_current()
            elif state != self._music_player.PlaybackState.PlayingState:
                self._play_current()
        except Exception as e:
            print(f"[AudioManager] Error al reanudar música: {e}")
            self._play_current()

    def _start_mode(self, mode):
        if mode not in (self.MODE_FONDO, self.MODE_EJERCICIO):
            return

        # Si ya estamos en ese modo y el player sigue activo, no reiniciar
        if (
            self._current_mode == mode
            and self._music_player is not None
            and self._can_play_music()
            and self._music_player.playbackState() == self._music_player.PlaybackState.PlayingState
        ):
            return

        self._current_mode = mode
        folder = self.fondo_dir if mode == self.MODE_FONDO else self.ejercicio_dir
        tracks = self._scan_tracks(folder)
        if not tracks:
            print(f"[AudioManager] No hay pistas en: {folder}")
            self._stop_player()
            return

        self._playlist = tracks[:]
        random.shuffle(self._playlist)
        self._playlist_index = 0
        self._current_track = None

        if not self._can_play_music():
            self._stop_player()
            return

        self._ensure_player()
        self._play_current()

    def _scan_tracks(self, folder):
        if not os.path.isdir(folder):
            return []
        tracks = []
        try:
            for name in os.listdir(folder):
                if name.lower().endswith(self._AUDIO_EXTS):
                    tracks.append(os.path.join(folder, name))
        except Exception as e:
            print(f"[AudioManager] Error listando {folder}: {e}")
        return tracks

    def _ensure_player(self):
        if self._music_player is not None:
            return

        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(self.music_volume)

        self._music_player = QMediaPlayer(self)
        self._music_player.setAudioOutput(self._audio_output)
        self._music_player.mediaStatusChanged.connect(self._on_media_status)
        self._music_player.errorOccurred.connect(self._on_player_error)

    def _ensure_playing(self):
        if not self._can_play_music():
            return
        if not self._playlist:
            folder = self.fondo_dir if self._current_mode == self.MODE_FONDO else self.ejercicio_dir
            self._playlist = self._scan_tracks(folder)
            random.shuffle(self._playlist)
            self._playlist_index = 0
        if not self._playlist:
            return
        self._ensure_player()
        self._play_current()

    def _play_current(self):
        if not self._playlist or self._music_player is None:
            return
        if not self._can_play_music():
            return

        if self._playlist_index >= len(self._playlist):
            last = self._current_track
            random.shuffle(self._playlist)
            # Evitar repetir inmediatamente la misma pista si hay más de una
            if len(self._playlist) > 1 and last and self._playlist[0] == last:
                self._playlist.append(self._playlist.pop(0))
            self._playlist_index = 0

        track = self._playlist[self._playlist_index]
        self._current_track = track
        try:
            self._audio_output.setVolume(self.music_volume)
            self._music_player.setSource(QUrl.fromLocalFile(track))
            self._music_player.play()
            print(f"[AudioManager] Reproduciendo ({self._current_mode}): {os.path.basename(track)}")
        except Exception as e:
            print(f"[AudioManager] Error al reproducir {track}: {e}")
            self._advance_track()

    def _advance_track(self):
        if self._advancing:
            return
        self._advancing = True
        try:
            if not self._can_play_music():
                return
            self._playlist_index += 1
            self._play_current()
        finally:
            self._advancing = False

    def _on_media_status(self, status):
        try:
            from PyQt6.QtMultimedia import QMediaPlayer
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                self._advance_track()
            elif status == QMediaPlayer.MediaStatus.InvalidMedia:
                print("[AudioManager] Medio inválido, pasando a la siguiente pista")
                self._advance_track()
        except Exception as e:
            print(f"[AudioManager] Error en mediaStatusChanged: {e}")

    def _on_player_error(self, error, error_string=""):
        print(f"[AudioManager] Error del reproductor ({error}): {error_string}")
        # Intentar continuar con la siguiente pista
        self._advance_track()

    def _stop_player(self):
        if self._music_player is not None:
            try:
                self._music_player.stop()
            except Exception:
                pass
