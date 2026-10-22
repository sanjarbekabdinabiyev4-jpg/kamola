import sqlite3
import os
import shutil
import hashlib
import json

SOURCE_DB = os.path.join(os.path.dirname(__file__), "algoplay.db")

def get_writable_db_path():
    # Vercel yoki serverless yoki read-only fayl tizimini aniqlash
    is_serverless = bool(
        os.environ.get("VERCEL") or 
        os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or 
        os.environ.get("NOW_REGION") or
        not os.access(os.path.dirname(SOURCE_DB) or ".", os.W_OK)
    )
    
    if is_serverless:
        tmp_dir = "/tmp" if os.path.exists("/tmp") else os.environ.get("TEMP", ".")
        target_db = os.path.join(tmp_dir, "algoplay.db")
        if not os.path.exists(target_db) and os.path.exists(SOURCE_DB):
            try:
                shutil.copyfile(SOURCE_DB, target_db)
                try:
                    os.chmod(target_db, 0o666)
                except Exception:
                    pass
            except Exception:
                pass
        return target_db
    return SOURCE_DB

DB_FILE = get_writable_db_path()

def get_db():
    db_path = get_writable_db_path()
    try:
        conn = sqlite3.connect(db_path, timeout=15)
    except Exception:
        tmp_db = os.path.join("/tmp" if os.path.exists("/tmp") else os.environ.get("TEMP", "."), "algoplay.db")
        if not os.path.exists(tmp_db) and os.path.exists(SOURCE_DB):
            try:
                shutil.copyfile(SOURCE_DB, tmp_db)
            except Exception:
                pass
        conn = sqlite3.connect(tmp_db, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Admins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Game scores table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_type TEXT NOT NULL,
        score INTEGER NOT NULL,
        xp_earned INTEGER NOT NULL,
        details TEXT,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 4. Questions table (Savol-javoblar uchun)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        code_snippet TEXT,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL,
        explanation TEXT,
        points INTEGER DEFAULT 10
    );
    """)

    # 5. Code puzzles table (Kod puzzle o'yini)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS puzzles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        language TEXT DEFAULT 'python',
        blocks_json TEXT NOT NULL,
        correct_order_json TEXT NOT NULL,
        points INTEGER DEFAULT 25
    );
    """)

    # 6. Bug hunter table (Xatoni top o'yini)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bugs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        code_with_bug TEXT NOT NULL,
        bug_line INTEGER NOT NULL,
        options_json TEXT NOT NULL,
        correct_index INTEGER NOT NULL,
        explanation TEXT NOT NULL,
        points INTEGER DEFAULT 20
    );
    """)

    conn.commit()

    # Default admin tekshirish va yaratish
    cursor.execute("SELECT id FROM admins WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        admin_pass_hash = hash_password("admin777")
        cursor.execute("""
            INSERT INTO admins (username, password_hash, full_name, phone)
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_pass_hash, "AlgoPlay Bosh Admini", "+998901234567"))
        conn.commit()

    # Default questions kiritish (agar bo'sh bo'lsa)
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    if cursor.fetchone()["count"] == 0:
        seed_questions(conn)

    # Default puzzles kiritish (agar bo'sh bo'lsa)
    cursor.execute("SELECT COUNT(*) as count FROM puzzles")
    if cursor.fetchone()["count"] == 0:
        seed_puzzles(conn)

    # Default bugs kiritish (agar bo'sh bo'lsa)
    cursor.execute("SELECT COUNT(*) as count FROM bugs")
    if cursor.fetchone()["count"] == 0:
        seed_bugs(conn)

    conn.close()

