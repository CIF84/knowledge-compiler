// Synthetic offline renderer smoke only. No benchmark source/output is accepted
// or loaded from disk, no installs/retrieval, and every browser request is denied.
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const {chromium} = require(process.env.BENCH_PLAYWRIGHT);
const fixture = JSON.parse(fs.readFileSync(0, 'utf8'));
if (fixture.kind !== 'SYNTHETIC_OFFLINE_CONTRACT_TEST') throw Error('Not a synthetic contract fixture');
const browser = await chromium.launch({headless:true,executablePath:process.env.BENCH_BROWSER_EXECUTABLE,
  args:['--disable-background-networking','--disable-component-update','--no-first-run']});
const errors = [], requests = [];
try {
  let tested = 0;
  for (const viewport of [{width:1280,height:900},{width:390,height:844}]) {
    // A fresh document realm prevents redeclaring frozen native top-level consts.
    const page = await browser.newPage({offline:true,viewport});
    page.on('pageerror', e => errors.push(String(e)));
    await page.route('**/*', route => {requests.push(route.request().url());return route.abort();});
    for (const html of fixture.neutral_html) {
      await page.setContent(html.replace(/<link[^>]*>/g,''));
      await page.addStyleTag({content:fixture.styles['neutral.css']});
      if (!await page.locator('main').count()) throw Error('Neutral main absent');
      if (!await page.locator('pre').count()) throw Error('Original source recovery absent');
      tested++;
    }
    const html = fixture.current_html;
    const invocation = html.match(/<script>\s*(renderCurrent\([\s\S]*?)<\/script>/)[1];
    await page.setContent(html.replace(/<link[^>]*>/g,'').replace(/<script[\s\S]*?<\/script>/g,''));
    for (const raw of Object.values(fixture.styles)) await page.addStyleTag({content:raw});
    for (const name of ['current-native-plan.js','current-native-diagram.js','c0-adapter.js'])
      await page.addScriptTag({content:fixture.scripts[name]});
    await page.evaluate(invocation);
    const count = await page.locator('#current select option').count();
    if (count !== fixture.current_focus_count) throw Error('Current focus menu incomplete');
    for (let i=0;i<count;i++) {
      await page.locator('#current select').selectOption(String(i));
      if (!await page.locator('#current .strategy-surface').count()) throw Error('Current renderer absent');
      if (await page.locator('.strategy-badge,.learning-surface-marker').count()) throw Error('Metadata chrome leaked');
    }
    if (!await page.locator('.spec038-diagram').count()) throw Error('Native diagram absent');
    tested++;
    await page.close();
  }
  if (errors.length || requests.length) throw Error(JSON.stringify({errors,requests}));
  console.log(JSON.stringify({result:'PASS',synthetic_viewport_checks:tested,
    current_focus_count:fixture.current_focus_count,browser_requests:requests.length,
    benchmark_outputs:0,provider_calls:0}));
} finally {await browser.close();}
