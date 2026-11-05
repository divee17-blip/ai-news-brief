#!/usr/bin/env python3
"""카카오톡 '나에게 보내기' 도구.

  python3 kakao.py auth            # 최초 1회: 브라우저 로그인 → 토큰 저장
  python3 kakao.py send FILE       # FILE(json: text, url, button_title) 내용을 나에게 전송
  python3 kakao.py send-pending    # 오늘 날짜 pending 메시지가 있으면 전송 (launchd 8시용)

설정/토큰은 ~/.config/ai-news-brief/ 에만 저장 (저장소에 올라가지 않음).
kakao_app.json: {"rest_api_key": "...", "client_secret": "..."}  (client_secret 끈 경우 생략)
"""
import json, sys, time, datetime, webbrowser, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CFG = Path.home() / ".config/ai-news-brief"
APP = CFG / "kakao_app.json"
TOK = CFG / "kakao_token.json"
PENDING = Path(__file__).resolve().parent.parent / "pending"
REDIRECT = "http://localhost:8765/callback"


def log(*a):
    print(datetime.datetime.now().strftime("%F %T"), *a, flush=True)


def post(url, data, token=None):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()}")


def app():
    return json.loads(APP.read_text())


def save_tokens(t):
    old = json.loads(TOK.read_text()) if TOK.exists() else {}
    old.update(t)
    now = time.time()
    old["access_expires_at"] = now + t["expires_in"] - 300
    if "refresh_token_expires_in" in t:
        old["refresh_expires_at"] = now + t["refresh_token_expires_in"]
    TOK.write_text(json.dumps(old, indent=1))
    TOK.chmod(0o600)


def auth():
    a = app()
    url = "https://kauth.kakao.com/oauth/authorize?" + urllib.parse.urlencode(
        {"response_type": "code", "client_id": a["rest_api_key"], "redirect_uri": REDIRECT, "scope": "talk_message"})
    got = {}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("인증 완료. 이 창은 닫아도 됩니다.".encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("localhost", 8765), H)
    print("브라우저에서 카카오 로그인 후 동의해 주세요:\n" + url)
    webbrowser.open(url)
    while "code" not in got and "error" not in got:
        srv.handle_request()
    if "error" in got:
        raise SystemExit(f"인증 실패: {got}")
    data = {"grant_type": "authorization_code", "client_id": a["rest_api_key"],
            "redirect_uri": REDIRECT, "code": got["code"]}
    if a.get("client_secret"):
        data["client_secret"] = a["client_secret"]
    save_tokens(post("https://kauth.kakao.com/oauth/token", data))
    print("토큰 저장 완료:", TOK)


def access_token():
    t = json.loads(TOK.read_text())
    if time.time() < t.get("access_expires_at", 0):
        return t["access_token"]
    a = app()
    data = {"grant_type": "refresh_token", "client_id": a["rest_api_key"], "refresh_token": t["refresh_token"]}
    if a.get("client_secret"):
        data["client_secret"] = a["client_secret"]
    save_tokens(post("https://kauth.kakao.com/oauth/token", data))
    log("액세스 토큰 갱신")
    return json.loads(TOK.read_text())["access_token"]


def send(msg):
    text = msg["text"]
    if len(text) > 200:  # 텍스트 템플릿 최대 200자
        raise SystemExit(f"text가 200자를 넘음({len(text)}자)")
    tmpl = {"object_type": "text", "text": text,
            "link": {"web_url": msg["url"], "mobile_web_url": msg["url"]},
            "button_title": msg.get("button_title", "브리핑 보기")}
    r = post("https://kapi.kakao.com/v2/api/talk/memo/default/send",
             {"template_object": json.dumps(tmpl, ensure_ascii=False)}, access_token())
    if r.get("result_code") != 0:
        raise SystemExit(f"전송 실패: {r}")
    log("전송 완료:", msg["url"])


def send_pending():
    today = datetime.date.today().isoformat()
    f = PENDING / f"{today}.json"
    if not f.exists():
        log("오늘 보낼 메시지 없음")
        return
    send(json.loads(f.read_text()))
    f.rename(f.with_suffix(".sent"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "auth":
        auth()
    elif cmd == "send":
        send(json.loads(Path(sys.argv[2]).read_text()))
    elif cmd == "send-pending":
        send_pending()
    else:
        print(__doc__)
