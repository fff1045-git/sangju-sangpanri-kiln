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
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "uyVNoMrnUku1dZyVEXwD")  # Anna Kim: 한국어 원어민 여성, 서울 표준어
MODEL = "eleven_multilingual_v2"
VOICE = {
    "intro":   "상주 상판리 가마터에서 나온 파편처럼, 조각을 맞춰 왕실 분청사기를 완성해 보세요.",
    "lv1":     "첫 번째 도자기, 인화문 대접이에요. 여섯 조각입니다.",
    "lv2":     "두 번째 도자기, 분청사기 향로예요. 아홉 조각입니다.",
    "lv3":     "세 번째 도자기, 상감 분청사기 자라병이에요. 열두 조각입니다.",
    "lv4":     "네 번째 도자기, 굽 높은 잔 고족배예요. 열여섯 조각입니다.",
    "lv5":     "다섯 번째 도자기, 뚜껑 있는 그릇 합이에요. 스무 조각입니다.",
    "lv6":     "여섯 번째 도자기, 인화문 베개예요. 스물네 조각입니다.",
    "lv7":     "일곱 번째 도자기, 분청사기 장고예요. 스물다섯 조각입니다.",
    "lv8":     "여덟 번째 도자기, 화분과 받침이에요. 서른 조각입니다.",
    "lv9":     "아홉 번째 도자기, 제기 보예요. 서른여섯 조각입니다.",
    "lv10":    "마지막 열 번째 도자기, 도자기 의자 돈이에요. 마흔두 조각입니다.",
    "praise1": "잘했어요! 멋지게 완성했어요.",
    "praise2": "훌륭해요! 조각이 딱 맞았어요.",
    "praise3": "와, 대단해요! 도자기가 되살아났어요.",
    "praise4": "정말 잘했어요! 솜씨가 아주 좋네요.",
    "praise5": "완벽해요! 옛 도공도 감탄하겠어요.",
    "half":    "좋아요, 절반을 맞췄어요.",
    "hint":    "잠시 완성된 모습을 보여드릴게요.",
    "shuffle": "조각을 다시 섞었어요.",
    "done1":   "이 도자기는 분청사기 인화문 대접이에요. 관청 이름을 새겨 궁중에 납품하던 그릇이랍니다.",
    "done2":   "이 도자기는 분청사기 향로예요. 제사와 의례에 쓰던 왕실용 특수 기종이랍니다.",
    "done3":   "이 도자기는 상감 분청사기 자라병이에요. 전해 오는 물건으로만 알려졌다가, 상판리에서 조각이 처음 나왔답니다.",
    "done4":   "이 도자기는 분청사기 고족배예요. 굽이 높은 잔으로, 제사상에 올리던 그릇이랍니다.",
    "done5":   "이 도자기는 분청사기 인화문 합이에요. 뚜껑이 있는 그릇으로, 음식이나 귀한 물건을 담았답니다.",
    "done6":   "이 도자기는 머리를 받치던 베개예요. 도장을 찍어 꽃무늬를 냈고, 상판리 첫 번째 가마에서 나왔답니다.",
    "done7":   "이 도자기는 분청사기 장고예요. 장구 몸통을 흙으로 빚어 구운, 아주 드문 기종이랍니다.",
    "done8":   "이 도자기는 분청사기 화분과 받침이에요. 궁궐 뜰을 꾸미던 왕실용 화분이랍니다.",
    "done9":   "이 도자기는 나라 제사에 곡식을 담던 네모난 제기예요. 이름은 보라고 해요.",
    "done10":  "이 도자기는 분청사기 돈, 도자기 의자예요. 왕실 정원에 놓던 귀한 물건이랍니다.",
    "allclear": "축하해요! 상판리 가마의 왕실 도자기 열 점을 모두 완성했어요. 당신은 이제 분청사기 전문가예요.",
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
                     "voice_settings": {"stability": 0.55, "similarity_boost": 0.85, "style": 0.15, "use_speaker_boost": True}, "language_code": "ko"})
        save(fname, data)

if __name__ == "__main__":
    if ONLY in (None, "sfx"): gen_sfx()
    if ONLY in (None, "voice"): gen_voice()
    print("done ->", OUT)
