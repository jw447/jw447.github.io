// Explicit review links select a Chinese name style without saving the design.
(() => {
  const style = new URLSearchParams(location.search).get('chinese-font');
  if (!['kai', 'xingkai', 'cursive'].includes(style)) return;
  document.documentElement.dataset.chineseFont = style;
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href]').forEach(link => {
      const raw = link.getAttribute('href');
      if (raw.startsWith('#') || link.closest('.name-font-sample')) return;
      const url = new URL(raw, location.href);
      if (url.origin !== location.origin || !url.pathname.endsWith('.html') || url.searchParams.has('chinese-font')) return;
      url.searchParams.set('chinese-font', style);
      link.setAttribute('href', url.pathname + url.search + url.hash);
    });
  });
})();
