const $ = id => document.getElementById(id);
const tabs = ['reading', 'corrections', 'source', 'integration'];
const canonicalRef = /^[1-3]?[A-Za-z]+\.[1-9][0-9]*\.[1-9][0-9]*$/;
const loopback = ['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname);
let entries = new Map();
let current = null;
let localEvidence = null;
let serial = 0;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function card(title, description, extraClass = '') {
  const node = el('article', `data-card ${extraClass}`);
  node.append(el('h4', '', title), el('p', '', description));
  return node;
}

function external(label, url) {
  const a = el('a', '', label);
  a.href = url;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  return a;
}

function setStatus(message) { $('status').textContent = message; }

function renderReading() {
  const root = $('reading-content');
  root.replaceChildren();
  if (localEvidence?.state === 'indexed_transcription') {
    root.append(el('p', 'evidence-note', 'Local research adapter · official project XML transcription. This display is confined to your loopback server.'));
    const main = card('Project main reading', '');
    main.querySelector('p').textContent = localEvidence.initial_text;
    main.querySelector('p').className = 'greek';
    root.append(main);
    const info = card('Physical locator', `Page ${localEvidence.page} · folio ${localEvidence.folio} · scribe ${localEvidence.scribe || 'unrecorded'}`);
    root.append(info);
  } else {
    root.append(el('p', 'evidence-note', 'The public prototype distributes no transcription or manuscript image. The source institution remains authoritative for the reading.'));
    const source = card('Read this passage at the source', 'The official manuscript viewer provides the image, transcription, and translations under its own terms.');
    source.append(external('Open official manuscript view ↗', current.url));
    root.append(source);
  }
}

function renderCorrections() {
  const root = $('corrections-content');
  root.replaceChildren();
  if (localEvidence?.state === 'indexed_transcription') {
    root.append(el('p', 'evidence-note', 'Correction hands are labels from the XML transcription. They are not a reconstructed copying sequence.'));
    const readings = localEvidence.corrections || [];
    if (!readings.length) root.append(card('No correction row in this pilot span', 'This is an index observation, not proof that the physical manuscript was never corrected.'));
    for (const reading of readings) {
      const title = reading.reading_order === 0 ? 'Main reading · project XML' : `Correction · ${reading.hand || 'unidentified hand'}`;
      const row = card(title, '');
      row.querySelector('p').textContent = reading.text || 'Omission or unreadable reading';
      row.querySelector('p').className = 'greek';
      root.append(row);
    }
  } else {
    root.append(card('Correction view ready for approved data', 'The component can present distinct reading hands, omissions, and uncertainty. No correction text is bundled with this public demo.'));
    root.append(el('p', 'evidence-note', 'Open the official project viewer to inspect the actual correction evidence.'));
  }
}

function renderSource() {
  const root = $('source-content');
  root.replaceChildren();
  const path = el('ol', 'path-list');
  const steps = [
    ['Passage label', current.ref, 'A navigation label, not a proved translation alignment.'],
    ['Physical witness', 'Codex Sinaiticus · GA 01', 'The manuscript is held across partner institutions.'],
    ['Electronic transcription', localEvidence?.state === 'indexed_transcription' ? `Project XML ${localEvidence.source_version}` : 'Project-hosted source', 'No manuscript scan is bundled in this interface.'],
    ['Official locator', 'Open source record', 'The project site supplies the authoritative image and transcription.'],
  ];
  for (const [kind, label, detail] of steps) {
    const row = el('li');
    row.append(el('span', 'path-dot'));
    const content = el('div');
    content.append(el('b', '', `${kind} · ${label}`), el('small', '', detail));
    row.append(content);
    path.append(row);
  }
  root.append(path);
  const link = card('Citation and rights', 'Codex Sinaiticus Project. The XML transcription is CC BY-NC-SA 3.0. Electronic copy and image permissions are governed separately by the holding institutions.');
  link.append(external('Official source ↗', current.url));
  root.append(link);
  if (localEvidence?.import_run_id) root.append(el('p', 'evidence-note', `Local index import: ${localEvidence.import_run_id} · fragment SHA-256: ${localEvidence.fragment_sha256}`));
}

function renderIntegration() {
  const root = $('integration-content');
  root.replaceChildren();
  root.append(card('A small handoff surface', 'A host portal can supply a locus URI, approved reading annotations, an IIIF canvas, and a rights decision. The component does not need to own the manuscript collection.'));
  const sample = {ref: current.ref, source_uri: current.url, rights: {text: 'source_link_only', image: 'source_link_only'}, annotations: 'supplied by host only'};
  root.append(el('pre', 'integration-code', JSON.stringify(sample, null, 2)));
  root.append(el('p', 'evidence-note', 'An upstream React portal could embed this panel or reuse its accessible interaction pattern. See INTEGRATION.md for the typed adapter contract.'));
}

function render() {
  $('detail-ref').textContent = current.ref;
  $('stage-ref').textContent = current.ref;
  $('official-link').href = current.url;
  $('mode-pill').textContent = localEvidence?.state === 'indexed_transcription' ? 'Local verified XML' : 'Source link only';
  renderReading(); renderCorrections(); renderSource(); renderIntegration();
}

function selectTab(name, focus = false) {
  for (const tab of tabs) {
    const chosen = tab === name;
    const button = $(`tab-${tab}`);
    button.setAttribute('aria-selected', String(chosen));
    button.tabIndex = chosen ? 0 : -1;
    $(`panel-${tab}`).hidden = !chosen;
  }
  if (focus) $(`tab-${name}`).focus();
}

async function openRef(ref, updateUrl = true) {
  const request = ++serial;
  const key = ref.trim();
  if (!canonicalRef.test(key) || !entries.has(key)) {
    setStatus('This bounded study links only Matt.7.7–8 and Luke.11.9–10.');
    return;
  }
  setStatus('');
  current = entries.get(key);
  localEvidence = null;
  $('ref-input').value = key;
  if (updateUrl) {
    const url = new URL(location.href);
    url.searchParams.set('ref', key);
    history.replaceState(null, '', url);
  }
  render();
  if (loopback && new URLSearchParams(location.search).get('mode') === 'local') {
    try {
      const response = await fetch(`./api/evidence?ref=${encodeURIComponent(key)}`, {cache: 'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (request !== serial) return;
      if (data.ref !== key || !['indexed_transcription', 'outside_curated_pilot', 'index_unavailable', 'index_revision_mismatch'].includes(data.state)) throw new Error('Unexpected adapter response');
      localEvidence = data;
      render();
    } catch {
      if (request === serial) setStatus('Local evidence adapter unavailable. Official source links remain usable.');
    }
  }
}

async function start() {
  const response = await fetch('./data/loci.json', {cache: 'no-store'});
  if (!response.ok) throw new Error('Reference catalog unavailable');
  const catalog = await response.json();
  if (catalog.schema_version !== 1 || !Array.isArray(catalog.loci)) throw new Error('Unsupported reference catalog');
  for (const row of catalog.loci) {
    if (!canonicalRef.test(row.ref) || !/^https:\/\/codexsinaiticus\.org\/en\/manuscript\.aspx\?/.test(row.url)) throw new Error('Unsafe catalog row');
    entries.set(row.ref, row);
  }
  const requested = new URLSearchParams(location.search).get('ref') || 'Luke.11.10';
  await openRef(requested, false);
}

$('ref-form').addEventListener('submit', event => { event.preventDefault(); openRef($('ref-input').value); });
for (const tab of tabs) {
  $(`tab-${tab}`).addEventListener('click', () => selectTab(tab));
  $(`tab-${tab}`).addEventListener('keydown', event => {
    const index = tabs.indexOf(tab);
    const next = event.key === 'ArrowRight' ? tabs[(index + 1) % tabs.length] :
                 event.key === 'ArrowLeft' ? tabs[(index + tabs.length - 1) % tabs.length] :
                 event.key === 'Home' ? tabs[0] : event.key === 'End' ? tabs[tabs.length - 1] : null;
    if (next) { event.preventDefault(); selectTab(next, true); }
  });
}
start().catch(() => setStatus('Reference catalog unavailable. Try the official Codex Sinaiticus site link above.'));
