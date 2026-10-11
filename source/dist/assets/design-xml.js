/* Design-only XML import/export. No content records or executable CSS. */
(function(root,factory){const model=typeof module==='object'&&module.exports?require('./design-model.js'):root.HPDiDesignModel;const api=factory(model);if(typeof module==='object'&&module.exports)module.exports=api;else root.HPDiDesignXML=api;})(globalThis,function(D){
  const MAX_BYTES=65536;
  const escape=value=>String(value).replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  function stringify(design,groups){
    const errors=D.validate(design,groups);if(errors.length)throw new Error(errors.join('\n'));
    const lines=['<?xml version="1.0" encoding="UTF-8"?>','<website-design version="1">'];
    for(const group of groups){lines.push(`  <${group.key}`);for(const field of group.fields)lines.push(`    ${field.key.replaceAll('_','-')}="${escape(design[group.key][field.key])}"`);lines.push('  />');}
    return lines.concat('</website-design>','').join('\n');
  }
  function parse(source,groups){
    if(typeof source!=='string'||new TextEncoder().encode(source).length>MAX_BYTES)throw new Error('Choose a design XML file smaller than 64 KiB.');
    if(/<!\s*(DOCTYPE|ENTITY)/i.test(source))throw new Error('Document types and entity declarations are not supported.');
    const document=new DOMParser().parseFromString(source,'application/xml');
    if(document.querySelector('parsererror'))throw new Error('The design XML is malformed.');
    const root=document.documentElement;
    if(root.tagName!=='website-design'||root.attributes.length!==1||root.getAttribute('version')!=='1')throw new Error('Use <website-design version="1"> as the root.');
    const text=node=>[...node.childNodes].some(child=>(child.nodeType===3||child.nodeType===4)&&child.textContent.trim());
    if(text(root))throw new Error('Design groups must use attributes, without text content.');
    const known=new Map(groups.map(group=>[group.key,group])),design={};
    for(const node of root.children){
      if(!known.has(node.tagName)||Object.hasOwn(design,node.tagName))throw new Error('Each known design group must appear exactly once.');
      if(node.children.length||text(node))throw new Error('Design groups must be empty elements with attributes.');
      const fields=known.get(node.tagName).fields,expected=fields.map(field=>field.key.replaceAll('_','-'));
      if(node.attributes.length!==expected.length||[...node.attributes].some(attr=>!expected.includes(attr.name)))throw new Error(`${node.tagName}: include every documented attribute, with no extras.`);
      const values={};for(const field of fields){let value=node.getAttribute(field.key.replaceAll('_','-'));if(field.type==='range'){if(!/^-?(?:\d+(?:\.\d+)?|\.\d+)$/.test(value))throw new Error(`${node.tagName}: ${field.key} must be a number without units.`);value=Number(value);}values[field.key]=value;}design[node.tagName]=values;
    }
    const errors=D.validate(design,groups);if(errors.length)throw new Error(errors.join('\n'));return design;
  }
  return {stringify,parse,MAX_BYTES};
});
