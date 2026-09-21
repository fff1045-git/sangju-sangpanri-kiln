# -*- coding: utf-8 -*-
"""폭죽 '펑' 원샷, 발사 휘파람, 클리어 축하 징글 후보를 audio/_fx_cand/ 에 만든다."""
import os, sys, json, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import post, OUT, KEY  # noqa

d = os.path.join(OUT, "_fx_cand"); os.makedirs(d, exist_ok=True)
def save(name, data):
    p = os.path.join(d, name + ".mp3"); open(p, "wb").write(data); print("saved", name, len(data)//1024, "KB")

SFX = {
    "boom": ("single loud firework explosion: one deep powerful BOOM bang right at the start, followed by short sparkling crackle, close, punchy, no whistle, no music", 1.5),
    "whistle": ("single firework rocket launch: short rising whistle whoosh going up, no explosion at the end, no music", 0.7),
    "jingle_sfx": ("short cheerful victory jingle, bright celebratory fanfare with bells, gayageum pluck and small drum hit, happy ending chord, game level clear sound", 3.0),
}
for name, (p, dur) in SFX.items():
    for k in range(3 if name == "boom" else 2):
        save(f"{name}_{k}", post("https://api.elevenlabs.io/v1/sound-generation",
                                 {"text": p, "duration_seconds": dur, "prompt_influence": 0.7}))

# 음악 API로 짧은 징글 (최소 길이 제한이 있으면 실패 메시지만 출력)
body = {"prompt": "A short joyful celebration jingle for completing a puzzle level in a Korean traditional pottery game. "
                  "Korean fusion: bright gayageum run, daegeum flourish, light janggu and a sparkling bell, "
                  "ends on a warm major resolving chord. Instrumental, happy, triumphant but gentle.",
        "music_length_ms": 5000, "force_instrumental": True}
req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
    data=json.dumps(body).encode(), method="POST",
    headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
for k in range(2):
    try:
        with urllib.request.urlopen(req, timeout=300) as r: save(f"jingle_music_{k}", r.read())
    except urllib.error.HTTPError as e:
        print("music api:", e.code, e.read().decode("utf-8", "ignore")[:300]); break