def seed_questions(conn):
    questions_data = [
        (
            "python",
            "Python tilida ekranga matn chiqarish uchun qaysi funksiyadan foydalaniladi?",
            '# Misol:\n???("Salom Dunyo")',
            "echo()",
            "print()",
            "console.log()",
            "System.out.println()",
            "B",
            "Python tilida standart ma'lumot chiqarish buyrug'i print() hisoblanadi.",
            10
        ),
        (
            "python",
            "Quyidagi kod natijasi nima bo'ladi?",
            'x = 5\ny = 2\nprint(x ** y)',
            "10",
            "7",
            "25",
            "2.5",
            "C",
            "Python'da ** operatori darajaga ko'tarishni bildiradi: 5 ning 2-darajasi 25 ga teng.",
            15
        ),
        (
            "algorithms",
            "Ikkilik qidiruv (Binary Search) algoritmining o'rtacha vaqt murakkabligi qanday?",
            '# Saralangan ro\'yxatdan qidirish',
            "O(n)",
            "O(log n)",
            "O(n^2)",
            "O(1)",
            "B",
            "Binary Search har bir qadamda qidiruv maydonini yarmiga qisqartiradi, shuning uchun murakkabligi O(log n).",
            20
        ),
        (
            "python",
            "Python ro'yxatida (list) elementlar sonini bilish uchun qaysi funksiya ishlatiladi?",
            'mevalar = ["olma", "banan", "anor"]\nprint(???(mevalar))',
            "count()",
            "size()",
            "length()",
            "len()",
            "D",
            "Python'da obyekt uzunligini aniqlash uchun o'rnatilgan len() funksiyasi ishlatiladi.",
            10
        ),
        (
            "data_structures",
            "Qaysi ma'lumotlar tuzilmasi LIFO (Oxirgi kirgan - birinchi chiqadi) tamoyilida ishlaydi?",
            '# Oxirgi qo\'shilgan element birinchi olinadi',
            "Navbat (Queue)",
            "Stek (Stack)",
            "Lug'at (Dictionary)",
            "Bog'langan ro'yxat (Linked List)",
            "B",
            "Stek (Stack) LIFO (Last In First Out) prinsipi asosida ishlaydi (masalan, likopchalar taxlami).",
            15
        ),
        (
            "web",
            "Veb sahifaning tuzilishi (skeleti) qaysi texnologiya orqali yaratiladi?",
            '<!-- Saytning skeleti -->',
            "CSS",
            "HTML",
            "JavaScript",
            "PHP",
            "B",
            "HTML (HyperText Markup Language) veb-sahifaning asosiy tuzilishi va bloklarini belgilaydi.",
            10
        ),
        (
            "algorithms",
            "Qaysi saralash algoritmi 'Bo'lib tashla va hukmronlik qil' (Divide and Conquer) usulidan foydalanadi?",
            '# Ro\'yxat ikkiga bo\'linadi va birlashtiriladi',
            "Bubble Sort",
            "Selection Sort",
            "Merge Sort",
            "Insertion Sort",
            "C",
            "Merge Sort massivni teng qismlarga bo'lib, keyin saralab birlashtiradi.",
            20
        ),
        (
            "python",
            "Python'da o'zgarmas (immutable) ketma-ketlik turi qaysi?",
            '# Elementlarini o\'zgartirib bo\'lmaydi',
            "List (Ro'yxat)",
            "Dictionary (Lug'at)",
            "Tuple (Kortej)",
            "Set (To'plam)",
            "C",
            "Tuple (kortej) yaratilgandan so'ng uning elementlarini o'zgartirib bo'lmaydi (immutable).",
            15
        )
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO questions (category, question, code_snippet, option_a, option_b, option_c, option_d, correct_option, explanation, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, questions_data)
    conn.commit()

def seed_puzzles(conn):
    puzzles_data = [
        (
            "1 dan 5 gacha sonlarni chiqarish",
            "For sikli yordamida 1 dan 5 gacha sonlarni ekranga chiqaruvchi kod bloklarini to'g'ri tartibda joylashtiring.",
            "python",
            json.dumps([
                "    print(son)",
                "for son in range(1, 6):",
                "# Sikl tugadi",
                "print('Bajarildi!')"
            ]),
            json.dumps([1, 0, 2, 3]),
            25
        ),
        (
            "Ikkita sonning kattasini topuvchi funksiya",
            "Kattasini topish funksiyasini to'g'ri ketma-ketlikda yig'ing.",
            "python",
            json.dumps([
                "    if a > b:",
                "def eng_katta(a, b):",
                "    return b",
                "        return a",
                "    else:"
            ]),
            json.dumps([1, 0, 3, 4, 2]),
            30
        ),
        (
            "Ro'yxat elementlari yig'indisini hisoblash",
            "Ro'yxatdagi sonlar yig'indisini hisoblash dasturi bloklarini tartiblang.",
            "python",
            json.dumps([
                "yigindi = 0",
                "    yigindi += son",
                "sonlar = [10, 20, 30]",
                "for son in sonlar:",
                "print('Natija:', yigindi)"
            ]),
            json.dumps([2, 0, 3, 1, 4]),
            35
        )
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO puzzles (title, description, language, blocks_json, correct_order_json, points)
        VALUES (?, ?, ?, ?, ?, ?)
    """, puzzles_data)
    conn.commit()

def seed_bugs(conn):
    bugs_data = [
        (
            "Sintaksis xatoni aniqlang",
            "def salom_ber(ism)\n    print('Assalomu alaykum ' + ism)",
            1,
            json.dumps([
                "1-qator: Funksiya e'lonida ikki nuqta (:) qolib ketgan",
                "2-qator: Satr qo'shishda xato bor",
                "1-qator: ism o'zgaruvchisiga default qiymat berilmagan",
                "Xato yo'q, kod to'g'ri"
            ]),
            0,
            "Python'da funksiya e'loni oxirida ikki nuqta ':' bo'lishi shart: def salom_ber(ism):",
            20
        ),
        (
            "Tenglik xatosini aniqlang",
            "yosh = 18\nif yosh = 18:\n    print('Siz balog\'atga yetgansiz')",
            2,
            json.dumps([
                "1-qator: son qiymati qo'shtirnoqda bo'lishi kerak",
                "2-qator: Taqqoslash uchun '==' ishlatilishi kerak, '=' emas",
                "3-qator: Matndagi apostrof xato yozilgan",
                "Kodda hech qanday xato yo'q"
            ]),
            1,
            "Taqqoslov operatori sifatida ikki barobar '==' ishlatiladi. Yagona '=' o'zlashtirish uchun mo'ljallangan.",
            20
        ),
        (
            "Indeks xatosi (IndexError)",
            "mevalar = ['Olma', 'Banan', 'Uzum']\nprint(mevalar[3])",
            2,
            json.dumps([
                "1-qator: Ro'yxat elementlari noto'g'ri yozilgan",
                "2-qator: mevalar[3] mavjud emas, indekslar 0 dan boshlanadi (oxirgi indeks 2)",
                "2-qator: print() funksiyasiga argument berilmagan",
                "Bunday ro'yxatni chop etib bo'lmaydi"
            ]),
            1,
            "3 ta elementli ro'yxat indekslari: 0, 1, 2. mevalar[3] chaqirilsa IndexError yuzaga keladi.",
            25
        )
    ]
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO bugs (title, code_with_bug, bug_line, options_json, correct_index, explanation, points)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, bugs_data)
    conn.commit()

# --- Helper functions ---

def register_user(phone, username, password):
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (phone, username, password_hash, xp, level)
            VALUES (?, ?, ?, 0, 1)
        """, (phone.strip(), username.strip(), pwd_hash))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, user_id, "Muvaffaqiyatli ro'yxatdan o'tdingiz!"
    except sqlite3.IntegrityError as e:
        conn.close()
        err_msg = str(e)
        if "phone" in err_msg:
            return False, None, "Bu telefon raqami allaqachon ro'yxatdan o'tgan!"
        elif "username" in err_msg:
            return False, None, "Bu foydalanuvchi nomi allaqachon band!"
        return False, None, "Ro'yxatdan o'tishda xatolik yuz berdi."
    except sqlite3.OperationalError as e:
        conn.close()
        if "readonly" in str(e).lower():
            try:
                tmp_dir = "/tmp" if os.path.exists("/tmp") else os.environ.get("TEMP", ".")
                tmp_db = os.path.join(tmp_dir, "algoplay.db")
                if not os.path.exists(tmp_db) and os.path.exists(SOURCE_DB):
                    shutil.copyfile(SOURCE_DB, tmp_db)
                conn_retry = sqlite3.connect(tmp_db)
                cursor_retry = conn_retry.cursor()
                cursor_retry.execute("""
                    INSERT INTO users (phone, username, password_hash, xp, level)
                    VALUES (?, ?, ?, 0, 1)
                """, (phone.strip(), username.strip(), pwd_hash))
                conn_retry.commit()
                uid = cursor_retry.lastrowid
                conn_retry.close()
                return True, uid, "Muvaffaqiyatli ro'yxatdan o'tdingiz!"
            except Exception as retry_err:
                return False, None, f"Baza xatosi: {str(retry_err)}"
        return False, None, f"Baza xatosi: {str(e)}"

def login_user(phone_or_user, password):
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute("""
        SELECT * FROM users
        WHERE (phone = ? OR username = ?) AND password_hash = ?
    """, (phone_or_user.strip(), phone_or_user.strip(), pwd_hash))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, dict(user), "Xush kelibsiz!"
    return False, None, "Telefon raqami / foydalanuvchi nomi yoki parol noto'g'ri!"

def login_admin(username, password):
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute("""
        SELECT * FROM admins
        WHERE username = ? AND password_hash = ?
    """, (username.strip(), pwd_hash))
    admin = cursor.fetchone()
    conn.close()
    if admin:
        return True, dict(admin), "Admin tizimiga xush kelibsiz!"
    return False, None, "Admin login yoki paroli noto'g'ri!"

def add_xp(user_id, xp_amount, game_type, score, details=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (xp_amount, user_id))
    # Darajani yangilash (har 100 XP da 1 daraja)
    cursor.execute("""
        UPDATE users
        SET level = (xp / 100) + 1
        WHERE id = ?
    """, (user_id,))
    cursor.execute("""
        INSERT INTO game_scores (user_id, game_type, score, xp_earned, details)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, game_type, score, xp_amount, details))
    conn.commit()
    cursor.execute("SELECT xp, level FROM users WHERE id = ?", (user_id,))
    updated = cursor.fetchone()
    conn.close()
    return dict(updated) if updated else {}

def get_leaderboard(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, phone, xp, level, created_at
        FROM users
        ORDER BY xp DESC, created_at ASC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.phone, u.xp, u.level, u.created_at,
               COUNT(g.id) as games_played,
               COALESCE(MAX(g.played_at), 'Hali o''ynamagan') as last_played
        FROM users u
        LEFT JOIN game_scores g ON u.id = g.user_id
        GROUP BY u.id
        ORDER BY u.id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_questions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_puzzles():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM puzzles ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_all_bugs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bugs ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_admin_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_users, COALESCE(SUM(xp), 0) as total_xp FROM users")
    user_stats = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) as total_games FROM game_scores")
    game_stats = dict(cursor.fetchone())

    cursor.execute("SELECT COUNT(*) as total_questions FROM questions")
    q_stats = dict(cursor.fetchone())

    cursor.execute("""
        SELECT g.id, u.username, g.game_type, g.score, g.xp_earned, g.played_at
        FROM game_scores g
        JOIN users u ON g.user_id = u.id
        ORDER BY g.played_at DESC
        LIMIT 10
    """)
    recent_games = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_users": user_stats["total_users"],
        "total_xp": user_stats["total_xp"],
        "total_games": game_stats["total_games"],
        "total_questions": q_stats["total_questions"],
        "recent_games": recent_games
    }

def get_user_profile_data(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, phone, xp, level, created_at FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        return None
    user = dict(user_row)

    # Reytingdagi o'rni
    cursor.execute("SELECT COUNT(*) + 1 as rank FROM users WHERE xp > ?", (user["xp"],))
    rank_row = cursor.fetchone()
    user["rank"] = rank_row["rank"] if rank_row else 1

    # O'ynagan o'yinlari statistikasi
    cursor.execute("SELECT COUNT(*) as total_games, COALESCE(SUM(xp_earned), 0) as total_earned FROM game_scores WHERE user_id = ?", (user_id,))
    stats_row = cursor.fetchone()
    user["total_games"] = stats_row["total_games"] if stats_row else 0
    user["total_earned"] = stats_row["total_earned"] if stats_row else 0

    # Oxirgi o'yinlar tarixi
    cursor.execute("""
        SELECT game_type, score, xp_earned, details, played_at
        FROM game_scores
        WHERE user_id = ?
        ORDER BY played_at DESC
        LIMIT 8
    """, (user_id,))
    user["history"] = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return user

def delete_user_account(user_id, password=None):
    conn = get_db()
    cursor = conn.cursor()
    if password is not None and password.strip() != "":
        pwd_hash = hash_password(password.strip())
        cursor.execute("SELECT id FROM users WHERE id = ? AND password_hash = ?", (user_id, pwd_hash))
        if not cursor.fetchone():
            conn.close()
            return False, "Kiritilgan parol noto'g'ri!"

    cursor.execute("DELETE FROM game_scores WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, "Hisobingiz va barcha ma'lumotlaringiz muvaffaqiyatli o'chirildi."

if __name__ == "__main__":
    init_db()
    print("Database muvaffaqiyatli ishga tushirildi!")
