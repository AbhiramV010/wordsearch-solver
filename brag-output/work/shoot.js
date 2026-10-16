const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve('comp.html'));
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
  if (mode === 'stills') {
    for (const t of args) { await page.evaluate(t => render(+t), t); await page.screenshot({ path: `still-${t}.png` }); }
  } else {
    const fps = 30, total = Math.round(+args[0] * fps);
    require('fs').mkdirSync('frames', { recursive: true });
    for (let f = 0; f < total; f++) {
      await page.evaluate(t => render(t), f / fps);
      await page.screenshot({ path: `frames/f${String(f).padStart(4, '0')}.png` });
    }
  }
  await browser.close();
})();
