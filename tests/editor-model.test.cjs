const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const M = require('../assets/editor-model.js');
const D = require('../assets/design-model.js');
const root = path.resolve(__dirname, '..');
const baseline = JSON.parse(fs.readFileSync(path.join(root, 'dist/admin/editor-data.json'))).content;
const schema = JSON.parse(fs.readFileSync(path.join(root, 'dist/admin/editor-schema.json')));
const errors = data => M.validate(data, schema, baseline);

test('existing content and reordered object keys remain valid', () => {
  assert.deepEqual(errors(baseline), []);
  const data = M.clone(baseline);
  data.site = Object.fromEntries(Object.entries(data.site).reverse());
  assert.deepEqual(errors(data), []);
  assert.deepEqual(M.changed(data, baseline), []);
});
test('unsafe links, bad dates, duplicate paper keys and empty names are rejected', () => {
  for (const url of ['javascript:alert(1)', 'https://user:secret@example.com', 'file:///tmp/test']) {
    const data = M.clone(baseline); data.news[0].url = url;
    assert.ok(errors(data).length);
  }
  const data = M.clone(baseline);
  data.news[0].date = '2026-13';
  data.publications[1].id = data.publications[0].id;
  data.publications[0].year = 26;
  data.profile.name = ' ';
  assert.ok(errors(data).length >= 4);
});
test('imports cannot silently change navigation or omit sections', () => {
  const data = M.clone(baseline); data.site.navigation = [];
  assert.ok(errors(data).some(x => x.includes('navigation')));
  delete data.people;
  assert.ok(errors(data).length);
});
test('editing biography is detected and new student profiles stay hidden', () => {
  const data = M.clone(baseline); data.profile.bio = ['A revised biography.'];
  assert.deepEqual(errors(data), []);
  assert.deepEqual(M.changed(data, baseline), ['profile']);
  assert.equal(M.newRecord(schema.find(x => x.key === 'people')).approved, false);
  const papers = schema.find(x => x.key === 'publications');
  assert.notEqual(M.newRecord(papers).id, M.newRecord(papers).id);
  assert.equal(M.label({short: 'IEEE Cluster', year: 2026}), "[Cluster'26]");
});

test('design export/import retains settings and rejects tiny text and unsafe colors', () => {
  const data=M.clone(baseline);
  data.design.typography.body_size=18;
  data.design.layout.portrait_position='left';
  data.design.layout.news_height=440;
  const restored=JSON.parse(JSON.stringify(data));
  assert.deepEqual(errors(restored),[]);
  assert.deepEqual(M.changed(restored,baseline),['design']);
  assert.equal(restored.design.layout.news_height,440);
  data.design.typography.body_size=15;
  assert.ok(errors(data).some(x=>x.includes('Body and minimum text size')));
  data.design.typography.body_size=18;
  data.design.light.accent='#FFFFFF';
  assert.ok(errors(data).some(x=>x.includes('contrast')));
  data.design.light.accent='red; background:url(https://example.org)';
  assert.ok(errors(data).some(x=>x.includes('hex color')));
});

test('preview tokens match the Python generator after layout and font edits', () => {
  const {execFileSync}=require('node:child_process');
  const design=M.clone(baseline.design),groups=schema.find(x=>x.key==='design').groups;
  design.typography.body_font='inter';design.typography.heading_font='source-serif';
  design.typography.body_size=20;design.typography.line_height=1.85;
  design.layout.page_width=1200;design.spacing.publication_gap=24;
  const generated=execFileSync('python3',['-c','import json,sys;from editor.design import token_css;sys.stdout.write(token_css(json.load(sys.stdin)))'],{cwd:root,input:JSON.stringify(design),encoding:'utf8'});
  assert.equal(D.css(design,groups),generated);
  assert.equal(D.contrast('#FFFFFF','#000000'),21);
  assert.throws(()=>D.css({...design,layout:{...design.layout,page_width:Infinity}},groups));
});

test('normal navigation preserves imported design fonts; explicit font previews propagate', () => {
  const vm=require('node:vm'),source=fs.readFileSync(path.join(root,'assets/site.js'),'utf8');
  for(const search of ['', '?font=palatino', '?preview=fonts']){
    let href='lab.html';const styles={};
    const link={getAttribute:()=>href,closest:()=>null,setAttribute:(_,value)=>{href=value;}};
    const document={documentElement:{classList:{add(){}}},body:{dataset:{font:'optima'},style:{setProperty:(key,value)=>{styles[key]=value;}}},querySelector:()=>null,querySelectorAll:selector=>selector==='a[href]'?[link]:[]};
    vm.runInNewContext(source,{document,window:{},location:{search,href:'https://example.org/index.html'+search,origin:'https://example.org'},URL,URLSearchParams});
    if(!search){assert.equal(href,'lab.html');assert.deepEqual(styles,{});}
    else if(search.includes('palatino')){assert.match(href,/font=palatino/);assert.match(styles['--d-body-font'],/Pagella/);}
    else{assert.match(href,/preview=fonts/);assert.match(styles['--d-body-font'],/Optima/);}
  }
});
