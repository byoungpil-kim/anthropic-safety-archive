# Anthropic 안전 보고서 아카이브

두 보고서 계열을 판본별 요약 + 누적 비교로 정리한 정적 사이트.

- Series A: Detecting and countering misuse of AI (오용 위협 인텔리전스, 비정기) — `misuse/`
- Series B: RSP Risk Report (RSP v3 제3조, 3–6개월 주기) — `risk/`

## 폴더

- `dist/` — 바로 열거나 웹서버에 올릴 수 있는 완성본 (index.html에서 시작)
- `frag/` — 각 페이지 본문 원고
- `style.css`, `style2.css` — 공통 스타일
- `build.py` — 원고를 완성본으로 조립

## 새 판본 추가

1. `frag/`에서 같은 시리즈의 최신 판본 파일을 복사해 새 이름으로 저장
   (예: `frag/risk-2026-11.html`). 섹션 번호와 제목은 그대로 두고 내용만 교체.
   - Series A 공통 목차: 01 서지 · 02 위해 영역 · 03 추세 · 04 사례 · 05 AI 관여 · 06 안전장치 · 07 대응 · 08 권고 · 09 인용 · 10 주석
   - Series B 공통 목차: 01 서지 · 02 대상 모델 · 03 위험 모델·임계치 · 04 증거 · 05 완화 · 06 위험 평가 · 07 사고 · 08 변경 검토 · 09 생태계 · 10 외부 검토 · 11 인용 · 12 주석
2. `build.py`의 `PAGES` 목록에 한 줄 추가 (시리즈 안에서 날짜순).
3. 비교 원고(`frag/misuse-compare.html` 또는 `frag/risk-compare.html`)의 각 표에
   새 열을 추가하고, 이전 최신 열의 `class="cur"`를 새 열로 옮긴 뒤 "변화 해설"을 갱신.
4. 허브(`frag/index.html`)의 판본 목록과 수록 판본 수를 갱신.
5. `python3 build.py` 실행.

본문에서 `{{ROOT}}`는 사이트 최상위 경로로 치환된다.
