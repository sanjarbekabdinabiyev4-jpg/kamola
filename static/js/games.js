/**
 * AlgoPlay - Mini Games Interactive Engine
 * Handles: Quiz, Code Puzzle, Bug Hunter, Output Guesser, XP Sync
 */

// Global State
let currentQuizIdx = 0;
let userQuizScore = 0;
let totalQuizXpEarned = 0;
let quizStreak = 0;
let userQuizAnswers = []; // O'quvchi tanlagan javoblar saqlanadi

let currentPuzzleIdx = 0;
let currentPuzzleBlocks = [];

let currentBugIdx = 0;

let currentOutputIdx = 0;
const outputChallenges = [
    {
        code: `a = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))`,
        options: ["3", "4", "Error", "[1, 2, 3, 4]"],
        correct: 1,
        explanation: "Python'da 'b = a' ro'yxatning nusxasini emas, balki aynan o'sha xotira manziliga havolani beradi. b ga 4 qo'shilganda, a ham o'zgaradi va uning uzunligi 4 bo'ladi.",
        points: 15
    },
    {
        code: `x = 10\ndef ozgartir():\n    x = 20\nozgartir()\nprint(x)`,
        options: ["20", "10", "UnboundLocalError", "None"],
        correct: 1,
        explanation: "Funksiya ichidagi 'x = 20' faqat lokal o'zgaruvchidir. Global x o'zgaruvchisining qiymati o'zgarmaydi va 10 ligicha qoladi.",
        points: 15
    },
    {
        code: `matn = "AlgoPlay"\nprint(matn[0:4])`,
        options: ["Algo", "AlgoP", "lgoP", "AlgoPlay"],
        correct: 0,
        explanation: "Satrni kesishda matn[0:4] 0-indeksdan boshlab 4-indeksgacha oladi (4 kirmaydi), ya'ni 'A', 'l', 'g', 'o'.",
        points: 10
    },
    {
        code: `sonlar = [1, 2, 3]\nprint(sonlar * 2)`,
        options: ["[2, 4, 6]", "[1, 2, 3, 1, 2, 3]", "Error", "[1, 2, 3, 2]"],
        correct: 1,
        explanation: "Python'da ro'yxatni songa ko'paytirish uning elementlarini takrorlaydi, har bir sonni 2 ga ko'paytirmaydi.",
        points: 15
    }
];

// Switch Game Modes
function switchGameMode(mode) {
    sfx.click();
    const modes = ['quiz', 'puzzle', 'bug', 'output'];
    modes.forEach(m => {
        const tabBtn = document.getElementById(`tabBtn${capitalize(m)}`);
        const section = document.getElementById(`gameSection${capitalize(m)}`);
        if (tabBtn) tabBtn.classList.remove('active');
        if (section) section.style.display = 'none';
    });

    const activeBtn = document.getElementById(`tabBtn${capitalize(mode)}`);
    const activeSection = document.getElementById(`gameSection${capitalize(mode)}`);
    if (activeBtn) activeBtn.classList.add('active');
    if (activeSection) activeSection.style.display = 'flex';
}

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

// ==================== 1. QUIZ ARENA ====================
function renderQuizQuestion() {
    const questions = window.ALGOPLAY_QUESTIONS || [];
    if (!questions.length) return;

    if (currentQuizIdx >= questions.length) {
        // Hamma savollar ishlab bo'lingach, natijalar va to'g'ri javoblarni ko'rsatish
        finishQuizArena(questions);
        return;
    }

    const q = questions[currentQuizIdx];
    document.getElementById("quizCurrentNum").textContent = currentQuizIdx + 1;
    document.getElementById("quizCategory").textContent = q.category ? q.category.toUpperCase() : "DASTURLASH";
    document.getElementById("quizQuestionText").textContent = q.question;

    const codeBox = document.getElementById("quizCodeBox");
    if (q.code_snippet && q.code_snippet.trim() !== "") {
        codeBox.style.display = "block";
        codeBox.textContent = q.code_snippet;
    } else {
        codeBox.style.display = "none";
    }

    const optionsGrid = document.getElementById("quizOptionsGrid");
    optionsGrid.innerHTML = "";

    const options = [
        { key: "A", text: q.option_a },
        { key: "B", text: q.option_b },
        { key: "C", text: q.option_c },
        { key: "D", text: q.option_d }
    ];

    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.className = "quiz-option-btn";
        btn.innerHTML = `<span class="option-letter">${opt.key}</span> <span>${escapeHtml(opt.text)}</span>`;
        btn.onclick = () => selectQuizAnswer(opt.key, btn);
        optionsGrid.appendChild(btn);
    });

    const feedbackBox = document.getElementById("quizFeedbackBox");
    if (feedbackBox) feedbackBox.style.display = "none";
}

