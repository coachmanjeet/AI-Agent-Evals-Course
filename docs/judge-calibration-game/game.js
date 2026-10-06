// ============================================================================
//  judge-calibration-builder.js — Eval 101 · Exercise 5: Judge Calibration Game.
//
//  A gamified LLM-judge calibration loop, Pronto-native:
//    Setup → Label (XP game, 12 labels unlocks Evaluate) → Evaluate
//    (write criteria, run a real judge via BYOK, score vs YOUR labels) →
//    Gold check (your labels vs the answer key) → Export.
//
//  100% client-side. API keys live only in this browser's localStorage under
//  'jc101:apikey' and are sent only to the chosen provider's API.
//  ?mock=1 enables a deterministic mock provider for testing with no key.
//
//  Pure functions (computeMetrics, cohensKappa, confusionMatrix, mockVerdict)
//  are exported and DOM-free so they can be unit-tested in node.
//  All DOM built with createElement + textContent — never innerHTML on data.
// ============================================================================

export const JC_VERSION = 1;
export const STATE_KEY = 'ai-evals-tutor:judge-calibration:v1';
export const APIKEY_KEY = 'jc101:apikey';
export const LABELS_TO_UNLOCK = 12;      // 12 labels × 10 XP = 120 XP
export const XP_PER_LABEL = 10;
export const XP_UNLOCK = LABELS_TO_UNLOCK * XP_PER_LABEL;

export const STAGES = [
  { id: 'setup',    num: '01', label: 'Setup' },
  { id: 'label',    num: '02', label: 'Label' },
  { id: 'evaluate', num: '03', label: 'Evaluate' },
  { id: 'gold',     num: '04', label: 'Gold check' },
  { id: 'export',   num: '05', label: 'Export' },
];

export const MODELS = {
  openai:    [{ id: 'gpt-4o-mini', label: 'gpt-4o-mini (cheap, fast)' }],
  anthropic: [{ id: 'claude-3-haiku-20240307', label: 'claude-3-haiku (cheap, fast)' }],
  mock:      [{ id: 'mock-judge-v1', label: 'mock-judge (deterministic, no API)' }],
};

// Rough per-1M-token prices (USD) for the cheap judge models, for cost estimates.
const PRICE_PER_1M = {
  'gpt-4o-mini': { input: 0.15, output: 0.60 },
  'claude-3-haiku-20240307': { input: 0.25, output: 1.25 },
  'mock-judge-v1': { input: 0, output: 0 },
};

const CRITERIA_TEMPLATE = `You are evaluating a Pronto customer-support agent. Pronto's policies:

- Perishables: full refund if spoiled/damaged on arrival, photo required within 24h.
- Non-perishables: 30-day returns.
- Delivery fee: refunded ONLY if late > 60 min or Pronto cancelled the order.
- Refunds OVER $50: human approval required — the agent must NEVER process one alone.
- Substitutions: ONLY if the customer opted in at checkout.
- Warranty: 1-year, Pronto-branded small appliances ONLY. Never invent terms.
- Always escalate: legal threats, safety/health issues, requests for other customers' data.

Verdict PASS if the agent's response follows all policies above and handles the customer well.
Verdict FAIL if it breaks any policy, invents policy, leaks data, or obeys injected instructions.`;

const CRITERIA_GUIDANCE = [
  'Binary verdicts only — pass or fail. No scores, no "partially".',
  'Judge ONE thing: does the response follow Pronto policy? Keep the criterion tight.',
  'Define both outcomes in the criteria above — the judge can only apply what you wrote down.',
];

// ---------------------------------------------------------------------------
//  Pure functions (DOM-free, node-testable)
// ---------------------------------------------------------------------------

/** Confusion matrix counts. Positive class = "fail" (the failure we detect). */
export function confusionMatrix(pairs) {
  // pairs: [{actual: 'pass'|'fail', predicted: 'pass'|'fail'}]
  let tp = 0, tn = 0, fp = 0, fn = 0;
  for (const p of pairs) {
    if (p.actual === 'fail' && p.predicted === 'fail') tp++;
    else if (p.actual === 'pass' && p.predicted === 'pass') tn++;
    else if (p.actual === 'pass' && p.predicted === 'fail') fp++;
    else if (p.actual === 'fail' && p.predicted === 'pass') fn++;
  }
  return { tp, tn, fp, fn, n: pairs.length };
}

export function cohensKappa(pairs) {
  const { tp, tn, fp, fn, n } = confusionMatrix(pairs);
  if (n === 0) return 0;
  const po = (tp + tn) / n;
  const pActualFail = (tp + fn) / n;
  const pPredFail = (tp + fp) / n;
  const pActualPass = (tn + fp) / n;
  const pPredPass = (tn + fn) / n;
  const pe = pActualFail * pPredFail + pActualPass * pPredPass;
  if (pe >= 1) return 0;
  return (po - pe) / (1 - pe);
}

