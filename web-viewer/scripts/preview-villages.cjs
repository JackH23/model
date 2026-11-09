const { chromium } = require('playwright');
const { readFileSync, writeFileSync } = require('node:fs');
const assert = require('node:assert/strict');

(async () => {
  const manifest = JSON.parse(readFileSync('public/models/villages/manifest.json', 'utf8'));
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const results = [];
  try {
    for (const model of manifest) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      await page.goto(`${process.env.TEST_URL || 'http://127.0.0.1:4174/model/'}viewer.html?model=${model.id}`);
      await page.waitForFunction(() => window.roboJack?.ready || document.querySelector('#loading')?.dataset.stage === 'error', null, { timeout: 120000 });
      assert.equal(await page.evaluate(() => window.roboJack.ready), true, `${model.id}: ${errors.join('\n')}`);
      const metrics = await page.evaluate(() => window.roboJack.metrics);
      assert.equal(metrics.partCount, model.partCount, model.id);
      assert.ok(metrics.triangles > 0, model.id);
      assert.deepEqual(errors, [], model.id);
      if (['crystalbrook-village', 'ashwick-walled-village', 'ashwick-small-cottage'].includes(model.id)) {
        await page.screenshot({ path: `test-results/${model.id}-desktop.png` });
      }
      await page.addStyleTag({ content: '#viewport { position:fixed!important; inset:0 auto auto 0!important; width:900px!important; height:900px!important; z-index:100!important; background:radial-gradient(ellipse at center,#2c454d,#132027); }' });
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      await page.locator('#fit-model').evaluate(button => button.click());
      await page.waitForTimeout(700);
      // Leave room for the existing card's landscape crop of the square preview.
      if (!model.id.endsWith('village')) {
        await page.locator('#viewport canvas').hover();
        await page.mouse.wheel(0, 180);
        await page.waitForTimeout(500);
      }
      await page.locator('#viewport canvas').screenshot({ path: `public/models/villages/${model.id}-preview.jpg`, type: 'jpeg', quality: 88 });
      results.push({ id: model.id, ...metrics, readyMs: await page.evaluate(() => window.roboJack.loading.readyMs) });
      console.log(`VERIFIED ${model.id}: ${metrics.partCount} parts; preview saved`);
      await page.close();
    }
    writeFileSync('test-results/village-browser.json', JSON.stringify(results, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
