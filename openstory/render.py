"""Compile measured speech, illustrated shots and captions into a vertical film."""
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

from .sound import FPS, mix, score, synthesize
from .story import compose, read_story


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


def motion(shot, frames):
    progress = f"on/{max(1, frames-1)}"
    modes = {"hold": "1", "push": f"1+0.085*{progress}", "pull": f"1.085-0.085*{progress}"}
    zoom = modes[shot.get("camera", "push")]
    return (f"scale=1440:2560,zoompan=z='{zoom}':x='iw/2-iw/zoom/2':"
            f"y='(ih-ih/zoom)*0.4':d={frames}:s=720x1280:fps={FPS},setsar=1,ass=shot.ass")


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
        music = score(len(speech), rate, seed or data["title"])
        mix(tmp / "mix.wav", rate, speech, music, cues)
        segments, cache = [], {}
        start_frame = cue_index = 0
        for i, (shot, frames) in enumerate(zip(data["shots"], durations)):
            name = shot["board"]
            if name not in cache:
                board_file = tmp / f"board{len(cache)}.png"
                compose(data, name, source.parent).save(board_file)
                cache[name] = board_file
            end = cue_index + len(shot["lines"])
            (tmp / "shot.ass").write_text(captions(cues[cue_index:end], start_frame / FPS), encoding="utf-8-sig")
            clip = f"shot{i:03}.mp4"
            ffmpeg(["-i", cache[name].name, "-vf", motion(shot, frames), "-frames:v", str(frames),
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
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                "-metadata", f"title={data['title']}", "result/film.mp4"], tmp)
        srt = "\n\n".join(f"{i}\n{stamp(a,True)} --> {stamp(b,True)}\n{line}"
                          for i, (a, b, line) in enumerate(cues, 1))
        (result / "altyazi.srt").write_text(srt + "\n", encoding="utf-8-sig")
        result.rename(destination)
    print(destination / "film.mp4")
