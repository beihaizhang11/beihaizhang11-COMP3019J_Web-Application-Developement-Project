document.addEventListener("DOMContentLoaded", () => {
    const leftBackground = document.querySelector('.login-left');
    
    function createParticle() {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random initial position
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.opacity = Math.random() * 0.5 + 0.3;

        // Random animation delay and duration
        particle.style.animationDelay = `-${Math.random() * 15}s`;
        particle.style.animationDuration = `${Math.random() * 5 + 15}s`;

        leftBackground.appendChild(particle);
    }

    // Initially create more particles
    for (let i = 0; i < 50; i++) {
        createParticle();
    }

    // Mouse interaction effect
    leftBackground.addEventListener('mousemove', (event) => {
        const rect = leftBackground.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const particles = leftBackground.querySelectorAll('.particle');
        particles.forEach(particle => {
            const particleRect = particle.getBoundingClientRect();
            const particleX = particleRect.left - rect.left + particleRect.width / 2;
            const particleY = particleRect.top - rect.top + particleRect.height / 2;

            const distanceX = mouseX - particleX;
            const distanceY = mouseY - particleY;
            const distance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);

            if (distance < 120) {
                const angle = Math.atan2(distanceY, distanceX);
                const force = (120 - distance) / 120;
                const moveX = Math.cos(angle) * force * 40;
                const moveY = Math.sin(angle) * force * 40;

                // Add additional transformations while maintaining original animation
                const currentTransform = getComputedStyle(particle).transform;
                particle.style.transform = `${currentTransform} translate(${-moveX}px, ${-moveY}px)`;
            }
        });
    });

    // Reset particles when the mouse leaves
    leftBackground.addEventListener('mouseleave', () => {
        const particles = leftBackground.querySelectorAll('.particle');
        particles.forEach(particle => {
            particle.style.transform = '';
        });
    });
});