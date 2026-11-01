"""Run locally with `py smoke_test.py`; uses a temporary SQLite database.

SMS SDK and AI providers are mocked: no paid/external API calls.
"""
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import uvicorn


def main():
    with tempfile.TemporaryDirectory(prefix="volleyball-smoke-") as tmp:
        os.environ.update(
            SECRET_KEY="smoke-test-only-fixed-secret-key-32-characters",
            DB_TYPE="sqlite", DB_NAME=str(Path(tmp) / "smoke.db"),
            ALIYUN_ACCESS_KEY_ID=os.getenv("ALIYUN_ACCESS_KEY_ID", "").strip()
        )
        from app import config
        config.UPLOAD_DIR = str(Path(tmp) / "uploads")
        config.AVATAR_DIR = str(Path(config.UPLOAD_DIR) / "avatars")
        from app.main import app
        from app.routers import ai
        from app.database import engine, SessionLocal
        from app.utils.security import create_access_token
        from app.utils.sms import AliyunSmsClient
        from alibabacloud_dypnsapi20170525 import models as sms_models
        sms_client = Mock()
        sms_client.send_sms_verify_code_with_options.return_value = sms_models.SendSmsVerifyCodeResponse(
            status_code=200,
            body=sms_models.SendSmsVerifyCodeResponseBody(
                code="OK", success=True,
                model=sms_models.SendSmsVerifyCodeResponseBodyModel(biz_id="mock-biz-id"),
            ),
        )

        def verify_sms(request, runtime):
            return sms_models.CheckSmsVerifyCodeResponse(
                status_code=200,
                body=sms_models.CheckSmsVerifyCodeResponseBody(
                    code="OK", success=True,
                    model=sms_models.CheckSmsVerifyCodeResponseBodyModel(
                        verify_result="PASS" if request.verify_code == "123456" else "FAIL",
                    ),
                ),
            )

        sms_client.check_sms_verify_code_with_options.side_effect = verify_sms
        sms_patch = patch.object(AliyunSmsClient, "get_client", return_value=sms_client)
        sms_patch.start()
        ai.chat_with_ai = lambda *a, **k: {
            "success": True, "content": "Smoke test coach reply", "usage": {"total_tokens": 5}
        }
        ai.simple_chat = lambda *a, **k: {"success": True, "content": "Smoke test answer"}
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{port}"
        session = requests.Session()
        checks = 0

        def call(method, path, expected=200, **kwargs):
            nonlocal checks
            response = session.request(method, origin + path, timeout=10, **kwargs)
            assert response.status_code == expected, f"{method} {path}: {response.status_code} {response.text}"
            checks += 1
            return response.json()

        api = "/api/v1"
        try:
            for _ in range(100):
                if server.started:
                    break
                if not thread.is_alive():
                    raise RuntimeError("Smoke server failed to start")
                time.sleep(0.05)
            assert server.started, "Smoke server startup timed out"
            call("GET", "/health")
            call("POST", api + "/auth/register", 201, json={"username": "smoke_user", "password": "smoke12345"})
            sms = call("POST", api + "/auth/send-sms-code", json={"phone": "13800000000", "scene": "login"})
            assert sms["success"]
            call("POST", api + "/auth/sms-login", 400, json={"phone": "13800000000", "code": "000000"})
            sms_login = call("POST", api + "/auth/sms-login", json={"phone": "13800000000", "code": "123456"})
            session.headers["Authorization"] = "Bearer " + sms_login["access_token"]
            call("GET", api + "/auth/me")
            session.headers.pop("Authorization")
            login = call("POST", api + "/auth/login", json={"username": "smoke_user", "password": "smoke12345"})
            session.headers["Authorization"] = "Bearer " + login["access_token"]
            call("GET", api + "/auth/me")
            call("PUT", api + "/auth/me", json={"username": "smoke_renamed"})
            import base64
            png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a5Z0AAAAASUVORK5CYII=")
            avatar = call("POST", api + "/auth/me/avatar", files={"file": ("pixel.png", png, "image/png")})
            assert session.get(origin + api + "/uploads/" + avatar["avatar"], timeout=10).status_code == 200
            call("GET", api + "/banners/")
            courses = call("GET", api + "/courses/")["courses"]
            assert courses, "No seeded courses"
            course = courses[0]
            course_id = course["id"]
            call("GET", api + f"/courses/{course_id}")
            call("GET", api + "/courses/categories/list")
            call("GET", api + "/courses/skills/list")
            call("POST", api + "/courses/favorites", json={"course_id": course_id, "is_favorite": True})
            assert call("GET", api + "/courses/favorites/list")
            call("POST", api + "/courses/progress", json={"course_id": course_id, "skill_type": course["skill_type"], "progress": 50, "study_duration": 5})
            call("GET", api + "/courses/progress/list")
            call("GET", api + "/courses/studying/list")
            call("GET", api + "/courses/statistics")
            call("DELETE", api + f"/courses/favorites/{course_id}")
            rules = call("GET", api + "/rules/content")
            call("POST", api + "/rules/progress", json={"rule_content_id": rules["sections"][0]["id"]})
            for mode in ["ball", "color", "direction"]:
                call("POST", api + "/training/reaction/record", json={"game_mode": mode, "score": 100, "avg_reaction_time": 250, "hit_rate": 100, "total_rounds": 2, "hit_count": 2, "duration": 30})
            assert len(call("GET", api + "/training/reaction/records")) == 3
            call("GET", api + "/training/reaction/statistics")
            offline = call("GET", api + "/offline-courses/")["courses"]
            available = next(c for c in offline if c["current_participants"] < c["max_participants"])
            oid = available["id"]
            call("GET", api + f"/offline-courses/{oid}")
            call("POST", api + f"/offline-courses/{oid}/enroll", json={"course_id": oid, "contact_phone": "13800000000"})
            assert call("GET", api + "/offline-courses/my-enrollments/list")
            call("GET", api + "/ai/preset-questions")
            chat = call("POST", api + "/ai/chat", json={"message": "How to serve?", "context_type": "coach"})
            sid = chat["session_id"]
            call("POST", api + "/ai/chat", json={"message": "And then?", "context_type": "coach", "session_id": sid})
            assert call("GET", api + "/ai/sessions")["sessions"], "Authenticated AI session not associated with user"
            detail = call("GET", api + f"/ai/sessions/{sid}")
            assert len(detail["messages"]) == 4
            owner_token = session.headers["Authorization"]
            session.headers.pop("Authorization")
            call("GET", api + f"/ai/sessions/{sid}", 403)
            call("POST", api + "/ai/chat", 403, json={"message": "steal history", "session_id": sid})
            call("POST", api + "/ai/analyze-action", 403, json={"action_type": "serve", "description": "steal history", "session_id": sid})
            session.headers["Authorization"] = owner_token
            call("GET", api + f"/ai/sessions/{sid}")
            from app.models.user import User
            db = SessionLocal()
            try:
                other_user = User(username="smoke_other", hashed_password="unused", is_active=True)
                db.add(other_user)
                db.commit()
                db.refresh(other_user)
                other_token = create_access_token({"sub": str(other_user.id), "type": "user_id"})
            finally:
                db.close()
            session.headers["Authorization"] = "Bearer " + other_token
            call("GET", api + f"/ai/sessions/{sid}", 403)
            call("POST", api + "/ai/chat", 403, json={"message": "steal history", "session_id": sid})
            call("POST", api + "/ai/analyze-action", 403, json={"action_type": "serve", "description": "steal history", "session_id": sid})
            session.headers["Authorization"] = owner_token
            call("DELETE", api + f"/ai/sessions/{sid}")
            legacy_token = create_access_token({"sub": "smoke_renamed"})
            session.headers["Authorization"] = "Bearer " + legacy_token
            call("GET", api + "/auth/me")
            call("GET", api + "/ai/sessions")
            from app.utils.sms import check_sms_code
            assert check_sms_code("13800000000", "123456") == (True, "验证成功")
            sms_client.send_sms_verify_code_with_options.assert_called_once()
            assert sms_client.check_sms_verify_code_with_options.call_count == 3
            # Verify a token in a fresh Python process with the same fixed secret.
            subprocess.run([sys.executable, "-c", "from app.utils.security import decode_access_token; import sys; assert decode_access_token(sys.stdin.read())"], input=login["access_token"], text=True, check=True)
            print(f"PASS: {checks} API smoke checks; avatar file reachable; JWT survives a fresh process; AI and SMS providers mocked.")
        finally:
            session.close()
            server.should_exit = True
            thread.join(timeout=10)
            engine.dispose()
            sms_patch.stop()


if __name__ == "__main__":
    main()
