#!/usr/bin/env python3
"""
Anthropic 안전 보고서 아카이브 — 정적 사이트 빌더

  frag/<page-id>.html  각 페이지 본문 조각 (공통 머리말·내비게이션 없이 본문만)
  PAGES                페이지 목록 (새 판본은 여기에 한 항목 추가)
  dist/                단독으로 열리는 전체 HTML (배포·자체 호스팅용)
  dist_artifact/       Claude 아티팩트 게시용 (index-body.html + 하위 페이지 전체 문서)

새 판본 추가 절차
  1) frag/ 에 요약 조각 추가 — 같은 시리즈의 기존 판본 파일을 복사해 섹션 번호·제목을 그대로 유지
  2) 아래 PAGES 에 항목 추가
  3) 해당 시리즈 비교 조각(frag/misuse-compare.html · frag/risk-compare.html)의 표마다 열 하나 추가
  4) python3 build.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).parent
FRAG, DIST, DART = ROOT / "frag", ROOT / "dist", ROOT / "dist_artifact"
SITE = "Anthropic 안전 보고서 아카이브"
UPDATED = "2026.09.16"

PAGES = [
  dict(id="index", path="index.html", kind="hub", series=None, title="Anthropic 안전 보고서 아카이브", nav="홈"),
  dict(id="misuse-compare", path="misuse/compare.html", kind="compare", series="A", title="오용 위협보고서 누적 비교", nav="누적 비교"),
  dict(id="misuse-2025-03", path="misuse/2025-03.html", kind="edition", series="A", title="오용 위협보고서 2025.03", nav="2025.03"),
  dict(id="misuse-2025-08", path="misuse/2025-08.html", kind="edition", series="A", title="오용 위협보고서 2025.08", nav="2025.08"),
  dict(id="misuse-2025-11", path="misuse/2025-11.html", kind="edition", series="A", title="오용 위협보고서 2025.11", nav="2025.11"),
  dict(id="misuse-2026-02", path="misuse/2026-02.html", kind="edition", series="A", title="증류 공격 공개 2026.02", nav="2026.02 증류"),
  dict(id="misuse-2026-09", path="misuse/2026-09.html", kind="edition", series="A", title="오용 위협보고서 2026.09", nav="2026.09"),
  dict(id="risk-compare", path="risk/compare.html", kind="compare", series="B", title="Risk Report 누적 비교", nav="누적 비교"),
  dict(id="risk-2026-02", path="risk/2026-02.html", kind="edition", series="B", title="Risk Report 2026.02", nav="2026.02"),
  dict(id="risk-2026-08", path="risk/2026-08.html", kind="edition", series="B", title="Risk Report 2026.08", nav="2026.08"),
]
SERIES = {"A": ("오용 위협보고서", "misuse/compare.html", "sa"),
          "B": ("RSP Risk Report", "risk/compare.html", "sb")}

# Keep source links beside every edition so claims can be checked in context.
SOURCES = {
    "misuse-2025-03": [
        ("공식 게시글", "https://www.anthropic.com/news/detecting-and-countering-malicious-uses-of-claude-march-2025"),
        ("사례 PDF", "https://cdn.sanity.io/files/4zrzovbb/website/45bc6adf039848841ed9e47051fb1209d6bb2b26.pdf"),
    ],
    "misuse-2025-08": [
        ("공식 게시글", "https://www.anthropic.com/news/detecting-countering-misuse-aug-2025"),
        ("원문 PDF", "https://www-cdn.anthropic.com/b2a76c6f6992465c09a6f2fce282f6c0cea8c200.pdf"),
    ],
    "misuse-2025-11": [
        ("공식 게시글", "https://www.anthropic.com/news/disrupting-AI-espionage"),
        ("개정 PDF", "https://assets.anthropic.com/m/ec212e6566a0d47/original/Disrupting-the-first-reported-AI-orchestrated-cyber-espionage-campaign.pdf"),
    ],
    "misuse-2026-02": [
        ("공식 게시글", "https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks"),
    ],
    "misuse-2026-09": [
        ("공식 게시글", "https://www.anthropic.com/threat-intelligence-report-september-2026"),
        ("원문 PDF", "https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf"),
    ],
    "risk-2026-02": [
        ("원문 PDF（7월 8일 개정）", "https://www.anthropic.com/feb-2026-risk-report"),
        ("RSP v3.0", "https://www.anthropic.com/responsible-scaling-policy/rsp-v3-0"),
    ],
    "risk-2026-08": [
        ("원문 PDF", "https://www.anthropic.com/aug-2026-risk-report"),
        ("RSP v3.4", "https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf"),
        ("공개·개정 이력", "https://www.anthropic.com/responsible-scaling-policy"),
    ],
}

CSS = (ROOT / "style.css").read_text(encoding="utf-8") + (ROOT / "style2.css").read_text(encoding="utf-8")
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700'
         '&family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')

def rel(frm, to):
    depth = frm.count("/")
    return "../" * depth + to

def topbar(p):
    here = p["path"]
    s = p["series"]
    links = []
    for key, (name, home, cls) in SERIES.items():
        on = " on" if s == key else ""
        links.append(f'<a class="{cls}{on}" href="{rel(here, home)}">{name}</a>')
    out = ['<header class="topbar"><div class="wrap">',
           '<div class="tb1">',
           f'<a class="home" href="{rel(here, "index.html")}">{SITE}</a>',
           '<nav class="serieslinks" aria-label="보고서 시리즈">' + "".join(links) + '</nav>',
           '</div>']
    if s:
        items = [q for q in PAGES if q["series"] == s]
        sub = []
        for q in items:
            cur = ' class="cur" aria-current="page"' if q["id"] == p["id"] else ""
            sub.append(f'<a{cur} href="{rel(here, q["path"])}">{q["nav"]}</a>')
        out.append('<nav class="tb2" aria-label="판본">' + "".join(sub) + '</nav>')
    out.append('</div></header>')
    return "\n".join(out)

def prevnext(p):
    if p["kind"] != "edition":
        return ""
    eds = [q for q in PAGES if q["series"] == p["series"] and q["kind"] == "edition"]
    i = eds.index(p)
    here = p["path"]
    left = right = "<span></span>"
    if i > 0:
        q = eds[i-1]; left = f'<a href="{rel(here, q["path"])}"><span class="lab">이전 판본</span>{q["title"]}</a>'
    if i < len(eds) - 1:
        q = eds[i+1]; right = f'<a href="{rel(here, q["path"])}" style="text-align:right"><span class="lab">다음 판본</span>{q["title"]}</a>'
    cmp_ = [q for q in PAGES if q["series"] == p["series"] and q["kind"] == "compare"][0]
    mid = f'<a href="{rel(here, cmp_["path"])}"><span class="lab">시리즈</span>누적 비교로 이동</a>'
    return f'<nav class="pn wrap" aria-label="판본 이동">{left}{mid}{right}</nav>'

FOOT = ('<footer class="wrap"><p>국문 요약 · 원문 대조 {u}. 수치·귀속·위험 평가는 Anthropic의 공개 보고에 근거하며, '
        '사건의 실재나 비공개 증거를 독립적으로 검증했다는 뜻은 아니다. <span class="pg">p.</span>는 연결된 PDF의 쪽수다. '
        '"요약자 주석"과 "변화 해설"은 요약자의 해석이다. '
        '<a href="https://github.com/byoungpil-kim/anthropic-safety-archive/blob/main/VERIFICATION.md">검증·수정 기록</a></p></footer>')

def page_body(p):
    body = (FRAG / f'{p["id"]}.html').read_text(encoding="utf-8")
    body = body.replace("{{ROOT}}", rel(p["path"], ""))
    if p["id"] in SOURCES:
        links = " · ".join(f'<a href="{url}">{label}</a>' for label, url in SOURCES[p["id"]])
        body = body.replace('<nav class="toc"', f'<p class="meta">공식 출처: {links}</p>\n<nav class="toc"', 1)
    return "\n".join([topbar(p), '<main class="wrap">', body, '</main>', prevnext(p), FOOT.format(u=UPDATED)])

def full_doc(p):
    s = p["series"] or ""
    return (f'<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<title>{p["title"]}</title>\n{FONTS}\n<style>\n{CSS}\n</style>\n</head>\n'
            f'<body data-series="{s}">\n{page_body(p)}\n</body>\n</html>\n')

def artifact_body(p):
    # 아티팩트 게시 규약: doctype/html/head/body 없이 작성 → data-series 는 스크립트로 부여
    s = p["series"] or ""
    return (f'<title>{p["title"]}</title>\n{FONTS}\n<style>\n{CSS}\n</style>\n'
            f'<script>document.body && document.body.setAttribute("data-series","{s}")</script>\n'
            f'{page_body(p)}\n')

def main():
    for p in PAGES:
        out = DIST / p["path"]; out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(full_doc(p), encoding="utf-8")
        if p["kind"] == "hub":
            (DART / "index-body.html").parent.mkdir(parents=True, exist_ok=True)
            (DART / "index-body.html").write_text(artifact_body(p), encoding="utf-8")
        else:
            o2 = DART / p["path"]; o2.parent.mkdir(parents=True, exist_ok=True)
            o2.write_text(full_doc(p), encoding="utf-8")
    print("built", len(PAGES), "pages")

if __name__ == "__main__":
    main()
