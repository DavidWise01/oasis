import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await b.new_page(viewport={'width':1500,'height':1000},accept_downloads=True)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content((ROOT/'index.html').read_text(),wait_until='load')
  assert await page.locator('#hallGrid .hallrail').count()==19
  assert await page.locator('#dualBoard').count()==1
  await page.click('#hNext');await page.click('#mAdvance128')
  for _ in range(5):await page.click('#hNext')
  assert await page.evaluate('FiveGyro.harvester().phase')=='SECURED'
  await page.click('#pipeLoad');await page.click('#pipeIn')
  assert await page.evaluate('FiveGyro.integrity().readA') is None
  await page.click('#pipeOut')
  assert await page.evaluate('FiveGyro.pipe().phase')=='HELD'
  await page.click('#dualTicks16')
  assert await page.evaluate('FiveGyro.dualEngine.evaluate(FiveGyro.dual()).ready')
  await page.click('#pipeResume');await page.click('#pipeOut')
  assert await page.evaluate('FiveGyro.pipe().egress')==1
  assert await page.evaluate('FiveGyro.integrity().delivered')=='01337AB4FF'
  await page.click('#pipeOut')
  assert await page.evaluate('FiveGyro.pipe().egress')==1
  async with page.expect_download() as dl:await page.click('#pipeExport')
  assert (await dl.value).suggested_filename=='harvester-v14-dual-path-receipts.json'
  await page.click('#pipeClear')
  await page.locator('#dualModeB').select_option('DROP')
  await page.locator('#pipeHex').fill('ABCDE12345')
  await page.click('#pipeLoad');await page.click('#pipeIn');await page.click('#dualTicks16')
  assert await page.evaluate('FiveGyro.dual().paths.B.status')=='MISSING_BYTES'
  await page.click('#pipeOut')
  assert await page.evaluate('FiveGyro.pipe().phase')=='HELD'
  await page.locator('#dualModeB').select_option('NORMAL')
  await page.click('#dualRetryB')
  assert await page.evaluate('FiveGyro.dual().paths.B.rxHex') is None
  await page.click('#dualTicks16');await page.click('#pipeResume');await page.click('#pipeOut')
  assert await page.evaluate('FiveGyro.pipe().egress')==2
  mobile=await b.new_page(viewport={'width':430,'height':930},is_mobile=True,has_touch=True)
  mobile.on('pageerror',lambda e:errors.append('mobile:'+str(e)))
  await mobile.set_content((ROOT/'index.html').read_text(),wait_until='load')
  assert await mobile.locator('#dualBoard').count()==1
  assert not errors,errors
  print('PASS Chromium: real byte arrivals, HOLD, explicit retry, duplicate protection, JSON, mobile')
  await b.close()
asyncio.run(main())