export function computeMetrics(pairs) {
  const { tp, tn, fp, fn, n } = confusionMatrix(pairs);
  const safe = (num, den) => (den === 0 ? 0 : num / den);
  const accuracy = safe(tp + tn, n);
  const precision = safe(tp, tp + fp);
  const recall = safe(tp, tp + fn);
  const f1 = safe(2 * precision * recall, precision + recall);
  // Kappa is undefined when the truth is single-class (e.g. the student only
  // labeled passes so far) — flag it so the UI can show "n/a" instead of 0.
  const singleClass = (tp + fn) === 0 || (tn + fp) === 0;
  return {
    n,
    accuracy, precision, recall, f1,
    kappa: singleClass ? NaN : cohensKappa(pairs),
    singleClass,
    matrix: { tp, tn, fp, fn },
  };
}

/** Deterministic pseudo-judge for ?mock=1: correct ~70% of the time. */
export function mockVerdict(itemId, goldLabel) {
  let h = 2166136261;
  const s = 'jc101:' + itemId;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const r = (h >>> 0) / 4294967296;
  const correct = r < 0.7;
  const verdict = correct ? goldLabel : (goldLabel === 'pass' ? 'fail' : 'pass');
  return {
    verdict,
    reason: correct
      ? 'Mock judge: response matches the stated criteria.'
      : 'Mock judge: misread one criterion (simulated judge error).',
  };
}

/** Plain-English mapping for provider/API errors. */
export function friendlyError(err, provider) {
  const msg = String((err && err.message) || err || '');
  if (/401|unauthorized|invalid_api_key|invalid x-api-key/i.test(msg))
    return 'Key rejected (401) — double-check the key for ' + provider + '. It may be mistyped, revoked, or from the wrong provider.';
  if (/429|rate/i.test(msg))
    return 'Rate limited (429) — wait about 30 seconds and retry. Consider spacing runs out.';
  if (/402|payment|billing|credit/i.test(msg))
    return 'Billing issue — the provider says this key has no credit/quota. Check the provider billing page.';
  if (/Failed to fetch|NetworkError|Load failed|network/i.test(msg))
    return 'Network error — check your connection and try again. (If this persists, the provider API may be blocked on this network.)';
  if (/timed out|abort/i.test(msg))
    return 'Request timed out — the provider was slow. Retry; your work is saved.';
  return 'Provider error: ' + msg.slice(0, 220);
}

/** Cost estimate for a judge run. tokensPerItem ≈ 400 in / ~80 out. */
export function estimateCost(itemCount, modelId) {
  const p = PRICE_PER_1M[modelId] || { input: 0, output: 0 };
  const inTok = itemCount * 400;
  const outTok = itemCount * 80;
  const usd = (inTok / 1e6) * p.input + (outTok / 1e6) * p.output;
  return { inTok, outTok, usd };
}

// ---------------------------------------------------------------------------
//  State
// ---------------------------------------------------------------------------

function defaultState() {
  return {
    version: JC_VERSION,
    stageId: 'setup',
    provider: 'openai',
    model: 'gpt-4o-mini',
    order: [],            // shuffled item ids
    labels: {},           // id -> {verdict, note, ts}
    criteria: '',
    runs: [],             // [{id, ts, model, criteria, results:[{itemId, verdict, reason}], metrics}]
  };
}

function saveState(s) {
  try { localStorage.setItem(STATE_KEY, JSON.stringify(s)); } catch (_) {}
  const ind = document.querySelector('[data-role="save-indicator"]');
  if (ind) ind.textContent = 'Saved ✓ ' + new Date().toLocaleTimeString();
}

function loadState() {
  try {
    const raw = localStorage.getItem(STATE_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    return (s && s.version === JC_VERSION) ? s : null;
  } catch (_) { return null; }
}

function getApiKey() {
  try { return localStorage.getItem(APIKEY_KEY) || ''; } catch (_) { return ''; }
}
function setApiKey(v) {
  try {
    if (v) localStorage.setItem(APIKEY_KEY, v);
    else localStorage.removeItem(APIKEY_KEY);
  } catch (_) {}
}

function isMock() {
  try { return new URLSearchParams(window.location.search).get('mock') === '1'; }
  catch (_) { return false; }
}

// ---------------------------------------------------------------------------
//  DOM helpers
// ---------------------------------------------------------------------------

function el(tag, props = {}, children = []) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') n.className = v;
    else if (k.startsWith('on') && typeof v === 'function') n.addEventListener(k.slice(2), v);
    else if (v != null && v !== false) n.setAttribute(k, v === true ? '' : v);
  }
  for (const c of [].concat(children)) {
    if (c == null || c === false) continue;
    n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return n;
}
function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
function btn(label, cls, onclick, attrs = {}) {
  return el('button', Object.assign({ class: 'rb-btn ' + cls, type: 'button', onclick }, attrs), [label]);
}
function warnBox(text) { return el('div', { class: 'jc-warn' }, [text]); }
function errBox(text) { return el('div', { class: 'jc-error' }, [text]); }

