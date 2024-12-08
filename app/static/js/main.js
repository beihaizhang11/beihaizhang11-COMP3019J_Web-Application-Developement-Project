function toggleReplies() {
    const repliesSection = document.querySelector(".replies");
    const toggleButton = document.querySelector(".toggle-replies");

    if (repliesSection.style.maxHeight === "0px") {
        repliesSection.style.maxHeight = "1000px"; // Expand
        toggleButton.textContent = "Collapse Replies";
    } else {
        repliesSection.style.maxHeight = "0px"; // Collapse
        toggleButton.textContent = "Show Replies";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const background = document.querySelector('.interactive-background');
    
    // 只在存在背景元素时执行粒子效果
    if (background) {
        // Generate floating particles
        for (let i = 0; i < 40; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');

            // Randomly position particles
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.opacity = Math.random() * 0.5 + 0.5;

            background.appendChild(particle);
        }

        // Mousemove event for slight particle movement
        background.addEventListener('mousemove', (event) => {
            const particles = document.querySelectorAll('.particle');
            particles.forEach(particle => {
                const moveX = (event.clientX - window.innerWidth / 2) * 0.002;
                const moveY = (event.clientY - window.innerHeight / 2) * 0.002;
                particle.style.transform = `translate(${moveX}px, ${moveY}px)`;
            });
        });
    }

    // 自动隐藏通知
    const notifications = document.querySelectorAll('.notification');
    if (notifications.length > 0) {
        notifications.forEach(notification => {
            setTimeout(() => {
                notification.style.animation = 'slideOut 0.3s ease forwards';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }, 5000);
        });
    }

    // 添加滑出动画
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});
