"""Generate narration: one clip per segment, then one MP3 with a timings file.

Usage: .venv/bin/python tools/build_audio.py [voice]
Voices: uz-UZ-SardorNeural (male), uz-UZ-MadinaNeural (female)
"""
import asyncio, json, subprocess, sys, tempfile
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
VOICE = sys.argv[1] if len(sys.argv) > 1 else "uz-UZ-SardorNeural"
PAUSE = {"h1": 0.9, "h2": 0.6, "p": 0.8}   # silence after each segment, seconds
RATE = "-5%"                                 # a touch slower than default for a public space


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout)


async def main():
    content = json.loads((ROOT / "content.json").read_text())
    tmp = Path(tempfile.mkdtemp())
    parts, timings, t = [], [], 0.0
    for i, seg in enumerate(content["segments"]):
        clip = tmp / f"{i:02d}.mp3"
        # "ILMdir" would be spelled out letter by letter; speak it as a word
        text = seg["text"].replace("ILMdir", "ilmdir")
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(clip))
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
    out = ROOT / "docs" / "audio" / "narration.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c:a", "libmp3lame", "-b:a", "64k", str(out)], check=True)
    (ROOT / "docs" / "audio" / "timings.json").write_text(
        json.dumps({"voice": VOICE, "duration": round(t, 3), "segments": timings}, indent=1))
    print(f"{out}  {t:.1f}s  {out.stat().st_size // 1024} KB  voice={VOICE}")


asyncio.run(main())
