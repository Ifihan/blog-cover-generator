// Landing Page JavaScript

// Typewriter Effect
const words = ['Stunning Covers', 'Professional Images', 'Beautiful Designs', 'Eye-Catching Visuals', 'Amazing Graphics'];
let wordIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typewriterElement = document.getElementById('typewriter');
const typingSpeed = 100;
const deletingSpeed = 50;
const delayBetweenWords = 2000;

function typeWriter() {
    const currentWord = words[wordIndex];

    if (isDeleting) {
        typewriterElement.textContent = currentWord.substring(0, charIndex - 1);
        charIndex--;
    } else {
        typewriterElement.textContent = currentWord.substring(0, charIndex + 1);
        charIndex++;
    }

    if (!isDeleting && charIndex === currentWord.length) {
        isDeleting = true;
        setTimeout(typeWriter, delayBetweenWords);
        return;
    }

    if (isDeleting && charIndex === 0) {
        isDeleting = false;
        wordIndex = (wordIndex + 1) % words.length;
    }

    const speed = isDeleting ? deletingSpeed : typingSpeed;
    setTimeout(typeWriter, speed);
}

// Header Scroll Effect
function initHeaderScroll() {
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Mobile Menu Toggle
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-menu');

    mobileMenuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileMenuToggle.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link, .github-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            mobileMenuToggle.classList.remove('active');
        });
    });
}

// Fetch GitHub Stars
async function fetchGitHubStars() {
    try {
        const response = await fetch('https://api.github.com/repos/ifihan/blog-cover-generator');
        const data = await response.json();
        const stars = data.stargazers_count || 0;
        document.getElementById('github-stars').textContent = `★ ${stars}`;
    } catch (error) {
        console.error('Error fetching GitHub stars:', error);
        document.getElementById('github-stars').textContent = '★ 0';
    }
}

// Smooth Scrolling
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .showcase-card, .benefit-card, .step').forEach(el => {
        observer.observe(el);
    });
}

// Initialize all functionality on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Set current year in footer
    document.getElementById('currentYear').textContent = new Date().getFullYear();
    
    // Initialize features
    typeWriter();
    initHeaderScroll();
    initMobileMenu();
    fetchGitHubStars();
    initSmoothScrolling();
    initScrollAnimations();
});
