# -*- coding: utf-8 -*-
"""ElevenLabs로 퍼즐 게임 효과음·보이스를 생성해 audio/ 폴더에 저장한다.

사용법:
  set ELEVENLABS_API_KEY=...   (PowerShell: $env:ELEVENLABS_API_KEY="...")
  python tools/gen_audio.py            # 전부 생성 (이미 있는 파일은 건너뜀)
  python tools/gen_audio.py --force    # 전부 다시 생성
  python tools/gen_audio.py --only sfx | voice
"""
import os, sys, json, time, urllib.request, urllib.error

KEY = os.environ.get("ELEVENLABS_API_KEY")
if not KEY:
    sys.exit("ELEVENLABS_API_KEY 환경변수가 없습니다.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio")
os.makedirs(OUT, exist_ok=True)
FORCE = "--force" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None

# ---- 효과음: /v1/sound-generation ----
SFX = {
    "pickup":   ("a single small ceramic sherd being picked up from a wooden table, light porcelain tap, dry, short, no reverb", 0.6),
    "snap":     ("two porcelain fragments clicking together and locking into place, crisp ceramic click, satisfying, short", 0.7),
    "miss":     ("a ceramic sherd set down gently on cloth, soft muted thud, very short", 0.6),
    "shuffle":  ("a handful of broken pottery pieces being scattered across a wooden table, clattering ceramic shards, one second", 1.4),
    "hint":     ("soft magical shimmer, gentle rising glass chime, subtle, one second", 1.2),
    "complete": ("warm celebratory chime with a soft Korean gayageum pluck flourish, bright, resolving, two seconds", 2.5),
    "allclear": ("triumphant short fanfare with traditional Korean percussion buk drum hit and gong shimmer, three seconds", 3.5),
}

# ---- 보이스: /v1/text-to-speech ----
# 한국어가 자연스러운 다국어 프리메이드 보이스. 바꾸려면 VOICE_ID를 교체.
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "XrExE9yKIg1WjnnlVkGX")  # Matilda (multilingual)
MODEL = "eleven_multilingual_v2"
VOICE = {
    "intro":   "상주 상판리 가마터에서 나온 파편처럼, 조각을 맞춰 왕실 분청사기를 완성해 보세요.",
    "lv1":     "레벨 일. 인화문 대접. 여섯 조각입니다.",
    "lv2":     "레벨 이. 분청사기 향로. 아홉 조각입니다.",
    "lv3":     "레벨 삼. 상감 분청 자라병. 열두 조각입니다.",
    "half":    "좋아요, 절반을 맞췄어요.",
    "hint":    "잠시 완성된 모습을 보여드릴게요.",
    "shuffle": "조각을 다시 섞었어요.",
    "done1":   "대접 완성! 관청 이름을 새겨 궁중에 납품하던 그릇이에요.",
    "done2":   "향로 완성! 제사와 의례에 쓰인 왕실용 특수 기종이에요.",
    "done3":   "자라병 완성! 전세품으로만 알려졌다가, 상판리에서 조각이 처음 출토된 기종이에요.",
    "allclear": "축하해요! 상판리 가마의 왕실 도자기 세 점을 모두 완성했어요.",
}

def post(url, body, accept="audio/mpeg"):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": accept})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")
            if e.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(3 * (attempt + 1)); continue
            raise SystemExit(f"HTTP {e.code} {url}\n{msg}")

def save(name, data):
    path = os.path.join(OUT, name + ".mp3")
    with open(path, "wb") as f: f.write(data)
    print(f"  saved {name}.mp3 ({len(data)//1024} KB)")

def gen_sfx():
    print("[sfx]")
    for name, (prompt, dur) in SFX.items():
        if not FORCE and os.path.exists(os.path.join(OUT, name + ".mp3")):
            print(f"  skip {name}"); continue
        data = post("https://api.elevenlabs.io/v1/sound-generation",
                    {"text": prompt, "duration_seconds": dur, "prompt_influence": 0.5})
        save(name, data)

def gen_voice():
    print(f"[voice] voice={VOICE_ID} model={MODEL}")
    for name, text in VOICE.items():
        fname = "v_" + name
        if not FORCE and os.path.exists(os.path.join(OUT, fname + ".mp3")):
            print(f"  skip {fname}"); continue
        data = post(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_96",
                    {"text": text, "model_id": MODEL,
                     "voice_settings": {"stability": 0.5, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}})
        save(fname, data)

if ONLY in (None, "sfx"): gen_sfx()
if ONLY in (None, "voice"): gen_voice()
print("done ->", OUT)
