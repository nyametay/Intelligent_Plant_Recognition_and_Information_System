document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('togglePassword');
  const password = document.getElementById('password');
  if (toggle && password) {
    toggle.addEventListener('click', () => {
      const type = password.type === 'password' ? 'text' : 'password';
      password.type = type;
      toggle.classList.toggle('fa-eye');
      toggle.classList.toggle('fa-eye-slash');
    });
  }
});
