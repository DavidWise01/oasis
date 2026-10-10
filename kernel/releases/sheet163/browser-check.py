from pathlib import Path
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':920})
 page.set_content((P/'index.html').read_text(),wait_until='domcontentloaded')
 count=0
 for i in range(8):
  page.locator('.scenario').nth(i).click()
  assert page.locator('.scenario').nth(i).get_attribute('aria-pressed')=='true'
  assert page.locator('#detailTitle').inner_text().strip()
  print(f'PASS {count+1} scenario {i+1}');count+=1
 page.select_option('#trial','1');assert '329.52' in page.locator('#kpiFast').inner_text();print(f'PASS {count+1} benchmark toggle');count+=1
 with page.expect_download() as download:
  page.locator('#export').click()
 d=download.value
 assert d.suggested_filename=='sheet163-dashboard-evidence.json'
 assert 'prepared' in page.locator('#exportStatus').inner_text()
 print(f'PASS {count+1} JSON export');count+=1
 page.locator('#reset').click();assert page.locator('.scenario').first.get_attribute('aria-pressed')=='true';assert '298.71' in page.locator('#kpiFast').inner_text();print(f'PASS {count+1} reset');count+=1
 page.screenshot(path=str(P/'preview.png'),full_page=True)
 print(f'SHEET163 CHROMIUM {count}/{count} PASS')
 browser.close()
