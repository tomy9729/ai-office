// Run: node scripts/check_dashboard.cjs. Synthetic data; no browser packages.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(require('node:path').join(__dirname,'dashboard.html'),'utf8');
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.events={};this.attrs={};this.style={};this.textContent='';}
  append(...nodes){this.children.push(...nodes)} prepend(...nodes){this.children.unshift(...nodes)}
  replaceChildren(...nodes){this.children=[...nodes]}
  setAttribute(k,v){this.attrs[k]=v}
  addEventListener(k,f){this.events[k]=f}
  click(){if(!this.disabled)this.events.click?.({})}
  showModal(){this.open=true} close(){this.open=false}
}
const ids=Object.fromEntries(['data','content','cards','tabs','filters','chips','subtitle','archives','detail','detail-body','close'].map(id=>[id,new Element('div')]));
const rows=Array.from({length:28},(_,i)=>({title:'Task '+i,ticket:'AO-'+i,date:i===27?null:'2026-10-'+String(1+i%7).padStart(2,'0'),status:i%2?'PARTIAL':'COMPLETED',size:i%2?'L':'S',estimated_md:i===0?0:null,final_md:i===0?0:i===1?2:null,md:i===0?0:i===1?2:null,project:i%2?'beta':'alpha',agents:i%2?['Reviewer']:['Implementer'],models:['actual'],metadata:i!==27,path:'Reports/'+i+'.md',url:'../Reports/'+i+'.md',type:i===0?'core':'task',content:'# Task '+i}));
ids.data.textContent=JSON.stringify({view:'current',date:'2026-10-07',timezone:'UTC',navigation:{current:'index.html'},periods:Object.fromEntries(['current','daily','weekly','monthly'].map(k=>[k,{reports:rows,decisions:Array.from({length:7},(_,i)=>({date:'2026-10-07',text:'Decision '+i,url:'../Decisions/DECISIONS.md'})),start:null,end:null}]))});
const events={},location={_hash:'',get hash(){return this._hash},set hash(v){this._hash='#'+v.replace(/^#/,'');events.hashchange?.()}};
const context=vm.createContext({document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag)},window:{addEventListener:(k,f)=>events[k]=f},location,URLSearchParams,console});
const code=html.split('<script>')[1].split('</script>')[0];vm.runInContext(code,context);
const evalJS=s=>vm.runInContext(s,context),all=n=>[n,...n.children.flatMap(all)],text=n=>[n.textContent,...n.children.map(text)].join(' '),find=(root,label)=>all(root).find(n=>n.tag==='button'&&n.textContent===label);
assert.equal(evalJS('visible.length'),28);
assert.match(text(ids.content),/Decision 6/);assert.doesNotMatch(text(ids.content),/Decision 0/);
assert.equal(evalJS('trendRows(visible,"weekly").length'),2);
assert.equal(evalJS('trendRows(visible,"daily").find(v=>v.from==="2026-10-01").md'),0);
assert.equal(evalJS('trendRows(visible,"daily").find(v=>v.from==="2026-10-03").md'),null);
const metric=all(ids.content).find(n=>n.tag==='select'&&n.attrs['aria-label']==='업무량 지표');metric.value='md';metric.events.change();assert.equal(evalJS('state.metric'),'md');
assert.equal(all(ids.content).filter(n=>n.tag==='circle'&&n.attrs['aria-label']?.startsWith('2026-')).length,2);
assert.equal(evalJS('sum(visible)'),2);
assert.equal(evalJS("sum(visible.filter(r=>r.project==='alpha'))"),0);
assert.equal(evalJS("sum(visible.filter(r=>r.md===null))"),null);
// Donut legend -> shared filter and matching table.
find(ids.content,'PARTIAL 14').click();assert.equal(evalJS('visible.length'),14);assert.match(text(ids.chips),/status: PARTIAL/);assert.match(location.hash,/status=PARTIAL/);
find(ids.chips,'status: PARTIAL ×').click();assert.equal(evalJS('visible.length'),28);
// Keyboard SVG activation -> date range, list, removable chips.
const point=all(ids.content).find(n=>n.tag==='circle'&&n.attrs['aria-label']?.startsWith('2026-'));
point.events.keydown({key:'Enter',preventDefault(){}});assert(evalJS('state.from===state.to && visible.every(r=>r.date===state.from)'));
find(ids.chips,'필터 초기화').click();
find(ids.tabs,'History').click();assert.equal(all(ids.content).filter(n=>n.tag==='tbody')[0].children.length,25);
find(ids.content,'다음').click();assert.equal(evalJS('state.page'),2);assert.equal(all(ids.content).filter(n=>n.tag==='tbody')[0].children.length,3);
// Sorting and detail dialog use the same records.
find(ids.content,'대표 MD').click();assert.equal(evalJS('state.sort'),'md');assert.equal(evalJS('state.page'),1);
const task=all(ids.content).find(n=>n.className==='title-button');task.click();assert(ids.detail.open);assert.match(text(ids['detail-body']),/# Task/);ids.close.click();assert(!ids.detail.open);
// Back/forward hash restoration is handled by the browser hashchange event.
location.hash='view=analytics&project=beta&role=Reviewer&model=actual&size=L';assert.equal(evalJS('visible.length'),14);assert.match(text(ids.content),/Estimated vs Final/);
location.hash='view=health&health=md';assert.equal(evalJS('visible.length'),26);assert.match(text(ids.chips),/health: md/);
find(ids.chips,'필터 초기화').click();assert.equal(evalJS('visible.length'),28);
assert.equal(evalJS("decodeState('#view=invalid&page=-4&sort=bad').page"),1);
assert.equal(evalJS("decodeState('#view=invalid').view"),'overview');
for(const key of ['__proto__','constructor','toString']){location.hash='view=health&health='+key;assert.equal(evalJS('state.health'),'');assert.equal(evalJS('visible.length'),28)}
assert.equal(evalJS("decodeState('#page=Infinity').page"),1);
location.hash='view=history&search=Task+1&from=2026-10-01&to=2026-10-07';assert(evalJS("visible.every(r=>r.title.includes('Task 1')&&r.date)"));
assert.equal(evalJS("decodeState('#'+encodeState(state)).search"),'Task 1');
console.log('Dashboard interaction check passed: shared chart/list filters, keyboard, dates, sort, pagination, dialog, URL restoration, health, null/zero.');
