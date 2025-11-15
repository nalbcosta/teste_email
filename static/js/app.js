// Tailwind + UI logic
(function(){
  const form = document.getElementById('emailForm');
  const resultWrapper = document.getElementById('resultWrapper');
  const classificationBadge = document.getElementById('classificationBadge');
  const suggestedResponse = document.getElementById('suggestedResponse');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const historyList = document.getElementById('historyList');
  const emptyHistory = document.getElementById('emptyHistory');
  const charCount = document.getElementById('charCount');
  const resetBtn = document.getElementById('resetBtn');
  const formError = document.getElementById('formError');
  const toggleTheme = document.getElementById('toggleTheme');
  const yearEl = document.getElementById('year');
  yearEl.textContent = new Date().getFullYear();

  let history = [];

  function updateCharCount(){
    const txt = document.getElementById('text_input').value || '';
    charCount.textContent = txt.length + ' caracteres';
  }

  document.getElementById('text_input').addEventListener('input', updateCharCount);

  function setLoading(state){
    loadingOverlay.classList.toggle('hidden', !state);
  }

  function showError(msg){
    formError.textContent = msg;
    formError.classList.remove('hidden');
  }
  function clearError(){
    formError.classList.add('hidden');
    formError.textContent = '';
  }

  function addToHistory(item){
    history.unshift(item); // newest first
    if(history.length > 10) history.pop();
    renderHistory();
  }

  function renderHistory(){
    historyList.innerHTML = '';
    if(history.length === 0){
      emptyHistory.classList.remove('hidden');
      return;
    }
    emptyHistory.classList.add('hidden');
    history.forEach((h, idx)=>{
      const li = document.createElement('li');
      const badgeColor = h.classification === 'Produtivo' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-700 dark:text-emerald-100' : 'bg-orange-100 text-orange-700 dark:bg-orange-700 dark:text-orange-100';
      const countLabel = h.count > 1 ? ` (${h.count} emails)` : '';
      li.className = 'p-3 rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex flex-col gap-1';
      li.innerHTML = `
        <div class="flex justify-between items-center">
          <span class="text-xs font-medium px-2 py-1 rounded ${badgeColor}">${h.classification}${countLabel}</span>
          <span class="text-[10px] text-gray-400">#${history.length - idx}</span>
        </div>
        <p class="text-xs line-clamp-3">${h.rawSnippet}</p>
      `;
      historyList.appendChild(li);
    });
  }

  function applyTheme(theme){
    if(theme === 'dark'){
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('pref-theme', theme);
  }

  // Initialize theme
  const savedTheme = localStorage.getItem('pref-theme');
  if(savedTheme){ applyTheme(savedTheme); }
  toggleTheme.addEventListener('click', ()=>{
    const isDark = document.documentElement.classList.contains('dark');
    applyTheme(isDark ? 'light' : 'dark');
  });

  resetBtn.addEventListener('click', ()=>{
    classificationBadge.className = 'hidden';
    classificationBadge.innerHTML = '';
    suggestedResponse.innerHTML = '<em>Sem resultados ainda. Envie um email para análise.</em>';
    clearError();
    updateCharCount();
  });

  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    clearError();
    const fd = new FormData();
    const file = document.getElementById('file').files[0];
    const txt = document.getElementById('text_input').value.trim();
    if(!file && !txt){
      showError('Forneça arquivo ou texto.');
      return;
    }
    if(file) fd.append('file', file);
    if(txt) fd.append('text_input', txt);
    setLoading(true);
    suggestedResponse.innerHTML = '<em>Aguardando resposta...</em>';
    classificationBadge.className = 'hidden';
    classificationBadge.innerHTML = '';
    try{
      const r = await fetch('/process', { method: 'POST', body: fd });
      const data = await r.json();
      
      if(data.error){
        showError(data.error);
        suggestedResponse.innerHTML = '<em>Falha ao processar.</em>';
        return;
      }
      
      // Verificar se é múltiplo ou único
      if(data.is_multiple && data.items){
        renderMultipleResults(data);
      } else {
        renderSingleResult(data);
      }
      
      // history
      addToHistory({
        classification: data.classification,
        rawSnippet: (txt || (file ? file.name : '')).slice(0,160) + '…',
        count: data.items ? data.items.length : 1
      });
    }catch(err){
      showError('Erro de rede ou servidor: ' + err.message);
      suggestedResponse.innerHTML = '<em>Erro ao obter resposta.</em>';
    }finally{
      setLoading(false);
    }
  });

  function renderSingleResult(data){
    const isProd = data.classification === 'Produtivo';
    const badgeBase = 'inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-full shadow';
    const badgeColor = isProd ? 'bg-emerald-600 text-white dark:bg-emerald-500' : 'bg-orange-600 text-white dark:bg-orange-500';
    classificationBadge.className = badgeBase + ' ' + badgeColor;
    classificationBadge.innerHTML = isProd ? 'Produtivo' : 'Improdutivo';
    suggestedResponse.innerHTML = `<div class="space-y-2"><h3 class="text-sm font-semibold">Resposta sugerida</h3><pre class="whitespace-pre-wrap text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded-md border border-gray-200 dark:border-gray-700">${data.suggested_response}</pre></div>`;
  }

  function renderMultipleResults(data){
    const isProd = data.classification === 'Produtivo';
    const badgeBase = 'inline-flex items-center gap-1 text-xs font-medium px-3 py-1.5 rounded-full shadow';
    const badgeColor = isProd ? 'bg-emerald-600 text-white dark:bg-emerald-500' : 'bg-orange-600 text-white dark:bg-orange-500';
    classificationBadge.className = badgeBase + ' ' + badgeColor;
    classificationBadge.innerHTML = `${data.classification} (${data.items.length} emails)`;
    
    let html = '<div class="space-y-3">';
    data.items.forEach((item) => {
      const itemBadge = item.classification === 'Produtivo' 
        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-700 dark:text-emerald-100'
        : 'bg-orange-100 text-orange-700 dark:bg-orange-700 dark:text-orange-100';
      html += `
        <details class="border border-gray-200 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900">
          <summary class="cursor-pointer p-3 hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between">
            <span class="text-sm font-medium">Email ${item.id}</span>
            <span class="text-xs px-2 py-1 rounded ${itemBadge}">${item.classification}</span>
          </summary>
          <div class="p-3 border-t border-gray-200 dark:border-gray-700">
            <h4 class="text-xs font-semibold mb-2">Resposta sugerida:</h4>
            <pre class="whitespace-pre-wrap text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded border border-gray-200 dark:border-gray-700">${item.suggested_response}</pre>
          </div>
        </details>
      `;
    });
    html += '</div>';
    suggestedResponse.innerHTML = html;
  }

  // initial
  updateCharCount();
})();
