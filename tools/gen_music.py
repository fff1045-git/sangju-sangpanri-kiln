# -*- coding: utf-8 -*-
"""ElevenLabs Music API로 잔잔한 퓨전 국악 배경음악을 생성해 audio/bgm.mp3 로 저장한다."""
import os, sys, json, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import KEY, OUT  # noqa

PROMPT = ("Calm, gentle Korean fusion instrumental (퓨전 국악) for a relaxing puzzle game. "
          "Solo gayageum plucked melody with soft daegeum bamboo flute phrases, light haegeum long tones, "
          "sparse warm piano pads and subtle ambient synth bed, very soft janggu brush rhythm. "
          "Slow tempo around 62 BPM, pentatonic, meditative, no vocals, no drums drops, no build-ups, "
          "consistent dynamics so it can loop seamlessly. Museum-like, contemplative, warm.")
LEN_MS = int(os.environ.get("BGM_MS", "90000"))
FORCE = "--force" in sys.argv
path = os.path.join(OUT, "bgm.mp3")
if os.path.exists(path) and not FORCE:
    sys.exit(f"exists: {path} (use --force)")

body = {"prompt": PROMPT, "music_length_ms": LEN_MS, "force_instrumental": True}
req = urllib.request.Request("https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128",
    data=json.dumps(body).encode("utf-8"), method="POST",
    headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}\n{e.read().decode('utf-8','ignore')}")
with open(path, "wb") as f: f.write(data)
print(f"saved bgm.mp3 ({len(data)//1024} KB)")
