(() => {
  const value = document.querySelector('#visitor-count');
  if (!value) return;
  const zh = document.documentElement.lang === 'zh-CN';
  async function read(url) {
    const response = await fetch(url, { cache: 'no-cache', signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new Error('Counter unavailable');
    const data = await response.json();
    if (!Number.isSafeInteger(data.totals?.visitors) || data.totals.visitors < 0) throw new Error('Invalid counter');
    return data;
  }
  const url = 'https://raw.githubusercontent.com/YimingYang23/YimingYang23.github.io/visitor-stats/visitor-stats.json';
  read(url).catch(() => read('assets/visitor-stats.json')).then(data => {
    value.textContent = new Intl.NumberFormat(zh ? 'zh-CN' : 'en').format(data.totals.visitors);
    const date = new Date(data.updated_at);
    if (!Number.isNaN(date.getTime())) value.title = (zh ? '统计更新于 ' : 'Updated ') + date.toLocaleString(zh ? 'zh-CN' : 'en');
  }).catch(() => {
    value.textContent = '—';
    value.title = zh ? '统计暂时无法加载' : 'Statistics temporarily unavailable';
  });
})();
