# AI 브리핑 수집 절차 (예약 작업이 매번 이 순서대로 실행)

폴더: /Users/kimduho/Documents/ClaudeCode/ai-news-brief
사이트: https://divee17-blip.github.io/ai-news-brief/

## 범위
- 대상 기간: 직전 브리핑 이후 ~ 어제까지 (보통 2일). 오늘 날짜 = 브리핑 날짜.
- 주제: AI **영상 / 이미지 / 사운드(음악·음성·TTS·효과음)** 생성·편집 도구의 출시·업데이트, 실전 제작 팁·워크플로, 눈에 띄는 작품 사례.
- 제외: LLM 일반 뉴스, 투자·주가, 루머성 유출, 같은 소식의 중복(가장 원문에 가까운 것 하나만).

## 1. X 수집 (크롬, 로그인된 사용자 크롬 사용)
- claude-in-chrome 도구로 X 검색. 검색어 예: `Kling`, `Seedance`, `Veo`, `Sora`, `Runway`, `Hailuo`, `Higgsfield`, `Midjourney`, `Seedream`, `nano banana`, `GPT Image`, `Suno`, `ElevenLabs`, `Udio`, `AI video`, `AI music` 등 + `since:YYYY-MM-DD`, 정렬은 인기(Top).
- 공식 계정 발표와 반응 많은 실사용 팁 위주. 게시물 URL(x.com/.../status/...)을 반드시 기록.
- X에서 글을 쓰거나 좋아요·팔로우 등 어떤 행동도 하지 않는다. 읽기만.
- 크롬 연결이 안 되면 X는 건너뛰고 브리핑 sub에 "X 수집 실패"를 남긴다.

## 2. 웹 수집
- WebSearch로 같은 주제 검색(공식 블로그, 체인지로그, 뉴스, Reddit r/StableDiffusion·r/aivideo·r/SunoAI 등, Threads 공개 글).
- 날짜가 대상 기간 안인지 확인. 확인 안 되면 넣지 않는다.

## 3. 선별·작성
- 15~25건. 각 항목: category(영상|이미지|사운드), title(한 줄), summary(2~3문장, 무엇이 되고 왜 참고할 만한지), source("X @계정" / "Threads @계정" / 사이트명), url(원문), posted(YYYY-MM-DD).
- 원문에 없는 내용 지어내지 않기. 수치·기능명은 원문 그대로.
- headline: 가장 중요한 3건을 한 줄씩.
- `briefs/YYYY-MM-DD.json` 저장:
  {"date","range":"11월 4~5일","sources":{"X":n,"웹":m},"headline":[3],"items":[...]}

## 4. 사이트 반영
    python3 scripts/build_site.py
    git add -A && git commit -m "brief YYYY-MM-DD" && git push

## 5. 카톡 메시지 예약 (실제 발송은 08:00 launchd가 함)
`pending/YYYY-MM-DD.json` 작성: {"text": ..., "url": "https://divee17-blip.github.io/ai-news-brief/#YYYY-MM-DD", "button_title": "브리핑 보기"}
- text는 **200자 이하**(카카오 텍스트 템플릿 제한). 형식:
  안녕하세요 ☀️ M월 D일 AI 브리핑입니다.
  M월 D~D일 소식 N건 (X a건, 웹 b건)
  - 헤드라인1
  - 헤드라인2
  - 헤드라인3
- 08:00이 이미 지났으면 바로 `python3 scripts/kakao.py send-pending` 실행.
