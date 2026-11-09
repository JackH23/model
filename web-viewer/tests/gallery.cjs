const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const { models } = require('../src/catalog.js');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  let glbRequests = 0;
  page.on('request', request => { if (request.url().endsWith('.glb')) glbRequests++; });
  const base = process.env.TEST_URL || 'http://127.0.0.1:4174/model/';
  try {
    await page.goto(base);
    assert.equal(await page.locator('.model-card').count(), models.length);
    assert.equal(glbRequests, 0);
    assert.equal(await page.locator('#model-count').textContent(), String(models.length));
    await page.locator('#model-search').fill('missing');
    assert.equal(await page.locator('.model-card').count(), 0);
    assert.equal(await page.locator('#catalog-empty').isVisible(), true);
    for (const [query, count] of [['Ashwick', 34], ['Crystalbrook', 1], ['robo', 1]]) {
      await page.locator('#model-search').fill(query);
      assert.equal(await page.locator('.model-card').count(), count);
    }
    await page.locator('#model-search').fill('');
    await page.locator('#collection').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => [...document.querySelectorAll('.model-card img')].slice(0, 3).every(image => image.complete && image.naturalWidth > 0));
    await page.screenshot({ path: 'test-results/gallery-desktop.png' });
    await page.locator('#model-search').fill('robo');
    await page.locator('.model-card').click();
    await page.waitForFunction(() => window.roboJack?.ready, null, { timeout: 60000 });
    assert.equal(await page.evaluate(() => window.roboJack.parts.length), 387);
    await page.locator('.library-back').click();
    assert.equal(await page.locator('.model-card').count(), models.length);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('#collection').scrollIntoViewIfNeeded();
    await page.screenshot({ path: 'test-results/gallery-mobile.png' });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []);
    console.log(`PASS: ${models.length} cards, lazy model loading, collection search, viewer navigation, mobile layout`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
