const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('docs/assets/signup.js', 'utf8');
class Element {
  constructor(values = {}) { Object.assign(this, { listeners: {}, hidden: false, disabled: false, required: false, checked: false, dataset: {}, textContent: '' }, values); this.classList = { add() {}, remove() {} }; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  setAttribute() {} removeAttribute() {} focus() { this.focused = true; }
  emit(type, event = {}) { return this.listeners[type]?.({ preventDefault() {}, target: this, ...event }); }
}
function setup(fetchImpl, valid = true, gtagThrows = false) {
  const ids = Object.fromEntries(['join-form','signup-status','membership-fields','fname','first-name-optional','lname','newsletter'].map(id => [id, new Element()]));
  const form = ids['join-form'];
  const submit = new Element();
  const intents = [new Element({ value: 'matchday_emails', name:'signup_type', checked:true }), new Element({value:'membership',name:'signup_type'})];
  const membershipFields = [ids.lname, new Element(), new Element()];
  ids['membership-fields'].querySelectorAll = () => membershipFields;
  form.action = 'https://formspree.io/f/xljrnona';
  form.reportValidity = () => valid;
  form.querySelector = selector => selector === '[type=submit]' ? submit : intents.find(i => i.checked);
  form.querySelectorAll = () => intents;
  const events = [], requests = [], timers = new Map();
  const context = { document: {getElementById:id=>ids[id]||null,querySelectorAll:()=>[]},window:{gtag:(...args)=>{if(gtagThrows)throw Error('blocked');events.push(args);}},AbortController,FormData:class {constructor(){this.intent=intents.find(i=>i.checked).value;}},setTimeout:fn=>{timers.set(1,fn);return 1;},clearTimeout:id=>timers.delete(id),fetch:async (...args)=>{requests.push(args);return fetchImpl(...args);} };
  vm.runInNewContext(source, context);
  return {ids,form,submit,intents,events,requests,timers};
}
const accepted = async()=>({ok:true,json:async()=>({ok:true})});
(async()=>{
  let t=setup(accepted);
  assert.equal(t.ids['membership-fields'].hidden,true);
  assert.equal(t.ids.fname.required,false);
  assert.equal(t.ids.newsletter.required,true);
  assert.equal(t.ids.lname.disabled,true);
  await t.form.emit('input');await t.form.emit('input');
  assert.equal(t.events.filter(e=>e[1]==='signup_start').length,1);
  await t.form.emit('submit');await t.form.emit('submit');
  assert.equal(t.requests.length,1,'repeat submit must not issue a second request');
  assert.equal(t.events.filter(e=>e[1]==='generate_lead').length,1);
  assert.equal(t.form.hidden,true);assert.equal(t.timers.size,0);
  assert.equal(t.requests[0][1].headers.Accept,'application/json');
  assert.equal(t.requests[0][1].body.intent,'matchday_emails');

  t=setup(accepted);t.intents[0].checked=false;t.intents[1].checked=true;t.intents[1].emit('change');
  assert.equal(t.ids.fname.required,true);assert.equal(t.ids.lname.required,true);
  assert.equal(t.ids.lname.disabled,false);assert.equal(t.ids.newsletter.required,false);
  await t.form.emit('submit');assert.equal(t.events.find(e=>e[1]==='generate_lead')[2].signup_type,'membership');

  for(const failure of [async()=>({ok:false,json:async()=>({errors:[{message:'private value'}]})}),async()=>{throw Error('network');},async()=>({ok:true,json:async()=>{throw Error('bad JSON');}})]){
    t=setup(failure);await t.form.emit('submit');
    assert.equal(t.form.hidden,false);assert.equal(t.submit.disabled,false);
    assert.equal(t.events.some(e=>e[1]==='generate_lead'),false);
    assert.equal(t.events.filter(e=>e[1]==='signup_error').length,1);
    assert.equal(JSON.stringify(t.events).includes('private value'),false);
    assert.equal(t.timers.size,0);
  }
  t=setup(accepted,false);await t.form.emit('submit');assert.equal(t.requests.length,0);
  let release; t=setup(()=>new Promise(resolve=>{release=resolve;}));
  const pending=t.form.emit('submit');await t.form.emit('submit');assert.equal(t.requests.length,1);
  release(await accepted());await pending;
  t=setup(accepted,true,true);await t.form.emit('submit');assert.equal(t.form.hidden,true,'analytics failure must not break signup');
  console.log('Signup tests passed: intents, consent, validation, success, rejection, network/JSON errors, duplicate prevention, and blocked analytics.');
})();
