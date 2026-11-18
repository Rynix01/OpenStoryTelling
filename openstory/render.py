"""Compile measured speech, illustrated shots and captions into a vertical film."""
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

import numpy as np

from .sound import FPS, mix, score, synthesize
from .story import compose, read_story
from .stage import film_shot


def ffmpeg(args, cwd, capture=False):
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-loglevel",
           "info" if capture else "error", "-y", *args]
    run = subprocess.run(cmd, cwd=cwd, check=True, stderr=subprocess.PIPE if capture else None)
    return run.stderr.decode("utf-8", "replace") if capture else ""


def stamp(t, srt=False):
    unit = 1000 if srt else 100
    whole, part = divmod(round(max(t, 0) * unit), unit)
    hours, tail = divmod(whole, 3600)
    minutes, seconds = divmod(tail, 60)
    if srt:
        return f"{hours:02}:{minutes:02}:{seconds:02},{part:03}"
    return f"{hours}:{minutes:02}:{seconds:02}.{part:02}"


ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Story,Georgia,39,&H00F3F7FF,&H00FFFFFF,&H0023211C,&H70201D1A,0,0,0,0,100,100,0,0,1,2.6,1,2,48,48,318,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def captions(cues, offset):
    events = []
    for a, b, line in cues:
        clean = line.replace("\\", "＼").replace("{", "｛").replace("}", "｝")
        wrapped = r"\N".join(textwrap.wrap(clean, width=32, break_long_words=False))
        events.append(f"Dialogue: 0,{stamp(a-offset)},{stamp(b-offset)},Story,,0,0,0,,{wrapped}")
    return ASS + "\n".join(events) + "\n"


def motion(shot, frames, animated=False):
    progress = f"on/{max(1, frames-1)}"
    modes = {"hold": "1", "push": f"1+0.085*{progress}", "pull": f"1.085-0.085*{progress}"}
    zoom = modes[shot.get("camera", "push")]
    return (f"scale=1440:2560,zoompan=z='{zoom}':x='iw/2-iw/zoom/2':"
            f"y='(ih-ih/zoom)*0.4':d={1 if animated else frames}:s=720x1280:fps={FPS},setsar=1,ass=shot.ass")


def mouth_intervals(speech, rate, first, count):
    # Use short RMS windows to switch the mouth drawing at syllable boundaries.
    levels = []
    for frame in range(first, first + count):
        sample = speech[round(frame * rate/FPS):round((frame+1) * rate/FPS)]
        levels.append(float(np.sqrt(np.mean(sample**2))) if len(sample) else 0)
    threshold = max(0.025, float(np.percentile(levels, 65)) * 0.8)
    active = np.array([False, *(v > threshold for v in levels), False], dtype=int)
    starts = np.flatnonzero(np.diff(active) == 1)
    ends = np.flatnonzero(np.diff(active) == -1)
    return "+".join(f"between(n,{a},{b-1})" for a, b in zip(starts, ends)) or "0"


def shot_inputs(images, shot, frames, speech, rate, start):
    if len(images) == 1:
        return ["-i", images["always"].name, "-vf", motion(shot, frames)]
    inputs = ["-loop", "1", "-framerate", str(FPS), "-i", images["always"].name]
    filters, previous = [], "[0:v]"
    for i, state in enumerate((s for s in ("speaking", "blink") if s in images), 1):
        inputs.extend(["-i", images[state].name])
        switch = mouth_intervals(speech, rate, start, frames) if state == "speaking" else f"lt(mod(n+{start}+41,113),4)"
        filters.append(f"{previous}[{i}:v]overlay=enable='{switch}'[p{i}]")
        previous = f"[p{i}]"
    filters.append(previous + motion(shot, frames, animated=True) + "[film]")
    return inputs + ["-filter_complex_threads", "2", "-filter_complex", ";".join(filters), "-map", "[film]"]


def normalize(path):
    args = ["-i", "mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=6:print_format=json", "-f", "null", "-"]
    log = ffmpeg(args, path, capture=True)
    stats = json.loads(log[log.rindex("{"):log.rindex("}")+1])
    return ("loudnorm=I=-14:TP=-1.5:LRA=6:linear=true"
            f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
            f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
            f":offset={stats['target_offset']}")


def render(source, destination, model, pace, seed):
    data = read_story(source)
    if destination.exists():
        raise ValueError(f"Çıktı zaten var: {destination}")
    if not shutil.which("ffmpeg"):
        raise ValueError("ffmpeg bulunamadı")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as staging:
        tmp = Path(staging).resolve()
        result = tmp / "result"
        result.mkdir()
        print("Türkçe anlatım hazırlanıyor…", flush=True)
        rate, speech, cues, durations = synthesize(data, model, pace)
        if data["version"] == 2:
            script = [line for shot in data["shots"] for line in shot["lines"]]
            takes = [dict(start=round(a, 3), end=round(b, 3), voice=data["voices"][line["speaker"]], **line)
                     for (a, b, _), line in zip(cues, script)]
            (result / "seslendirme.json").write_text(json.dumps({"engine": "Seslen TTS", "lines": takes},
                                                    ensure_ascii=False, indent=2), encoding="utf-8")
        music = score(len(speech), rate, seed or data["title"])
        mix(tmp / "mix.wav", rate, speech, music, cues)
        segments, cache = [], {}
        start_frame = cue_index = 0
        for i, (shot, frames) in enumerate(zip(data["shots"], durations)):
            name = shot["board"]
            staged = bool(data["boards"][name].get("actors"))
            if name not in cache:
                layers = data["boards"][name].get("layers", [])
                states = {"always"} | {layer.get("when", "always") for layer in layers}
                files = {}
                for state in sorted(states):
                    if staged:
                        files[state] = compose(data, name, source.parent, size=(540,960), state=state)
                        continue
                    board_file = tmp / f"board{len(cache)}-{state}.png"
                    compose(data, name, source.parent, state=state).save(board_file)
                    files[state] = board_file
                cache[name] = files
            end = cue_index + len(shot["lines"])
            (tmp / "shot.ass").write_text(captions(cues[cue_index:end], start_frame / FPS), encoding="utf-8-sig")
            clip = f"shot{i:03}.mp4"
            if staged:
                plates = (cache[name]["always"], cache[name].get("front"))
                film_shot(tmp, clip, data, shot, plates, cues[cue_index:end], speech, rate, start_frame, frames)
            else:
                inputs = shot_inputs(cache[name], shot, frames, speech, rate, start_frame)
                ffmpeg([*inputs, "-frames:v", str(frames),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                        "-threads", "4", clip], tmp)
            segments.append(f"file '{clip}'")
            start_frame += frames
            cue_index = end
            print(f"Plan {i+1}/{len(durations)}", flush=True)
        (tmp / "clips.txt").write_text("\n".join(segments), encoding="ascii")
        gain = normalize(tmp)
        ffmpeg(["-f", "concat", "-safe", "1", "-i", "clips.txt", "-i", "mix.wav",
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", gain, "-ar", "48000",
                "-c:a", "aac", "-b:a", "160k", "-t", f"{start_frame/FPS:.9f}", "-movflags", "+faststart",
                "-metadata", f"title={data['title']}", "-metadata", "comment=Yapay zekâ ile Türkçe seslendirme",
                "result/film.mp4"], tmp)
        srt = "\n\n".join(f"{i}\n{stamp(a,True)} --> {stamp(b,True)}\n{line}"
                          for i, (a, b, line) in enumerate(cues, 1))
        (result / "altyazi.srt").write_text(srt + "\n", encoding="utf-8-sig")
        result.rename(destination)
    print(destination / "film.mp4")
