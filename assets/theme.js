(() => {
  try {
    const saved = localStorage.getItem('yiming-theme');
    if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
  } catch (_) { /* Theme remains usable without storage. */ }
})();
