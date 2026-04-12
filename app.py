from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "survey.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                company     TEXT NOT NULL,
                name        TEXT NOT NULL,
                phone       TEXT NOT NULL,
                system      TEXT,
                ai_solutions TEXT,
                app_idea    TEXT,
                learning_goal TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


# ── 정적 파일 서빙 ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "survey.html")


@app.route("/admin")
def admin():
    return send_from_directory(".", "admin.html")


# ── 설문 제출 ────────────────────────────────────────────────────
@app.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)

    required = ["company", "name", "phone"]
    for field in required:
        if not data.get(field, "").strip():
            return jsonify({"ok": False, "error": f"{field} 필드는 필수입니다."}), 400

    ai_solutions = data.get("ai_solutions", [])
    if isinstance(ai_solutions, str):
        ai_solutions = [ai_solutions]
    ai_str = ", ".join(ai_solutions)

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO responses (company, name, phone, system, ai_solutions, app_idea, learning_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("company", "").strip(),
                data.get("name", "").strip(),
                data.get("phone", "").strip(),
                data.get("system", "").strip(),
                ai_str,
                data.get("app_idea", "").strip(),
                data.get("learning_goal", "").strip(),
            ),
        )
        conn.commit()

    return jsonify({"ok": True, "message": "저장 완료"})


# ── 응답 목록 조회 ───────────────────────────────────────────────
@app.route("/api/responses", methods=["GET"])
def responses():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM responses ORDER BY submitted_at DESC"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    print("서버 시작: http://localhost:5000")
    app.run(debug=True, port=5000)
