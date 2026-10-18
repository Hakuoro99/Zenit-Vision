import os
import wave
import struct
import math

def save_wav(filename, samples, sample_rate=44100):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        nchannels = 1
        sampwidth = 2  # 16 bits
        nframes = len(samples)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((nchannels, sampwidth, sample_rate, nframes, comptype, compname))
        
        # Clamp and pack samples into 16-bit signed integers
        packed_data = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s))
            int_val = int(val * 32767.0)
            packed_data.extend(struct.pack('<h', int_val))
        wav_file.writeframes(packed_data)
    print(f"Generado: {filename} ({len(samples)} samples)")

def generate_click(sample_rate=44100):
    duration = 0.035
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        freq = 1600 - 1000 * (t / duration)
        env = math.exp(-t * 120.0)
        s = math.sin(2 * math.pi * freq * t) * env * 0.4
        samples.append(s)
    return samples

def generate_select(sample_rate=44100):
    duration = 0.09
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        # Subida suave de 600Hz a 950Hz
        freq = 600 + (350 * (t / duration))
        env = math.sin(math.pi * (t / duration)) ** 0.8
        s = math.sin(2 * math.pi * freq * t) * env * 0.45
        samples.append(s)
    return samples

def generate_countdown_tick(sample_rate=44100):
    duration = 0.08
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        env = math.exp(-t * 50.0)
        s = (0.7 * math.sin(2 * math.pi * 880 * t) + 
             0.3 * math.sin(2 * math.pi * 1760 * t)) * env * 0.55
        samples.append(s)
    return samples

def generate_countdown_go(sample_rate=44100):
    duration = 0.22
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        # Pitch sweep enérgico 1000Hz -> 1600Hz
        freq = 1000 + 600 * (t / duration)
        env = math.exp(-t * 12.0)
        s = (0.65 * math.sin(2 * math.pi * freq * t) + 
             0.35 * math.sin(4 * math.pi * freq * t)) * env * 0.7
        samples.append(s)
    return samples

def generate_rep_ding(sample_rate=44100):
    # Campana cristalina de repetición satisfactoria
    duration = 0.38
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        env1 = math.exp(-t * 8.0)
        env2 = math.exp(-t * 14.0)
        # Fundamental C6 (1046.5Hz) y armónicos brillantes
        s = (0.60 * math.sin(2 * math.pi * 1046.5 * t) * env1 +
             0.30 * math.sin(2 * math.pi * 2093.0 * t) * env2 +
             0.10 * math.sin(2 * math.pi * 3139.5 * t) * env2) * 0.65
        samples.append(s)
    return samples

def generate_warning(sample_rate=44100):
    # Advertencia de postura sutil
    duration = 0.20
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        env = math.exp(-t * 10.0)
        # Tono dual suave
        s = (0.5 * math.sin(2 * math.pi * 330.0 * t) +
             0.5 * math.sin(2 * math.pi * 310.0 * t)) * env * 0.5
        samples.append(s)
    return samples

def generate_transition(sample_rate=44100):
    # Arpegio ascendente brillante para siguiente ejercicio: E5 -> G#5 -> B5 -> E6
    duration = 0.45
    total_samples = int(duration * sample_rate)
    samples = [0.0] * total_samples
    notes = [659.25, 830.61, 987.77, 1318.51] # E5, G#5, B5, E6
    step_duration = 0.08
    
    for idx, freq in enumerate(notes):
        start_time = idx * step_duration
        start_sample = int(start_time * sample_rate)
        note_dur = duration - start_time
        note_samples = int(note_dur * sample_rate)
        
        for i in range(note_samples):
            if start_sample + i < total_samples:
                t = i / sample_rate
                env = math.exp(-t * 9.0)
                s = (0.7 * math.sin(2 * math.pi * freq * t) + 
                     0.3 * math.sin(2 * math.pi * freq * 2 * t)) * env * 0.35
                samples[start_sample + i] += s
    return samples

def generate_victory(sample_rate=44100):
    # Fanfarria triunfal futurista para fin de sesión y puntos
    duration = 1.15
    total_samples = int(duration * sample_rate)
    samples = [0.0] * total_samples
    # Acorde mayor arpegiado con clímax: C5, E5, G5, C6 + Acorde sostenido
    chords = [
        (0.00, 523.25),  # C5
        (0.12, 659.25),  # E5
        (0.24, 783.99),  # G5
        (0.36, 1046.50), # C6
        (0.48, 1318.51), # E6
    ]
    for start_time, freq in chords:
        start_sample = int(start_time * sample_rate)
        note_dur = duration - start_time
        note_samples = int(note_dur * sample_rate)
        for i in range(note_samples):
            if start_sample + i < total_samples:
                t = i / sample_rate
                env = math.exp(-t * 3.8)
                s = (0.55 * math.sin(2 * math.pi * freq * t) +
                     0.30 * math.sin(2 * math.pi * freq * 2 * t) +
                     0.15 * math.sin(2 * math.pi * freq * 3 * t)) * env * 0.28
                samples[start_sample + i] += s
    return samples

def generate_logout(sample_rate=44100):
    # Desconexión / Cierre de sesión suave
    duration = 0.25
    total_samples = int(duration * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / sample_rate
        freq = 520 - (260 * (t / duration))
        env = math.exp(-t * 9.0)
        s = (0.7 * math.sin(2 * math.pi * freq * t) + 
             0.3 * math.sin(2 * math.pi * freq * 0.5 * t)) * env * 0.4
        samples.append(s)
    return samples

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
    os.makedirs(base_dir, exist_ok=True)
    
    effects = {
        "click.wav": generate_click(),
        "select.wav": generate_select(),
        "countdown_tick.wav": generate_countdown_tick(),
        "countdown_go.wav": generate_countdown_go(),
        "rep_ding.wav": generate_rep_ding(),
        "warning.wav": generate_warning(),
        "transition.wav": generate_transition(),
        "victory.wav": generate_victory(),
        "logout.wav": generate_logout()
    }
    
    for fname, samples in effects.items():
        path = os.path.join(base_dir, fname)
        save_wav(path, samples)
    print("¡Todos los efectos de sonido temáticos generados exitosamente en assets/sounds/!")

if __name__ == "__main__":
    main()
