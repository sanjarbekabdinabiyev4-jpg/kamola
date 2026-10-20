# AlgoPlay - Dasturlashni O'yinlar Orqali O'rganish Platformasi 🎮🚀

**AlgoPlay** — bu dasturlash, Python tili, algoritmlar va ma'lumotlar tuzilmalarini interaktiv mini o'yinlar, kodli puzzlelar hamda testlar orqali o'rganishga mo'ljallangan zamonaviy veb-platforma.

---

## 🌟 Talab qilingan 5 ta Sahifa Tuzilishi:

1. **1-sahifa: "Home" (Bosh sahifa)**
   - Sayt haqida qisqacha, ta'sirchan ma'lumot
   - Yuqori sifatli rasmlar va SVG illyustratsiyalar
   - Interaktiv kodli kartalar, animatsiyalar, 3D gaming badge-lar
   - 4 ta o'yin turi shoukeysi va platforma statistikasi
   - Peshqadamlar doskasi (Top 5 o'yinchilar)

2. **2-sahifa: "Login / Registratsiya" (Kirish & Profil)**
   - Foydalanuvchining **telefon raqami**, **foydalanuvchi nomi (username)** va **paroli**
   - Tizimga kirish (Login) va yangi hisob ochish (Register)
   - Kirilgandan so'ng shaxsiy profil kartasi, daraja (Level), joriy XP ballari va progress bari
   - Tizimdan chiqish (Logout)

3. **3-sahifa: "Dasturlash" (Bilimlar Bazasi / Darslar)**
   - Dasturlash haqida to'liq va tushunarli ma'lumotlar:
     1. Python Asoslari, sintaksis va ma'lumot turlari
     2. Shartlar (`if`, `elif`, `else`) va mantiqiy amallar
     3. Sikllar (`for`, `while`) va `range()`
     4. Funksiyalar (`def`, `return`)
     5. Ma'lumotlar tuzilmasi: Ro'yxat (`List`), Kortej (`Tuple`), Stek (`Stack` - LIFO), Navbat (`Queue` - FIFO)
     6. Algoritmlar: Ikkilik qidiruv (Binary Search - O(log n)), Saralash algoritmlari (Bubble Sort, Merge Sort)
     7. Veb-dasturlash: HTML, CSS, JavaScript, Backend vs Frontend
     8. Koddagi xatolar turlari (`SyntaxError`, `IndexError`, `TypeError`)
   - Har bir dars oxirida 4-sahifadagi tegishli o'yinga yo'naltiruvchi tugmalar!

4. **4-sahifa: "O'yinlar" (Mini-o'yinlar & Testlar)**
   - **Quiz Arena (Savol-Javob Test):** 3-sahifadagi darslar asosida tuzilgan savollar. To'g'ri/noto'g'ri javoblarda ovoz effektlari (Web Audio API), rangli indikatorlar, tushuntirish va XP mukofotlari!
   - **Kod Puzzle (Tartiblash):** Aralashtirilgan kod qatorlarini ⬆️ va ⬇️ tugmalari bilan to'g'ri mantiqiy tartibda yig'ish.
   - **Bug Hunter (Xatoni Top):** Xatoli kod ko'rsatiladi va xato qaysi qatorda va nima ekanligini topish kerak.
   - **Natijani Top (Code Output Predictor):** Kod parchasi terminalga qanday natija chiqarishini oldindan topish.
   - **Jonli Peshqadamlar Jadvali (Leaderboard):** Barcha foydalanuvchilar to'plagan XP reytingi!

5. **5-sahifa: "Admin Panel" (Himoyalangan Boshqaruv)**
   - Boshqa oddiy foydalanuvchilar kira olmaydi (maxsus himoyalangan dekorator bilan ta'minlangan).
   - Faqat admin o'zining foydalanuvchi nomi va maxfiy paroli bilan kira oladi.
   - **Boshlang'ich Admin Login:** `admin` | **Parol:** `admin777`
   - Barcha foydalanuvchilar ro'yxati va ularni o'chirish imkoniyati
   - Yangi test savollari qo'shish va mavjudlarini o'chirish formasi
   - Yangi kod puzzle qo'shish va o'chirish formasi
   - O'yinlar tarixi va umumiy tizim statistikasi

---

## 🛠 Texnologiyalar:
- **Backend:** Python (Flask)
- **Ma'lumotlar Bazasi:** SQLite (`algoplay.db`)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), FontAwesome 6, Canvas Confetti
- **Ovoz Effektlari:** Web Audio API (qo'shimcha audio fayllar talab qilmaydi, brauzerning o'zida generatsiya qilinadi)

---

## 🚀 Ishga Tushirish:

1. Ushbu papkadagi `start.bat` fayliga sichqonchani ikki marta bosing.
   Yoki terminalda:
   ```bash
   python app.py
   ```
2. Brauzerda quyidagi manzilni oching:
   ```
   http://127.0.0.1:5050
   ```
3. Admin panelga kirish manzili:
   ```
   http://127.0.0.1:5050/admin/login
   ```
   - Login: `admin`
   - Parol: `admin777`
