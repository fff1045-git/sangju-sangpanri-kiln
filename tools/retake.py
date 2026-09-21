# -*- coding: utf-8 -*-
"""지정한 대사를 STT 결과가 대본과 일치할 때까지(최대 N회) 다시 생성한다.
사용: python tools/retake.py s1_2 s8_3 [--tries 4]"""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import VOICE, VOICE_ID, MODEL, OUT, post  # noqa
from check_audio import stt  # noqa

def norm(t):
    t = re.sub(r"[\s.,!?·'\"]", "", t)
    for a, b in [("2015", "이천십오"), ("이천십오년", "이천십오년")]:
        t = t.replace(a, b)
    return t.replace("상팔리", "상판리")  # STT의 연음 표기 차이는 허용

tries = int(sys.argv[sys.argv.index("--tries") + 1]) if "--tries" in sys.argv else 4
keys = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()]
for k in keys:
    text = VOICE[k]; path = os.path.join(OUT, f"v_{k}.mp3"); best = None
    for i in range(tries):
        data = post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_96",
                    {"text": text, "model_id": MODEL, "language_code": "ko",
                     "voice_settings": {"stability": 0.6, "similarity_boost": 0.85, "style": 0.1, "use_speaker_boost": True}})
        open(path, "wb").write(data)
        got = stt(path); ok = norm(got) == norm(text)
        print(f"{k} take{i+1} {'OK ' if ok else 'NG '} {got}")
        if ok: best = data; break
    if best is None: print(f"  !! {k}: 일치하는 테이크 없음 (마지막 테이크 유지)")