function selectQuizAnswer(selectedKey, clickedBtn) {
    sfx.click();
    
    // Savol paytida to'g'ri/noto'g'ri javob fosh etilmaydi va yashil qilinmaydi!
    // Faqat tanlangan holat (selected) ko'rsatiladi
    const buttons = document.querySelectorAll(".quiz-option-btn");
    buttons.forEach(btn => btn.disabled = true);
    clickedBtn.classList.add("selected");

    // Foydalanuvchining javobini xotiraga yozamiz
    userQuizAnswers[currentQuizIdx] = selectedKey;

    // 350ms dan so'ng keyingi savolga o'tish
    setTimeout(() => {
        currentQuizIdx++;
        renderQuizQuestion();
    }, 380);
}

function finishQuizArena(questions) {
    document.getElementById("quizContentBox").style.display = "none";
    document.getElementById("quizFinishBox").style.display = "block";

    let correctCount = 0;
    let earnedTotalXp = 0;
    const reviewContainer = document.getElementById("quizReviewList");
    reviewContainer.innerHTML = "";

    questions.forEach((q, idx) => {
        const userAns = userQuizAnswers[idx] || "—";
        const isCorrect = userAns === q.correct_option;
        const qPoints = q.points || 10;

        if (isCorrect) {
            correctCount++;
            earnedTotalXp += qPoints;
        }

        // Har bir savol varianti matnini topish
        let userAnsText = "";
        let correctAnsText = "";
        const optMap = { "A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d };
        userAnsText = optMap[userAns] || "Javob berilmadi";
        correctAnsText = optMap[q.correct_option] || "";

        const card = document.createElement("div");
        card.className = "quiz-review-card";
        card.style.cssText = `
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid ${isCorrect ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)'};
            border-left: 4px solid ${isCorrect ? 'var(--green)' : 'var(--red)'};
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;

        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <span style="font-weight: 700; color: #fff; font-size: 0.98rem;">
                    ${idx + 1}-savol: ${escapeHtml(q.question)}
                </span>
                <span class="badge-beta" style="background: ${isCorrect ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)'}; color: ${isCorrect ? '#34d399' : '#f87171'}; border-color: ${isCorrect ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'};">
                    ${isCorrect ? `<i class="fa-solid fa-check"></i> To'g'ri (+${qPoints} XP)` : `<i class="fa-solid fa-xmark"></i> Noto'g'ri`}
                </span>
            </div>
            
            ${q.code_snippet ? `<pre class="code-pre" style="padding: 10px; font-size: 0.85rem; margin: 4px 0;"><code>${escapeHtml(q.code_snippet)}</code></pre>` : ''}

            <div style="display: flex; gap: 16px; flex-wrap: wrap; font-size: 0.9rem; margin-top: 4px;">
                <div style="color: ${isCorrect ? 'var(--green)' : '#fca5a5'};">
                    <strong>Sizning javobingiz:</strong> [${userAns}] ${escapeHtml(userAnsText)}
                </div>
                ${!isCorrect ? `
                <div style="color: var(--green);">
                    <strong>To'g'ri javob:</strong> [${q.correct_option}] ${escapeHtml(correctAnsText)}
                </div>` : ''}
            </div>

            ${q.explanation ? `
            <div style="background: rgba(0, 242, 254, 0.05); border: 1px solid rgba(0, 242, 254, 0.15); border-radius: 6px; padding: 10px 14px; font-size: 0.86rem; color: var(--text-secondary); margin-top: 4px;">
                <i class="fa-solid fa-lightbulb" style="color: var(--amber); margin-right: 6px;"></i>
                <strong>Tushuntirish:</strong> ${escapeHtml(q.explanation)}
            </div>` : ''}
        `;
        reviewContainer.appendChild(card);
    });

    document.getElementById("quizCorrectCount").textContent = correctCount;
    document.getElementById("quizTotalCount").textContent = questions.length;
    document.getElementById("quizFinalXp").textContent = `+${earnedTotalXp} XP`;
    document.getElementById("quizUserScore").textContent = earnedTotalXp;

    if (earnedTotalXp > 0) {
        saveScoreToServer("quiz", earnedTotalXp, earnedTotalXp, `Quiz Arena: ${correctCount}/${questions.length} ta to'g'ri`);
        fireConfetti();
        sfx.levelUp();
    } else {
        sfx.wrong();
    }
}

function restartQuiz() {
    sfx.click();
    currentQuizIdx = 0;
    userQuizScore = 0;
    totalQuizXpEarned = 0;
    userQuizAnswers = [];
    document.getElementById("quizUserScore").textContent = "0";
    document.getElementById("quizContentBox").style.display = "block";
    document.getElementById("quizFinishBox").style.display = "none";
    renderQuizQuestion();
}

// ==================== 2. KOD PUZZLE (TARTIBLASH) ====================
function renderPuzzle() {
    const puzzles = window.ALGOPLAY_PUZZLES || [];
    if (!puzzles.length) return;

    if (currentPuzzleIdx >= puzzles.length) {
        currentPuzzleIdx = 0; // Tsiklda aylanish
    }

    const p = puzzles[currentPuzzleIdx];
    document.getElementById("puzzleTitle").textContent = p.title;
    document.getElementById("puzzleDesc").textContent = p.description;
    document.getElementById("puzzleReward").textContent = p.points || 25;

    const feedback = document.getElementById("puzzleFeedback");
    feedback.style.display = "none";

    // Bloklarni nusxalash
    currentPuzzleBlocks = [...p.blocks];

    renderPuzzleBlocks();
}

function renderPuzzleBlocks() {
    const container = document.getElementById("puzzleBlocksContainer");
    container.innerHTML = "";

    currentPuzzleBlocks.forEach((line, index) => {
        const item = document.createElement("div");
        item.className = "puzzle-block";
        item.dataset.index = index;

        item.innerHTML = `
            <div style="display: flex; align-items: center; gap: 14px;">
                <span class="puzzle-drag-handle"><i class="fa-solid fa-grip-vertical"></i></span>
                <span style="color: var(--cyan); font-weight: 700; width: 24px;">#${index + 1}</span>
                <code>${escapeHtml(line)}</code>
            </div>
            <div style="display: flex; gap: 6px;">
                <button class="btn btn-outline btn-sm" onclick="moveBlock(${index}, -1)" ${index === 0 ? 'disabled' : ''} title="Yuqoriga surish">
                    <i class="fa-solid fa-arrow-up"></i>
                </button>
                <button class="btn btn-outline btn-sm" onclick="moveBlock(${index}, 1)" ${index === currentPuzzleBlocks.length - 1 ? 'disabled' : ''} title="Pastga surish">
                    <i class="fa-solid fa-arrow-down"></i>
                </button>
            </div>
        `;
        container.appendChild(item);
    });
}

function moveBlock(index, direction) {
    sfx.click();
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= currentPuzzleBlocks.length) return;

    const temp = currentPuzzleBlocks[index];
    currentPuzzleBlocks[index] = currentPuzzleBlocks[newIndex];
    currentPuzzleBlocks[newIndex] = temp;

    renderPuzzleBlocks();
}

