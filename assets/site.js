(() => {
  const toggle = document.querySelector('.theme-toggle');
  const updateLabel = () => toggle.setAttribute('aria-label', `Switch to ${document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'} theme`);
  updateLabel();
  toggle.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem('yiming-theme', theme); } catch (_) {}
    updateLabel();
  });
  document.querySelector('.publication-tools').hidden = false;
  const papers = [...document.querySelectorAll('.paper')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const search = document.querySelector('#paper-search');
  let topic = 'All';
  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    papers.forEach(paper => {
      const match = (topic === 'All' || paper.dataset.topic === topic) && paper.textContent.toLocaleLowerCase().includes(query);
      paper.hidden = !match;
      if (match) count++;
    });
    document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'publication / preprint' : 'publications & preprints'}`;
    document.querySelector('#empty-results').hidden = count !== 0;
  }
  filters.forEach(button => button.addEventListener('click', () => {
    topic = button.dataset.filter;
    filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    filter();
  }));
  search.addEventListener('input', filter);
  const copy = document.querySelector('#copy-citation');
  let toastTimer;
  copy.addEventListener('click', async () => {
    const toast = document.querySelector('#toast');
    try {
      await navigator.clipboard.writeText(document.querySelector('#copo-bib').textContent);
      toast.textContent = 'Citation copied';
    } catch (_) {
      toast.textContent = 'Please select the citation text or download the .bib file.';
    }
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
  });
})();