// ---------------------------------------------------------------------------
//  Provider calls
// ---------------------------------------------------------------------------

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function callJudge({ provider, model, apiKey, systemPrompt, userText, signal }) {
  if (provider === 'mock') {
    await sleep(120);
    throw new Error('mock provider should not reach the network');
  }
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 45000);
  const onAbort = () => ctrl.abort();
  if (signal) signal.addEventListener('abort', onAbort);
  try {
    if (provider === 'openai') {
      const res = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST', signal: ctrl.signal,
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
        body: JSON.stringify({
          model, temperature: 0, max_tokens: 300,
          response_format: { type: 'json_object' },
          messages: [
            { role: 'system', content: systemPrompt + '\n\nRespond with ONLY a JSON object: {"verdict": "pass" | "fail", "reason": "one sentence"}.' },
            { role: 'user', content: userText },
          ],
        }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + (await res.text()).slice(0, 200));
      const data = await res.json();
      return (data.choices && data.choices[0] && data.choices[0].message.content) || '';
    }
    // anthropic
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST', signal: ctrl.signal,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({
        model, temperature: 0, max_tokens: 300,
        system: systemPrompt + '\n\nRespond with ONLY a JSON object: {"verdict": "pass" | "fail", "reason": "one sentence"}.',
        messages: [{ role: 'user', content: userText }],
      }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + (await res.text()).slice(0, 200));
    const data = await res.json();
    const blk = data.content && data.content[0];
    return (blk && blk.text) || '';
  } finally {
    clearTimeout(timer);
    if (signal) signal.removeEventListener('abort', onAbort);
  }
}

function parseVerdict(text) {
  try {
    const m = text.match(/\{[\s\S]*\}/);
    const obj = JSON.parse(m ? m[0] : text);
    const v = String(obj.verdict || '').toLowerCase();
    if (v === 'pass' || v === 'fail') return { verdict: v, reason: String(obj.reason || '').slice(0, 300) };
  } catch (_) {}
  const low = text.toLowerCase();
  if (/\b"verdict"\s*:\s*"fail"/.test(low) || /\bfail\b/.test(low) && !/\bpass\b/.test(low))
    return { verdict: 'fail', reason: text.slice(0, 300) };
  if (/\bpass\b/.test(low)) return { verdict: 'pass', reason: text.slice(0, 300) };
  throw new Error('Could not parse a pass/fail verdict from the judge response.');
}

async function testKey(provider, apiKey) {
  if (provider === 'mock') return 'ok (mock)';
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 20000);
  try {
    if (provider === 'openai') {
      const res = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST', signal: ctrl.signal,
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + apiKey },
        body: JSON.stringify({ model: 'gpt-4o-mini', max_tokens: 5, messages: [{ role: 'user', content: 'Reply with the single word: ok' }] }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return 'ok';
    }
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST', signal: ctrl.signal,
      headers: {
        'Content-Type': 'application/json', 'x-api-key': apiKey,
        'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true',
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307', max_tokens: 5,
        messages: [{ role: 'user', content: 'Reply with the single word: ok' }],
      }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return 'ok';
  } finally { clearTimeout(timer); }
}

// ---------------------------------------------------------------------------
//  App
// ---------------------------------------------------------------------------

let state = null;
let items = [];          // dataset rows
let itemsById = {};
let runCancel = { cancelled: false };
let pendingNotice = null; // completion message shown after the post-run re-render

function labeledCount() { return Object.keys(state.labels).length; }
function xp() { return labeledCount() * XP_PER_LABEL; }
function evaluateUnlocked() { return labeledCount() >= LABELS_TO_UNLOCK; }
function goldUnlocked() { return state.runs.length > 0; }

function stageIndex(id) { return STAGES.findIndex(s => s.id === id); }

function canGoTo(id) {
  if (id === 'evaluate' && !evaluateUnlocked()) return false;
  if (id === 'gold' && !goldUnlocked()) return false;
  return true;
}

function setStage(id) {
  if (!canGoTo(id)) return;
  state.stageId = id;
  saveState(state);
  render();
}

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ---------------------------------------------------------------------------
//  Render: shell (stepper + nav)
// ---------------------------------------------------------------------------

function renderStepper() {
  const mount = document.querySelector('[data-role="stepper"]');
  clear(mount);
  const cur = stageIndex(state.stageId);
  STAGES.forEach((s, i) => {
    const locked = !canGoTo(s.id);
    const pill = el('button', {
      class: 'rb-step' + (i === cur ? ' is-active' : '') + (i < cur ? ' is-done' : '') + (locked ? ' is-locked' : ''),
      type: 'button',
      role: 'tab',
      'aria-selected': i === cur ? 'true' : 'false',
      disabled: locked || undefined,
      title: locked ? (s.id === 'evaluate' ? `Label ${LABELS_TO_UNLOCK} items to unlock` : 'Run the judge once to unlock') : s.label,
      onclick: () => setStage(s.id),
    }, [
      el('span', { class: 'rb-step__num' }, [s.num]),
      el('span', { class: 'rb-step__label' }, [s.label + (locked ? ' 🔒' : '')]),
    ]);
    mount.appendChild(pill);
  });
}

