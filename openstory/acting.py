"""Draw articulated cel actors. The actor origin is the centre of the face."""
from math import exp, pi, sin

INK = "#382e32"
HAIR = {"bob", "wave", "silver", "crop", "braid"}
GESTURES = {"rest", "reach", "offer", "heart", "listen", "point", "press", "wipe", "wave", "recoil", "clap"}
PROPS = {"cassette", "mic", "wire"}


def path(d, fill, stroke=INK, width=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'


def oval(x, y, rx, ry, fill, stroke="none", width=1):
    return f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def group(transform, *parts):
    return '<g transform="' + transform + '">' + "".join(parts) + '</g>'


def clamp(x):
    return min(1., max(0., x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def face(p, mood, mouth, blink, glance):
    skin, hair = p["skin"], p["hair_color"]
    style = p["hair"]
    senior, child = style == "silver", p.get("child", False)
    cut = {
        "bob": "M-54 16 Q-66-30-38-58 Q-13-81 20-62 Q53-60 56-21 Q52 9 60 29 Q48 45 28 40 L30 2 Q31-14 24-32 Q6-15-21-13 Q-18-21-17-26 Q-35-19-38 5 L-31 41 Q-49 42-58 31Z",
        "wave": "M-52 23 Q-72 2-57-17 Q-62-36-44-48 Q-39-68-16-65 Q6-82 27-65 Q48-67 56-44 Q71-31 54-9 L43 6 Q35-10 29-29 Q16-14 3-15 Q10-23 11-29 Q-13-11-28-13 L-39 9 L-31 35 Q-48 44-52 23Z",
        "silver": "M-49 18 Q-62-19-46-43 Q-25-66-5-64 Q18-73 41-56 Q51-48 51-40 Q30-44 17-39 Q4-38-12-44 Q-23-47-29-29 L-33-3 L-43 15Z",
        "crop": "M-48 12 Q-58-13-50-40 L-58-44 Q-45-48-33-47 Q-30-62-11-63 L-15-72 Q3-71 14-60 Q40-68 54-41 Q59-31 48-18 Q41-19 35-27 Q25-13 10-12 L15-25 Q4-13-17-16 L-12-26 Q-27-20-35-13 L-40 8Z",
        "braid": "M-53 8 Q-59-42-32-58 Q0-76 35-56 Q59-38 50-10 Q31-22 17-41 Q-4-17-33-14 L-39 12Z",
    }[style]
    back = ""
    if style in {"bob", "wave", "braid"}:
        back = path("M-52-14 Q-61 8-58 39 Q-62 53-67 60 Q-48 72-29 58 L31 56 Q51 58 60 46 Q50 25 52 1 L39-32Z",hair)
    if style == "braid":
        back += "".join(oval(-48-i,25+11*i,10-i,10,hair,INK,1.4) for i in range(5))
        back += path("M-59 70 L-47 69","none",p["trim"],4)
    outline = ("M-42-26 Q-25-54 12-47 Q47-44 49-8 Q50 17 41 34 Q27 53 7 55 Q-17 55-33 38 Q-47 24-48 7Z" if child else
               "M-41-29 Q-17-57 18-47 Q46-42 49-16 L50 9 Q55 26 45 37 Q32 54 13 61 Q-5 66-23 51 Q-40 43-43 17 L-48 2Z")
    head = [back, path(outline, skin), path("M-40 5 Q-54-7-57 5 Q-60 18-44 23 Q-39 25-37 20",skin),
            path("M-51 8 Q-46 5-42 14 L-47 15","none","#ae7664",1.6)]
    # Soft cheek colour and a narrow turned nose keep the face legible in a two-shot.
    head += [oval(34,24,9,3.2,"#da9786"),oval(-22,23,10,3.7,"#da9786"),
             path("M16 8 Q17 17 23 21 Q21 25 15 24","none","#a06b5b",1.6)]
    worried = mood in ("uzgun","ozur","fisilti")
    bright = mood in ("neseli","heyecan","merak")
    angry = mood in ("kizgin","uyari")
    for x, wide in [(-14,12.5),(34,9.2)]:
        slope = (4.4 if worried else -4.4 if angry else 0) * (1 if x < 0 else -1)
        by = -9 - (3 if bright else 0)
        head.append(path(f"M{x-wide:.1f} {by+slope:.1f} Q{x} {by-5:.1f} {x+wide:.1f} {by-slope:.1f}","none",hair,3.8 if senior else 3))
        h = 5.2 if worried else 8.2 if bright or child else 6.3
        if blink:
            head.append(path(f"M{x-wide:.1f} 8 Q{x} 13 {x+wide:.1f} 7","none",INK,2.2))
        else:
            head.append(path(f"M{x-wide:.1f} 8 Q{x-1} {4-h:.1f} {x+wide:.1f} 6 Q{x} {9+h:.1f} {x-wide:.1f} 8Z","#fff3dc",INK,1.7))
            pupil = x+2.4+glance
            py = 9.2 if worried else 7.2
            head.extend([oval(pupil,py,3.8,4.2,"#533f33"),oval(pupil+.5,py,2.1,3,INK),oval(pupil+1,py-1.5,1.1,1.1,"#fff7db")])
    if mouth > .10:
        h = 3 + 12 * mouth
        w = 6 + 5 * (1-mouth) + (2 if bright else 0)
        head.extend([path(f"M{15-w:.1f} 38 Q13 34 {16+w:.1f} 36 Q19 {42+h:.1f} 12 {39+h:.1f} Q7 {38+h:.1f} {15-w:.1f} 38Z","#593038"),
                     oval(14,39+h*.55,w*.40,max(1,h*.18),"#c07c74")])
    else:
        bend = 45 if mood in ("neseli","heyecan") else 32 if worried else 39
        head.append(path(f"M4 39 Q14 {bend} 26 36","none",INK,2))
    if senior:
        head.extend([path("M0 30 Q8 23 16 28 Q23 23 34 29 L39 33 Q28 36 15 32 Q5 37-4 35Z",hair),
                     path("M-29 17 Q-19 22-12 20 M29 18 Q36 20 42 15 M-19 42 Q-16 49-10 50","none","#ae7968",1.3)])
    head.append(path(cut,hair))
    if style == "bob":
        head += [path("M-34-26 L-17-37 M-32-21 L-16-31","none","#d99c65",2.8), oval(-46,22,2.8,4.2,"#d4a15b",INK,1)]
    if style == "wave":
        head += [oval(-46,24,5.2,6.2,"#d9a54a",INK,1.6), path("M-40-43 Q-25-59-11-53 M7-55 Q20-61 31-51","none","#7b5944",2)]
    if style == "silver":
        head.append(path("M-43-38 Q-27-57-12-53 M-33-39 Q-18-50-7-49 M8-53 Q23-61 37-52","none","#e0d5be",2.4))
    return "".join(head)


def prop(name):
    if name == "cassette":
        return (path("M-21-13 L22-13 Q25-13 25-9 L24 14 L-22 14 Q-25 13-24 9 V-9Z","#c98638",INK,2)
                +path("M-18-8 H18 V4 H-18Z","#e0bc72",INK,1.3)
                +oval(-9,-2,4.1,4.1,"#494047")+oval(10,-2,4.1,4.1,"#494047")
                +path("M-13 12 L-10 7 H12 L16 12Z","none",INK,1.2))
    if name == "mic":
        return path("M-4-7 H5 V20 Q1 24-4 19Z","#797c70")+oval(1,-14,10,14,"#697a76",INK,2)+path("M-5-18 H7 M-6-14 H8 M-5-10 H7","none","#bdbfa8",1.6)
    if name == "wire":
        return path("M0 0 Q35-14 32 12 T77 18","none","#b94435",3)
    return ""


def arm(root, elbow, hand, skin, cloth, cuff, item="", gesture="rest", item_art=""):
    sx, sy = root
    ex, ey = elbow
    hx, hy = hand
    # The cuff and hand share a joint so objects follow the gesture.
    dx, dy = hx-ex, hy-ey
    length = max(1, (dx*dx+dy*dy)**.5)
    nx, ny = -dy/length, dx/length
    skeleton = f"M{sx:.1f} {sy:.1f} Q{ex:.1f} {ey:.1f} {ex:.1f} {ey:.1f} L{hx:.1f} {hy:.1f}"
    palm = oval(0,0,9,10,skin,INK,1.8)
    fingers = path("M-4-2 Q0-8 5-7 Q9-5 6-2 L2 1",skin,INK,1.3)
    if not (item or item_art) and gesture in ("point","press"):
        palm = path("M-8 5 Q-12-4-5-9 Q-2-12 4-9 L18-18 Q24-19 20-13 L9-2 Q15 5 8 10 Q1 14-8 5Z",skin)
        fingers = path("M1 1 L7-4 M4 4 L10 0","none","#a16f5a",1.2)
    elif not (item or item_art) and gesture in ("offer","wave","reach","clap"):
        palm = path("M-10 3 Q-13-4-11-11 Q-9-15-7-10 L-4-5 L0-14 Q2-17 4-13 L3-8 L8-14 Q12-15 11-11 L8-5 L14-10 Q19-10 16-6 L9 3 Q2 13-6 11Z",skin)
        fingers = path("M-5 3 Q0-2 6-2","none","#ac7962",1.2)
    return (path(skeleton,"none",INK,24)+path(skeleton,"none",cloth,20)
            +path(f"M{hx+8*nx:.1f} {hy+8*ny:.1f} l{-16*nx:.1f} {-16*ny:.1f}","none",cuff,3)
            +group(f"translate({hx+4*dx/length:.1f} {hy+4*dy/length:.1f})",
                   palm, group("translate(5 -7) rotate(-12)",item_art or prop(item)), fingers))


HANDS = {"rest":(56,203), "offer":(103,127), "reach":(102,101), "heart":(8,110),
         "listen":(35,37), "point":(107,86), "press":(93,151), "wipe":(22,27),
         "wave":(64,34), "recoil":(38,108), "clap":(18,119)}


def actor_svg(p, actor, t, phase, emotion, speaking, mouth, progress, item_art=""):
    x, y, s = actor["x"], actor["y"], actor["scale"]
    flip = -1 if actor.get("face", "right") == "left" else 1
    pose = actor.get("gesture","rest")
    move = smooth(progress * 4) * (1 - .22 * smooth((progress-.81)*5))
    # Prepare, lift, settle. A listener reacts a little later than the speaker.
    lead = .20 + .80 * move
    breath = sin(t*2.1+phase)
    nod = sin(t*4.4+phase)*1.4 if speaking else sin(t*1.35+phase)*.7
    lean = {"reach":-3, "press":-3, "recoil":5, "listen":2, "wipe":3}.get(pose,-1.2)
    tilt = {"merak":-6, "uzgun":7, "ozur":6, "heyecan":-4, "kizgin":3, "fisilti":5}.get(emotion,-1)
    glance = sin(phase+t*.9)*.7 - (3.8*move if emotion in ("uzgun","ozur") else 0)
    blink = ((t+phase*.71)%3.63 < .115) or (pose=="wipe" and .32<progress<.47)
    child = p.get("child",False)
    skin, cloth, cuff = p["skin"],p["coat"],p["trim"]
    pants = p["pants"]
    legs = path("M-38 213 Q0 201 40 213 L33 368 L9 369 L1 258 L-8 370 L-35 369Z",pants)
    feet = path("M-36 362 L-9 362 L-8 373 L-46 375 Q-53 369-36 362Z M8 362 L34 362 Q48 366 48 374 L8 374Z",INK)
    costume = [path("M-44 91 Q-31 75-13 75 L15 75 Q39 76 48 94 L40 146 L48 218 Q3 232-44 220 L-37 153Z",cloth),
               path("M-16 75 L-11 57 L18 55 L21 78 L2 96Z",skin),
               path("M-14 77 L1 94 L-7 114 L-27 86Z M18 76 L1 94 L13 112 L29 85Z",cuff),
               path("M1 96 L3 220","none",INK,1.5)]
    if p["hair"] in ("bob","silver"):
        costume += [path("M-31 141 L-10 140 L-11 159 Q-22 166-31 160Z","none",INK,1.4),
                    path("M12 125 L32 125 L31 141 L13 143Z",cuff,INK,1.3)]
    else:
        costume += [path("M-35 190 Q0 199 39 190","none",cuff,3)]
    for cy in (119,145,175,202):
        costume.append(oval(5,cy,1.9,2,"#e5bb83",INK,.8))
    target = HANDS[pose]
    hx = 51 + (target[0]-51)*lead
    hy = 188 + (target[1]-188)*lead + (2.8*nod if speaking else 1.5*breath)
    if pose=="press":
        hy += 16*exp(-((progress-.48)/.14)**2)
    if pose=="wave":
        hx += 11*sin(progress*5*pi)
    elbow = (max(51,hx*.68+17), 146+(hy-130)*.35)
    counter = move * (1 if pose in ("offer","recoil","wave") else .24)
    left_hand = (-43+3*breath-16*counter,199-35*counter)
    if pose == "clap":
        gap = 7 + 29 * (1+sin(4*pi*t))/2
        hx, hy = gap, 122+breath
        left_hand = (-gap,hy)
    left = arm((-35,98),(-52-8*counter,146),left_hand,skin,cloth,cuff,gesture=pose if pose=="clap" else "rest")
    right = arm((34,98),elbow,(hx,hy),skin,cloth,cuff,actor.get("prop",""),pose,item_art)
    head_scale = 1.16 if child else 1.
    head = group(f"translate({nod:.1f} {breath*1.6:.1f}) rotate({tilt*lead+nod:.2f} 0 56) scale({head_scale})",
                 face(p,emotion,mouth if speaking else 0,blink,glance))
    upper = group(f"rotate({lean*lead+breath*.6:.2f} 0 215) translate({nod*.6:.2f} {breath*.85:.2f})",
                  left,*costume,head,right)
    return group(f"translate({x} {y}) scale({s*flip} {s})",legs,feet,upper)
