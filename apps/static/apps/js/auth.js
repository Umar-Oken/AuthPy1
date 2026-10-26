document.querySelectorAll('[data-toggle-password]').forEach(button => {
  button.addEventListener('click', () => {
    const input = document.getElementById(button.dataset.togglePassword);
    const visible = input.type === 'text';
    input.type = visible ? 'password' : 'text';
    button.textContent = visible ? 'Ko‘rish' : 'Yashirish';
  });
});

const password = document.querySelector('[data-password]');
if (password) {
  const bar = document.querySelector('.strength span');
  const items = document.querySelectorAll('[data-rule]');
  password.addEventListener('input', () => {
    const value = password.value;
    const rules = {length: value.length >= 8, upper: /[A-Z]/.test(value), number: /\d/.test(value), symbol: /[^A-Za-z0-9]/.test(value)};
    let score = 0;
    items.forEach(item => {
      const ok = rules[item.dataset.rule];
      item.classList.toggle('ok', ok);
      item.textContent = (ok ? '✓ ' : '○ ') + item.dataset.label;
      if (ok) score++;
    });
    bar.style.width = `${score * 25}%`;
    bar.style.background = score < 2 ? '#dc2626' : score < 4 ? '#d97706' : '#15803d';
  });
}

document.querySelectorAll('[data-theme]').forEach(button => button.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem('auth-theme', document.body.classList.contains('dark') ? 'dark' : 'light');
}));
if (localStorage.getItem('auth-theme') === 'dark') document.body.classList.add('dark');

function showMessage(text, type = 'success') {
  const area = document.querySelector('[data-message-area]');
  if (!area) return;
  area.hidden = false;
  area.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
}

document.querySelectorAll('[data-message-form]').forEach(form => form.addEventListener('submit', event => {
  event.preventDefault();
  showMessage(form.dataset.messageForm);
}));
document.querySelectorAll('[data-demo-message]').forEach(button => button.addEventListener('click', () => showMessage(button.dataset.demoMessage, 'info')));

document.querySelectorAll('[data-revoke]').forEach(button => button.addEventListener('click', () => button.closest('[data-other-session]').remove()));
const removeOthers = document.querySelector('[data-remove-other-sessions]');
if (removeOthers) removeOthers.addEventListener('click', () => document.querySelectorAll('[data-other-session]').forEach(row => row.remove()));
