const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

// Load saved theme or system preference
const userPref = localStorage.getItem('theme');
    if (
    userPref === 'dark' ||
    (!userPref && window.matchMedia('(prefers-color-scheme: dark)').matches)
    ) {
    html.classList.add('dark');
    } else {
    html.classList.remove('dark');
}

// Handle toggle click
themeToggle.addEventListener('click', () => {
    html.classList.toggle('dark');
    const isDark = html.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});
