(() => {
  const root = document.querySelector('#visitors');
  if (!root) return;
  const zh = document.documentElement.lang === 'zh-CN';
  const t = (en, cn) => zh ? cn : en;
  const number = value => new Intl.NumberFormat(zh ? 'zh-CN' : 'en').format(value);
  const names = new Intl.DisplayNames([zh ? 'zh-CN' : 'en'], { type: 'region' });
  const monthSelect = root.querySelector('#visitor-month');
  const map = root.querySelector('#visitor-map');
  const detail = root.querySelector('#visitor-region-detail');
  const status = root.querySelector('#visitor-status');
  const list = root.querySelector('#visitor-regions');
  const liveUrl = 'https://raw.githubusercontent.com/YimingYang23/YimingYang23.github.io/visitor-stats/visitor-stats.json';
  const ns = 'http://www.w3.org/2000/svg';
  let data, world, selected;
  function svg(tag, attrs) {
    const el = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    return el;
  }
  async function json(url) {
    const response = await fetch(url, { signal: AbortSignal.timeout(12000), cache: 'no-cache' });
    if (!response.ok) throw new Error('Statistics unavailable');
    return response.json();
  }
  function showRegion(code) {
    const counts = data.months[monthSelect.value].countries;
    selected = code;
    detail.textContent = `${names.of(code)} · ${number(counts[code] || 0)} ${t('visits this month', '次当月访问')}`;
    map.querySelectorAll('[data-region]').forEach(el => {
      el.classList.toggle('is-selected', el.dataset.region === code);
      el.setAttribute('aria-pressed', String(el.dataset.region === code));
    });
  }
  function render() {
    const monthly = data.months[monthSelect.value];
    const counts = monthly.countries;
    const entries = Object.entries(counts).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]);
    root.querySelector('#visitor-total').textContent = number(data.totals.pageviews);
    root.querySelector('#visitor-month-total').textContent = number(monthly.visitors);
    root.querySelector('#visitor-country-total').textContent = number(entries.length);
    map.replaceChildren();
    const max = Math.max(1, ...entries.map(([, n]) => n));
    const palette = ['#dcebe2', '#b1d1bd', '#79ac90', '#437d5d', '#24593f'];
    for (const region of world.countries) {
      const count = counts[region.code] || 0;
      const color = count ? palette[Math.min(4, Math.floor(Math.log1p(count) / Math.log1p(max) * 4))] : '#e9ede8';
      const attrs = { fill: color, class: 'visitor-land', 'data-region': region.code, role: 'button',
        tabindex: count ? '0' : '-1', 'aria-pressed': 'false',
        'aria-label': `${names.of(region.code)}: ${number(count)} ${t('visits', '次访问')}` };
      const el = region.d ? svg('path', { ...attrs, d: region.d }) : svg('circle', { ...attrs, cx: region.center[0], cy: region.center[1], r: 3 });
      const title = svg('title', {}); title.textContent = attrs['aria-label']; el.append(title);
      el.addEventListener('mouseenter', () => showRegion(region.code));
      el.addEventListener('focus', () => showRegion(region.code));
      el.addEventListener('click', () => showRegion(region.code));
      el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); showRegion(region.code); } });
      map.append(el);
    }
    list.replaceChildren();
    for (const [code, count] of entries) {
      const row = document.createElement('li');
      const button = document.createElement('button'); button.type = 'button';
      const name = document.createElement('span'); name.textContent = names.of(code);
      const value = document.createElement('strong'); value.textContent = number(count);
      button.append(name, value); button.addEventListener('click', () => showRegion(code));
      row.append(button); list.append(row);
    }
    if (entries.length) showRegion(counts[selected] ? selected : entries[0][0]);
    else detail.textContent = t('No visits recorded in this month.', '本月暂无访问记录。');
  }
  async function init() {
    try {
      [world, data] = await Promise.all([
        json('assets/visitor-world.json'),
        json(liveUrl).catch(() => json('assets/visitor-stats.json'))
      ]);
      if (data.version !== 1 || !data.months || !data.totals) throw new Error('Invalid statistics');
      const months = Object.keys(data.months).filter(m => data.months[m].complete).sort().reverse();
      if (!months.length) throw new Error('Month not yet available');
      monthSelect.replaceChildren();
      for (const month of months) {
        const option = document.createElement('option'); option.value = month;
        option.textContent = zh ? `${month.slice(0,4)} 年 ${Number(month.slice(5))} 月` : new Date(month + '-01T12:00:00Z').toLocaleDateString('en', { year: 'numeric', month: 'long', timeZone: 'UTC' });
        monthSelect.append(option);
      }
      map.setAttribute('viewBox', world.viewBox);
      monthSelect.disabled = false;
      monthSelect.addEventListener('change', render);
      render();
      const updated = new Date(data.updated_at);
      const stale = Date.now() - updated.getTime() > 3 * 60 * 60 * 1000;
      const currentUTC = new Date().toISOString().slice(0,7);
      status.textContent = `${t('Updated', '更新于')} ${updated.toLocaleString(zh ? 'zh-CN' : 'en', { dateStyle: 'short', timeStyle: 'short' })}${stale || data.current_month !== currentUTC ? t(' · Refresh delayed; showing the last successful snapshot.', ' · 同步延迟，当前显示最近一次成功统计。') : ''}`;
      root.querySelector('.visitor-map-content').hidden = false;
    } catch (_) {
      status.textContent = t('Statistics are temporarily unavailable. You can still open the source statistics below.', '统计暂时无法加载，可通过下方链接查看原始统计。');
    }
  }
  init();
})();
