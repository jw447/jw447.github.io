/* Browser drafts and forms. Repository writes require the local editor service. */
(async () => {
  'use strict';
  const M = window.HPDiEditorModel;
  const $ = id => document.getElementById(id);
  const storageKey = 'hpdi-content-editor-v2';
  const text = (tag, value, className) => { const node = document.createElement(tag); node.textContent = value; if (className) node.className = className; return node; };
  const button = (label, action, className) => { const node = text('button', label, className); node.type = 'button'; node.addEventListener('click', action); return node; };
  let seed, schema, draft, baseline, local = null, section, index = 0, busy = false, crossTab = false, exactPreview = false;
  function notice(message) { $('notice').textContent = message; $('notice').hidden = !message; }
  function showErrors(errors) { $('errors').replaceChildren(); $('errors').hidden = !errors.length; if (errors.length) { const list = document.createElement('ul'); errors.slice(0, 12).forEach(error => list.append(text('li', error))); $('errors').append(list); } }
  function report(error) { notice(error.message || String(error)); }
  function check() { const errors = M.validate(draft.content, schema, baseline); showErrors(errors); return !errors.length; }
  function updateStatus() {
    const names = M.changed(draft.content, baseline);
    $('draft-count').textContent = names.length ? `${names.length} content ${names.length === 1 ? 'file' : 'files'} changed` : 'No changes';
    $('save-status').textContent = names.length ? 'Draft saved in this browser' : 'Current content';
    if (crossTab) $('save-status').textContent = 'Another tab changed this draft';
    if (local?.push_status) renderGitHubStatus();
  }
  function persist() {
    updateStatus();
    if (crossTab) return;
    try { localStorage.setItem(storageKey, JSON.stringify({...draft, saved_at: new Date().toISOString()})); }
    catch { $('save-status').textContent = 'Draft is in memory only'; notice('Browser storage is unavailable. Download your updates before closing this page.'); }
  }
  function changed() {
    persist(); showErrors([]);
    if (exactPreview) $('preview-caption').textContent = 'Draft changed — click Preview to rebuild';
    updateRecordLabels();
  }
  function records() { return M.get(draft.content, section.path); }
  function selected() { return section.list ? records()[index] : records(); }
  function recordTitle(record) { return record.title || record.name || record.text || 'New entry'; }
  function updateRecordLabels() {
    if (!section.list) return;
    const query = $('record-search').value.toLowerCase();
    $('record-list').replaceChildren();
    records().forEach((record, i) => {
      if (!JSON.stringify(record).toLowerCase().includes(query)) return;
      const node = button('', () => { index = i; renderForm(); updateRecordLabels(); });
      node.setAttribute('aria-current', String(i === index));
      node.append(text('strong', recordTitle(record)));
      node.append(text('small', record.date || (record.short ? `${record.short} · ${record.year}` : record.context || record.group || record.terms || '')));
      $('record-list').append(node);
    });
    if (!$('record-list').children.length) $('record-list').append(text('p', records().length ? 'No matching entries.' : 'No entries yet. Add your first one.', 'empty'));
  }
  function renderFields(container, record, definitions) {
    for (const field of definitions) {
      const target = field.store ? draft.content[field.store] : record;
      const getValue = () => target[field.key];
      const setValue = value => { target[field.key] = value; changed(); };
      if (field.type === 'pdf') {
        const label = text('label', '', 'field');
        label.append(text('span', field.label), text('span', getValue() || 'No CV uploaded', 'field-hint'));
        const upload = document.createElement('input'); upload.type = 'file'; upload.accept = '.pdf,application/pdf'; upload.disabled = !local;
        label.append(upload, text('span', local ? 'Choose a PDF (up to 10 MB). Save or Publish to apply it.' : 'Open the local editor to upload your CV.', 'field-hint'));
        upload.addEventListener('change', async () => {
          const file = upload.files[0]; if (!file) return;
          if (file.size > 10 * 1024 * 1024) { notice('CV must be at most 10 MB.'); return; }
          try {
            const encoded = await new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(',')[1]); reader.onerror = reject; reader.readAsDataURL(file); });
            const response = await fetch('/api/upload-cv', {method:'POST', headers:{'Content-Type':'application/json','X-Editor-Token':local.token}, body:JSON.stringify({base_revision:draft.base_revision, data:encoded})});
            const result = await response.json(); if (!response.ok) throw new Error(result.error);
            setValue(result.path); notice('CV uploaded locally. Save or Publish to update the website.'); renderForm();
          } catch(error) { report(error); }
        });
        container.append(label); continue;
      }
      if (field.type === 'records') {
        const group = text('div', '', 'nested-field'); const heading = text('div', '', 'nested-heading');
        heading.append(text('span', field.label));
        heading.append(button('+ Add', () => { target[field.key] ||= []; target[field.key].push(M.newRecord({key:field.key, fields:field.fields})); changed(); renderForm(); }));
        group.append(heading);
        (getValue() || []).forEach((child, i) => { const item = text('div', '', 'nested-record'); renderFields(item, child, field.fields); item.append(button('Remove entry', () => { target[field.key].splice(i, 1); changed(); renderForm(); }, 'nested-remove')); group.append(item); });
        container.append(group); continue;
      }
      const label = text('label', '', field.type === 'checkbox' ? 'field field-check' : 'field');
      const value = getValue(); let input;
      if (field.type === 'select') {
        input = document.createElement('select'); field.choices.forEach((choice, i) => { const option = text('option', field.labels?.[i] || choice); option.value = choice; input.append(option); }); input.value = value || '';
      } else if (['textarea', 'lines', 'paragraphs'].includes(field.type)) {
        input = document.createElement('textarea'); input.rows = field.type === 'paragraphs' ? 7 : field.type === 'lines' ? 3 : 4;
        input.value = Array.isArray(value) ? value.join(field.type === 'paragraphs' ? '\n\n' : '\n') : value || '';
      } else {
        input = document.createElement('input'); input.type = ['checkbox', 'number', 'month', 'email', 'url'].includes(field.type) ? field.type : 'text';
        if (field.type === 'checkbox') input.checked = !!value; else input.value = value ?? '';
        if (field.type === 'number') { input.min = 1900; input.max = 2100; input.step = 1; }
      }
      input.required = !!field.required;
      input.addEventListener(field.type === 'checkbox' || field.type === 'select' ? 'change' : 'input', () => {
        let value = field.type === 'checkbox' ? input.checked : field.type === 'number' ? (input.value === '' ? '' : Number(input.value)) : input.value;
        if (field.type === 'lines') value = value.split('\n').map(x => x.trim()).filter(Boolean);
        if (field.type === 'paragraphs') value = value.split(/\n\s*\n/).map(x => x.trim()).filter(Boolean);
        setValue(value);
      });
      if (field.type === 'checkbox') label.append(input, text('span', field.label)); else label.append(text('span', field.label + (field.required ? ' *' : '')), input);
      if (field.type === 'paragraphs') label.append(text('span', 'Separate paragraphs with a blank line.', 'field-hint'));
      container.append(label);
    }
  }
  function renderForm() {
    const record = selected(); $('content-form').replaceChildren(); $('student-authors').replaceChildren();
    $('student-authors').hidden = section.key !== 'publications';
    $('record-actions').hidden = !section.list || !record;
    $('form-title').textContent = section.label;
    $('form-note').textContent = section.key === 'people' ? 'Profiles stay off the lab page until you choose “Show this profile”.' : section.key === 'publications' ? "Labels are generated as [venue'year]. Record keys remain stable automatically." : '';
    if (record) renderFields($('content-form'), record, section.fields);
    else $('content-form').append(text('p', 'Add an entry to start editing.', 'empty'));
    if (section.key === 'publications') renderFields($('student-authors'), draft.content.site, [{key:'student_authors',label:'Underlined student authors — one name per line',type:'lines'}]);
    if (section.key === 'publications' && record) {
      const fetchBib = button('Fetch publisher BibTeX', async () => {
        fetchBib.disabled = true;
        try {
          const response = await fetch('/api/bibtex', {method:'POST', headers:{'Content-Type':'application/json','X-Editor-Token':local.token}, body:JSON.stringify({paper:record})});
          const result = await response.json(); if (!response.ok) throw new Error(result.error);
          record.doi = result.doi; record.bibtex = result.bibtex; record.citation_source = result.source; changed(); renderForm();
          notice('Publisher citation loaded. Review the BibTeX before saving.');
        } catch(error) { report(error); } finally { fetchBib.disabled = false; }
      });
      fetchBib.disabled = !local;
      $('content-form').append(fetchBib, text('p', 'Lookup uses publisher DOI metadata. You can also paste a BibTeX export from Google Scholar, IEEE or ACM.', 'field-hint'));
    }
    $('move-up').disabled = index <= 0; $('move-down').disabled = !section.list || index >= records().length - 1;
  }
  function choose(key) {
    section = schema.find(x => x.key === key); index = 0; $('record-search').value = '';
    for (const node of $('sections').children) node.setAttribute('aria-current', String(node.dataset.section === key));
    $('records-panel').hidden = !section.list; $('edit-panel').style.gridTemplateColumns = section.list ? '' : '1fr';
    $('records-title').textContent = `${section.label} (${section.list ? records().length : 1})`;
    $('section-description').textContent = `Manage ${section.label.toLowerCase()}, then preview your changes.`;
    $('preview-page').value = ['projects', 'people', 'lab', 'sponsors'].includes(key) ? 'lab.html' : 'index.html';
    $('edit-panel').hidden = false; $('preview-panel').hidden = true;
    renderForm(); updateRecordLabels();
  }
  async function api(action) {
    const response = await fetch(`/api/${action}`, {method:'POST', headers:{'Content-Type':'application/json','X-Editor-Token':local.token}, body:JSON.stringify(draft)});
    const result = await response.json();
    if (!response.ok) { if (action === 'publish') showPushStatus(result.push_status || {state:'unconfirmed', confirmed:false, message:result.error + ' Please retry Publish when the issue is resolved.'}); if (result.bundle) adopt(result.bundle); if (result.errors) showErrors(result.errors); throw new Error(result.error || 'The operation did not complete.'); }
    if (result.push_status) showPushStatus(result.push_status);
    return result;
  }
  let checkingGitHub = false;
  function showPushStatus(status) {
    local.push_status = status; renderGitHubStatus();
  }
  function renderGitHubStatus() {
    const status = local.push_status;
    const unpublishedDraft = draft && M.changed(draft.content, baseline).length;
    $('github-status').textContent = status.message + (unpublishedDraft ? ' Browser draft changes have not been published.' : '') + (status.checked_at ? ' Checked ' + new Date(status.checked_at).toLocaleTimeString() + '.' : '');
    $('github-status-panel').dataset.state = unpublishedDraft && status.state === 'synced' ? 'draft' : status.state;
  }
  async function checkGitHub() {
    if (!local || busy || checkingGitHub) return;
    checkingGitHub = true; $('check-github').disabled = true;
    try {
      const response = await fetch('/api/push-status', {method:'POST', headers:{'Content-Type':'application/json','X-Editor-Token':local.token}, body:'{}'});
      const status = await response.json(); if (!response.ok) throw new Error(status.error);
      showPushStatus(status);
    } catch(error) { showPushStatus({state:'unconfirmed', confirmed:false, message:'Cannot confirm the GitHub push. Check the connection, then retry Check GitHub or Publish.'}); }
    finally { checkingGitHub = false; $('check-github').disabled = false; }
  }
  function adopt(value) { seed = M.clone(value); baseline = M.clone(value.content); draft = M.clone(value); persist(); }
  async function operation(action, fn) {
    if (busy || crossTab) return;
    if (checkingGitHub) { notice('GitHub status is being checked. Try this action when the check finishes.'); return; }
    busy = true;
    for (const id of ['preview-button','save-button','confirm-publish']) $(id).disabled = true;
    $('save-status').textContent = action;
    try { await fn(); } catch(error) { if (action.startsWith('Publishing')) showPushStatus({state:'unconfirmed', confirmed:false, message:'Push was not confirmed. ' + (error.message || 'Check your connection.') + ' Retry Publish when ready.'}); report(error); }
    finally { busy = false; updateStatus(); for (const id of ['preview-button','save-button','confirm-publish']) $(id).disabled = false; }
  }
  function download() {
    const blob = new Blob([JSON.stringify(draft, null, 2)+'\n'], {type:'application/json'}); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'HPDi-content-updates.json'; anchor.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  try {
    [seed, schema] = await Promise.all(['editor-data.json','editor-schema.json'].map(async file => { const response = await fetch(file); if (!response.ok) throw new Error('Content could not be loaded. Please reload the editor.'); return response.json(); }));
    try { const response = await fetch('/api/status'); if (response.ok) { const status = await response.json(); if (status.mode === 'local') { local = status; seed = status.bundle; } } } catch { /* Hosted editor supports browser drafts without a local service. */ }
    baseline = M.clone(seed.content); draft = M.clone(seed);
    function upgradeDraft(value) { if(value?.schema_version===1&&value.content)value.content.design=M.clone(seed.content.design);return value; }
    try { const saved = upgradeDraft(JSON.parse(localStorage.getItem(storageKey))); if (saved?.schema_version === 1 && !M.validate(saved.content,schema,baseline).length) { draft = saved; if (saved.base_revision !== seed.base_revision) notice('A saved draft is based on older content. Download it before loading current content; publishing will protect newer changes.'); } } catch { /* Start from the published content if there is no readable draft. */ }
    if (local) { $('save-button').hidden = false; $('mode-note').textContent = 'Save writes checked content on this computer. Publish commits and pushes local-design; merge into main to deploy.'; }
    for (const item of schema.filter(item => item.key !== 'design')) { const node = button(item.label,()=>choose(item.key)); node.dataset.section = item.key; $('sections').append(node); }
    choose('profile'); updateStatus();
    if (local) { $('github-status-panel').hidden = false; $('check-github').addEventListener('click', checkGitHub); checkGitHub(); setInterval(() => { if (!document.hidden) checkGitHub(); }, 60000); }
    $('content-form').addEventListener('submit',event=>event.preventDefault());
    $('record-search').addEventListener('input',updateRecordLabels);
    $('add-button').addEventListener('click',()=>{ records().unshift(M.newRecord(section)); index=0; changed(); renderForm(); updateRecordLabels(); });
    $('delete-button').addEventListener('click',()=>{ if (!confirm(`Remove “${recordTitle(selected())}” from this draft?`)) return; records().splice(index,1); index=Math.max(0,Math.min(index,records().length-1)); changed(); renderForm(); });
    function move(delta) { const array=records(), destination=index+delta; if(destination<0||destination>=array.length)return; [array[index],array[destination]]=[array[destination],array[index]];index=destination;changed();renderForm(); }
    $('move-up').addEventListener('click',()=>move(-1)); $('move-down').addEventListener('click',()=>move(1));
    $('download-button').addEventListener('click',download);
    $('import-button').addEventListener('click',()=>$('import-file').click());
    $('import-file').addEventListener('change',async event=>{ const file=event.target.files[0]; if(!file)return; try { if(file.size>1000000)throw new Error('This file is too large.'); const value=upgradeDraft(JSON.parse(await file.text())); if(value.schema_version!==1||!value.base_revision)throw new Error('Choose an exported editor draft.'); const errors=M.validate(value.content,schema,baseline); if(errors.length){showErrors(errors);return;} if(M.changed(draft.content,baseline).length&&!confirm('Replace the current browser draft with this imported draft? Download current updates first if you need them.'))return; draft=value;persist();choose(section.key);notice(value.base_revision===seed.base_revision?'Draft imported. Preview your changes before publishing.':'Draft imported from older content. Publishing will require the current source revision.'); } catch(error){report(error);} finally{event.target.value='';} });
    $('reset-button').addEventListener('click',async()=>{ if(!confirm('Load current content and replace this browser draft? Download your updates first if you need them.'))return; try{ if(local){const response=await fetch('/api/status');const status=await response.json();if(!response.ok)throw new Error('Current content could not be loaded.');local=status;seed=status.bundle;}crossTab=false;adopt(seed);choose(section.key);notice('Current content loaded.');}catch(error){report(error);} });
    async function preview() { if(!check())return; if(!local){notice('Exact draft previews require the local editor. Run python3 edit.py, then import this draft. View current site shows the published page.');return;} await operation('Generating preview…',async()=>{ $('edit-panel').hidden=true;$('preview-panel').hidden=false;if(local){const result=await api('preview');exactPreview=true;$('preview-frame').removeAttribute('srcdoc');$('preview-frame').src=result.preview_url.replace('index.html',$('preview-page').value)+`?draft=${Date.now()}`;$('preview-caption').textContent='Draft preview · current website design';} }); }
    $('preview-button').addEventListener('click',preview);$('preview-page').addEventListener('change',preview);$('back-button').addEventListener('click',()=>{$('edit-panel').hidden=false;$('preview-panel').hidden=true;});
    $('save-button').addEventListener('click',()=>{if(check())operation('Saving and checking…',async()=>{const result=await api('save');adopt(result.bundle);notice('Content saved on this computer. Publish when you are ready to update GitHub.'); showPushStatus({state:'saved', confirmed:false, message:'Saved changes have not been pushed. Click Publish when ready.'});});});
    $('publish-button').addEventListener('click',()=>{
      if(!check())return; const container=$('publish-content');container.replaceChildren();$('confirm-publish').hidden=true;
      if(local?.publishing.ready){const names=M.changed(draft.content,baseline);container.append(text('p',names.length?'This will save and validate your changes, create a commit summarizing the changes, and push local-design to GitHub. Merge into main to deploy.':'No draft changes. Publish can retry a previously saved commit.'));const list=document.createElement('ul');names.forEach(name=>list.append(text('li',name)));container.append(list);container.append(text('p',local.publishing.repository,'publish-reason'));$('confirm-publish').hidden=false;}
      else {container.append(text('p','This hosted editor supports forms, browser drafts, previews, and downloading updates. Publishing is not connected here yet.'));container.append(text('p',local?local.publishing.reason:'To save and publish from your own computer, run the included local editor in the GitHub website checkout.','publish-reason'));container.append(text('pre','python3 edit.py'));container.append(text('p','Open http://127.0.0.1:8765/admin/, import this draft, then use Save files or Publish. GitHub publishing becomes available once this codebase is installed in the website repository.'));container.append(button('Download this draft',download));}
      $('publish-dialog').showModal();
    });
    $('confirm-publish').addEventListener('click',()=>operation('Publishing to GitHub…',async()=>{const result=await api('publish');adopt(result.bundle);$('publish-dialog').close();notice(result.message); }));
    $('close-dialog').addEventListener('click',()=>$('publish-dialog').close());$('cancel-publish').addEventListener('click',()=>$('publish-dialog').close());
    window.addEventListener('storage',event=>{if(event.key===storageKey){crossTab=true;notice('Another tab changed this draft. Download this tab’s updates before reloading; edits here will not overwrite the other tab.');updateStatus();}});
    function syncPreviewTheme() { try { const root=$('preview-frame').contentDocument?.documentElement;if(root)root.dataset.theme=document.documentElement.dataset.theme || 'light'; } catch { /* A preview link may have navigated away. */ } }
    $('preview-frame').addEventListener('load',syncPreviewTheme);
    new MutationObserver(()=>{if(!$('preview-panel').hidden){if(exactPreview)syncPreviewTheme();}}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    window.addEventListener('beforeunload',event=>{if($('save-status').textContent==='Draft is in memory only' || (local?.push_status && ['unpushed','saved','unconfirmed','diverged'].includes(local.push_status.state))){event.preventDefault();event.returnValue='';}});
  } catch(error) { report(error);$('save-status').textContent='Editor could not start';for(const node of document.querySelectorAll('.toolbar button'))node.disabled=true; }
})();