function checkPuzzleOrder() {
    const puzzles = window.ALGOPLAY_PUZZLES || [];
    const p = puzzles[currentPuzzleIdx];
    const feedback = document.getElementById("puzzleFeedback");

    // To'g'ri tartibni aniqlash
    // p.correct_order har bir o'rindagi to'g'ri blok indeksini ifodalaydi
    let isCorrect = true;
    for (let i = 0; i < p.correct_order.length; i++) {
        const correctLine = p.blocks[p.correct_order[i]];
        if (currentPuzzleBlocks[i] !== correctLine) {
            isCorrect = false;
            break;
        }
    }

    if (isCorrect) {
        sfx.levelUp();
        fireConfetti();
        feedback.style.display = "block";
        feedback.style.background = "rgba(16, 185, 129, 0.2)";
        feedback.style.color = "#6ee7b7";
        feedback.style.border = "1px solid #10b981";
        feedback.innerHTML = `<i class="fa-solid fa-trophy"></i> Qoyilmaqom! Kod to'g'ri tartibda yig'ildi! +${p.points || 25} XP qo'shildi!`;

        saveScoreToServer("puzzle", p.points || 25, p.points || 25, `Puzzle: ${p.title}`);
    } else {
        sfx.wrong();
        feedback.style.display = "block";
        feedback.style.background = "rgba(239, 68, 68, 0.2)";
        feedback.style.color = "#fca5a5";
        feedback.style.border = "1px solid #ef4444";
        feedback.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Tartibda xatolik bor! Kod mantiqini qaytadan o'ylab ko'ring va bloklar o'rnini almashtiring.`;
    }
}

