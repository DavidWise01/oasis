import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text()
async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1510,'height':1100},accept_downloads=True)
  errs=[]
  page.on('pageerror',lambda e: errs.append(str(e)))
  await page.set_content(html,wait_until='load')
  await page.wait_for_timeout(220)
  assert await page.locator('#integrityBoard').count()==1
  assert await page.locator('#pipeFlow .pipestage').count()==8
  # old v11/v12 interlocks: secure before sending
  await page.click('#hNext')
  await page.click('#mAdvance128')
  for _ in range(5):await page.click('#hNext')
  assert (await page.evaluate('FiveGyro.harvester().phase'))=='SECURED'
  await page.click('#pipeLoad')
  await page.click('#pipeIn')
  assert (await page.evaluate('FiveGyro.pipe().phase'))=='IN_FLIGHT'
  assert (await page.locator('#readScore').inner_text())=='40 / 40'
  await page.locator('#integrityBoard').screenshot(path=str(ROOT/'preview-verified-inflight.png'))
  # fault receiver A then B at the same bit, agreement between A/B must still fail
  await page.click('#flipReadA')
  assert (await page.evaluate('FiveGyro.pipe().phase'))=='HELD'
  assert (await page.evaluate('FiveGyro.pipe().egress'))==0
  await page.click('#flipReadB')
  status=await page.evaluate('({a:FiveGyro.integrity().readA,b:FiveGyro.integrity().readB,reference:FiveGyro.integrity().captured,phase:FiveGyro.pipe().phase})')
  assert status['a']==status['b']!=status['reference'],status
  assert (await page.locator('#readVerdict').inner_text())=='HELD'
  await page.locator('#integrityBoard').screenshot(path=str(ROOT/'preview-mismatch-held.png'))
  await page.click('#pipeResume')
  assert (await page.evaluate('FiveGyro.pipe().phase'))=='HELD'
  await page.click('#repairRead')
  await page.click('#pipeResume')
  assert (await page.evaluate('FiveGyro.pipe().phase'))=='IN_FLIGHT'
  await page.click('#pipeOut')
  outcome=await page.evaluate('({pipe:FiveGyro.pipe(),integrity:FiveGyro.integrity()})')
  assert outcome['pipe']['phase']=='COMPLETE' and outcome['pipe']['egress']==1
  assert outcome['integrity']['delivered']==outcome['integrity']['captured']
  assert outcome['integrity']['receipts'][-1]['kind']=='OUT_40_MATCH'
  await page.locator('#vesselPipeBoard').screenshot(path=str(ROOT/'preview-verified-egress.png'))
  async with page.expect_download() as d:await page.click('#pipeExport')
  downloaded=await d.value
  assert downloaded.suggested_filename=='harvester-v13-readback.json'
  await page.screenshot(path=str(ROOT/'preview-desktop.png'),full_page=True)
  # independent fault in B on new packet
  await page.click('#pipeClear')
  await page.locator('#pipeHex').fill('FEDCBA9876')
  await page.click('#pipeLoad')
  await page.click('#pipeIn')
  await page.locator('#faultBit').fill('39')
  await page.click('#flipReadB')
  assert (await page.evaluate('FiveGyro.integrity().last.badB'))==[39]
  assert (await page.evaluate('FiveGyro.pipe().egress'))==1
  await page.click('#pipeAbort')
  assert (await page.evaluate('FiveGyro.pipe().phase'))=='ABORTED'
  mobile=await browser.new_page(viewport={'width':430,'height':970},is_mobile=True,has_touch=True)
  mobile.on('pageerror',lambda e:errs.append('mobile:'+str(e)))
  await mobile.set_content(html,wait_until='load')
  await mobile.locator('#integrityBoard').screenshot(path=str(ROOT/'preview-mobile.png'))
  assert await mobile.locator('#integrityBoard').count()==1
  assert not errs,errs
  print('PASS browser: 40-bit verified OUT, double-bit same-position common fault, HOLD, repair/resume, abort, export, mobile')
  await browser.close()
asyncio.run(run())
