import os
import json
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import database as db

app = Flask(__name__)
app.secret_key = "algoplay_gaming_super_secret_key_2026_xyz"

# Ma'lumotlar bazasini tekshirish
db.init_db()

# Admin himoyasi dekoratori
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Ruxsat etilmagan! Faqat admin uchun."}), 403
            flash("Admin panelga kirish uchun avval tizimga kiring!", "danger")
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated_function

# Context processor - har bir shablonda foydalanuvchi ma'lumotlarini taqdim etish
@app.context_processor
def inject_user():
    current_user = None
    if "user_id" in session:
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone, xp, level FROM users WHERE id = ?", (session["user_id"],))
        row = cursor.fetchone()
        conn.close()
        if row:
            current_user = dict(row)
    
    current_admin = None
    if "admin_id" in session:
        current_admin = {
            "id": session.get("admin_id"),
            "username": session.get("admin_username"),
            "full_name": session.get("admin_name")
        }

    return dict(current_user=current_user, current_admin=current_admin)

# Healthcheck / Keep-alive endpoint (Serverni uxlatmaslik uchun)
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "message": "AlgoPlay server is alive!"}), 200

# ==================== 1-SAHIFA: HOME ====================
@app.route("/")
def home_page():
    leaderboard = db.get_leaderboard(limit=5)
    stats = {
        "games_count": 4,
        "topics_count": 8,
        "users_count": len(db.get_all_users()),
        "questions_count": len(db.get_all_questions())
    }
    return render_template("home.html", active_page="home", leaderboard=leaderboard, stats=stats)

# ==================== 2-SAHIFA: LOGIN / REGISTRATSIYA ====================
@app.route("/auth")
def auth_page():
    return render_template("auth.html", active_page="auth")

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json(silent=True) or {}
        phone = data.get("phone", "").strip()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not phone or not username or not password:
            return jsonify({"success": False, "message": "Barcha maydonlarni to'ldiring!"}), 400

        if len(username) < 3:
            return jsonify({"success": False, "message": "Foydalanuvchi nomi kamida 3 belgidan iborat bo'lishi kerak!"}), 400

        if len(password) < 4:
            return jsonify({"success": False, "message": "Parol kamida 4 belgidan iborat bo'lishi kerak!"}), 400

        success, user_id, message = db.register_user(phone, username, password)
        if success:
            session["user_id"] = user_id
            session["username"] = username
            return jsonify({"success": True, "message": message, "user": {"id": user_id, "username": username, "phone": phone, "xp": 0, "level": 1}})
        else:
            return jsonify({"success": False, "message": message}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Serverda xatolik yuz berdi: {str(e)}"}), 500

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        phone_or_user = data.get("phone_or_user", "").strip()
        password = data.get("password", "").strip()

        if not phone_or_user or not password:
            return jsonify({"success": False, "message": "Login va parolni kiriting!"}), 400

        success, user, message = db.login_user(phone_or_user, password)
        if success:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return jsonify({"success": True, "message": message, "user": user})
        else:
            return jsonify({"success": False, "message": message}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"Serverda xatolik yuz berdi: {str(e)}"}), 500

@app.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    session.pop("user_id", None)
    session.pop("username", None)
    if request.method == "POST":
        return jsonify({"success": True, "message": "Tizimdan chiqdingiz!"})
    flash("Tizimdan muvaffaqiyatli chiqdingiz!", "info")
    return redirect(url_for("home_page"))

# ==================== 3-SAHIFA: DASTURLASH HAQIDA MA'LUMOTLAR ====================
@app.route("/learn")
def learn_page():
    return render_template("learn.html", active_page="learn")

# ==================== 4-SAHIFA: QIZIQARLI O'YINLAR ====================
@app.route("/games")
def games_page():
    questions = db.get_all_questions()
    puzzles = db.get_all_puzzles()
    bugs = db.get_all_bugs()
    leaderboard = db.get_leaderboard(limit=10)
    
    # JSON ga xavfsiz aylantirish
    for p in puzzles:
        if isinstance(p["blocks_json"], str):
            p["blocks"] = json.loads(p["blocks_json"])
            p["correct_order"] = json.loads(p["correct_order_json"])
    
    for b in bugs:
        if isinstance(b["options_json"], str):
            b["options"] = json.loads(b["options_json"])

    return render_template("games.html", 
                           active_page="games", 
                           questions=questions, 
                           puzzles=puzzles, 
                           bugs=bugs, 
                           leaderboard=leaderboard)

