// Run: osascript -l JavaScript tests/story.test.js
ObjC.import('Foundation');
function run(argv) {
  const path = (argv[0] || '.') + '/index.html';
  const s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  if (s.isNil()) return 'FAIL: index.html missing';
  const html = s.js;
  const m = html.match(/<script id="story">([\s\S]*?)<\/script>/);
  if (!m) return 'FAIL: story script block missing';
  const api = (new Function(m[1] + '\nreturn {STORY, pickFinale, applyEffects, resetState};'))();
  const { STORY, pickFinale, applyEffects, resetState } = api;
  const P = STORY.passages, ids = Object.keys(P), out = []; let fails = 0;
  function t(name, fn) { try { fn(); out.push('ok   ' + name); } catch (e) { fails++; out.push('FAIL ' + name + ': ' + e.message); } }
  function ok(c, msg) { if (!c) throw new Error(msg); }
  const finales = ids.filter(i => P[i].finale);
  t('every link resolves', () => { for (const id of ids) for (const c of P[id].choices || []) ok(c.to === '@finale' || P[c.to], id + ' -> ' + c.to); });
  t('non-endings have >=2 choices', () => { for (const id of ids) if (!P[id].ending) ok((P[id].choices || []).length >= 2, id + ' dead end'); });
  t('all reachable from start', () => {
    const seen = new Set([STORY.start]), q = [STORY.start];
    while (q.length) { const id = q.shift(); for (const c of P[id].choices || []) for (const x of (c.to === '@finale' ? finales : [c.to])) if (!seen.has(x)) { seen.add(x); q.push(x); } }
    const orphan = ids.filter(i => !seen.has(i)); ok(!orphan.length, 'orphans: ' + orphan);
  });
  t('endings exist, 25-35 passages', () => { ok(ids.some(i => P[i].ending), 'no ending'); ok(ids.length >= 25 && ids.length <= 35, 'count ' + ids.length); });
  t('all characters + fart gun', () => { const tx = JSON.stringify(STORY).toLowerCase();
    for (const w of ['gru','lucy','margo','edith','agnes','kyle','minion','unicorn','fart gun','snoozemonger']) ok(tx.includes(w), 'missing ' + w); });
  t('stats clamp at 0', () => ok(applyEffects({chaos:0,bananas:0},{bananas:-5}).bananas === 0, 'negative'));
  t('reset', () => { const r = resetState(); ok(r.chaos === 0 && r.bananas === 0 && Object.keys(r).length === 2, 'bad reset'); });
  t('pickFinale returns real ending', () => { for (const s of [[0,0],[99,99],[0,99],[99,0]]) { const id = pickFinale({chaos:s[0],bananas:s[1]}); ok(P[id] && P[id].ending, 'bad ' + id); } });
  out.push(fails ? fails + ' FAILED' : 'ALL PASS (' + ids.length + ' passages)');
  return out.join('\n');
}
