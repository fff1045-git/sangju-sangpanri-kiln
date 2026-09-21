# -*- coding: utf-8 -*-
"""생성된 보이스를 ElevenLabs Scribe(STT)로 되읽어 대본과 비교하고, 파일 길이를 출력한다."""
import os, sys, json, subprocess, urllib.request, uuid
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import VOICE, SFX, OUT, KEY  # noqa

def dur(path):
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],capture_output=True,text=True)
        return float(r.stdout.strip())
    except Exception:
        return -1

def stt(path):
    boundary = uuid.uuid4().hex
    data = open(path,"rb").read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\nscribe_v1\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"language_code\"\r\n\r\nko\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=body, method="POST",
        headers={"xi-api-key": KEY, "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r).get("text","")

print("[sfx durations]")
for n in SFX: print(f"  {n:9s} {dur(os.path.join(OUT,n+'.mp3')):5.2f}s")
print("[voice: script -> STT]")
for n,t in VOICE.items():
    p=os.path.join(OUT,"v_"+n+".mp3")
    print(f"  {n:9s} {dur(p):5.2f}s | {t}\n            STT: {stt(p)}")
