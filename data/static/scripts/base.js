// Mobile menu toggle
const toggle = document.getElementById('nav-toggle');
const menu = document.getElementById('nav-menu');
toggle?.addEventListener('click', () => menu.classList.toggle('hidden'));

// Theme toggle
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const html = document.documentElement;

const userPref = localStorage.getItem('theme');
if (userPref === 'dark' || (!userPref && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  html.classList.add('dark');
  themeIcon.classList.replace('ri-moon-line', 'ri-sun-line');
}

themeToggle.addEventListener('click', () => {
  html.classList.toggle('dark');
  const isDark = html.classList.contains('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  themeIcon.classList.toggle('ri-sun-line', isDark);
  themeIcon.classList.toggle('ri-moon-line', !isDark);
});