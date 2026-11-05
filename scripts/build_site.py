#!/usr/bin/env python3
"""briefs/*.json → docs/index.html (날짜별 #YYYY-MM-DD 앵커)."""
import json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATS = ["영상", "이미지", "사운드"]
e = html.escape


def item_html(it):
    return f"""<article class="item" data-cat="{e(it['category'])}">
  <div class="meta"><span class="cat c-{CATS.index(it['category']) if it['category'] in CATS else 9}">{e(it['category'])}</span>
  <span>{e(it.get('source',''))}</span><span>{e(it.get('posted',''))}</span></div>
  <h3><a href="{e(it['url'])}" target="_blank" rel="noopener">{e(it['title'])}</a></h3>
  <p>{e(it['summary'])}</p>
</article>"""


def brief_html(b):
    src = ", ".join(f"{k} {v}건" for k, v in b.get("sources", {}).items())
    heads = "".join(f"<li>{e(h)}</li>" for h in b.get("headline", []))
    items = "\n".join(item_html(i) for i in b["items"])
    return f"""<section id="{b['date']}" class="brief">
  <h2>{e(b['date'])} 브리핑</h2>
  <p class="sub">{e(b.get('range',''))} 소식 {len(b['items'])}건 ({e(src)})</p>
  <ul class="heads">{heads}</ul>
  {items}
</section>"""


def main():
    briefs = [json.loads(p.read_text()) for p in sorted((ROOT / "briefs").glob("*.json"), reverse=True)]
    nav = "".join(f'<a href="#{b["date"]}">{b["date"]}</a>' for b in briefs)
    body = "\n".join(brief_html(b) for b in briefs)
    filt = "".join(f'<button data-f="{c}">{c}</button>' for c in CATS)
    page = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 영상·이미지·사운드 브리핑</title>
<style>
:root{{--bg:#fafaf8;--fg:#1d1d1b;--mute:#6b6b66;--line:#e4e2dc;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe6;--mute:#9a9992;--line:#2c2b29;--card:#1d1d1b}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,"Apple SD Gothic Neo",sans-serif}}
header{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px;z-index:2}}
header h1{{font-size:18px;margin:0 0 6px}}nav{{display:flex;gap:10px;overflow-x:auto;font-size:13px}}
nav a{{color:var(--mute);text-decoration:none;white-space:nowrap}}
.f{{display:flex;gap:6px;margin-top:8px}}.f button{{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:14px;padding:2px 12px;font-size:13px}}
.f button.on{{background:var(--fg);color:var(--bg)}}
main{{max-width:760px;margin:0 auto;padding:8px 16px 60px}}
.brief{{scroll-margin-top:110px;padding-top:20px}}.brief h2{{margin:0}}.sub{{color:var(--mute);margin:2px 0 8px;font-size:14px}}
.heads{{margin:0 0 12px;padding-left:20px}}
.item{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}}
.item h3{{font-size:16px;margin:4px 0}}.item h3 a{{color:inherit}}.item p{{margin:0;font-size:15px}}
.meta{{display:flex;gap:10px;font-size:12px;color:var(--mute)}}
.cat{{font-weight:600}}.c-0{{color:#d4572a}}.c-1{{color:#2a7bd4}}.c-2{{color:#2a9d6a}}
</style></head><body>
<header><h1>AI 영상·이미지·사운드 브리핑</h1><nav>{nav}</nav>
<div class="f"><button data-f="" class="on">전체</button>{filt}</div></header>
<main>{body}</main>
<script>
document.querySelectorAll('.f button').forEach(b=>b.onclick=()=>{{
 document.querySelectorAll('.f button').forEach(x=>x.classList.toggle('on',x===b));
 document.querySelectorAll('.item').forEach(i=>i.style.display=!b.dataset.f||i.dataset.cat===b.dataset.f?'':'none');}});
</script></body></html>"""
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs/index.html").write_text(page)
    print(f"built {len(briefs)} briefs")


if __name__ == "__main__":
    main()
