# -*- coding: utf-8 -*-
"""워크플로 합성 결과(JSON)를 관요 논쟁 정리 HTML로 렌더한다.
사용: python tools/render_gwanyo.py <result.json> <out.html>"""
import json, sys, html, re

src, out = sys.argv[1], sys.argv[2]
data = json.load(open(src, encoding="utf-8"))
S = data["합성"]; C = data.get("점검") or {}
refs = {r["n"]: r for r in S["references"]}

def esc(t): return html.escape(str(t), quote=False)
def fn(t):
    """[n] 각주 → 링크. [1, 2] 형태도 처리."""
    t = esc(t)
    def rep(m):
        nums = [n.strip() for n in m.group(1).split(",")]
        return "".join(f'<sup><a href="#ref{n}" class="fn">[{n}]</a></sup>' for n in nums if n.isdigit())
    return re.sub(r"\[(\d+(?:\s*,\s*\d+)*)\]", rep, t)

def table(tb):
    if not tb or not tb.get("rows"): return ""
    h = "".join(f"<th>{fn(c)}</th>" for c in tb.get("columns", []))
    rows = "".join("<tr>" + "".join(f"<td>{fn(c)}</td>" for c in r) + "</tr>" for r in tb["rows"])
    cap = f'<caption>{fn(tb["caption"])}</caption>' if tb.get("caption") else ""
    return f'<div class="tw"><table>{cap}<tr>{h}</tr>{rows}</table></div>'

IMGS = {
    0: ("images/gwanyo/gamjo_1411.jpg", "1411년 한양에서 온 관원이 중모현 가마에서 화기 견본을 살펴보는 상상도",
        "그림 1. 1411년, 한양에서 파견된 내수(內竪)가 중모현 가마의 화기(花器) 제작을 감독하는 장면(AI 상상도). 『태종실록』의 '監做花器' 기록을 그림으로 옮긴 것으로, 실제 인물·복식·기물의 고증 자료가 아니에요."),
    3: ("images/gwanyo/gongnap_route.jpg", "짚으로 싼 도자기를 지게와 달구지에 싣고 산길을 넘어 한양으로 가는 공납 행렬 상상도",
        "그림 2. 상주에서 한양으로 가는 공납 도자기 행렬(AI 상상도). 관청 이름을 새긴 그릇은 이런 길을 거쳐 궁궐 관청에 닿았어요."),
    5: ("images/gwanyo/bunwon_vs_jibang.jpg", "왼쪽은 관청 건물과 여러 가마가 있는 광주 분원, 오른쪽은 초가 작업장과 가마 하나가 있는 지방 자기소를 나란히 그린 상상도",
        "그림 3. 왼쪽은 사옹원 분원(경기 광주)의 관요, 오른쪽은 지방의 상품 자기소(AI 상상도). 학계가 '관요'라는 말을 쓸 때 보통 떠올리는 것은 왼쪽 같은 체제예요."),
}