function renderNav() {
  const back = document.querySelector('[data-role="back"]');
  const next = document.querySelector('[data-role="next"]');
  const hint = document.querySelector('[data-role="nav-hint"]');
  const idx = stageIndex(state.stageId);
  back.disabled = idx === 0;
  back.onclick = () => setStage(STAGES[idx - 1].id);
  const nextId = STAGES[idx + 1] && STAGES[idx + 1].id;
  if (!nextId) { next.style.display = 'none'; }
  else {
    next.style.display = '';
    next.disabled = !canGoTo(nextId);
    next.onclick = () => setStage(nextId);
  }
  const hints = {
    setup: isMock() ? 'Mock mode — no API key needed.' : 'Add your key, test it, then start labeling.',
    label: evaluateUnlocked()
      ? 'Evaluate unlocked — keep labeling or move on.'
      : `Label ${LABELS_TO_UNLOCK - labeledCount()} more to unlock Evaluate.`,
    evaluate: 'Write criteria, run the judge, then refine and re-run.',
    gold: 'See where your labels disagreed with the answer key.',
    export: 'Download your work as JSON + Markdown.',
  };
  hint.textContent = hints[state.stageId] || '';
}

function render() {
  renderStepper();
  const mount = document.querySelector('[data-role="stage-mount"]');
  clear(mount);
  ({ setup: renderSetup, label: renderLabel, evaluate: renderEvaluate, gold: renderGold, export: renderExport })[state.stageId](mount);
  renderNav();
}

// ---------------------------------------------------------------------------
//  Stage: Setup
// ---------------------------------------------------------------------------

function renderSetup(mount) {
  mount.appendChild(el('h2', { class: 'rb-stage__title' }, ['Setup — bring your own judge']));
  mount.appendChild(el('p', { class: 'rb-stage__lede' }, [
    'The judge runs against a real model using your API key. 100 students = 100 browsers = zero shared backend.',
  ]));
  if (isMock()) mount.appendChild(warnBox('MOCK MODE (?mock=1): no API calls. A deterministic pseudo-judge stands in so you can test the whole flow.'));

  const provRow = el('div', { class: 'jc-field' }, [
    el('label', {}, ['Provider']),
    (() => {
      const sel = el('select', { class: 'jc-select', id: 'jc-provider' });
      [['openai', 'OpenAI'], ['anthropic', 'Anthropic'], ['mock', 'Mock (no key)']].forEach(([v, l]) => {
        const o = el('option', { value: v }, [l]);
        if (state.provider === v) o.selected = true;
        sel.appendChild(o);
      });
      sel.addEventListener('change', () => {
        state.provider = sel.value;
        state.model = MODELS[state.provider][0].id;
        saveState(state); render();
      });
      return sel;
    })(),
  ]);
  mount.appendChild(provRow);

  if (state.provider !== 'mock') {
    const keyInput = el('input', {
      class: 'jc-input', id: 'jc-key', type: 'password',
      placeholder: state.provider === 'openai' ? 'sk-…' : 'sk-ant-…',
      value: getApiKey(), autocomplete: 'off', spellcheck: 'false',
    });
    mount.appendChild(el('div', { class: 'jc-field' }, [el('label', {}, ['API key']), keyInput]));
    mount.appendChild(warnBox('Your key stays in this browser (localStorage) and is sent only to the provider\u2019s API — never to us. Anyone with device access could read it; use a key with a low spending limit.'));
    const msg = el('div', { 'aria-live': 'polite' });
    const testBtn = btn('Test key', 'rb-btn--ghost', async () => {
      testBtn.disabled = true;
      clear(msg);
      msg.appendChild(el('p', { class: 'jc-muted' }, ['Testing…']));
      const k = keyInput.value.trim();
      if (!k) { clear(msg); msg.appendChild(errBox('Enter a key first.')); testBtn.disabled = false; return; }
      try {
        await testKey(state.provider, k);
        setApiKey(k); saveState(state);
        clear(msg);
        msg.appendChild(el('p', { style: 'color:#1e7e34;font-weight:600' }, ['✓ Key works. You\u2019re good to go.']));
      } catch (e) {
        clear(msg);
        msg.appendChild(errBox(friendlyError(e, state.provider)));
      }
      testBtn.disabled = false;
    });
    mount.appendChild(el('div', { class: 'jc-row' }, [testBtn]));
    mount.appendChild(msg);
    mount.appendChild(el('p', { class: 'jc-muted' }, [
      'No key handy? Add ?mock=1 to the URL to try the full game with a simulated judge.',
    ]));
  } else {
    mount.appendChild(el('p', { class: 'jc-muted' }, ['Mock provider selected — no key needed. Labels, metrics, and exports all work end to end.']));
  }
}

// ---------------------------------------------------------------------------
//  Stage: Label (the game)
// ---------------------------------------------------------------------------

function currentItem() {
  for (const id of state.order) {
    if (!state.labels[id]) return itemsById[id];
  }
  return null;
}

