"""Write short clips of hard words in several spellings to pronunciation_tests/, to choose by ear."""
import asyncio
from pathlib import Path

import edge_tts

OUT = Path(__file__).resolve().parent.parent / "pronunciation_tests"
V = "uz-UZ-SardorNeural"
TESTS = {
    "school_1_as_written": "VOSIQ International School",
    "school_2_english_respelled": "Vosiq Interneshnl Skul",
    "school_3_english_respelled_alt": "Vosiq Interneshenal Skuul",
    "oz_1_plain_apostrophe": "quyosh o'z atrofidagi sayyoralarga",
    "oz_2_uzbek_letter": "quyosh oʻz atrofidagi sayyoralarga",
    "oz_3_doubled": "quyosh oʻʻz atrofidagi sayyoralarga",
    "atom_1_as_written": "mikro olamni (atom tuzilishi)",
    "atom_2_atoom": "mikro olamni (atoom tuzilishi)",
    "atom_3_accent": "mikro olamni (atóm tuzilishi)",
    "atom_4_attom": "mikro olamni (attom tuzilishi)",
}


async def main():
    OUT.mkdir(exist_ok=True)
    for name, text in TESTS.items():
        await edge_tts.Communicate(text, V, rate="-5%").save(str(OUT / f"{name}.mp3"))
    print(len(TESTS), "clips in", OUT)

asyncio.run(main())