parts = []
parts.append(f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(S['title'])}</title>
<meta name="description" content="{esc(S['one_line'])}">
<style>
:root{{--bg:#f6f3ee;--paper:#fffdf9;--ink:#23211d;--muted:#6b655b;--line:#e2dbcf;--accent:#4f6f63;--accent-soft:#e3ece7;--clay:#a8683f;--clay-soft:#f4e6db;--warn:#8a5a14;--warn-soft:#fbf1dc;--ok:#3f6e4f;--ok-soft:#e1efe4;--no:#8c3b2f;--no-soft:#f6e3df}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#1a1917;--paper:#23221f;--ink:#ece7de;--muted:#a9a193;--line:#3a3731;--accent:#8fb8a8;--accent-soft:#2c3a34;--clay:#d99a6e;--clay-soft:#3a2d24;--warn:#e3b563;--warn-soft:#3a3120;--ok:#9ccaa9;--ok-soft:#263a2c;--no:#e39b8e;--no-soft:#3d2723}}}}
:root[data-theme="dark"]{{--bg:#1a1917;--paper:#23221f;--ink:#ece7de;--muted:#a9a193;--line:#3a3731;--accent:#8fb8a8;--accent-soft:#2c3a34;--clay:#d99a6e;--clay-soft:#3a2d24;--warn:#e3b563;--warn-soft:#3a3120;--ok:#9ccaa9;--ok-soft:#263a2c;--no:#e39b8e;--no-soft:#3d2723}}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{background:var(--bg);color:var(--ink);font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;line-height:1.75;font-size:16px;word-break:keep-all;overflow-wrap:break-word}}
.wrap{{max-width:900px;margin:0 auto;padding:32px 16px 64px}}
header.hero{{padding:8px 0 24px;border-bottom:1px solid var(--line);margin-bottom:28px}}
.eyebrow{{font-size:13px;letter-spacing:.08em;color:var(--clay);font-weight:700}}
h1{{font-family:"Noto Serif KR","Noto Serif CJK KR",serif;font-size:32px;line-height:1.3;margin:8px 0 12px}}
h2{{font-family:"Noto Serif KR","Noto Serif CJK KR",serif;font-size:22px;margin:50px 0 14px}}
h2 .n{{color:var(--clay);margin-right:8px}}
h3{{font-size:17px;margin:22px 0 8px}}
.lede{{color:var(--muted);font-size:17px;margin:0}}
.meta{{font-size:13px;color:var(--muted);margin-top:12px}}
p{{margin:0 0 12px}}ul,ol{{margin:0 0 14px;padding-left:22px}}li{{margin:4px 0}}a{{color:var(--accent)}}
.card{{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:16px 0}}
.key{{background:var(--accent-soft);border:none}}.key h3{{margin-top:0}}
.note{{background:var(--warn-soft);border:none;font-size:15px}}.note b{{color:var(--warn)}}
.callout{{border-left:3px solid var(--clay);background:var(--paper);padding:10px 16px;margin:14px 0;font-size:15px}}
.tw{{overflow-x:auto;margin:14px 0}}
table{{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--paper)}}
caption{{caption-side:top;text-align:left;font-size:13px;color:var(--muted);padding:0 0 6px}}
th,td{{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}}th{{background:var(--clay-soft);font-weight:700}}
figure{{margin:20px 0}}figure img{{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:12px;background:#efebe4}}
figcaption{{font-size:13px;color:var(--muted);margin-top:8px}}
.pill{{display:inline-block;font-size:12px;padding:2px 9px;border-radius:99px;font-weight:700;white-space:nowrap}}
.pill.ok{{background:var(--ok-soft);color:var(--ok)}}.pill.no{{background:var(--no-soft);color:var(--no)}}.pill.mid{{background:var(--warn-soft);color:var(--warn)}}
.fn{{text-decoration:none;font-size:11px;color:var(--accent)}}
.src{{font-size:13.5px}}.src li{{margin:5px 0}}
.corr td:first-child{{color:var(--no)}}.corr td:nth-child(2){{color:var(--ok)}}
.toc{{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:14px 18px;font-size:14px;columns:2;column-gap:24px}}
.toc a{{text-decoration:none}}
footer{{margin-top:48px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px}}
@media (max-width:640px){{h1{{font-size:26px}}.toc{{columns:1}}table{{font-size:13.5px}}th,td{{padding:8px}}}}
@media print{{:root{{--bg:#fff;--paper:#fff}}body{{font-size:11.5pt}}.wrap{{max-width:none;padding:0}}h2{{break-after:avoid}}figure,.card,table{{break-inside:avoid}}a{{color:var(--ink);text-decoration:none}}}}
@page{{size:A4;margin:16mm 15mm}}
</style>
</head>
<body><div class="wrap">
<header class="hero">
  <div class="eyebrow">쟁점 정리 · 2026년 9월 30일 기준</div>
  <h1>{esc(S['title'])}</h1>
  <p class="lede">{esc(S['one_line'])}</p>
  <div class="meta">조선왕조실록·국가유산포털·국가법령정보센터·학술 논문·언론 보도를 조사하고, 주장마다 별도 검증을 거쳐 정리했어요. 삽화 3점은 AI(GPT Image)로 그린 상상도예요. 보존회 관계자의 실명은 쓰지 않았어요.</div>
</header>
""")

# 핵심 요약
parts.append('<section class="card key"><h3>핵심 요약</h3><ol>' + "".join(f"<li>{fn(k)}</li>" for k in S["key_points"]) + "</ol></section>")

# 목차
secs = S["sections"]
for s in secs:  # 합성 단계가 붙인 "1. " 번호는 렌더러가 다시 붙이므로 뗀다
    s["heading"] = re.sub(r"^\s*\d+\.\s*", "", s["heading"])
toc = "".join(f'<div><a href="#s{i+1}">{i+1:02d} {esc(s["heading"])}</a></div>' for i, s in enumerate(secs))
extra = [("term", "용어 선택 권고"), ("corr", "원문 글의 바로잡을 점"), ("rec", "실행 권고"), ("ref", "출처")]
toc += "".join(f'<div><a href="#{a}">{len(secs)+i+1:02d} {t}</a></div>' for i, (a, t) in enumerate(extra))
parts.append(f'<nav class="toc">{toc}</nav>')

# 본문 절
for i, s in enumerate(secs):
    parts.append(f'<h2 id="s{i+1}"><span class="n">{i+1:02d}</span>{esc(s["heading"])}</h2>')
    if i in IMGS:
        src_, alt, cap = IMGS[i]
        parts.append(f'<figure><img src="{src_}" alt="{esc(alt)}" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>')
    for para in s["body"]:
        parts.append(f"<p>{fn(para)}</p>")
    parts.append(table(s.get("table")))
    if s.get("callout"):
        parts.append(f'<div class="callout">{fn(s["callout"])}</div>')

# 용어 권고
n0 = len(secs)
badge = {"권장": "ok", "조건부 사용": "mid", "비권장": "no"}
rows = "".join(f'<tr><td><b>{esc(t["term"])}</b></td><td><span class="pill {badge.get(t["recommendation"],"mid")}">{esc(t["recommendation"])}</span></td><td>{fn(t["support"])}</td><td>{fn(t["against"])}</td><td>{fn(t["reason"])}</td></tr>' for t in S["term_positions"])
parts.append(f'<h2 id="term"><span class="n">{n0+1:02d}</span>용어 선택 권고</h2><div class="tw"><table><tr><th style="width:16%">용어</th><th style="width:11%">권고</th><th>뒷받침하는 근거</th><th>반대 근거</th><th>판단 이유</th></tr>{rows}</table></div>')

# 바로잡을 점
if S["corrections"]:
    rows = "".join(f'<tr><td>{fn(c["original"])}</td><td>{fn(c["corrected"])}</td><td>{fn(c["why"])}</td></tr>' for c in S["corrections"])
    parts.append(f'<h2 id="corr"><span class="n">{n0+2:02d}</span>원문 글의 바로잡을 점</h2><p style="font-size:14px;color:var(--muted)">보존회에 공유된 글과 AI 자료에서 사실과 다르거나 확인되지 않은 부분이에요. 논쟁에서 상대가 먼저 지적할 수 있는 대목이라 미리 고쳐 두는 것이 안전해요.</p><div class="tw"><table class="corr"><tr><th style="width:32%">원문 표현</th><th style="width:34%">바른 내용</th><th>이유</th></tr>{rows}</table></div>')

# 실행 권고
parts.append(f'<h2 id="rec"><span class="n">{n0+3:02d}</span>실행 권고</h2><div class="card"><ol>' + "".join(f"<li>{fn(r)}</li>" for r in S["recommendations"]) + "</ol></div>")

# 남은 과제 + 점검 결과
unc = list(S.get("uncertainties", []))
for m in C.get("missing", []):
    if not m.get("found"): unc.append(f'{m["what"]} — {m["why_matters"]}')
if unc or C.get("risky_statements"):
    parts.append('<div class="card note"><b>확인하지 못한 것</b><ul>' + "".join(f"<li>{fn(u)}</li>" for u in unc) + "</ul>" +
                 ("<b>근거가 약해 단정을 피한 문장</b><ul>" + "".join(f"<li>{fn(r)}</li>" for r in C["risky_statements"]) + "</ul>" if C.get("risky_statements") else "") + "</div>")

# 점검자가 보완한 내용
found = [m for m in C.get("missing", []) if m.get("found")]
if found:
    parts.append('<h3>점검 단계에서 보완한 내용</h3><ul>' + "".join(f'<li><b>{esc(m["what"])}</b> — {fn(m["found"])} ' + " ".join(f'<a href="{esc(s["url"])}">↗</a>' for s in m.get("sources", [])) + "</li>" for m in found) + "</ul>")

# 출처
items = "".join(f'<li id="ref{r["n"]}"><a href="{esc(r["url"])}">{esc(r["title"])}</a>' + (f' — {esc(r["publisher"])}' if r.get("publisher") else "") + (f' ({esc(r["date"])})' if r.get("date") else "") + (f' <span style="color:var(--muted)">{esc(r["note"])}</span>' if r.get("note") else "") + "</li>" for r in sorted(S["references"], key=lambda r: r["n"]))
parts.append(f'<h2 id="ref"><span class="n">{n0+4:02d}</span>출처</h2><ol class="src">{items}</ol>')

parts.append("""<footer>2026년 9월 30일 작성 · 이 문서는 공개 자료를 바탕으로 한 정리이며 법률 자문이나 학술 감정이 아니에요. 그림 1~3은 AI 상상도로 실제 유구·인물의 고증 자료가 아니에요. 함께 보기: <a href="index.html">상판리 가마터 정리</a> · <a href="puzzle.html">파편 맞추기 퍼즐</a></footer>
</div></body></html>""")

open(out, "w", encoding="utf-8").write("\n".join(parts))
print("written", out, len("\n".join(parts)) // 1024, "KB")
