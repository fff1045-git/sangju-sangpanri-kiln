# -*- coding: utf-8 -*-
"""완성 축하 연출용 효과음(폭죽·박수) 후보를 audio/_cele_cand/ 에 만든다."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import post, OUT  # noqa

SFX = {
    "fireworks": ("three small festive fireworks: quick whistle launches followed by bright pops and sparkling crackle, cheerful celebration, close, no music, no voices", 3.0),
    "fireworks_big": ("grand fireworks finale: several whistling rockets, big booming bursts and long glittering crackle, festive celebration, no music, no voices", 5.0),
    "cheer": ("small group of people clapping and cheering happily, short warm applause, indoor, no music", 3.0),
}
d = os.path.join(OUT, "_cele_cand"); os.makedirs(d, exist_ok=True)
for name, (p, dur) in SFX.items():
    for k in range(2):
        data = post("https://api.elevenlabs.io/v1/sound-generation",
                    {"text": p, "duration_seconds": dur, "prompt_influence": 0.6})
        path = os.path.join(d, f"{name}_{k}.mp3")
        open(path, "wb").write(data); print("saved", path, len(data)//1024, "KB")
