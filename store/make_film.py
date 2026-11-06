#!/usr/bin/env python3
"""Cut the Ashford menswear film and the vertical reel from the campaign stills."""

import math
import struct
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"
FILM = ROOT / "film"
BUILD = Path("/tmp/ashford-build")
FPS = 24
FADE = 0.5

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"
INK = "0x141210"
CREAM = "0xF4F0E8"
WARM = "0xE4D7C4"

WIDE = [
    {
        "kind": "full",
        "img": "ashford-atelier.jpg",
        "hold": 3.4,
        "title": "ASHFORD",
        "sub": "MENSWEAR",
        "title_y": 450,
        "sub_y": 545,
        "title_size": 92,
        "scrim": False,
    },
    {
        "kind": "full",
        "img": "ashford-hero-coat.jpg",
        "hold": 4.4,
        "title": "The Charter Coat",
        "sub": "CHARCOAL WOOL",
        "title_y": 860,
        "sub_y": 935,
        "title_size": 64,
        "scrim": True,
    },
    {
        "kind": "panel",
        "img": "ashford-oxford.jpg",
        "hold": 3.8,
        "title": "The Meridian Shirt",
        "sub": "IVORY OXFORD",
        "price": "INR 6,800",
        "side": "left",
        "index": "01",
    },
    {
        "kind": "panel",
        "img": "ashford-knit.jpg",
        "hold": 3.8,
        "title": "The Harbor Knit",
        "sub": "NAVY MERINO",
        "price": "INR 9,400",
        "side": "right",
        "index": "02",
    },
    {
        "kind": "panel",
        "img": "ashford-suede.jpg",
        "hold": 3.6,
        "title": "The Ledger Jacket",
        "sub": "CAMEL SUEDE",
        "price": "INR 22,000",
        "side": "left",
        "index": "03",
    },
    {
        "kind": "panel",
        "img": "ashford-linen.jpg",
        "hold": 4.0,
        "title": "The Night Linen",
        "sub": "BLACK LINEN",
        "price": "INR 16,500",
        "side": "right",
        "index": "04",
    },
    {
        "kind": "end",
        "hold": 4.0,
        "title": "ASHFORD",
        "sub": "Cut for the city.",
        "foot": "SHOP THE COLLECTION",
    },
]

REEL = [
    {
        "kind": "letter",
        "img": "ashford-atelier.jpg",
        "hold": 3.2,
        "title": "ASHFORD",
        "sub": "MENSWEAR",
    },
    {
        "kind": "portrait",
        "img": "ashford-oxford.jpg",
        "hold": 3.6,
        "title": "The Meridian Shirt",
        "sub": "IVORY OXFORD",
    },
    {
        "kind": "letter",
        "img": "ashford-hero-coat.jpg",
        "hold": 3.6,
        "title": "The Charter Coat",
        "sub": "CHARCOAL WOOL",
    },
    {
        "kind": "portrait",
        "img": "ashford-knit.jpg",
        "hold": 3.4,
        "title": "The Harbor Knit",
        "sub": "NAVY MERINO",
    },
    {
        "kind": "portrait",
        "img": "ashford-suede.jpg",
        "hold": 3.4,
        "title": "The Ledger Jacket",
        "sub": "CAMEL SUEDE",
    },
    {
        "kind": "portrait",
        "img": "ashford-linen.jpg",
        "hold": 3.6,
        "title": "The Night Linen",
        "sub": "BLACK LINEN",
    },
    {
        "kind": "card",
        "hold": 3.6,
        "title": "ASHFORD",
        "sub": "Cut for the city.",
    },
]


def run(cmd):
    subprocess.run(cmd, check=True)


def tracked(text):
    return "  ".join(text)


def alpha(hold):
    out_start = max(1.15, hold - 0.55)
    return (
        f"if(lt(t\\,0.35)\\,0\\,"
        f"if(lt(t\\,1.05)\\,(t-0.35)/0.7\\,"
        f"if(lt(t\\,{out_start:.2f})\\,1\\,"
        f"max(0\\,({out_start + 0.4:.2f}-t)/0.4))))"
    )


