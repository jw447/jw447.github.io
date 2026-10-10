// Apply the remembered theme before styles paint; default to the device setting.
(() => {
  const key = 'hpdil-theme';
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const readPreference = () => {
    try {
      const value = localStorage.getItem(key);
      return value === 'dark' || value === 'light' ? value : null;
    } catch { return null; }
  };
  let preference = readPreference();
  const apply = theme => {
    root.dataset.theme = theme;
    document.querySelectorAll('.theme-toggle').forEach(button => {
      const dark = theme === 'dark';
      button.textContent = dark ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      button.setAttribute('aria-pressed', String(dark));
      button.hidden = false;
    });
    const chrome = document.querySelector('meta[name="theme-color"]');
    if (chrome) {
      const tone = getComputedStyle(root).getPropertyValue(theme === 'dark' ? '--paper' : '--accent').trim();
      if (tone) chrome.content = tone;
    }
  };
  const current = () => preference || (system.matches ? 'dark' : 'light');
  apply(current());
  document.addEventListener('DOMContentLoaded', () => {
    apply(current());
    document.querySelectorAll('.theme-toggle').forEach(button => {
      button.addEventListener('click', () => {
        preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem(key, preference); } catch { /* Still works for this page. */ }
        apply(preference);
      });
    });
  });
  system.addEventListener('change', () => { if (!preference) apply(current()); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      preference = readPreference();
      apply(current());
    }
  });
})();
