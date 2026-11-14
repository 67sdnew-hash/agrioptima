/**
 * AgriOptima - Interactive Touch/Cursor Detection & 3D Tilt Engine
 */

(function () {
  'use strict';

  // 1. Dual-Layer Cursor System
  const dot = document.createElement('div');
  dot.className = 'cursor-dot';
  document.body.appendChild(dot);

  const glow = document.createElement('div');
  glow.className = 'cursor-glow';
  document.body.appendChild(glow);

  let mouseX = -100, mouseY = -100;
  let glowX = -100, glowY = -100;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left = `${mouseX}px`;
    dot.style.top = `${mouseY}px`;
  });

  // Smooth lerp loop for the glow aura
  function animateCursor() {
    glowX += (mouseX - glowX) * 0.18;
    glowY += (mouseY - glowY) * 0.18;
    glow.style.left = `${glowX}px`;
    glow.style.top = `${glowY}px`;
    requestAnimationFrame(animateCursor);
  }
  requestAnimationFrame(animateCursor);

  // Hover detection for interactive elements
  const hoverSelectors = 'button, a, input, select, textarea, [data-tilt], .interactive';
  document.addEventListener('mouseover', (e) => {
    if (e.target.closest(hoverSelectors)) {
      document.body.classList.add('cursor-hover');
    }
  });

  document.addEventListener('mouseout', (e) => {
    if (e.target.closest(hoverSelectors)) {
      document.body.classList.remove('cursor-hover');
    }
  });

  // Touch device fallback: ripple effect on tap
  window.addEventListener('touchstart', (e) => {
    if (e.touches && e.touches[0]) {
      const touch = e.touches[0];
      const ripple = document.createElement('div');
      ripple.className = 'touch-ripple';
      ripple.style.position = 'fixed';
      ripple.style.left = `${touch.clientX}px`;
      ripple.style.top = `${touch.clientY}px`;
      ripple.style.width = '10px';
      ripple.style.height = '10px';
      ripple.style.borderRadius = '50%';
      ripple.style.pointerEvents = 'none';
      ripple.style.transform = 'translate(-50%, -50%)';
      ripple.style.background = 'radial-gradient(circle, rgba(16,185,129,0.5) 0%, transparent 80%)';
      ripple.style.transition = 'all 0.5s ease-out';
      ripple.style.zIndex = '9999';
      document.body.appendChild(ripple);

      setTimeout(() => {
        ripple.style.width = '70px';
        ripple.style.height = '70px';
        ripple.style.opacity = '0';
      }, 10);

      setTimeout(() => ripple.remove(), 550);
    }
  }, { passive: true });

  // 2. 3D Card Tilt Engine
  function init3DTilt() {
    const cards = document.querySelectorAll('[data-tilt]');

    cards.forEach((card) => {
      card.classList.add('tilt-card');

      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const cardX = e.clientX - rect.left;
        const cardY = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = ((cardY - centerY) / centerY) * -7; // max 7 deg
        const rotateY = ((cardX - centerX) / centerX) * 7;

        card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.015, 1.015, 1.015)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        card.style.transition = 'transform 0.4s cubic-bezier(0.2, 0, 0, 1)';
      });

      card.addEventListener('mouseenter', () => {
        card.style.transition = 'transform 0.1s ease-out';
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init3DTilt);
  } else {
    init3DTilt();
  }
})();
