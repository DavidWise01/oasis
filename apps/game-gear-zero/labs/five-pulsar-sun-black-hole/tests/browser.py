import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
HTML=Path(__file__).resolve().parents[1].joinpath('index.html').read_text()
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True)
  page=await browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content(HTML,wait_until='load')
  m=await page.evaluate('FiveGyro.groundMetrics()')
  assert m['sunResidual']<1e-8 and m['pulsars']['emission']>0 and len(m['pulsars']['nodes'])==5
  await page.click('#demoGround')
  m=await page.evaluate('FiveGyro.groundMetrics()')
  assert m['rawStress']>.5 and m['absorbed']>.44 and not m['flare']
  await page.click('#toggleGround')
  m=await page.evaluate('FiveGyro.groundMetrics()')
  assert m['flare'] and m['absorbed']==0 and m['sunResidual']>.5
  await page.click('#toggleGround')
  assert not (await page.evaluate('FiveGyro.groundMetrics()'))['flare']
  await page.locator('#groundCapacity').evaluate("e=>{e.value='.10';e.dispatchEvent(new Event('input',{bubbles:true}))}")
  assert (await page.evaluate('FiveGyro.groundMetrics()'))['flare']
  await page.click('#resetGround')
  assert (await page.evaluate('FiveGyro.groundMetrics()'))['sunResidual']<1e-8
  await page.click('#view')
  ascii=await page.locator('#asciiFrame').inner_text()
  assert 'FIVE PULSARS' in ascii and 'BLACK HOLE' in ascii
  await page.click('#view')
  for theme in ['aquatic','stellar','atomic','hybrid']:
   await page.locator('#mode').select_option(theme)
  async with page.expect_download() as d:await page.click('#saveTXT')
  assert (await d.value).suggested_filename.endswith('.txt')
  async with page.expect_download() as d:await page.click('#savePNG')
  assert (await d.value).suggested_filename.endswith('.png')
  mobile=await browser.new_page(viewport={'width':390,'height':844})
  mobileErrors=[];mobile.on('pageerror',lambda e:mobileErrors.append(str(e)))
  await mobile.set_content(HTML,wait_until='load')
  assert float(await mobile.locator('#sunStress').inner_text())<.001
  assert not errors and not mobileErrors,(errors,mobileErrors)
  await browser.close()
  print('PASS desktop/mobile, ground vs disconnected, flare, ASCII, 4 themes, PNG/TXT')
asyncio.run(main())