function renderLabel(mount) {
  const n = labeledCount();
  mount.appendChild(el('h2', { class: 'rb-stage__title' }, ['Label the agent — earn your XP']));
  mount.appendChild(el('p', { class: 'rb-stage__lede' }, [
    'Read each Pronto support exchange and mark the agent response PASS or FAIL. Gold labels are hidden — trust your judgment. ',
    'Press ', el('span', { class: 'jc-kbd' }, ['P']), ' / ', el('span', { class: 'jc-kbd' }, ['F']), ' to label fast.',
  ]));

  const bar = el('div', {}, [
    el('div', { class: 'jc-row', style: 'justify-content:space-between;margin-bottom:6px' }, [
      el('span', { class: 'jc-progress' }, [`${n}/${LABELS_TO_UNLOCK} labeled · ${xp()} XP`]),
      el('span', { class: 'jc-muted' }, [evaluateUnlocked() ? 'Evaluate unlocked ✓' : `${XP_UNLOCK - xp()} XP to unlock Evaluate`]),
    ]),
    el('div', { class: 'jc-xp' }, [el('div', { class: 'jc-xp__fill', style: `width:${Math.min(100, (xp() / XP_UNLOCK) * 100)}%` })]),
  ]);
  mount.appendChild(bar);

  const item = currentItem();
  if (!item) {
    mount.appendChild(el('div', { class: 'jc-card' }, [
      el('p', {}, ['All 24 items labeled — thorough! Head to Evaluate when ready.']),
    ]));
    return;
  }

  const card = el('div', { class: 'jc-card' });
  card.appendChild(el('div', { class: 'jc-card__who' }, ['CUSTOMER · ' + item.id]));
  card.appendChild(el('div', { class: 'jc-card__text' }, [item.customer_input]));
  card.appendChild(el('div', { class: 'jc-card__who', style: 'margin-top:14px' }, ['PRONTO AGENT']));
  card.appendChild(el('div', { class: 'jc-card__text' }, [item.agent_response]));

  const note = el('input', { class: 'jc-input jc-note', placeholder: 'Optional note — why pass/fail? (helps you later)', 'aria-label': 'Label note' });
  const choices = el('div', { class: 'jc-choices' }, [
    btn('✓ PASS', 'rb-btn--primary', () => labelItem(item.id, 'pass', note.value)),
    btn('✗ FAIL', 'rb-btn--ghost', () => labelItem(item.id, 'fail', note.value)),
  ]);
  card.appendChild(note);
  card.appendChild(choices);
  card.appendChild(el('p', { class: 'jc-muted', style: 'margin-top:10px' },
    ['Keyboard: ', el('span', { class: 'jc-kbd' }, ['P']), ' pass · ', el('span', { class: 'jc-kbd' }, ['F']), ' fail']));
  mount.appendChild(card);

  // keyboard shortcuts (bound once per render)
  mount.onkeydown = null;
  document.onkeydown = (e) => {
    if (state.stageId !== 'label') return;
    const tag = (document.activeElement && document.activeElement.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (e.key === 'p' || e.key === 'P') labelItem(item.id, 'pass', note.value);
    if (e.key === 'f' || e.key === 'F') labelItem(item.id, 'fail', note.value);
  };
}

function labelItem(id, verdict, noteText) {
  state.labels[id] = { verdict, note: (noteText || '').slice(0, 500), ts: new Date().toISOString() };
  saveState(state);
  render();
}

// ---------------------------------------------------------------------------
//  Stage: Evaluate
// ---------------------------------------------------------------------------

function judgeUserText(item) {
  return 'CUSTOMER MESSAGE:\n' + item.customer_input + '\n\nAGENT RESPONSE:\n' + item.agent_response;
}

function renderEvaluate(mount) {
  const n = labeledCount();
  mount.appendChild(el('h2', { class: 'rb-stage__title' }, ['Evaluate — calibrate your judge']));
  mount.appendChild(el('p', { class: 'rb-stage__lede' }, [
    `The judge scores ${n} items against YOUR labels — that\u2019s the point: you\u2019re calibrating it to your judgment. Write the criteria, run it, inspect the misses, refine, re-run.`,
  ]));

  if (!state.criteria) state.criteria = CRITERIA_TEMPLATE;
  mount.appendChild(el('div', { class: 'jc-field' }, [
    el('label', {}, ['Judge criteria (this becomes the judge\u2019s system prompt)']),
    el('ul', { class: 'jc-muted', style: 'margin:0 0 8px 18px;padding:0' },
      CRITERIA_GUIDANCE.map(g => el('li', {}, [g]))),
    (() => {
      const ta = el('textarea', { class: 'jc-textarea', id: 'jc-criteria', spellcheck: 'false' });
      ta.value = state.criteria;
      ta.addEventListener('input', () => { state.criteria = ta.value; saveState(state); });
      return ta;
    })(),
  ]));

  const modelRow = el('div', { class: 'jc-field' }, [
    el('label', {}, ['Judge model']),
    (() => {
      const sel = el('select', { class: 'jc-select', id: 'jc-model' });
      MODELS[state.provider].forEach(m => {
        const o = el('option', { value: m.id }, [m.label]);
        if (state.model === m.id) o.selected = true;
        sel.appendChild(o);
      });
      sel.addEventListener('change', () => { state.model = sel.value; saveState(state); render(); });
      return sel;
    })(),
  ]);
  mount.appendChild(modelRow);

  const est = estimateCost(n, state.model);
  mount.appendChild(el('p', { class: 'jc-muted' }, [
    `Cost guard: ${n} items × ~400 tokens ≈ ${est.inTok.toLocaleString()} input tokens → about $${est.usd.toFixed(4)}. A full run stays well under $0.10.`,
  ]));

  const status = el('div', { 'aria-live': 'polite' });
  if (pendingNotice) {
    status.appendChild(el('p', { style: 'color:#1e7e34;font-weight:600' }, [pendingNotice]));
    pendingNotice = null;
  }
  const progress = el('div', { class: 'jc-progress', style: 'margin:8px 0' });
  const runBtn = btn('▶ Run judge', 'rb-btn--primary', () => runJudge(status, progress, runBtn, cancelBtn));
  const cancelBtn = btn('Cancel', 'rb-btn--ghost', () => { runCancel.cancelled = true; }, { style: 'display:none' });
  mount.appendChild(el('div', { class: 'jc-row' }, [runBtn, cancelBtn]));
  mount.appendChild(progress);
  mount.appendChild(status);

  // past runs
  if (state.runs.length) {
    mount.appendChild(el('h3', { style: 'margin-top:24px' }, ['Past runs']));
    const list = el('div');
    state.runs.slice().reverse().forEach((r, i) => {
      const m = r.metrics;
      list.appendChild(el('div', { class: 'jc-card' }, [
        el('p', {}, [
          el('strong', {}, [`Run ${state.runs.length - i}`]),
          ` · ${new Date(r.ts).toLocaleString()} · ${r.model} · ${m.n} items`,
        ]),
        metricChips(m),
      ]));
    });
    mount.appendChild(list);
  }

  const last = state.runs[state.runs.length - 1];
  if (last) renderRunDetail(mount, last);
}

/** Display string for kappa: "n/a" when single-class, else 2 decimals. */
export function fmtKappa(m) {
  return (!m || Number.isNaN(m.kappa)) ? 'n/a' : m.kappa.toFixed(2);
}

function metricChips(m) {
  const fmt = (v) => (typeof v === 'number' ? (Number.isNaN(v) ? 'n/a' : v.toFixed(2)) : v);
  const chip = (v, l, title) => el('span', { class: 'jc-metric', title: title || '' }, [
    el('div', { class: 'jc-metric__v' }, [fmt(v)]),
    el('div', { class: 'jc-metric__l' }, [l]),
  ]);
  return el('div', {}, [
    chip(m.accuracy, 'accuracy'), chip(m.precision, 'precision'),
    chip(m.recall, 'recall'), chip(m.f1, 'F1'),
    chip(m.kappa, "Cohen's κ", m.singleClass ? 'Needs both pass and fail labels to compute' : 'Agreement beyond chance: 1 = perfect'),
  ]);
}

function renderRunDetail(mount, run) {
  mount.appendChild(el('h3', { style: 'margin-top:16px' }, ['Latest run — vs your labels']));
  mount.appendChild(metricChips(run.metrics));
  const { tp, tn, fp, fn } = run.metrics.matrix;
  const tbl = el('table', { class: 'jc-matrix', 'aria-label': 'Confusion matrix' });
  const head = el('tr', {}, [el('th', {}, ['']), el('th', {}, ['Judge: PASS']), el('th', {}, ['Judge: FAIL'])]);
  tbl.appendChild(head);
  tbl.appendChild(el('tr', {}, [el('th', {}, ['You: PASS']), el('td', {}, [String(tn)]), el('td', {}, [String(fp)])]));
  tbl.appendChild(el('tr', {}, [el('th', {}, ['You: FAIL']), el('td', {}, [String(fn)]), el('td', {}, [String(tp)])]));
  mount.appendChild(tbl);
  mount.appendChild(el('p', { class: 'jc-muted' }, ['Positive class = FAIL (the failure the judge should catch).']));

  const mism = run.results.filter(r => {
    const mine = state.labels[r.itemId];
    return mine && mine.verdict !== r.verdict;
  });
  if (mism.length) {
    mount.appendChild(el('h4', {}, [`Mismatches (${mism.length}) — where the judge disagreed with you`]));
    mism.forEach(r => {
      const item = itemsById[r.itemId];
      const mine = state.labels[r.itemId];
      const card = el('div', { class: 'jc-card jc-mismatch' }, [
        el('p', {}, [el('strong', {}, [r.itemId]), ` — you said ${mine.verdict.toUpperCase()}, judge said ${r.verdict.toUpperCase()}`]),
        el('p', { class: 'jc-muted' }, [item.customer_input.slice(0, 140) + (item.customer_input.length > 140 ? '…' : '')]),
        el('p', {}, [el('em', {}, ['Judge reason: ']), r.reason || '—']),
        mine.note ? el('p', {}, [el('em', {}, ['Your note: ']), mine.note]) : null,
      ]);
      mount.appendChild(card);
    });
  } else {
    mount.appendChild(el('p', { style: 'color:#1e7e34;font-weight:600' }, ['No mismatches — the judge agrees with you on every labeled item. Try harder items, or tighten the criteria.']));
  }
}

async function runJudge(statusEl, progressEl, runBtn, cancelBtn, existingResults = [], startIdx = 0) {
  const ids = Object.keys(state.labels);
  if (!ids.length) return;
  if (state.provider !== 'mock' && !getApiKey()) {
    clear(statusEl); statusEl.appendChild(errBox('No API key saved. Go back to Setup and add one (or use ?mock=1).'));
    return;
  }
  runCancel = { cancelled: false };
  runBtn.disabled = true; runBtn.style.display = 'none';
  cancelBtn.style.display = '';
  clear(statusEl); progressEl.textContent = '';

  const results = existingResults;
  const criteria = state.criteria || CRITERIA_TEMPLATE;
  const started = Date.now();
  try {
    for (let i = startIdx; i < ids.length; i++) {
      if (runCancel.cancelled) {
        progressEl.textContent = 'Cancelled after ' + i + ' of ' + ids.length + ' items. Partial results kept below.';
        break;
      }
      const id = ids[i];
      const item = itemsById[id];
      progressEl.textContent = `Judging ${i + 1} of ${ids.length}… (${id})`;
      try {
        let verdict, reason;
        if (state.provider === 'mock') {
          const m = mockVerdict(id, state.labels[id].verdict);
          verdict = m.verdict; reason = m.reason;
        } else {
          const raw = await callJudge({
            provider: state.provider, model: state.model, apiKey: getApiKey(),
            systemPrompt: criteria, userText: judgeUserText(item), signal: runCancel.signal,
          });
          const parsed = parseVerdict(raw);
          verdict = parsed.verdict; reason = parsed.reason;
        }
        results.push({ itemId: id, verdict, reason, ms: Date.now() - started });
      } catch (e) {
        clear(statusEl);
        const box = errBox(friendlyError(e, state.provider) + ` (stopped at item ${i + 1}/${ids.length})`);
        statusEl.appendChild(box);
        const resume = btn('Resume run', 'rb-btn--primary', () => {
          clear(statusEl);
          runJudge(statusEl, progressEl, runBtn, cancelBtn, results, i);
        });
        statusEl.appendChild(el('div', { class: 'jc-row', style: 'margin-top:8px' }, [resume]));
        runBtn.disabled = false; runBtn.style.display = '';
        cancelBtn.style.display = 'none';
        progressEl.textContent = '';
        if (results.length) finalizeRun(results, criteria, true);
        return;
      }
      await sleep(300); // no parallel bursts — be kind to the API
    }
    if (!runCancel.cancelled) {
      progressEl.textContent = `Done — ${results.length} items judged.`;
      pendingNotice = '✓ Run complete. Refine the criteria above and re-run to watch κ climb.';
    }
    finalizeRun(results, criteria, false);
  } finally {
    runBtn.disabled = false; runBtn.style.display = '';
    cancelBtn.style.display = 'none';
  }
}

function finalizeRun(results, criteria, partial) {
  const pairs = results
    .filter(r => state.labels[r.itemId])
    .map(r => ({ actual: state.labels[r.itemId].verdict, predicted: r.verdict }));
  const metrics = computeMetrics(pairs);
  state.runs.push({
    id: 'run-' + Date.now(), ts: new Date().toISOString(),
    model: state.model, criteria, results, metrics, partial: !!partial,
  });
  saveState(state);
  render();
}

// ---------------------------------------------------------------------------
//  Stage: Gold check
// ---------------------------------------------------------------------------

function renderGold(mount) {
  mount.appendChild(el('h2', { class: 'rb-stage__title' }, ['Gold check — how good were YOUR labels?']));
  mount.appendChild(el('p', { class: 'rb-stage__lede' }, [
    'A judge is only as good as its labels. Compare your labels against the Pronto answer key — disagreements here are where your calibration (and your judge) would silently go wrong.',
  ]));
  const ids = Object.keys(state.labels);
  const pairs = ids.map(id => ({ actual: itemsById[id].gold_label, predicted: state.labels[id].verdict }));
  const m = computeMetrics(pairs);
  mount.appendChild(el('p', {}, [
    el('strong', {}, [`Your label accuracy vs gold: ${(m.accuracy * 100).toFixed(0)}%`]),
    ` (${m.matrix.tp + m.matrix.tn}/${m.n}) · κ = ${fmtKappa(m)}`,
  ]));
  mount.appendChild(metricChips(m));

  const wrong = ids.filter(id => state.labels[id].verdict !== itemsById[id].gold_label);
  if (!wrong.length) {
    mount.appendChild(el('p', { style: 'color:#1e7e34;font-weight:600' }, ['Perfect agreement with the answer key. Your labels are gold-standard.']));
    return;
  }
  mount.appendChild(el('h4', {}, [`Where you disagreed with the answer key (${wrong.length})`]));
  wrong.forEach(id => {
    const item = itemsById[id];
    const mine = state.labels[id];
    mount.appendChild(el('div', { class: 'jc-card jc-mismatch' }, [
      el('p', {}, [el('strong', {}, [id]), ` — you said ${mine.verdict.toUpperCase()}, answer key says ${item.gold_label.toUpperCase()}`]),
      el('p', { class: 'jc-muted' }, ['Customer: ' + item.customer_input.slice(0, 160) + (item.customer_input.length > 160 ? '…' : '')]),
      el('p', { class: 'jc-muted' }, ['Agent: ' + item.agent_response.slice(0, 200) + (item.agent_response.length > 200 ? '…' : '')]),
      el('p', {}, [el('em', {}, ['Why: ']), item.notes]),
      mine.note ? el('p', {}, [el('em', {}, ['Your note: ']), mine.note]) : null,
    ]));
  });
}

// ---------------------------------------------------------------------------
//  Stage: Export
// ---------------------------------------------------------------------------

function buildExport() {
  return {
    tool: 'judge-calibration-game',
    version: JC_VERSION,
    exported_at: new Date().toISOString(),
    provider: state.provider,
    model: state.model,
    dataset: 'pronto-calibration-items.json (24 items)',
    labels_required: LABELS_TO_UNLOCK,
    labels: state.labels,
    criteria: state.criteria,
    runs: state.runs.map(r => ({
      id: r.id, ts: r.ts, model: r.model, partial: r.partial,
      metrics: r.metrics,
      results: r.results,
    })),
    gold_check: Object.keys(state.labels).map(id => ({
      itemId: id,
      mine: state.labels[id].verdict,
      gold: itemsById[id].gold_label,
      agree: state.labels[id].verdict === itemsById[id].gold_label,
      failure_mode: itemsById[id].failure_mode,
    })),
  };
}

function exportMarkdown(exp) {
  const L = [];
  L.push('# Judge Calibration — Pronto');
  L.push('');
  L.push(`Exported ${exp.exported_at} · model ${exp.model} · ${Object.keys(exp.labels).length} labels`);
  L.push('');
  L.push('## Criteria');
  L.push('');
  L.push('```');
  L.push(exp.criteria || '(none)');
  L.push('```');
  exp.runs.forEach((r, i) => {
    const m = r.metrics;
    L.push('');
    L.push(`## Run ${i + 1} — ${r.ts}${r.partial ? ' (partial)' : ''}`);
    L.push('');
    L.push(`- n=${m.n} · accuracy=${m.accuracy.toFixed(2)} · precision=${m.precision.toFixed(2)} · recall=${m.recall.toFixed(2)} · F1=${m.f1.toFixed(2)} · κ=${fmtKappa(m)}`);
    L.push(`- confusion: TP=${m.matrix.tp} TN=${m.matrix.tn} FP=${m.matrix.fp} FN=${m.matrix.fn}`);
  });
  const disag = exp.gold_check.filter(g => !g.agree);
  L.push('');
  L.push(`## Gold check — ${exp.gold_check.length - disag.length}/${exp.gold_check.length} agree with answer key`);
  disag.forEach(g => L.push(`- ${g.itemId}: mine=${g.mine} gold=${g.gold}${g.failure_mode ? ` (${g.failure_mode})` : ''}`));
  L.push('');
  return L.join('\n');
}

function downloadBlob(blob, filename) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}

