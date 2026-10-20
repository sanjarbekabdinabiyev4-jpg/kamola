/**
 * AlgoPlay - Audio FX & Main Helper Scripts
 */

// Audio Controller using Web Audio API (No external sound files required)
class SoundFX {
    constructor() {
        this.ctx = null;
        this.enabled = localStorage.getItem("algoplay_sound") !== "false";
        this.initIcon();
    }

    initContext() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioCtx();
        }
    }

    playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.1) {
        if (!this.enabled) return;
        try {
            this.initContext();
            if (this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (e) {
            console.warn("Audio play error:", e);
        }
    }

    click() {
        this.playTone(800, 'sine', 0.05, 0.05);
    }

    correct() {
        if (!this.enabled) return;
        try {
            this.initContext();
            // Upward chord (C5 -> E5 -> G5)
            [523.25, 659.25, 783.99].forEach((freq, idx) => {
                setTimeout(() => {
                    this.playTone(freq, 'triangle', 0.18, 0.12);
                }, idx * 75);
            });
        } catch (e) {}
    }

    wrong() {
        if (!this.enabled) return;
        try {
            this.initContext();
            // Downward buzzer
            [300, 200].forEach((freq, idx) => {
                setTimeout(() => {
                    this.playTone(freq, 'sawtooth', 0.2, 0.1);
                }, idx * 100);
            });
        } catch (e) {}
    }

    levelUp() {
        if (!this.enabled) return;
        try {
            this.initContext();
            [440, 554.37, 659.25, 880].forEach((freq, idx) => {
                setTimeout(() => {
                    this.playTone(freq, 'sine', 0.25, 0.15);
                }, idx * 90);
            });
        } catch (e) {}
    }

    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem("algoplay_sound", this.enabled);
        this.initIcon();
        if (this.enabled) {
            this.click();
            showToast("Ovoz yoqildi!", "info");
        } else {
            showToast("Ovoz o'chirildi", "info");
        }
    }

    initIcon() {
        const icon = document.getElementById("soundIcon");
        if (icon) {
            if (this.enabled) {
                icon.className = "fa-solid fa-volume-high";
            } else {
                icon.className = "fa-solid fa-volume-xmark";
            }
        }
    }
}

const sfx = new SoundFX();

// Toast Notifications
function showToast(message, type = "success") {
    let container = document.getElementById("flashContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "flashContainer";
        container.className = "flash-messages-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `flash-toast flash-${type}`;
    let iconClass = "fa-circle-check";
    if (type === "danger" || type === "error") iconClass = "fa-circle-exclamation";
    if (type === "info") iconClass = "fa-circle-info";

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
        <button class="flash-close">&times;</button>
    `;

    toast.querySelector(".flash-close").onclick = () => toast.remove();
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(50px)";
            setTimeout(() => toast.remove(), 300);
        }
    }, 4000);
}

// Confetti burst
function fireConfetti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 90,
            spread: 80,
            origin: { y: 0.6 }
        });
    }
}

// Interactive Particle Background Canvas
function initParticleCanvas() {
    const canvas = document.getElementById('particlesCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = Math.min(Math.floor((width * height) / 22000), 55);

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 1.8 + 0.6,
            dx: (Math.random() - 0.5) * 0.45,
            dy: (Math.random() - 0.5) * 0.45,
            alpha: Math.random() * 0.5 + 0.2,
            color: Math.random() > 0.5 ? '0, 242, 254' : '139, 92, 246' // cyan or purple
        });
    }

    let mouse = { x: null, y: null };
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.dx;
            p.y += p.dy;

            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            // Draw particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${p.color}, ${p.alpha})`;
            ctx.shadowBlur = 8;
            ctx.shadowColor = `rgba(${p.color}, 0.8)`;
            ctx.fill();
            ctx.shadowBlur = 0;

            // Connect nearby particles
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 110) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(${p.color}, ${0.15 * (1 - dist / 110)})`;
                    ctx.lineWidth = 0.7;
                    ctx.stroke();
                }
            }

            // Mouse interaction
            if (mouse.x !== null && mouse.y !== null) {
                const mDist = Math.hypot(p.x - mouse.x, p.y - mouse.y);
                if (mDist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(0, 242, 254, ${0.25 * (1 - mDist / 120)})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
}

// Code Copy Feature
function initCodeCopyButtons() {
    document.querySelectorAll('.code-block-container, .code-mockup-card').forEach(container => {
        const header = container.querySelector('.code-block-header, .mockup-header');
        const codePre = container.querySelector('pre, .mockup-body');
        if (!header || !codePre || header.querySelector('.copy-code-btn')) return;

        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.className = 'copy-code-btn';
        copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Nusxa olish</span>';
        copyBtn.title = "Kodni nusxalash";

        copyBtn.addEventListener('click', () => {
            const codeText = codePre.innerText.trim();
            navigator.clipboard.writeText(codeText).then(() => {
                sfx.click();
                copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: #10b981;"></i> <span style="color: #10b981;">Ko\'chirildi!</span>';
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Nusxa olish</span>';
                    copyBtn.classList.remove('copied');
                }, 2200);
            }).catch(() => {
                showToast("Nusxalashda xatolik yuz berdi", "danger");
            });
        });

        header.appendChild(copyBtn);
    });
}

// Scroll to Top Handler
function initScrollToTop() {
    const btn = document.getElementById('scrollTopBtn');
    if (!btn) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 350) {
            btn.classList.add('visible');
        } else {
            btn.classList.remove('visible');
        }
    });

    btn.addEventListener('click', () => {
        sfx.click();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Password toggle (Show/Hide)
function initPasswordToggles() {
    document.querySelectorAll('.form-input-box').forEach(box => {
        const input = box.querySelector('input[type="password"]');
        if (!input || box.querySelector('.password-toggle-btn')) return;

        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle-btn';
        toggleBtn.innerHTML = '<i class="fa-regular fa-eye"></i>';
        toggleBtn.title = "Parolni ko'rsatish/yashirish";

        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            sfx.click();
            if (input.type === 'password') {
                input.type = 'text';
                toggleBtn.innerHTML = '<i class="fa-regular fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                toggleBtn.innerHTML = '<i class="fa-regular fa-eye"></i>';
            }
        });

        box.appendChild(toggleBtn);
    });
}

// DOM Loaded handlers
document.addEventListener("DOMContentLoaded", () => {
    // Init canvas particles
    initParticleCanvas();

    // Init code copy buttons
    initCodeCopyButtons();

    // Init scroll to top button
    initScrollToTop();

    // Init password show/hide
    initPasswordToggles();

    // Sound Toggle button
    const soundToggle = document.getElementById("soundToggle");
    if (soundToggle) {
        soundToggle.addEventListener("click", () => sfx.toggle());
    }

    // Mobile nav toggle
    const navToggle = document.getElementById("navToggle");
    const navMenu = document.getElementById("navMenu");
    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("open");
        });
    }

    // Audio click for buttons
    document.querySelectorAll(".btn, .nav-link, .game-tab-btn, .learn-pill-btn, .auth-tab-btn, .admin-tab-btn").forEach(el => {
        el.addEventListener("click", () => {
            sfx.click();
        });
    });

    // Auto-dismiss initial flash toasts after 5s
    document.querySelectorAll(".flash-toast").forEach(toast => {
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 5000);
    });
});
