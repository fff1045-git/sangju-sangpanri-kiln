# -*- coding: utf-8 -*-
"""맞춤(snap) 효과음 후보를 여러 개 만들어 audio/_snap_cand/ 에 저장한다."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import post, OUT  # noqa

PROMPTS = [
    "a heavy porcelain bowl set down firmly on a wooden table, single sharp clear ceramic 'tak' impact, close mic, loud, dry, no reverb, no music",
    "a ceramic cup placed down decisively onto a hard stone surface, one crisp solid clack, close up, loud, dry, no echo",
    "single loud clean click of a ceramic piece seated firmly into place on a wooden board, sharp transient, short, dry, no reverb",
]
d = os.path.join(OUT, "_snap_cand"); os.makedirs(d, exist_ok=True)
for i, p in enumerate(PROMPTS):
    for k in range(2):
        data = post("https://api.elevenlabs.io/v1/sound-generation",
                    {"text": p, "duration_seconds": 0.6, "prompt_influence": 0.7})
        path = os.path.join(d, f"snap_{i}{k}.mp3")
        open(path, "wb").write(data); print("saved", path, len(data)//1024, "KB")