def write_caption(path, text):
    path.write_text(text, encoding="utf-8")
    return str(path)


def drawtext(textfile, font, size, color, x, y, hold, fontcolor_alpha=1):
    return (
        f"drawtext=fontfile={font}:textfile={textfile}:fontsize={size}:"
        f"fontcolor={color}:x={x}:y={y}:alpha='{alpha(hold)}'"
    )


def grade():
    return "eq=saturation=0.9:contrast=1.05:gamma=0.98"


def encode(cmd_inputs, filter_complex, frames, out, fade_out=False, dur=0):
    vf = filter_complex
    if fade_out:
        vf += f",fade=t=out:st={max(0, dur - 0.55):.2f}:d=0.55"
    cmd = [
        "ffmpeg",
        "-y",
        *cmd_inputs,
        "-filter_complex",
        vf,
        "-frames:v",
        str(frames),
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-preset",
        "veryfast",
        "-an",
        str(out),
    ]
    run(cmd)


def render_wide_scene(scene, index, dur, out):
    frames = round(dur * FPS)
    cap = BUILD / "txt"
    title = write_caption(cap / f"w{index}-title.txt", scene["title"])
    sub = write_caption(cap / f"w{index}-sub.txt", tracked(scene["sub"]) if scene["sub"].isupper() else scene["sub"])
    hold = scene["hold"]
    img = str(MEDIA / scene["img"]) if scene.get("img") else None

    if scene["kind"] == "full":
        scrim = ""
        if scene.get("scrim"):
            scrim = f",drawbox=x=0:y=780:w=1920:h=300:color=black@0.34:t=fill"
        vf = (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,"
            f"zoompan=z='min(1+0.035*in_time\\,1.045)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:fps={FPS},"
            f"{grade()},format=yuv420p{scrim},"
            f"{drawtext(title, SERIF, scene['title_size'], CREAM, '(w-text_w)/2', scene['title_y'], hold)},"
            f"{drawtext(sub, SANS, 22, WARM, '(w-text_w)/2', scene['sub_y'], hold)}"
        )
        if index == 0:
            vf += ",fade=t=in:st=0:d=0.6"
        encode(
            ["-framerate", str(FPS), "-loop", "1", "-i", img],
            vf,
            frames,
            out,
        )
        return

    if scene["kind"] == "panel":
        left = scene["side"] == "left"
        img_x = 72 if left else 1920 - 72 - 810
        text_x = 960 if left else 88
        rule_x = text_x
        idx = write_caption(cap / f"w{index}-idx.txt", scene["index"])
        price = write_caption(cap / f"w{index}-price.txt", scene["price"])
        vf = (
            f"[0:v]scale=900:1200,zoompan=z='min(1+0.02*in_time\\,1.025)':"
            f"x='(iw-iw/zoom)/2':y=0:d=1:s=810x1080:fps={FPS},setsar=1,format=yuv420p[p];"
            f"[1:v][p]overlay={img_x}:0:format=auto,setsar=1,"
            f"{drawtext(idx, SANS, 18, WARM, text_x, 400, hold)},"
            f"drawbox=x={rule_x}:y=438:w=56:h=1:color={WARM}@0.9:t=fill,"
            f"{drawtext(title, SERIF, 48, CREAM, text_x, 470, hold)},"
            f"{drawtext(sub, SANS, 20, WARM, text_x, 550, hold)},"
            f"{drawtext(price, SANS, 22, CREAM, text_x, 610, hold)}"
        )
        encode(
            [
                "-framerate",
                str(FPS),
                "-loop",
                "1",
                "-i",
                img,
                "-f",
                "lavfi",
                "-i",
                f"color=c={INK}:s=1920x1080:r={FPS}:d={dur + 1}",
            ],
            vf,
            frames,
            out,
        )
        return

    foot = write_caption(cap / f"w{index}-foot.txt", tracked(scene["foot"]))
    vf = (
        f"[0:v]setsar=1,format=yuv420p,"
        f"{drawtext(title, SERIF, 92, CREAM, '(w-text_w)/2', 430, hold)},"
        f"{drawtext(sub, ITALIC, 36, WARM, '(w-text_w)/2', 545, hold)},"
        f"{drawtext(foot, SANS, 20, CREAM, '(w-text_w)/2', 630, hold)}"
    )
    encode(
        ["-f", "lavfi", "-i", f"color=c={INK}:s=1920x1080:r={FPS}:d={dur + 1}"],
        vf,
        frames,
        out,
        fade_out=True,
        dur=dur,
    )


