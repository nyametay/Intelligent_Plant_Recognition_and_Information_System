// safe DOM-ready setup
(function () {
  const html = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  const icon = document.getElementById('themeIcon');

  // initialize from localStorage (fallback: system)
  try {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      html.classList.add('dark');
      icon.classList.replace('fa-moon', 'fa-sun');
    } else {
      html.classList.remove('dark');
      icon.classList.replace('fa-sun', 'fa-moon');
    }
  } catch (e) {
    // ignore storage errors
  }

  toggle.addEventListener('click', () => {
    const isDark = html.classList.toggle('dark');
    try { localStorage.setItem('theme', isDark ? 'dark' : 'light'); } catch (e) {}
    if (isDark) icon.classList.replace('fa-moon', 'fa-sun');
    else icon.classList.replace('fa-sun', 'fa-moon');
  });
})();