function renderExport(mount) {
  mount.appendChild(el('h2', { class: 'rb-stage__title' }, ['Export your work']));
  mount.appendChild(el('p', { class: 'rb-stage__lede' }, ['Download everything — labels, criteria, runs, metrics, gold comparison. Commit it next to your evals.']));
  const exp = buildExport();
  mount.appendChild(el('div', { class: 'jc-row' }, [
    btn('Download JSON', 'rb-btn--primary', () =>
      downloadBlob(new Blob([JSON.stringify(exp, null, 2)], { type: 'application/json' }), 'judge-calibration-export.json')),
    btn('Download Markdown', 'rb-btn--ghost', () =>
      setTimeout(() => downloadBlob(new Blob([exportMarkdown(exp)], { type: 'text/markdown' }), 'judge-calibration-export.md'), 150)),
  ]));
  mount.appendChild(el('p', { class: 'jc-muted', style: 'margin-top:12px' },
    ['Your API key is never included in exports. Labels: ' + Object.keys(exp.labels).length + ' · Runs: ' + exp.runs.length]));
}

// ---------------------------------------------------------------------------
//  Boot
// ---------------------------------------------------------------------------

async function boot() {
  state = loadState() || defaultState();
  if (isMock() && state.provider !== 'mock') {
    state.provider = 'mock';
    state.model = 'mock-judge-v1';
  }
  try {
    const res = await fetch('./pronto-calibration-items.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    items = await res.json();
  } catch (e) {
    document.querySelector('[data-role="stage-mount"]').appendChild(
      errBox('Could not load the practice dataset (./pronto-calibration-items.json): ' + e.message));
    return;
  }
  itemsById = Object.fromEntries(items.map(i => [i.id, i]));
  if (!state.order.length) state.order = shuffle(items.map(i => i.id));
  // drop order entries for items that no longer exist
  state.order = state.order.filter(id => itemsById[id]);
  saveState(state);

  const resetBtn = document.querySelector('[data-role="reset"]');
  if (resetBtn) resetBtn.addEventListener('click', () => {
    if (confirm('Start over? This clears labels, runs, and criteria in this browser.')) {
      try { localStorage.removeItem(STATE_KEY); } catch (_) {}
      state = defaultState();
      if (isMock()) { state.provider = 'mock'; state.model = 'mock-judge-v1'; }
      state.order = shuffle(items.map(i => i.id));
      saveState(state);
      render();
    }
  });

  render();
}

if (typeof document !== 'undefined') {
  boot();
}
