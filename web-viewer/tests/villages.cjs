const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { models } = require('../src/catalog.js');

(async () => {
  const manifest = JSON.parse(fs.readFileSync('public/models/villages/manifest.json', 'utf8'));
  assert.equal(manifest.length, 35);
  assert.equal(models.length, 36);
  assert.equal(new Set(models.map(model => model.id)).size, 36);
  for (const model of models) {
    assert.ok(fs.statSync(`public/${model.file}`).size > 0, model.id);
    assert.ok(fs.statSync(`public/${model.preview}`).size > 0, model.id);
    if (model.id !== 'robo-jack') {
      const entry = manifest.find(entry => entry.id === model.id);
      assert.equal(entry.partCount, model.partCount);
      assert.ok(entry.maxBoundsDeviationMeters <= 0.001, model.id);
      assert.equal(new Set(entry.parts.map(part => part.sourceName)).size, entry.partCount);
    }
  }
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  const base = process.env.TEST_URL || 'http://127.0.0.1:4174/model/';
  try {
    const interactionModels = new Set(['crystalbrook-village', 'ashwick-walled-village', 'ashwick-small-cottage', 'ashwick-blacksmith-workshop', 'ashwick-supply-sack']);
    for (const { id } of models.filter(model => model.grouping !== 'robot')) {
      await page.goto(`${base}viewer.html?model=${id}`);
      await page.waitForFunction(() => window.roboJack?.ready, null, { timeout: 120000 });
      const model = models.find(model => model.id === id);
      assert.equal(await page.locator('.part-row').count(), model.partCount);
      if (!interactionModels.has(id)) {
        console.log(`PASS: ${id} loads all ${model.partCount} source parts`);
        continue;
      }
      const first = await page.evaluate(() => window.roboJack.parts[0]);
      await page.locator('#search').fill(first.name);
      await page.locator('.part-row button').first().click();
      assert.equal(await page.evaluate(() => window.roboJack.selected), first.name);
      await page.locator('#isolate').click();
      assert.equal(await page.evaluate(() => window.roboJack.parts.filter(part => part.visible).length), 1);
      await page.locator('#hide-selected').click();
      assert.equal(await page.evaluate(() => window.roboJack.parts.filter(part => part.visible).length), 0);
      await page.locator('#hide-selected').click();
      const beforeMove = await page.evaluate(name => window.roboJack.screenPoint(name), first.name);
      await page.locator('#move-x').fill('0.25');
      assert.equal(await page.evaluate(name => window.roboJack.parts.find(part => part.name === name).offset[0], first.name), 0.25);
      const afterMove = await page.evaluate(name => window.roboJack.screenPoint(name), first.name);
      assert.ok(Math.hypot(afterMove.x - beforeMove.x, afterMove.y - beforeMove.y) > 0.1, `${id}: source geometry must actually move`);
      await page.locator('#reset-part').click();
      const resetPoint = await page.evaluate(name => window.roboJack.screenPoint(name), first.name);
      assert.ok(Math.hypot(resetPoint.x - beforeMove.x, resetPoint.y - beforeMove.y) < 0.01, `${id}: source transform must restore`);
      if (id === 'crystalbrook-village') {
        await page.keyboard.press('Escape');
        const point = await page.evaluate(name => window.roboJack.screenPoint(name), first.name);
        await page.mouse.click(point.x, point.y);
        assert.ok(await page.evaluate(() => window.roboJack.selected), 'Picking a material primitive must select its source part');
        await page.locator('#search').fill(first.name);
        await page.locator('.part-row button').first().click();
      }
      await page.locator('#focus').click();
      await page.locator('#reset-all').click();
      assert.equal(await page.evaluate(() => window.roboJack.parts.filter(part => part.visible).length), model.partCount);
      await page.locator('#explode').fill('50');
      assert.ok(await page.evaluate(() => window.roboJack.parts.some(part => part.position.some(value => Math.abs(value) > 0.01))));
      await page.locator('#wireframe').check();
      await page.locator('#reset-all').click();
      await page.setViewportSize({ width: 390, height: 844 });
      await page.screenshot({ path: `test-results/${id}-mobile.png` });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `Mobile overflow: ${id}`);
      await page.setViewportSize({ width: 1440, height: 1000 });
      console.log(`PASS: ${id} selection, search, isolation, visibility, offsets, focus, reset, explosion, mobile`);
    }
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