@app.route("/api/game/save-score", methods=["POST"])
def api_save_score():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Ballaringizni saqlash uchun avval tizimga kiring!"}), 401

    data = request.get_json() or {}
    game_type = data.get("game_type", "general")
    score = int(data.get("score", 0))
    xp_earned = int(data.get("xp_earned", 0))
    details = data.get("details", "")

    updated_user = db.add_xp(session["user_id"], xp_earned, game_type, score, details)
    return jsonify({
        "success": True,
        "message": f"+{xp_earned} XP muvaffaqiyatli qo'shildi!",
        "xp": updated_user.get("xp", 0),
        "level": updated_user.get("level", 1)
    })

@app.route("/api/leaderboard", methods=["GET"])
def api_leaderboard():
    limit = int(request.args.get("limit", 10))
    return jsonify({"success": True, "leaderboard": db.get_leaderboard(limit)})

# ==================== 5-SAHIFA: ADMIN PANEL ====================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login_page():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        success, admin, message = db.login_admin(username, password)
        if success:
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            session["admin_name"] = admin["full_name"]
            flash(f"Xush kelibsiz, {admin['full_name']}!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash(message, "danger")

    return render_template("admin_login.html", active_page="admin")

@app.route("/admin")
@admin_required
def admin_dashboard():
    stats = db.get_admin_stats()
    users = db.get_all_users()
    questions = db.get_all_questions()
    puzzles = db.get_all_puzzles()
    bugs = db.get_all_bugs()
    return render_template("admin.html", 
                           active_page="admin",
                           stats=stats,
                           users=users,
                           questions=questions,
                           puzzles=puzzles,
                           bugs=bugs)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    session.pop("admin_name", None)
    flash("Admin panelidan muvaffaqiyatli chiqdingiz!", "info")
    return redirect(url_for("home_page"))

# Admin API endpoints
@app.route("/api/admin/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def api_admin_delete_user(user_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Foydalanuvchi muvaffaqiyatli o'chirildi!"})

@app.route("/api/admin/questions/add", methods=["POST"])
@admin_required
def api_admin_add_question():
    data = request.get_json() or {}
    category = data.get("category", "python").strip()
    question = data.get("question", "").strip()
    code_snippet = data.get("code_snippet", "").strip()
    opt_a = data.get("option_a", "").strip()
    opt_b = data.get("option_b", "").strip()
    opt_c = data.get("option_c", "").strip()
    opt_d = data.get("option_d", "").strip()
    correct = data.get("correct_option", "A").strip().upper()
    explanation = data.get("explanation", "").strip()
    points = int(data.get("points", 10))

    if not question or not opt_a or not opt_b or not opt_c or not opt_d:
        return jsonify({"success": False, "message": "Savol va barcha 4 ta variant to'ldirilishi shart!"}), 400

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (category, question, code_snippet, option_a, option_b, option_c, option_d, correct_option, explanation, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, question, code_snippet, opt_a, opt_b, opt_c, opt_d, correct, explanation, points))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Yangi test savoli muvaffaqiyatli qo'shildi!"})

@app.route("/api/admin/questions/delete/<int:question_id>", methods=["POST"])
@admin_required
def api_admin_delete_question(question_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Savol o'chirildi!"})

@app.route("/api/admin/puzzles/add", methods=["POST"])
@admin_required
def api_admin_add_puzzle():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    lines_raw = data.get("lines", []) # List of strings in correct order
    points = int(data.get("points", 25))

    if not title or not description or len(lines_raw) < 2:
        return jsonify({"success": False, "message": "Sarlavha, tavsif va kamida 2 ta kod qatori kiritilishi shart!"}), 400

    # Shuffled blocks
    import random
    indices = list(range(len(lines_raw)))
    shuffled_indices = list(indices)
    random.shuffle(shuffled_indices)

    # Shuffled blocks array
    blocks = [lines_raw[i] for i in shuffled_indices]
    # To restore correct order: correct_order[i] is index in blocks
    correct_order = [shuffled_indices.index(i) for i in indices]

    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO puzzles (title, description, language, blocks_json, correct_order_json, points)
        VALUES (?, ?, 'python', ?, ?, ?)
    """, (title, description, json.dumps(blocks), json.dumps(correct_order), points))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Yangi kod puzzle muvaffaqiyatli qo'shildi!"})

@app.route("/api/admin/puzzles/delete/<int:puzzle_id>", methods=["POST"])
@admin_required
def api_admin_delete_puzzle(puzzle_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM puzzles WHERE id = ?", (puzzle_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Puzzle o'chirildi!"})

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    port = int(os.environ.get("PORT", 5050))
    print("=" * 60)
    print("  [+] AlgoPlay Veb Ilovasi Ishga Tushmoqda!")
    print(f"  [*] URL: http://127.0.0.1:{port}")
    print(f"  [*] Admin Login: admin  |  Parol: admin777")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