function nextPuzzle() {
    sfx.click();
    const puzzles = window.ALGOPLAY_PUZZLES || [];
    currentPuzzleIdx = (currentPuzzleIdx + 1) % puzzles.length;
    renderPuzzle();
}

// ==================== 3. BUG HUNTER ====================
function renderBugChallenge() {
    const bugs = window.ALGOPLAY_BUGS || [];
    if (!bugs.length) return;

    if (currentBugIdx >= bugs.length) {
        currentBugIdx = 0;
    }

    const b = bugs[currentBugIdx];
    document.getElementById("bugTitle").textContent = b.title;
    document.getElementById("bugReward").textContent = b.points || 20;
    document.getElementById("bugCodeBox").textContent = b.code_with_bug;

    const optionsGrid = document.getElementById("bugOptionsGrid");
    optionsGrid.innerHTML = "";

    b.options.forEach((optText, index) => {
        const btn = document.createElement("button");
        btn.className = "quiz-option-btn";
        btn.innerHTML = `<span class="option-letter">${index + 1}</span> <span>${escapeHtml(optText)}</span>`;
        btn.onclick = () => selectBugAnswer(index, btn);
        optionsGrid.appendChild(btn);
    });

    document.getElementById("bugFeedbackBox").style.display = "none";
}

function selectBugAnswer(selectedIndex, clickedBtn) {
    const bugs = window.ALGOPLAY_BUGS || [];
    const b = bugs[currentBugIdx];
    const isCorrect = selectedIndex === b.correct_index;

    const buttons = document.querySelectorAll("#bugOptionsGrid .quiz-option-btn");
    buttons.forEach(btn => btn.disabled = true);

    const feedbackBox = document.getElementById("bugFeedbackBox");
    const feedbackTitle = document.getElementById("bugFeedbackTitle");
    const feedbackText = document.getElementById("bugFeedbackText");

    if (isCorrect) {
        clickedBtn.classList.add("correct");
        sfx.correct();
        fireConfetti();
        feedbackTitle.innerHTML = `<span style="color: var(--green);"><i class="fa-solid fa-bug-slash"></i> Xato aniqlandi! +${b.points || 20} XP</span>`;
        feedbackText.textContent = b.explanation;

        saveScoreToServer("bughunter", b.points || 20, b.points || 20, `Bug: ${b.title}`);
    } else {
        clickedBtn.classList.add("wrong");
        sfx.wrong();
        if (buttons[b.correct_index]) {
            buttons[b.correct_index].classList.add("correct");
        }
        feedbackTitle.innerHTML = `<span style="color: var(--red);"><i class="fa-solid fa-circle-xmark"></i> Noto'g'ri taxmin!</span>`;
        feedbackText.textContent = b.explanation;
    }

    feedbackBox.style.display = "flex";
}

function nextBugChallenge() {
    sfx.click();
    const bugs = window.ALGOPLAY_BUGS || [];
    currentBugIdx = (currentBugIdx + 1) % bugs.length;
    renderBugChallenge();
}

