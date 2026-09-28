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
    "oz_4_cyrillic_word": "quyosh ўз atrofidagi sayyoralarga",
    "oz_5_cyrillic_sentence": "Худди қуёш ўз атрофидаги сайёраларга ёруғлик ва ҳаёт бағишлаганидек",
    "oz_6_latin_sentence_now": "Xuddi quyosh oʻz atrofidagi sayyoralarga yorugʻlik va hayot bagʻishlaganidek",
    "oz_7_o_umlaut": "quyosh öz atrofidagi sayyoralarga",
    "atom_1_as_written": "mikro olamni (atom tuzilishi)",
    "atom_2_attom": "mikro olamni (attom tuzilishi)",
    "atom_3_accent": "mikro olamni (átom tuzilishi)",
    "atom_4_capital": "mikro olamni (Atom tuzilishi)",
    "atom_5_atam": "mikro olamni (atam tuzilishi)",
}


async def main():
    OUT.mkdir(exist_ok=True)
    for name, text in TESTS.items():
        try:
            await edge_tts.Communicate(text, V, rate="-5%").save(str(OUT / f"{name}.mp3"))
        except edge_tts.exceptions.NoAudioReceived:
            print("voice returned no audio for", name)
            (OUT / f"{name}.mp3").unlink(missing_ok=True)
    print(len(list(OUT.glob("*.mp3"))), "clips in", OUT)

asyncio.run(main())
