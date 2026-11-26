const $ = (selector) => document.querySelector(selector);
const state = { data: null, view: 'overview', city: 'all', period: '12m', search: '' };
const moneyFull = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 2 });
const number = new Intl.NumberFormat('pt-BR');
const compact = (value) => {
  const sign = value < 0 ? '−' : '';
  const n = Math.abs(value);
  if (n >= 1e6) return `${sign}R$ ${(n / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mi`;
  if (n >= 1e3) return `${sign}R$ ${(n / 1e3).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mil`;
  return `${sign}${moneyFull.format(n)}`;
};
const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const sum = (items, key) => items.reduce((total, item) => total + Number(item[key] || 0), 0);
const monthLabel = (month) => {
  const [year, m] = month.split('-').map(Number);
  return new Date(year, m - 1, 1).toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' }).replace('.', '');
};

function selectedMonths() {
  const all = [...new Set(state.data.transactions.map((row) => row.mes))].sort();
  if (state.period === '12m') return all.slice(-12);
  if (state.period === 'all') return all;
  return all.filter((month) => month.startsWith(state.period));
}
function filteredTransactions() {
  const months = new Set(selectedMonths());
  return state.data.transactions.filter((row) => months.has(row.mes) && (state.city === 'all' || row.cidade === state.city));
}
function filteredClients() {
  return state.data.clients.filter((row) => state.city === 'all' || row.cidade === state.city);
}
function citySummary(transactions, clients) {
  const cities = [...new Set(clients.map((row) => row.cidade))];
  return cities.map((city) => {
    const rows = transactions.filter((row) => row.cidade === city);
    const income = sum(rows.filter((row) => row.tipo === 'Crédito'), 'valor');
    const expense = sum(rows.filter((row) => row.tipo === 'Débito'), 'valor');
    return { city, clients: clients.filter((row) => row.cidade === city).length, income, expense, net: income - expense };
  }).sort((a, b) => b.net - a.net);
}
function renderTrend(transactions, months) {
  const series = months.map((month) => {
    const rows = transactions.filter((row) => row.mes === month);
    return { month, income: sum(rows.filter((row) => row.tipo === 'Crédito'), 'valor'), expense: sum(rows.filter((row) => row.tipo === 'Débito'), 'valor') };
  });
  const W = 760, H = 258, left = 56, right = 12, top = 16, bottom = 36;
  const cw = W - left - right, ch = H - top - bottom;
  const maximum = Math.max(1, ...series.flatMap((p) => [p.income, p.expense])) * 1.12;
  const x = (i) => left + (series.length <= 1 ? cw / 2 : (i / (series.length - 1)) * cw);
  const y = (v) => top + ch - (v / maximum) * ch;
  const points = (key) => series.map((p, i) => `${x(i).toFixed(1)},${y(p[key]).toFixed(1)}`).join(' ');
  const lines = [0, .25, .5, .75, 1].map((fraction) => {
    const yy = top + ch - ch * fraction;
    return `<line class="chart-grid" x1="${left}" y1="${yy}" x2="${W-right}" y2="${yy}"/><text class="chart-label" x="${left-9}" y="${yy+4}" text-anchor="end">${compact(maximum*fraction).replace('R$ ', '')}</text>`;
  }).join('');
  const labelEvery = Math.max(1, Math.ceil(series.length / 6));
  const labels = series.map((p, i) => (i % labelEvery === 0 || i === series.length-1) ? `<text class="chart-label" x="${x(i)}" y="${H-9}" text-anchor="middle">${monthLabel(p.month)}</text>` : '').join('');
  const dot = (key, color) => series.length ? `<circle cx="${x(series.length-1)}" cy="${y(series.at(-1)[key])}" r="5" fill="${color}" stroke="white" stroke-width="2"/>` : '';
  $('#trend-chart').innerHTML = `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">${lines}${labels}<polyline class="chart-line" points="${points('income')}" stroke="#a77aff"/><polyline class="chart-line" points="${points('expense')}" stroke="#df9aff"/>${dot('income','#a77aff')}${dot('expense','#df9aff')}</svg>`;
  $('#trend-chart').setAttribute('aria-label', `Entradas e saídas mensais de ${monthLabel(months[0])} a ${monthLabel(months.at(-1))}`);
}
function renderCategories(transactions) {
  const totals = new Map();
  transactions.filter((row) => row.tipo === 'Débito').forEach((row) => totals.set(row.categoria, (totals.get(row.categoria) || 0) + Number(row.valor)));
  const entries = [...totals.entries()].sort((a, b) => b[1] - a[1]);
  const max = entries[0]?.[1] || 1;
  $('#category-chart').innerHTML = entries.map(([category, value]) => `<div class="category-row"><div class="category-row-top"><strong>${escapeHtml(category)}</strong><span>${compact(value)}</span></div><div class="category-track"><div class="category-fill" style="width:${(value/max*100).toFixed(1)}%"></div></div></div>`).join('');
  return entries;
}
function renderHealth(clients) {
  const values = ['Excelente', 'Boa', 'Atenção'].map((name) => ({ name, count: clients.filter((row) => row.saude === name).length }));
  const colors = ['#986af0', '#c093ff', '#e0b2ff'];
  const total = clients.length || 1;
  let from = 0;
  const stops = values.map((item, i) => { const to = from + item.count / total * 100; const segment = `${colors[i]} ${from}% ${to}%`; from = to; return segment; });
  $('#health-donut').style.background = `conic-gradient(${stops.join(',')})`;
  $('#health-total').textContent = number.format(clients.length);
  $('#health-legend').innerHTML = values.map((item, i) => `<div class="health-legend-row"><i style="background:${colors[i]}"></i><span>${item.name}</span><strong>${Math.round(item.count/total*100)}%</strong></div>`).join('');
  $('#health-donut').setAttribute('aria-label', values.map((item) => `${item.name}: ${item.count}`).join(', '));
}
function renderOverview() {
  const tx = filteredTransactions(), clients = filteredClients(), months = selectedMonths();
  const income = sum(tx.filter((row) => row.tipo === 'Crédito'), 'valor');
  const expense = sum(tx.filter((row) => row.tipo === 'Débito'), 'valor');
  const count = sum(tx, 'quantidade');
  $('#period-caption').textContent = `${monthLabel(months[0])} – ${monthLabel(months.at(-1))}`;
  $('#kpi-income').textContent = compact(income);
  $('#kpi-income').title = moneyFull.format(income);
  $('#kpi-expense').textContent = compact(expense);
  $('#kpi-expense').title = moneyFull.format(expense);
  $('#kpi-net').textContent = compact(income - expense);
  $('#kpi-net').title = moneyFull.format(income - expense);
  $('#kpi-count').textContent = number.format(count);
  renderTrend(tx, months);
  const categories = renderCategories(tx);
  renderHealth(clients);
  const cities = citySummary(tx, clients);
  $('#cities-body').innerHTML = cities.map((row) => `<tr><td>${escapeHtml(row.city)}</td><td>${number.format(row.clients)}</td><td>${compact(row.net)}</td></tr>`).join('');
  $('#insight-title').textContent = categories.length ? `${categories[0][0]} lidera as despesas` : 'Sem despesas no período';
  $('#insight-text').textContent = categories.length ? `A categoria representa ${Math.round(categories[0][1] / expense * 100)}% das saídas da seleção. O resultado acumulado é ${moneyFull.format(income-expense)}.` : 'Ajuste os filtros para explorar a carteira.';
  $('#base-clients').textContent = number.format(state.data.meta.clients);
  $('#base-accounts').textContent = number.format(state.data.meta.accounts);
  $('#base-loans').textContent = number.format(state.data.meta.loans);
}
function renderClients() {
  const clients = filteredClients();
  const loans = state.data.loans.filter((row) => state.city === 'all' || row.cidade === state.city);
  $('#client-count').textContent = number.format(clients.length);
  $('#client-income').textContent = compact(sum(clients,'renda_mensal') / Math.max(clients.length,1));
  $('#client-debt').textContent = compact(sum(clients,'saldo_devedor'));
  $('#client-high-risk').textContent = number.format(clients.filter((row) => row.risco === 'Alto').length);
  const risks = [['Baixo','#a77aff'],['Moderado','#bd8eff'],['Alto','#df9aff']];
  $('#risk-bars').innerHTML = risks.map(([risk,color]) => { const n=clients.filter((row)=>row.risco===risk).length; return `<div class="risk-row"><span>${risk}</span><div class="bar-track"><div class="bar-fill" style="width:${(n/Math.max(clients.length,1)*100).toFixed(1)}%;background:${color}"></div></div><strong>${n}</strong></div>`; }).join('');
  const statuses = [['Ativo','#a77aff'],['Quitado','#c2a0eb'],['Atrasado','#df9aff']];
  $('#loan-status').innerHTML = statuses.map(([status,color]) => { const n=sum(loans.filter((row)=>row.status===status),'quantidade'); return `<div class="loan-row"><span>${status}</span><div class="bar-track"><div class="bar-fill" style="width:${(n/Math.max(sum(loans,'quantidade'),1)*100).toFixed(1)}%;background:${color}"></div></div><strong>${n}</strong></div>`; }).join('');
  renderClientTable(clients);
}
function renderClientTable(clients = filteredClients()) {
  const query = state.search.trim().toLocaleLowerCase('pt-BR');
  const riskOrder = { Alto: 0, Moderado: 1, Baixo: 2 };
  const shown = clients.filter((row) => !query || `${row.nome} ${row.cidade}`.toLocaleLowerCase('pt-BR').includes(query)).sort((a,b) => riskOrder[a.risco]-riskOrder[b.risco] || b.saldo_devedor-a.saldo_devedor);
  $('#clients-body').innerHTML = shown.slice(0,50).map((row) => `<tr><td>${escapeHtml(row.nome)}</td><td>${escapeHtml(row.cidade)}</td><td>${compact(row.renda_mensal)}</td><td>${compact(row.saldo_total)}</td><td>${compact(row.saldo_devedor)}</td><td><span class="badge ${row.risco==='Alto'?'high':row.risco==='Moderado'?'medium':'low'}">${row.risco}</span></td></tr>`).join('') || '<tr><td colspan="6">Nenhum cliente encontrado.</td></tr>';
  $('#client-table-count').textContent = `${number.format(Math.min(shown.length,50))} de ${number.format(shown.length)} clientes exibidos`;
}
function update() { if (!state.data) return; renderOverview(); renderClients(); }
function setView(view) {
  state.view = view;
  const labels = { overview: ['Visão geral', 'Uma leitura clara do comportamento financeiro da carteira.'], clients: ['Clientes', 'Explore perfis, endividamento e classificações de risco.'], method: ['Metodologia', 'Entenda a origem e os limites dos indicadores.'] };
  $('.view:not(.hidden)')?.classList.add('hidden');
  $(`#${view === 'method' ? 'method' : view === 'clients' ? 'clients' : 'overview'}-view`).classList.remove('hidden');
  document.querySelectorAll('.nav-link').forEach((button) => { const active=button.dataset.view===view; button.classList.toggle('active',active); if(active) button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current'); });
  $('#page-title').textContent = labels[view][0];
  $('#page-subtitle').textContent = labels[view][1];
  $('#breadcrumb-view').textContent = labels[view][0].toLocaleUpperCase('pt-BR');
  $('#filter-bar').classList.toggle('hidden', view === 'method');
  $('#export-button').classList.toggle('hidden', view === 'method');
  window.location.hash = view === 'overview' ? 'visao-geral' : view === 'clients' ? 'clientes' : 'metodologia';
}
function exportCsv() {
  const tx = filteredTransactions(), clients = filteredClients(), cities = citySummary(tx,clients);
  const rows = [['Cidade','Clientes','Entradas','Saídas','Resultado'], ...cities.map((row)=>[row.city,row.clients,row.income.toFixed(2),row.expense.toFixed(2),row.net.toFixed(2)])];
  const csv = '\ufeff' + rows.map((row)=>row.map((cell)=>`"${String(cell).replaceAll('"','""')}"`).join(';')).join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const link=document.createElement('a');link.href=url;link.download=`indicadores-financeiros-${state.period}-${state.city === 'all'?'todas':state.city.toLocaleLowerCase('pt-BR').replaceAll(' ','-')}.csv`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  $('#status-message').textContent='Resumo CSV exportado.';
}
async function init() {
  try {
    const response=await fetch('data/dashboard.json');
    if (!response.ok) throw new Error(`Falha ao carregar os dados: ${response.status}`);
    state.data=await response.json();
    const cities=[...new Set(state.data.clients.map((row)=>row.cidade))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    $('#city-filter').insertAdjacentHTML('beforeend',cities.map((city)=>`<option value="${escapeHtml(city)}">${escapeHtml(city)}</option>`).join(''));
    $('#period-filter').addEventListener('change',(event)=>{state.period=event.target.value;update();});
    $('#city-filter').addEventListener('change',(event)=>{state.city=event.target.value;update();});
    $('#reset-filters').addEventListener('click',()=>{state.period='12m';state.city='all';$('#period-filter').value=state.period;$('#city-filter').value=state.city;update();});
    $('#client-search').addEventListener('input',(event)=>{state.search=event.target.value;renderClientTable();});
    $('#export-button').addEventListener('click',exportCsv);
    document.querySelectorAll('.nav-link').forEach((button)=>button.addEventListener('click',()=>setView(button.dataset.view)));
    update();
    const hash=window.location.hash;
    setView(hash==='#clientes'?'clients':hash==='#metodologia'?'method':'overview');
  } catch(error) {
    $('#status-message').classList.remove('sr-only');
    $('#status-message').style.cssText='display:block;margin:20px;padding:20px;background:#422544;color:#f2b7dd;border-radius:8px';
    $('#status-message').textContent=`Não foi possível carregar o dashboard. ${error.message}`;
  }
}
init();
