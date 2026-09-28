"""Generate narration per language: one clip per segment, joined into one MP3 plus a timings file.

Usage: .venv/bin/python tools/build_audio.py [uz|ru|en ...]   (no argument = all languages)
Voice, spoken-only respellings ("say") and text come from content/<lang>.json.
"""
import asyncio, json, re, subprocess, sys, tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
PAUSE = {"h1": 0.9, "h2": 0.6, "p": 0.8}   # silence after each segment, seconds
RATE = "-5%"                                 # a touch slower than default for a public space


def speakable(text, c):
    for a, b in c.get("say", []):
        text = text.replace(a, b)
    if c["lang"] == "uz":
        # o‘ / g‘ as U+02BB, the official Uzbek letter; a plain ' reads as a short glottal stop
        text = re.sub(r"([OoGg])['‘’`]", "\\1\u02bb", text)
        text = re.sub(r"['’`]", "\u02bc", text)
    return text


async def synth(text, voice, path, tries=6):
    # the free Edge endpoint drops requests at random when called in quick succession; back off and retry
    for k in range(tries):
        try:
            return await edge_tts.Communicate(text, voice, rate=RATE).save(str(path))
        except edge_tts.exceptions.NoAudioReceived:
            if k == tries - 1:
                raise
            await asyncio.sleep(2 * (k + 1))


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout)


async def build(lang):
    c = json.loads((ROOT / "content" / f"{lang}.json").read_text())
    tmp = Path(tempfile.mkdtemp())
    parts, timings, t = [], [], 0.0
    for i, seg in enumerate(c["segments"]):
        clip = tmp / f"{i:02d}.mp3"
        await synth(speakable(seg["text"], c), c["voice"], clip)
        wav = tmp / f"{i:02d}.wav"
        pad = PAUSE[seg["type"]]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-af", f"apad=pad_dur={pad}",
                        "-ar", "24000", "-ac", "1", str(wav)], check=True)
        d = duration(wav)
        timings.append({"start": round(t, 3), "end": round(t + d - pad, 3)})
        parts.append(wav)
        t += d
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    outdir = ROOT / "docs" / "audio" / lang
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "narration.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "libmp3lame", "-b:a", "64k", str(out)], check=True)
    (outdir / "timings.json").write_text(
        json.dumps({"voice": c["voice"], "duration": round(t, 3), "segments": timings}, indent=1))
    print(f"{out.relative_to(ROOT)}  {t:.1f}s  {out.stat().st_size // 1024} KB  voice={c['voice']}")


langs = sys.argv[1:] or sorted(p.stem for p in (ROOT / "content").glob("*.json"))
for lang in langs:
    asyncio.run(build(lang))