def render_reel_scene(scene, index, dur, out):
    frames = round(dur * FPS)
    cap = BUILD / "txt"
    title = write_caption(cap / f"r{index}-title.txt", scene["title"])
    sub_text = tracked(scene["sub"]) if scene["sub"].isupper() else scene["sub"]
    sub = write_caption(cap / f"r{index}-sub.txt", sub_text)
    hold = scene["hold"]
    img = str(MEDIA / scene["img"]) if scene.get("img") else None

    if scene["kind"] == "portrait":
        vf = (
            f"[0:v]scale=1440:1920,zoompan=z='min(1+0.018*in_time\\,1.025)':"
            f"x='(iw-iw/zoom)/2':y=0:d=1:s=1080x1920:fps={FPS},"
            f"setsar=1,{grade()},format=yuv420p,"
            f"drawbox=x=0:y=1500:w=1080:h=420:color=black@0.38:t=fill,"
            f"{drawtext(title, SERIF, 54, CREAM, '(w-text_w)/2', 1600, hold)},"
            f"{drawtext(sub, SANS, 22, WARM, '(w-text_w)/2', 1685, hold)}"
        )
        if index == 0:
            vf += ",fade=t=in:st=0:d=0.45"
        encode(["-framerate", str(FPS), "-loop", "1", "-i", img], vf, frames, out)
        return

    if scene["kind"] == "letter":
        vf = (
            f"[0:v]scale=1280:-2,zoompan=z='min(1+0.03*in_time\\,1.04)':"
            f"x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1080x608:fps={FPS},setsar=1,{grade()},format=yuv420p[p];"
            f"[1:v][p]overlay=(W-w)/2:560:format=auto,setsar=1,"
            f"{drawtext(title, SERIF, 64, CREAM, '(w-text_w)/2', 1260, hold)},"
            f"{drawtext(sub, SANS, 22, WARM, '(w-text_w)/2', 1355, hold)}"
        )
        if index == 0:
            vf += ",fade=t=in:st=0:d=0.5"
        encode(
            [
                "-framerate",
                str(FPS),
                "-loop",
                "1",
                "-i",
                img,
                "-f",
                "lavfi",
                "-i",
                f"color=c={INK}:s=1080x1920:r={FPS}:d={dur + 1}",
            ],
            vf,
            frames,
            out,
        )
        return

    vf = (
        f"[0:v]setsar=1,format=yuv420p,"
        f"{drawtext(title, SERIF, 78, CREAM, '(w-text_w)/2', 860, hold)},"
        f"{drawtext(sub, ITALIC, 36, WARM, '(w-text_w)/2', 970, hold)}"
    )
    encode(
        ["-f", "lavfi", "-i", f"color=c={INK}:s=1080x1920:r={FPS}:d={dur + 1}"],
        vf,
        frames,
        out,
        fade_out=True,
        dur=dur,
    )


def xfade(clips, holds, out):
    inputs = []
    for clip in clips:
        inputs.extend(["-i", str(clip)])
    parts = []
    last = "[0:v]"
    acc = 0.0
    for i in range(1, len(clips)):
        acc += holds[i - 1]
        nxt = f"[v{i}]" if i < len(clips) - 1 else "[outv]"
        parts.append(
            f"{last}[{i}:v]xfade=transition=fade:duration={FADE}:offset={acc:.3f}{nxt}"
        )
        last = nxt
    run(
        [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            ";".join(parts),
            "-map",
            "[outv]",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-preset",
            "veryfast",
            "-an",
            str(out),
        ]
    )


