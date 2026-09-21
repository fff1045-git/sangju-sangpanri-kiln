# -*- coding: utf-8 -*-
"""ElevenLabs 보이스 라이브러리에서 한국어 원어민 여성 보이스를 찾는다."""
import os, sys, json, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from gen_audio import KEY  # noqa

def get(url):
    req = urllib.request.Request(url, headers={"xi-api-key": KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

q = urllib.parse.urlencode({"language": "ko", "gender": "female", "page_size": 40, "sort": "usage_character_count_1y"})
data = get("https://api.elevenlabs.io/v1/shared-voices?" + q)
for v in data.get("voices", []):
    print(json.dumps({k: v.get(k) for k in
        ["voice_id", "public_owner_id", "name", "accent", "age", "use_case", "descriptive", "language", "locale",
         "usage_character_count_1y", "cloned_by_count", "free_users_allowed"]}, ensure_ascii=False))
    print("   desc:", (v.get("description") or "")[:160].replace("\n", " "))
