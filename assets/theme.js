(() => {
  let theme = 'light';
  try {
    const saved = localStorage.getItem('yiming-theme-v2');
    if (saved === 'light' || saved === 'dark') theme = saved;
  } catch (_) {}
  document.documentElement.dataset.theme = theme;
})();
