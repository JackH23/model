const { chromium } = require('playwright');
const { createServer } = require('node:http');
const { readFileSync } = require('node:fs');
const { gzipSync } = require('node:zlib');
const assert = require('node:assert/strict');

(async () => {
  const bytes = readFileSync('public/models/villages/crystalbrook-village.meshopt-v2.glb');
  const compressed = gzipSync(bytes);
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  const server = createServer(async (request, response) => {
    response.writeHead(200, { 'Content-Type': 'model/gltf-binary', 'Content-Encoding': 'gzip', 'Content-Length': compressed.length, 'Access-Control-Allow-Origin': '*' });
    const split = Math.floor(compressed.length * 0.95);
    response.write(compressed.subarray(0, split));
    await gate;
    response.end(compressed.subarray(split));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  try {
    const page = await browser.newPage();
    await page.route('**/*.glb', route => route.continue({ url: `http://127.0.0.1:${server.address().port}/model.glb` }));
    await page.goto('http://127.0.0.1:4174/model/viewer.html?model=crystalbrook-village', { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => Number(document.querySelector('#loading').dataset.percent) >= 70, null, { timeout: 60000 });
    assert.equal(await page.evaluate(() => window.roboJack.loading.stage), 'downloading');
    assert.equal(await page.evaluate(() => window.roboJack.loading.downloadMs), null);
    assert.ok(Number(await page.locator('#loading').getAttribute('data-percent')) < 85);
    assert.ok(!(await page.locator('#progress').textContent()).includes('Download complete'));
    release();
    await page.waitForFunction(() => window.roboJack.ready, null, { timeout: 60000 });
    assert.equal(await page.evaluate(() => window.roboJack.parts.length), 161);
    assert.equal(await page.locator('#loading').getAttribute('data-percent'), '100');
    await page.close();
    const truncated = await browser.newPage();
    await truncated.route('**/*.glb', route => route.fulfill({ status: 200, contentType: 'model/gltf-binary', body: bytes.subarray(0, 1024) }));
    await truncated.goto('http://127.0.0.1:4174/model/viewer.html?model=crystalbrook-village');
    await truncated.waitForFunction(() => window.roboJack?.loading.stage === 'error');
    assert.equal(await truncated.evaluate(() => window.roboJack.ready), false);
    assert.notEqual(await truncated.locator('#loading').getAttribute('data-percent'), '100');
    console.log('PASS: gzip download stays below 85% until EOF; complete model renders; truncated download fails clearly');
  } finally {
    release();
    await browser.close();
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exit(1); });
