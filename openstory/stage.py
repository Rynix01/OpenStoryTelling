"""Sample a performance at 15 distinct poses per second and deliver 30 fps."""
import io
import math
import subprocess

import numpy as np
import resvg_py
from PIL import Image

from .acting import actor_svg
from .sound import FPS


def draw_actors(data, board, background, foreground, timing, scene_time, progress, level):
    line = timing or {}
    figures = []
    for index, actor in enumerate(board["actors"]):
        name = actor["id"]
        on_screen = line.get("speaker") == name and line.get("mode", "dialogue") == "dialogue"
        personal = line.get("speaker") == name
        pose = actor
        if personal and "gesture" in line:
            pose = {**actor, "gesture":line["gesture"]}
        mood = line["emotion"] if personal else actor.get("emotion","notr")
        figures.append(actor_svg(data["puppets"][name], pose, scene_time, 1.27*(index+1),
                                 mood, on_screen, level, progress))
    w, h = background.size
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 720 1280">{"".join(figures)}</svg>'
    layer = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg))).convert("RGBA")
    image = background.copy()
    image.paste(layer, mask=layer.getchannel("A"))
    if foreground is not None:
        image.paste(foreground, mask=foreground.getchannel("A"))
    return image


def film_shot(tmp, clip, data, shot, plates, cues, speech, rate, start_frame, frames):
    board = data["boards"][shot["board"]]
    base, front = plates
    # Every cut has a fresh shot-local clock. Audio and subtitle cues stay on the global clock.
    origin = start_frame / FPS
    zoom = shot.get("camera", "push")
    scale = {"hold":"1", "push":f"1+0.055*on/{max(1,frames-1)}",
             "pull":f"1.055-0.055*on/{max(1,frames-1)}"}[zoom]
    vf = (f"fps=30,scale=1080:1920,zoompan=z='{scale}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.42':"
          "d=1:s=720x1280:fps=30,setsar=1,ass=shot.ass")
    w, h = base.size
    command = ["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}",
               "-framerate","15","-i","pipe:0","-vf",vf,"-frames:v",str(frames),"-c:v","libx264","-threads","4",
               "-preset","veryfast","-crf","19","-pix_fmt","yuv420p",clip]
    with subprocess.Popen(command, cwd=tmp, stdin=subprocess.PIPE) as process:
        index = 0
        try:
            for n in range(math.ceil(frames / 2)):
                local = n / 15
                now = origin + local
                while index+1 < len(cues) and now >= cues[index+1][0]:
                    index += 1
                a,b,_ = cues[index]
                sound = speech[round(now*rate):round((now+1/15)*rate)]
                rms = float(np.sqrt(np.mean(sound**2))) if len(sound) and a <= now < b else 0
                progress = max(0, min(1, (now-a)/max(.1,b-a)))
                image = draw_actors(data,board,base,front,shot["lines"][index],now,progress,min(1,rms*9))
                process.stdin.write(image.tobytes())
        finally:
            process.stdin.close()
        if process.wait():
            raise subprocess.CalledProcessError(process.returncode, command)
