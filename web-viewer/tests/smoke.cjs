const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const output = path.join(process.cwd(), 'test-results');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  const failures = [];
  const checks = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('requestfailed', (r) => failures.push(`${r.url()} ${r.failure()?.errorText}`));
  try {
    await page.goto(new URL('viewer.html?model=robo-jack', (process.env.TEST_URL || 'http://127.0.0.1:5173/').replace(/\/?$/, '/')).href, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.roboJack?.ready, { timeout: 60000 });
    const originalPositions = await page.evaluate(() => window.roboJack.parts.map(p => p.position));
    assert.equal(await page.evaluate(() => window.roboJack.parts.length), 387);
    assert.equal(await page.locator('.part-row').count(), 387);
    assert.equal(await page.evaluate(() => window.roboJack.parts.some((p) => p.name === 'Studio_Ground')), false);
    checks.push('GLB loads all 387 individually named robot parts; no studio ground exported');
    await page.screenshot({ path: path.join(output, 'desktop.png') });

    // Pick a visible surface through the actual canvas/raycaster, not the object list.
    const point = await page.evaluate(() => window.roboJack.screenPoint('Finish_QuadCurvedVisor'));
    assert.ok(point && Number.isFinite(point.x));
    await page.mouse.click(point.x, point.y);
    assert.ok(await page.evaluate(() => window.roboJack.selected), 'Canvas click must select a model part');
    assert.equal(await page.locator('#selection').isVisible(), true);
    checks.push('Canvas raycasting selects a real mesh and opens its inspector');

    await page.locator('#search').fill('ReactorRecessedLens');
    const part = page.locator('button[data-part="Attach_ReactorRecessedLens"]');
    await part.click();
    assert.equal(await page.evaluate(() => window.roboJack.selected), 'Attach_ReactorRecessedLens');
    assert.equal(await page.locator('.part-row').count(), 1);
    checks.push('Part search filters the hierarchy and selects the named reactor lens');

    await page.locator('#isolate').click();
    assert.equal(await page.evaluate(() => window.roboJack.parts.filter((p) => p.visible).length), 1);
    await page.locator('#hide-selected').click();
    assert.equal(await page.evaluate(() => window.roboJack.parts.filter((p) => p.visible).length), 0);
    await page.locator('#hide-selected').click();
    assert.equal(await page.evaluate(() => window.roboJack.parts.filter((p) => p.visible).length), 1);
    await page.locator('#show-all').click();
    assert.equal(await page.evaluate(() => window.roboJack.parts.filter((p) => p.visible).length), 387);
    checks.push('Isolation, hide/show, and show-all correctly control mesh visibility');

    const initial = await page.evaluate(() => window.roboJack.parts.find((p) => p.name === window.roboJack.selected).position);
    await page.locator('#move-x').fill('0.12');
    const moved = await page.evaluate(() => window.roboJack.parts.find((p) => p.name === window.roboJack.selected));
    assert.equal(moved.offset[0], 0.12);
    assert.ok(Math.abs(moved.position[0] - initial[0] - 0.12) < 1e-5);
    await page.locator('#reset-part').click();
    assert.deepEqual(await page.evaluate(() => window.roboJack.parts.find((p) => p.name === window.roboJack.selected).offset), [0, 0, 0]);
    checks.push('Position offset moves the selected object by 0.12 m and reset restores it');

    await page.locator('#explode').fill('75');
    assert.equal(await page.locator('#explode-value').textContent(), '75%');
    assert.ok(await page.evaluate(() => window.roboJack.parts.some((p) => Math.hypot(...p.position) > 0.15)));
    await page.locator('#wireframe').check();
    await page.locator('[data-view="side"]').click();
    await page.waitForTimeout(650);
    assert.ok((await page.locator('[data-view="side"]').getAttribute('class')).includes('active'));
    await page.locator('#focus').click();
    await page.waitForTimeout(600);
    checks.push('Exploded view, wireframe, side preset, and focus run without rendering errors');

    const downloadPromise = page.waitForEvent('download');
    await page.locator('#download-shot').click();
    const download = await downloadPromise;
    assert.equal(download.suggestedFilename(), 'robo-jack-view.png');
    await download.saveAs(path.join(output, 'snapshot.png'));
    checks.push('Save image downloads a PNG of the current 3D canvas');

    await page.locator('#reset-all').click();
    await page.waitForTimeout(650);
    assert.equal(await page.evaluate(() => window.roboJack.selected), null);
    assert.ok(await page.evaluate(() => window.roboJack.parts.every(p => p.visible && p.offset.every(v => v === 0))));
    assert.deepEqual(await page.evaluate(() => window.roboJack.parts.map(p => p.position)), originalPositions);
    checks.push('Reset scene restores all visibility, positions, explosion and selection');
    await page.screenshot({ path: path.join(output, 'desktop-final.png') });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    assert.equal(await page.locator('#viewport canvas').isVisible(), true);
    await page.screenshot({ path: path.join(output, 'mobile.png'), fullPage: true });
    checks.push('Mobile layout keeps the canvas and controls accessible without horizontal overflow');
    assert.deepEqual(errors, []);
    assert.deepEqual(failures, []);
    const metrics = await page.evaluate(() => window.roboJack.metrics);
    fs.writeFileSync(path.join(output, 'smoke-report.json'), JSON.stringify({ passed: true, checks, metrics, errors, failures }, null, 2));
    console.log(JSON.stringify({ passed: true, checks, metrics }, null, 2));
  } catch (error) {
    await page.screenshot({ path: path.join(output, 'failure.png'), fullPage: true }).catch(() => {});
    fs.writeFileSync(path.join(output, 'smoke-report.json'), JSON.stringify({ passed: false, checks, errors, failures, error: error.stack }, null, 2));
    throw error;
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
