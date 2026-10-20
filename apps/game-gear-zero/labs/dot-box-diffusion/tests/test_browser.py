# Live Chromium smoke of recursive ASCII graphics. Requires playwright and chromium.
import asyncio,json,pathlib
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1500,'height':950},device_scale_factor=1,accept_downloads=True)
  errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
  await page.set_content((ROOT/'index.html').read_text(),wait_until='load')
  assert await page.locator('#statDots').inner_text()=='64'
  assert await page.locator('#fourASCII button').count()==4
  await page.locator('#unfold').click()
  assert await page.locator('#statDots').inner_text()=='256'
  await page.locator('#fold').click()
  assert await page.locator('#statDots').inner_text()=='64'
  await page.locator('#fourASCII button').nth(1).click()
  assert (await page.evaluate('DotBoxUI.get().path'))=='1'
  await page.locator('#firstChild').click()
  assert (await page.evaluate('DotBoxUI.get().path'))=='10'
  await page.locator('#back').click()
  assert (await page.evaluate('DotBoxUI.get().path'))=='1'
  await page.locator('#home').click()
  assert (await page.evaluate('DotBoxUI.get().path'))==''
  await page.locator('#hop').fill('9')
  assert (await page.evaluate('DotBoxUI.get().hop'))==9
  await page.locator('#glyphMode').select_option('density')
  assert '#' in await page.locator('#asciiGrid').inner_text()
  await page.locator('#glyphMode').select_option('bits')
  assert '111' in await page.locator('#asciiGrid').inner_text()
  await page.locator('#depth').fill('6')
  assert await page.locator('#statDots').inner_text()=='4,096'
  assert await page.locator('#snapshotPage').inner_text()=='PAGE 1 / 16'
  await page.locator('#nextPage').click()
  assert await page.locator('#snapshotPage').inner_text()=='PAGE 2 / 16'
  await page.locator('#prevPage').click()
  assert await page.locator('#snapshotPage').inner_text()=='PAGE 1 / 16'
  await page.locator('#depth').fill('3')
  await page.locator('#glyphMode').select_option('letters')
  await page.locator('#speed').select_option('150')
  await page.locator('#play').click()
  await page.wait_for_timeout(480)
  assert (await page.evaluate('DotBoxUI.get().hop'))>9
  await page.locator('#play').click()
  assert not (await page.evaluate('DotBoxUI.get().playing'))
  async with page.expect_download() as dl: await page.locator('#downloadText').click()
  assert (await dl.value).suggested_filename.endswith('.txt')
  mobile=await browser.new_page(viewport={'width':390,'height':844})
  mobileErrors=[];mobile.on('pageerror',lambda error:mobileErrors.append(str(error)))
  await mobile.set_content((ROOT/'index.html').read_text(),wait_until='load')
  assert await mobile.locator('#statDots').inner_text()=='64'
  assert not errors and not mobileErrors,(errors,mobileErrors)
  print('PASS desktop: unfold, nested focus, RGB modes, G6 paging, hop playback, TXT export')
  print('PASS mobile: loaded with no JavaScript errors')
  await browser.close()
asyncio.run(main())
