const { chromium } = require('playwright');
const { createServer } = require('node:http');
const { readFileSync, writeFileSync } = require('node:fs');
const { resolve, extname, sep } = require('node:path');
const { gzipSync } = require('node:zlib');

async function serve(directory) {
  const root = resolve(directory);
  const cache = new Map();
  const server = createServer((request, response) => {
    const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).replace(/^\/model\//, '');
    const file = resolve(root, relative);
    if (!file.startsWith(root + sep)) { response.writeHead(403).end(); return; }
    try {
      if (!cache.has(file)) {
        const glb = file.endsWith('.glb');
        const bytes = readFileSync(file);
        cache.set(file, { bytes: glb ? gzipSync(bytes) : bytes, glb });
      }
      const { bytes, glb } = cache.get(file);
      const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.glb': 'model/gltf-binary' };
      response.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream', 'Content-Length': bytes.length, ...(glb ? { 'Content-Encoding': 'gzip' } : {}) });
      response.end(bytes);
    } catch { response.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return server;
}

(async () => {
  const servers = { before: await serve(process.env.BASELINE_DIR || 'test-results/baseline-dist'), after: await serve('dist') };
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const measurements = [];
  try {
    for (let trial = 0; trial < 3; trial++) {
      for (const variant of trial % 2 ? ['after', 'before'] : ['before', 'after']) {
        const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
        const page = await context.newPage();
        const cdp = await context.newCDPSession(page);
        await cdp.send('Network.enable');
        await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
        await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 40, downloadThroughput: 625000, uploadThroughput: 1250000 });
        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
        await page.goto(`http://127.0.0.1:${servers[variant].address().port}/model/viewer.html?model=crystalbrook-village`, { waitUntil: 'domcontentloaded', timeout: 120000 });
        await page.waitForFunction(() => window.roboJack?.ready, null, { timeout: 120000 });
        const result = await page.evaluate(({ variant, trial }) => ({ variant, trial, navigationToReadyMs: performance.now(), ...window.roboJack.loading, parts: window.roboJack.parts.length, heapBytes: performance.memory?.usedJSHeapSize, resource: performance.getEntriesByType('resource').filter(entry => entry.name.includes('.glb')).map(entry => ({ duration: entry.duration, encodedBytes: entry.encodedBodySize, decodedBytes: entry.decodedBodySize })) }), { variant, trial });
        measurements.push(result);
        console.log(JSON.stringify(result));
        await context.close();
      }
    }
    const median = values => values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
    const medians = Object.fromEntries(['before', 'after'].map(variant => [variant, median(measurements.filter(result => result.variant === variant).map(result => result.navigationToReadyMs))]));
    const report = { conditions: '5 Mbps, 40 ms latency, gzip responses, cold cache, 4x CPU slowdown, 1920x1080', measurements, medians, improvementPercent: (1 - medians.after / medians.before) * 100 };
    writeFileSync('test-results/village-loading-comparison.json', JSON.stringify(report, null, 2));
    console.log(JSON.stringify({ medians, improvementPercent: report.improvementPercent }));
  } finally {
    await browser.close();
    for (const server of Object.values(servers)) { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); }
  }
})().catch(error => { console.error(error); process.exit(1); });
