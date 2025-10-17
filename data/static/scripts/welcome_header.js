document.addEventListener('DOMContentLoaded', () => {
  /* -------------------- Mobile menu toggle -------------------- */
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      menu.classList.toggle('hidden');
    });
  }

  /* -------------------- Theme toggle logic -------------------- */
  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  const html = document.documentElement;
  const userPref = localStorage.getItem('theme');

  // Apply saved or default theme
  if (
    userPref === 'dark' ||
    (!userPref && window.matchMedia('(prefers-color-scheme: dark)').matches)
  ) {
    html.classList.add('dark');
    if (themeIcon) {
      themeIcon.classList.remove('ri-moon-line');
      themeIcon.classList.add('ri-sun-line');
    }
  } else {
    html.classList.remove('dark');
    if (themeIcon) {
      themeIcon.classList.remove('ri-sun-line');
      themeIcon.classList.add('ri-moon-line');
    }
  }

  // Handle toggle button click
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      html.classList.toggle('dark');
      const isDark = html.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');

      if (themeIcon) {
        themeIcon.classList.toggle('ri-sun-line', isDark);
        themeIcon.classList.toggle('ri-moon-line', !isDark);
      }
    });
  }
});
