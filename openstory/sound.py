"""Local speech and a deterministic original score, aligned in sample time."""
import hashlib
import math
import random
import wave

import numpy as np
from piper import PiperVoice, SynthesisConfig


FPS = 30


def synthesize(data, model, pace):
    if model.is_dir():
        from seslen_tts import Seslen
        from seslen_tts.model import DOSYALAR, ORAN
        if not all((model / file).is_file() for file in DOSYALAR):
            raise ValueError("Seslen modeli eksik. ost.py voice ile kur.")
        voice = Seslen(klasor=str(model), denetim=False)
        rate = ORAN

        def speak(line):
            if isinstance(line, str):
                return voice.tum(line, ses="ege", ton="notr", hiz=1 / pace)
            return voice.tum(line["text"], ses=data["voices"][line["speaker"]], ton=line["emotion"],
                             yogunluk=line.get("intensity", 0.85), hiz=line.get("speed", 1) / pace)
    else:
        if data["version"] == 2 or not model.is_file() or not model.with_suffix(".onnx.json").is_file():
            raise ValueError("Karakter sesleri için ost.py voice çalıştır ve Seslen klasörünü kullan.")
        voice = PiperVoice.load(model)
        rate = voice.config.sample_rate
        settings = SynthesisConfig(length_scale=pace)

        def speak(line):
            chunks = [chunk.audio_float_array for chunk in voice.synthesize(line, settings)]
            return np.concatenate(chunks) if chunks else np.empty(0)
    pieces, cues, shot_frames = [], [], []
    cursor = 0
    for shot_index, shot in enumerate(data["shots"]):
        start_frame = round(cursor * FPS / rate)
        for line_index, line in enumerate(shot["lines"]):
            samples = speak(line)
            if not samples.size or not np.isfinite(samples).all():
                raise ValueError(f"Ses üretilemedi: {line}")
            active = np.flatnonzero(np.abs(samples) > 0.009)
            if not active.size:
                raise ValueError(f"Sessiz replik: {line}")
            # Keep soft consonants and natural space at both ends.
            samples = samples[max(0, active[0] - rate // 18):active[-1] + rate // 10]
            start = cursor
            cursor += len(samples)
            pieces.append(samples * 0.70)
            cues.append((start / rate, cursor / rate, line["text"] if isinstance(line, dict) else line))
            pause = 0.22 if line_index + 1 == len(shot["lines"]) else 0.13
            if isinstance(line, dict):
                pause = line.get("pause", 0.32)
            if shot_index + 1 == len(data["shots"]) and line_index + 1 == len(shot["lines"]):
                pause = 1.1
            silence = round(pause * rate)
            pieces.append(np.zeros(silence, dtype=np.float32))
            cursor += silence
        end_frame = math.ceil(cursor * FPS / rate)
        aligned = round(end_frame * rate / FPS)
        pieces.append(np.zeros(aligned - cursor, dtype=np.float32))
        cursor = aligned
        shot_frames.append(end_frame - start_frame)
    return rate, np.concatenate(pieces), cues, shot_frames


def score(length, rate, theme, bpm=68):
    rng = random.Random(hashlib.sha256(theme.encode("utf-8")).digest())
    bed = np.zeros(length, dtype=np.float32)
    beat = 60 / bpm
    transpose = rng.choice([-5, -2, 0, 2])
    chords = ((50, 57, 62, 65, 69), (46, 53, 58, 62, 65),
              (53, 60, 65, 69, 72), (48, 55, 60, 64, 67))
    motif = [rng.choice((2, 3, 4)) for _ in range(4)]

    def note(start, beats, midi, gain, decay):
        first = round(start * beat * rate)
        count = min(round(beats * beat * rate), length - first)
        if count <= 0:
            return
        t = np.arange(count, dtype=np.float32) / rate
        phase = t * (2 * np.pi * 440 * 2 ** ((midi + transpose - 69) / 12))
        envelope = (1 - np.exp(-t * 22)) * np.exp(-t * decay)
        release = min(count, round(0.25 * rate))
        envelope[-release:] *= np.linspace(1, 0, release)
        bed[first:first+count] += gain * envelope * (np.sin(phase) + 0.19 * np.sin(phase * 2.001) + 0.07 * np.sin(phase * 3))

    for bar in range(math.ceil(length / (rate * beat * 4))):
        chord = chords[bar % 4]
        note(bar * 4, 4.4, chord[0], 0.085, 0.7)
        note(bar * 4 + 1, 3.3, chord[1], 0.055, 0.9)
        note(bar * 4 + 1.5, 2.8, chord[motif[bar % 4]], 0.068, 1.35)
        if bar % 4 != 3:
            note(bar * 4 + 3, 2.3, chord[motif[(bar + 1) % 4]], 0.046, 1.6)
    fade = min(length, int(1.0 * rate))
    bed[-fade:] *= np.linspace(1, 0, fade)
    return bed


def mix(path, rate, speech, music, cues):
    # A slow, pre-emptive gain envelope keeps the musical phrase under each line.
    gain = np.ones(len(music), dtype=np.float32)
    for start, end, _ in cues:
        a, b = round(start * rate), round(end * rate)
        left, right = max(0, a - rate // 7), min(len(gain), b + rate // 3)
        gain[a:b] = 0.48
        gain[left:a] = np.minimum(gain[left:a], np.linspace(1, 0.48, a-left))
        gain[b:right] = np.minimum(gain[b:right], np.linspace(0.48, 1, right-b))
    bed = music * gain
    delay = min(len(bed), round(0.045 * rate))
    right = bed * 0.89
    right[delay:] += bed[:-delay] * 0.16
    stereo = np.column_stack((speech + bed, speech + right))
    with wave.open(str(path), "wb") as out:
        out.setparams((2, 2, rate, 0, "NONE", "not compressed"))
        out.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())