// ==================== 4. CODE OUTPUT PREDICTOR ====================
function renderOutputChallenge() {
    const challenge = outputChallenges[currentOutputIdx];
    document.getElementById("outputReward").textContent = challenge.points;
    document.getElementById("outputCodeBox").textContent = challenge.code;

    const grid = document.getElementById("outputOptionsGrid");
    grid.innerHTML = "";

    challenge.options.forEach((optText, index) => {
        const btn = document.createElement("button");
        btn.className = "quiz-option-btn";
        btn.innerHTML = `<span class="option-letter">${String.fromCharCode(65 + index)}</span> <span>${escapeHtml(optText)}</span>`;
        btn.onclick = () => selectOutputAnswer(index, btn);
        grid.appendChild(btn);
    });

    document.getElementById("outputFeedbackBox").style.display = "none";
}

function selectOutputAnswer(selectedIndex, clickedBtn) {
    const challenge = outputChallenges[currentOutputIdx];
    const isCorrect = selectedIndex === challenge.correct;

    const buttons = document.querySelectorAll("#outputOptionsGrid .quiz-option-btn");
    buttons.forEach(btn => btn.disabled = true);

    const feedbackBox = document.getElementById("outputFeedbackBox");
    const feedbackTitle = document.getElementById("outputFeedbackTitle");
    const feedbackText = document.getElementById("outputFeedbackText");

    if (isCorrect) {
        clickedBtn.classList.add("correct");
        sfx.correct();
        fireConfetti();
        feedbackTitle.innerHTML = `<span style="color: var(--green);"><i class="fa-solid fa-terminal"></i> To'g'ri bashorat! +${challenge.points} XP</span>`;
        feedbackText.textContent = challenge.explanation;

        saveScoreToServer("output", challenge.points, challenge.points, `Output Challenge #${currentOutputIdx + 1}`);
    } else {
        clickedBtn.classList.add("wrong");
        sfx.wrong();
        if (buttons[challenge.correct]) {
            buttons[challenge.correct].classList.add("correct");
        }
        feedbackTitle.innerHTML = `<span style="color: var(--red);"><i class="fa-solid fa-circle-xmark"></i> Noto'g'ri natija!</span>`;
        feedbackText.textContent = challenge.explanation;
    }

    feedbackBox.style.display = "flex";
}

function nextOutputChallenge() {
    sfx.click();
    currentOutputIdx = (currentOutputIdx + 1) % outputChallenges.length;
    renderOutputChallenge();
}

// ==================== XP SYNC & SERVER API ====================
async function saveScoreToServer(gameType, score, xpEarned, details) {
    if (!window.CURRENT_USER) {
        showToast("Ballaringizni saqlash uchun iltimos tizimga kiring!", "info");
        return;
    }

    try {
        const res = await fetch("/api/game/save-score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                game_type: gameType,
                score: score,
                xp_earned: xpEarned,
                details: details
            })
        });
        const data = await res.json();
        if (data.success) {
            // Navbar chipdagi XP ni yangilash
            const xpEl = document.querySelector(".chip-xp");
            const lvEl = document.querySelector(".chip-level");
            if (xpEl) xpEl.innerHTML = `<i class="fa-solid fa-star"></i> ${data.xp} XP`;
            if (lvEl) lvEl.innerHTML = `<i class="fa-solid fa-bolt"></i> Lv.${data.level}`;
            showToast(data.message, "success");
        }
    } catch (e) {
        console.warn("XP saqlashda xatolik:", e);
    }
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    // Agar foydalanuvchi tizimga kirgan bo'lsa va o'yin maydoni mavjud bo'lsa
    if (document.getElementById("gameSectionQuiz")) {
        renderQuizQuestion();
        renderPuzzle();
        renderBugChallenge();
        renderOutputChallenge();

        // URL da hash bo'lsa kerakli o'yinga o'tish (#puzzle, #bug, #output)
        const hash = window.location.hash.replace("#", "");
        if (['quiz', 'puzzle', 'bug', 'output'].includes(hash)) {
            switchGameMode(hash);
        }
    }
});
