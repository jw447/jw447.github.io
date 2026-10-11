/* Browser drafts and forms. Repository writes require the local editor service. */
(async () => {
  'use strict';
  const M = window.HPDiEditorModel;
  const $ = id => document.getElementById(id);
  const storageKey = 'hpdi-content-editor-v1';
  const text = (tag, value, className) => { const node = document.createElement(tag); node.textContent = value; if (className) node.className = className; return node; };
  const button = (label, action, className) => { const node = text('button', label, className); node.type = 'button'; node.addEventListener('click', action); return node; };
  let seed, schema, draft, baseline, designDefaults, designEditor, local = null, section, index = 0, busy = false, crossTab = false, exactPreview = false;
  function notice(message) { $('notice').textContent = message; $('notice').hidden = !message; }
  function showErrors(errors) { $('errors').replaceChildren(); $('errors').hidden = !errors.length; if (errors.length) { const list = document.createElement('ul'); errors.slice(0, 12).forEach(error => list.append(text('li', error))); $('errors').append(list); } }
  function report(error) { notice(error.message || String(error)); }
  function check() { const errors = M.validate(draft.content, schema, baseline); showErrors(errors); return !errors.length; }
  function updateStatus() {
    const names = M.changed(draft.content, baseline);
    $('draft-count').textContent = names.length ? `${names.length} content ${names.length === 1 ? 'file' : 'files'} changed` : 'No changes';
    $('save-status').textContent = names.length ? 'Draft saved in this browser' : 'Current content';
    if (crossTab) $('save-status').textContent = 'Another tab changed this draft';
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
    else if (!$('preview-panel').hidden) renderPreview();
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
      const getValue = () => field.type === 'compact' ? draft.content.compact.projects[record.id] || '' : target[field.key];
      const setValue = value => { if (field.type === 'compact') draft.content.compact.projects[record.id] = value; else target[field.key] = value; changed(); };
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
      } else if (['textarea', 'lines', 'paragraphs', 'compact'].includes(field.type)) {
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
      if (field.type === 'compact') label.append(text('span', 'Leave blank to use the full project description.', 'field-hint'));
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
    $('move-up').disabled = index <= 0; $('move-down').disabled = !section.list || index >= records().length - 1;
  }
  function choose(key) {
    section = schema.find(x => x.key === key); index = 0; $('record-search').value = '';
    for (const node of $('sections').children) node.setAttribute('aria-current', String(node.dataset.section === key));
    $('records-panel').hidden = !section.list; $('edit-panel').style.gridTemplateColumns = section.list ? '' : '1fr';
    $('records-title').textContent = `${section.label} (${section.list ? records().length : 1})`;
    $('section-description').textContent = `Manage ${section.label.toLowerCase()}, then preview your changes.`;
    $('preview-page').value = ['projects', 'people', 'lab', 'sponsors'].includes(key) ? 'lab.html' : 'index.html';
    $('design-panel').hidden = key !== 'design';
    $('edit-panel').hidden = key === 'design'; $('preview-panel').hidden = true;
    if (key === 'design') { $('section-description').textContent = 'Tune the design, preview every layout, and save a preset.'; designEditor.show(); }
    else { renderForm(); updateRecordLabels(); }
  }
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const asset = name => new URL(`../assets/${name}`, location.href).href;
  const link = (label, url) => `<a href="${esc(M.validURL(url) && url ? url : '#')}">${esc(label)}</a>`;
  function renderPreview() {
    const d = draft.content, p = d.profile; let body;
    const paragraphs = items => (items || []).map(item => `<p>${esc(item)}</p>`).join('');
    if ($('preview-page').value === 'lab.html') {
      body = `<section class="lab-hero"><h1>${esc(p.lab)}</h1><p class="lab-full-name">${esc(p.lab_name)}</p><p class="lede">${esc(d.lab.mission)}</p></section><section id="research"><h2>Research</h2><div class="research-list">${d.lab.research.map(r => `<div class="thrust"><div><h3>${esc(r.title)}</h3><p>${esc(r.description)}</p></div></div>`).join('')}</div></section><section id="projects"><h2>Projects</h2>${d.projects.map(project => `<div class="thrust"><div><h3>${esc(project.name)}</h3><p class="project-context">${esc(project.context)}</p><p>${esc(d.compact.projects[project.id] || project.description)}</p><p class="links">${(project.links || []).map(x => link(x.label,x.url)).join(' ')}</p></div></div>`).join('')}</section><section id="people"><h2>People</h2><p><strong>${esc(p.name)}</strong><br>Principal Investigator · ${esc(p.role)}</p>${d.people.filter(person => person.approved).map(person => `<h3>${esc(person.name)}</h3><p>${esc(person.role)}<br>${esc(person.topic)}</p>`).join('') || '<h3>Students</h3><p class="placeholder">Student profiles will be added here.</p>'}</section><section id="join"><h2>Join the lab</h2><p>${esc(d.lab.recruiting)}</p></section><section id="sponsors"><h2>Sponsors</h2><div class="sponsor-grid">${d.lab.sponsors.map(sponsor => `<article class="sponsor-card">${['logos/nsf.png','logos/doe.png','logos/charlotte.png'].includes(sponsor.logo) ? `<div class="sponsor-logo-panel"><img src="${esc(asset(sponsor.logo))}" alt="${esc(sponsor.name)} logo"></div>` : ''}<h3>${link(sponsor.label || sponsor.name,sponsor.url)}</h3><ul>${(sponsor.programs || []).map(program => `<li>${link(program.title,program.url)} <span class="sponsor-year">${esc(program.year)}</span></li>`).join('')}</ul></article>`).join('')}</div></section>`;
    } else {
      const news = [...d.news].sort((a,b) => b.date.localeCompare(a.date));
      const papers = [...d.publications].sort((a,b) => b.year-a.year);
      const authors = value => value.split(', ').map(name => { let result = esc(name); if (name === p.name) result = `<span class="me">${result}</span>`; if (d.site.student_authors.includes(name)) result = `<span class="lab">${result}</span>`; return result; }).join(', ');
      body = `<section class="compact-intro"><h1>${esc(p.name)} <span class="chinese-name" lang="zh-Hans">${esc(p.name_chinese)}</span></h1><p class="compact-role">${esc(p.role)}</p><div class="intro-columns"><div>${paragraphs(d.compact.bio)}<div class="resource-buttons">${link('Google Scholar',p.scholar)}${link('Curriculum vitae',p.cv)}</div><div class="contact-chips"><span>${esc(p.email)}</span><span>${esc(p.office)}</span></div><p class="recruit">${esc(d.lab.recruiting)}</p></div><img class="portrait" src="${esc(asset('jinzhen-wang.jpg'))}" alt="${esc(p.name)}"></div></section><section><h2>News</h2><div class="news-scroll" tabindex="0"><ul class="news">${news.map(n => `<li><time>${esc(n.date)}</time><div>${n.url ? link(n.text,n.url) : esc(n.text)}</div></li>`).join('')}</ul></div></section><section><h2>Publications</h2><p class="author-legend">Bold: ${esc(p.name)}. Underlined: lab student authors.</p>${[...new Set(papers.map(p=>p.year))].map(year => `<h3 class="year">${year}</h3><ul class="pubs">${papers.filter(p=>p.year===year).map(paper => `<li class="pub"><span class="venue">${esc(M.label(paper))}</span><div class="pub-body"><p class="pub-title">${esc(paper.title)}</p><p class="pub-authors">${authors(paper.authors)}</p><p class="pub-where"><em>${esc(paper.venue)}</em>, ${year}</p><p class="pub-links">${(paper.links || []).map(x=>link(x.label,x.url)).join(' ')}</p>${paper.note ? `<p class="pub-note">${esc(paper.note)}</p>` : ''}</div></li>`).join('')}</ul>`).join('')}</section><section><h2>Teaching</h2><ul class="courses">${d.teaching.map(t=>`<li><span class="course-code">${esc(t.code)}</span><div><p class="course-name">${esc(t.title)}</p><p class="course-meta">${esc(t.institution)}, ${esc(t.terms)}</p></div></li>`).join('')}</ul></section>`;
    }
    const theme = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
    const designCSS=window.HPDiDesignModel.css(d.design,schema.find(x=>x.key==='design').groups);
    $('preview-frame').srcdoc = `<!doctype html><html lang="en" data-theme="${theme}" data-portrait="${esc(d.design.layout.portrait_position)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">${['colors.css','simple.css','sponsors.css','compact.css','design.css'].map(name => `<link rel="stylesheet" href="${esc(asset(name))}">`).join('')}<style>${designCSS}</style></head><body><main class="wrap">${body}</main></body></html>`;
  }
  async function api(action) {
    const response = await fetch(`/api/${action}`, {method:'POST', headers:{'Content-Type':'application/json','X-Editor-Token':local.token}, body:JSON.stringify(draft)});
    const result = await response.json();
    if (!response.ok) { if (result.bundle) adopt(result.bundle); if (result.errors) showErrors(result.errors); throw new Error(result.error || 'The operation did not complete.'); }
    return result;
  }
  function adopt(value) { seed = M.clone(value); baseline = M.clone(value.content); draft = M.clone(value); persist(); if(section?.key==='design')designEditor?.refresh(); }
  async function operation(action, fn) {
    if (busy || crossTab) return; busy = true;
    for (const id of ['preview-button','save-button','confirm-publish']) $(id).disabled = true;
    $('save-status').textContent = action;
    try { await fn(); } catch(error) { report(error); }
    finally { busy = false; updateStatus(); for (const id of ['preview-button','save-button','confirm-publish']) $(id).disabled = false; }
  }
  function download() {
    const blob = new Blob([JSON.stringify(draft, null, 2)+'\n'], {type:'application/json'}); const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'HPDi-content-updates.json'; anchor.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  try {
    [seed, schema, designDefaults] = await Promise.all(['editor-data.json','editor-schema.json','design-defaults.json'].map(async file => { const response = await fetch(file); if (!response.ok) throw new Error('Content could not be loaded. Please reload the editor.'); return response.json(); }));
    try { const response = await fetch('/api/status'); if (response.ok) { const status = await response.json(); if (status.mode === 'local') { local = status; seed = status.bundle; } } } catch { /* Hosted editor supports browser drafts without a local service. */ }
    baseline = M.clone(seed.content); draft = M.clone(seed);
    function upgradeDraft(value) { if(value?.schema_version===1&&value.content&&!('design' in value.content))value.content.design=M.clone(seed.content.design);return value; }
    try { const saved = upgradeDraft(JSON.parse(localStorage.getItem(storageKey))); if (saved?.schema_version === 1 && !M.validate(saved.content,schema,baseline).length) { draft = saved; if (saved.base_revision !== seed.base_revision) notice('A saved draft is based on older content. Download it before loading current content; publishing will protect newer changes.'); } } catch { /* Start from the published content if there is no readable draft. */ }
    designEditor=window.HPDiDesignEditor({groups:schema.find(x=>x.key==='design').groups,defaults:designDefaults,get:()=>draft.content.design,set:value=>{draft.content.design=value;},changed,errors:showErrors,notice});
    if (local) { $('save-button').hidden = false; $('mode-note').textContent = 'Save writes checked content on this computer. Publish pushes the main branch to GitHub.'; }
    for (const item of schema) { const node = button(item.label,()=>choose(item.key)); node.dataset.section = item.key; $('sections').append(node); }
    choose(new URLSearchParams(location.search).get('tab')==='design'?'design':'profile'); updateStatus();
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
    async function preview() { if(!check())return; if(section.key==='design'){designEditor.enlarge();return;} await operation('Generating preview…',async()=>{ $('edit-panel').hidden=true;$('preview-panel').hidden=false;if(local){const result=await api('preview');exactPreview=true;$('preview-frame').removeAttribute('srcdoc');$('preview-frame').src=result.preview_url.replace('index.html',$('preview-page').value)+`?draft=${Date.now()}`;$('preview-caption').textContent='Built preview · compact layout';}else{exactPreview=false;renderPreview();$('preview-caption').textContent='Draft preview · compact layout';} }); }
    $('preview-button').addEventListener('click',preview);$('preview-page').addEventListener('change',preview);$('back-button').addEventListener('click',()=>{$('edit-panel').hidden=false;$('preview-panel').hidden=true;});
    $('save-button').addEventListener('click',()=>{if(check())operation('Saving and checking…',async()=>{const result=await api('save');adopt(result.bundle);notice('Content saved on this computer. Publish when you are ready to update GitHub.');});});
    $('publish-button').addEventListener('click',()=>{
      if(!check())return; const container=$('publish-content');container.replaceChildren();$('confirm-publish').hidden=true;
      if(local?.publishing.ready){const names=M.changed(draft.content,baseline);container.append(text('p',names.length?'This will save and validate your changes, create a content commit, and push the main branch to GitHub.':'No draft changes. Publish can retry a previously saved commit.'));const list=document.createElement('ul');names.forEach(name=>list.append(text('li',name)));container.append(list);container.append(text('p',local.publishing.repository,'publish-reason'));$('confirm-publish').hidden=false;}
      else {container.append(text('p','This hosted editor supports forms, browser drafts, previews, and downloading updates. Publishing is not connected here yet.'));container.append(text('p',local?local.publishing.reason:'To save and publish from your own computer, run the included local editor in the GitHub website checkout.','publish-reason'));container.append(text('pre','python3 scripts/editor_server.py'));container.append(text('p','Open http://127.0.0.1:8765/admin/, import this draft, then use Save files or Publish. GitHub publishing becomes available once this codebase is installed in the website repository.'));container.append(button('Download this draft',download));}
      $('publish-dialog').showModal();
    });
    $('confirm-publish').addEventListener('click',()=>operation('Publishing to GitHub…',async()=>{const result=await api('publish');adopt(result.bundle);$('publish-dialog').close();notice(result.message); }));
    $('close-dialog').addEventListener('click',()=>$('publish-dialog').close());$('cancel-publish').addEventListener('click',()=>$('publish-dialog').close());
    window.addEventListener('storage',event=>{if(event.key===storageKey){crossTab=true;notice('Another tab changed this draft. Download this tab’s updates before reloading; edits here will not overwrite the other tab.');updateStatus();}});
    function syncPreviewTheme() { try { const root=$('preview-frame').contentDocument?.documentElement;if(root)root.dataset.theme=document.documentElement.dataset.theme || 'light'; } catch { /* A preview link may have navigated away. */ } }
    $('preview-frame').addEventListener('load',syncPreviewTheme);
    new MutationObserver(()=>{if(!$('preview-panel').hidden){if(exactPreview)syncPreviewTheme();else renderPreview();}}).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
    window.addEventListener('beforeunload',event=>{if($('save-status').textContent==='Draft is in memory only'){event.preventDefault();event.returnValue='';}});
  } catch(error) { report(error);$('save-status').textContent='Editor could not start';for(const node of document.querySelectorAll('.toolbar button'))node.disabled=true; }
})();
