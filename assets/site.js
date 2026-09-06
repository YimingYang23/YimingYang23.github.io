(() => {
  const zh = document.documentElement.lang === 'zh-CN';
  const t = (en, cn) => zh ? cn : en;
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
    document.querySelector('#result-count').textContent = zh ? `${count} 篇论文` : `${count} ${count === 1 ? 'paper' : 'papers'}`;
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
      toast.textContent = t('Citation copied', '引用已复制');
    } catch (_) {
      toast.textContent = t('Please select the citation text or download the .bib file.', '请选中引用文本复制，或下载 .bib 文件。');
    }
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
  });
  const demoData = JSON.parse(document.querySelector('#demo-data').textContent);
  const tabs = [...document.querySelectorAll('.demo-tabs [role="tab"]')];
  const panels = [...document.querySelectorAll('.demo-panel')];
  function selectTab(tab) {
    tabs.forEach(item => {
      const active = item === tab;
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
      const panel = document.getElementById(item.getAttribute('aria-controls'));
      panel.hidden = !active;
      if (!active) panel.querySelector('video').pause();
    });
  }
  tabs.forEach((tab,index) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'ArrowLeft') next = tabs[(index + tabs.length - 1) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) { event.preventDefault(); selectTab(next); next.focus(); }
    });
  });
  panels.forEach(panel => {
    const video = panel.querySelector('video');
    const buttons = [...panel.querySelectorAll('[data-scene]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      const index = Number(button.dataset.scene);
      const item = demoData[panel.dataset.project][index];
      video.pause();
      video.poster = item.poster;
      video.querySelector('source').src = item.src;
      video.load();
      video.play().catch(() => {});
      panel.querySelector('.open-video').href = item.src;
      const label = zh ? item.label.replace('Scene', '场景') : item.label;
      panel.querySelector('.scene-status').textContent = `${label} · ${index + 1} / ${buttons.length}`;
      buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    }));
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) panels.forEach(panel => panel.querySelector('video').pause());
  });
  document.querySelectorAll('.language-switch a').forEach(link => link.addEventListener('click', () => {
    link.href = link.pathname + location.hash;
  }));
})();
