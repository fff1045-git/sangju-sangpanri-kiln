# -*- coding: utf-8 -*-
"""'관요'라는 말의 층위(사전·학계·대중·중국)를 다룬 새 절을 합성 JSON에 끼워 넣는다.
사용: python tools/add_gwanyo_term_section.py <section.json>
section.json: {"heading":..., "body":[...], "table":{...}, "callout":..., "references":[{n,title,url,publisher,date,note}], "term_note": "...(선택)"}"""
import json, sys, re
p = 'tools/gwanyo_result.json'
o = json.load(open(p, encoding='utf-8')); S = o['합성']
sec = json.load(open(sys.argv[1], encoding='utf-8'))

# 이미 넣었으면 교체
S['sections'] = [s for s in S['sections'] if not s['heading'].endswith(sec['heading'].split('. ', 1)[-1])]
# 5절(학계의 판단) 뒤에 삽입
idx = next(i for i, s in enumerate(S['sections']) if '학계의 판단' in s['heading']) + 1
S['sections'].insert(idx, {k: sec[k] for k in ('heading', 'body', 'table', 'callout') if k in sec})

have = {r['n'] for r in S['references']}
for r in sec.get('references', []):
    if r['n'] not in have: S['references'].append(r)

# 각주 정합성 검사
ns = {r['n'] for r in S['references']}
txt = json.dumps(S, ensure_ascii=False)
used = set(int(x) for m in re.findall(r'\[(\d+(?:\s*,\s*\d+)*)\]', txt) for x in m.split(','))
missing = sorted(used - ns)
assert not missing, f"본문에 있으나 목록에 없는 각주: {missing}"
json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("inserted at", idx + 1, "| sections", len(S['sections']), "| refs", len(S['references']))