def chord_weight(t, start, length, fade=1.4):
    if t < start or t > start + length:
        return 0.0
    local = t - start
    if local < fade:
        return local / fade
    if local > length - fade:
        return max(0.0, (length - local) / fade)
    return 1.0


def write_score(path, duration):
    rate = 48000
    count = int(duration * rate)
    chords = [
        (0.0, 11.0, (146.83, 174.61, 220.00)),
        (8.5, 11.0, (164.81, 196.00, 246.94)),
        (16.5, max(6.0, duration - 15.0), (130.81, 174.61, 220.00)),
    ]
    left = []
    right = []
    for i in range(count):
        t = i / rate
        master = 1.0
        if t < 1.6:
            master = t / 1.6
        if t > duration - 2.4:
            master = max(0.0, (duration - t) / 2.4)
        swell = 0.85 + 0.15 * math.sin(2 * math.pi * t / 9.0)
        sample_l = 0.0
        sample_r = 0.0
        for start, length, freqs in chords:
            weight = chord_weight(t, start, length) * swell
            if weight <= 0:
                continue
            for freq in freqs:
                # A slight detune between channels keeps the pad from sounding like a test tone.
                sample_l += math.sin(2 * math.pi * freq * t) * 0.045 * weight
                sample_l += math.sin(2 * math.pi * freq * 0.997 * t) * 0.02 * weight
                sample_r += math.sin(2 * math.pi * freq * 1.004 * t) * 0.045 * weight
                sample_r += math.sin(2 * math.pi * freq * 2 * t + 0.4) * 0.008 * weight
        sample_l = max(-0.9, min(0.9, sample_l * master))
        sample_r = max(-0.9, min(0.9, sample_r * master))
        left.append(sample_l)
        right.append(sample_r)

    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        frames = bytearray()
        for l, r in zip(left, right):
            frames += struct.pack("<hh", int(l * 32767), int(r * 32767))
        handle.writeframes(frames)


def mux(video, audio, out):
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            "-shortest",
            str(out),
        ]
    )


def stamp(seconds):
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    if ms == 1000:
        whole += 1
        ms = 0
    minutes, secs = divmod(whole, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def write_vtt(path, scenes):
    lines = ["WEBVTT", ""]
    cursor = 0.0
    for scene in scenes:
        end = cursor + scene["hold"]
        caption = scene["title"]
        if scene.get("sub"):
            caption += " — " + scene["sub"].replace("  ", " ")
        lines.append(f"{stamp(cursor)} --> {stamp(end)}")
        lines.append(caption)
        lines.append("")
        cursor = end
    path.write_text("\n".join(lines), encoding="utf-8")


def build(scenes, renderer, name):
    holds = [scene["hold"] for scene in scenes]
    clips = []
    for index, scene in enumerate(scenes):
        dur = scene["hold"] + (0 if index == len(scenes) - 1 else FADE)
        clip = BUILD / f"{name}-{index:02d}.mp4"
        print(f"rendering {clip.name} ({dur:.2f}s)")
        renderer(scene, index, dur, clip)
        clips.append(clip)
    silent = BUILD / f"{name}-silent.mp4"
    print(f"joining {name}")
    xfade(clips, holds, silent)
    duration = sum(holds)
    audio = BUILD / f"{name}.wav"
    write_score(audio, duration)
    final = FILM / f"ashford-{name}.mp4"
    mux(silent, audio, final)
    write_vtt(FILM / f"ashford-{name}.vtt", scenes)
    print(f"wrote {final} ({duration:.2f}s)")


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "txt").mkdir(exist_ok=True)
    FILM.mkdir(exist_ok=True)
    build(WIDE, render_wide_scene, "film")
    build(REEL, render_reel_scene, "reel")


if __name__ == "__main__":
    main()
