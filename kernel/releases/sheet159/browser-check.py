from playwright.sync_api import sync_playwright
from pathlib import Path
html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1200,'height':960});page.set_content(html)
 cases={'aligned':'ALLOW','subtree':'DENY','leaf':'DENY','stale':'DENY','signature':'DENY','crash':'ALLOW','partition':'DENY','live':'ALLOW'}
 for scenario,expected in cases.items():
  page.select_option('#scenario',scenario)
  assert page.locator('#decision').inner_text()==expected,(scenario,page.locator('#decision').inner_text())
  assert scenario in page.locator('#audit').inner_text()
  print('PASS CHROMIUM',scenario)
 with page.expect_download() as x:page.click('#export')
 assert x.value.suggested_filename=='sheet159-live.json'
 print('PASS CHROMIUM JSON export')
 page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
 browser.close()
