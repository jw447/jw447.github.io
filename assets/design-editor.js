/* Design controls and actual-page previews, using the static build's CSS. */
window.HPDiDesignEditor = function(options) {
  const $=id=>document.getElementById(id),D=window.HPDiDesignModel,M=window.HPDiEditorModel;
  const groups=options.groups,defaults=options.defaults,presetKey='hpdi-design-presets-v1';
  let saved=[],sequence=0,lastValid=M.clone(options.get());const pages=new Map();
  const node=(tag,value)=>{const el=document.createElement(tag);if(value!=null)el.textContent=value;return el;};
  try{const value=JSON.parse(localStorage.getItem(presetKey));if(Array.isArray(value))saved=value.filter(x=>typeof x.name==='string'&&x.name.length<=60&&!D.validate(x.design,groups).length).slice(0,30);}catch{}
  const compact=M.clone(defaults);compact.typography.line_height=1.5;Object.assign(compact.spacing,{paragraph_gap:10,section_gap:28,publication_gap:12});
  const comfortable=M.clone(defaults);Object.assign(comfortable.typography,{body_size:18,line_height:1.7});Object.assign(comfortable.spacing,{paragraph_gap:16,section_gap:40,publication_gap:22});
  const builtin=[{name:'Charlotte defaults',design:defaults},{name:'Compact reading',design:compact},{name:'Comfortable reading',design:comfortable}];
  function refreshPresets(){
    const selected=$('design-preset').value;$('design-preset').replaceChildren();
    for(const [type,list] of [['builtin',builtin],['saved',saved]])list.forEach((preset,i)=>{const el=node('option',preset.name+(type==='saved'?' · saved':''));el.value=`${type}-${i}`;$('design-preset').append(el);});
    if([...$('design-preset').options].some(x=>x.value===selected))$('design-preset').value=selected;
    $('delete-preset').disabled=!$('design-preset').value.startsWith('saved-');
  }
  function persistPresets(){try{localStorage.setItem(presetKey,JSON.stringify(saved));return true;}catch{options.notice('Preset storage is unavailable. Download updates to keep the current design.');return false;}}
  function drawFields(){
    $('design-fields').replaceChildren();
    for(const group of groups){
      const fieldset=node('fieldset');fieldset.append(node('legend',group.label));
      for(const field of group.fields){
        const label=node(field.type==='select'?'label':'div');label.className='field';label.append(node('span',field.label));const value=options.get()[group.key][field.key];
        const change=value=>{options.get()[group.key][field.key]=value;options.changed();apply();};
        if(field.type==='select'){
          const select=node('select');field.choices.forEach((choice,i)=>{const item=node('option',field.labels[i]);item.value=choice;select.append(item);});select.value=value;select.addEventListener('change',()=>change(select.value));label.append(select);
        }else if(field.type==='range'){
          const row=node('span');row.className='range-row';const slider=node('input'),number=node('input');slider.type='range';number.type='number';
          for(const input of [slider,number]){Object.assign(input,{min:field.min,max:field.max,step:field.step,value});input.setAttribute('aria-label',field.label+(input===number?' value':''));}
          slider.addEventListener('input',()=>{number.value=slider.value;change(Number(slider.value));});number.addEventListener('input',()=>{if(number.value!=='')slider.value=number.value;change(number.value===''?null:Number(number.value));});row.append(slider,number,node('span',field.unit));label.append(row);
        }else{
          const row=node('span');row.className='color-row';const swatch=node('input'),hex=node('input');Object.assign(swatch,{type:'color',value});Object.assign(hex,{type:'text',value,maxLength:7});swatch.setAttribute('aria-label',field.label);hex.setAttribute('aria-label',field.label+' hex value');
          swatch.addEventListener('input',()=>{hex.value=swatch.value.toUpperCase();change(hex.value);});hex.addEventListener('input',()=>{if(/^#[0-9a-f]{6}$/i.test(hex.value))swatch.value=hex.value;change(hex.value);});row.append(swatch,hex);label.append(row);
        }
        fieldset.append(label);
      }
      $('design-fields').append(fieldset);
    }
  }
  function scale(){const stage=$('design-frame').parentElement,width=Number($('design-viewport').value),factor=Math.min(1,stage.clientWidth/width);Object.assign($('design-frame').style,{width:`${width}px`,height:'820px',transform:`scale(${factor})`});stage.style.height=`${820*factor}px`;}
  function apply(){
    const errors=D.validate(options.get(),groups);options.errors(errors);if(!errors.length)lastValid=M.clone(options.get());
    $('design-preview-status').textContent=errors.length?'Adjust the highlighted settings. Preview keeps the last valid design.':'Live design preview · current site content · drafts stay in this browser';
    const document=$('design-frame').contentDocument;
    if(document?.getElementById('draft-design')){
      document.getElementById('draft-design').textContent=D.css(lastValid,groups);document.documentElement.dataset.portrait=lastValid.layout.portrait_position;document.documentElement.dataset.theme=$('design-theme').value;
      document.documentElement.classList.add('js');
      document.querySelectorAll('.theme-toggle').forEach(button=>{button.hidden=false;const dark=$('design-theme').value==='dark',label=dark?'Switch to light mode':'Switch to dark mode';button.setAttribute('aria-label',label);button.setAttribute('title',label);button.setAttribute('aria-pressed',String(dark));});
      document.querySelectorAll('.paper-tools').forEach(panel=>{panel.hidden=false;});
    }
    scale();
  }
  async function loadPage(){
    const request=++sequence,layout=$('design-layout').value,page=$('design-page').value,base=new URL(layout==='classic'?`../${page}`:`../${layout}/${page}`,location.href);$('design-preview-status').textContent='Loading page preview…';
    try{
      if(!pages.has(base.href))pages.set(base.href,fetch(base.href,{cache:'no-cache'}).then(async r=>{if(!r.ok)throw new Error('The page preview could not be loaded.');return r.text();}));
      const html=await pages.get(base.href);if(request!==sequence)return;const document=new DOMParser().parseFromString(html,'text/html');
      document.querySelectorAll('script,iframe,object,embed,base').forEach(el=>el.remove());
      for(const el of document.querySelectorAll('[href],[src]'))for(const attr of ['href','src'])if(el.hasAttribute(attr))el.setAttribute(attr,new URL(el.getAttribute(attr),base).href);
      document.documentElement.dataset.theme=$('design-theme').value;document.documentElement.dataset.portrait=lastValid.layout.portrait_position;
      const style=document.createElement('style');style.id='draft-design';style.textContent=D.css(lastValid,groups);document.head.append(style);$('design-frame').srcdoc='<!doctype html>'+document.documentElement.outerHTML;apply();
    }catch(error){pages.delete(base.href);if(request===sequence){$('design-preview-status').textContent=error.message;options.notice(error.message);}}
  }
  function replace(design,message){options.set(M.clone(design));options.changed();drawFields();apply();options.notice(message);}
  $('apply-preset').addEventListener('click',()=>{const [type,id]=$('design-preset').value.split('-'),preset=(type==='builtin'?builtin:saved)[Number(id)];if(preset)replace(preset.design,`Applied “${preset.name}” to this draft.`);});
  $('save-preset').addEventListener('click',()=>{
    const errors=D.validate(options.get(),groups);if(errors.length){options.errors(errors);return;}const name=$('preset-name').value.trim();if(!name){options.notice('Give your preset a name first.');$('preset-name').focus();return;}
    const existing=saved.findIndex(x=>x.name===name),preset={name,design:M.clone(options.get())};if(existing>=0)saved[existing]=preset;else if(saved.length<30)saved.push(preset);else{options.notice('You have 30 saved presets. Delete one before saving another.');return;}
    if(persistPresets()){refreshPresets();$('design-preset').value=`saved-${existing>=0?existing:saved.length-1}`;$('delete-preset').disabled=false;options.notice(`Preset “${name}” saved in this browser.`);}
  });
  $('design-preset').addEventListener('change',()=>{$('delete-preset').disabled=!$('design-preset').value.startsWith('saved-');});
  $('delete-preset').addEventListener('click',()=>{if(!$('design-preset').value.startsWith('saved-'))return;const index=Number($('design-preset').value.slice(6));if(!confirm(`Delete saved preset “${saved[index].name}”? The current design stays in your draft.`))return;saved.splice(index,1);persistPresets();refreshPresets();});
  $('export-design-xml').addEventListener('click',()=>{try{const xml=window.HPDiDesignXML.stringify(options.get(),groups),url=URL.createObjectURL(new Blob([xml],{type:'application/xml;charset=utf-8'})),anchor=node('a');anchor.href=url;anchor.download='HPDi-design.xml';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);options.notice('Design XML exported. Your content is unchanged.');}catch(error){options.errors([error.message]);}});
  $('import-design-xml').addEventListener('click',()=>$('design-xml-file').click());
  $('design-xml-file').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>window.HPDiDesignXML.MAX_BYTES)throw new Error('Choose a design XML file smaller than 64 KiB.');const design=window.HPDiDesignXML.parse(await file.text(),groups);replace(design,'Design XML imported into this draft. Preview it, then save locally.');}catch(error){options.errors([error.message]);options.notice('XML was not imported; your current design is unchanged.');}finally{event.target.value='';}});
  $('reset-design').addEventListener('click',()=>replace(defaults,'Charlotte green and charcoal defaults restored to this draft.'));
  for(const id of ['design-layout','design-page'])$(id).addEventListener('change',loadPage);
  for(const id of ['design-viewport','design-theme'])$(id).addEventListener('change',apply);
  $('design-frame').addEventListener('load',apply);new ResizeObserver(scale).observe($('design-frame').parentElement);
  const enlarge=()=>{$('design-dialog-slot').append($('design-preview-shell'));$('design-dialog').showModal();scale();};$('enlarge-design').addEventListener('click',enlarge);$('close-design-dialog').addEventListener('click',()=>$('design-dialog').close());$('design-dialog').addEventListener('close',()=>{$('design-preview-home').append($('design-preview-shell'));scale();});
  refreshPresets();return{show(){drawFields();apply();loadPage();},enlarge,refresh(){drawFields();apply();}};
};
