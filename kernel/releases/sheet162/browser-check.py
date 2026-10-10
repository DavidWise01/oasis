from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path(__file__).parent
html=(p/'index.html').read_text()
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1250,'height':1000},accept_downloads=True)
 page.set_content(html,wait_until='domcontentloaded')
 scenarios=page.locator('button[data-scenario]')
 assert scenarios.count()==8
 for n in range(8):
  b=scenarios.nth(n);b.click()
  assert 'active' in b.get_attribute('class')
  assert page.locator('#fault-state').inner_text()
  print('PASS browser scenario',n+1,b.inner_text())
 with page.expect_download() as d:page.locator('#export').click()
 assert d.value.suggested_filename=='oasis-sheet162-fault.json'
 print('PASS browser JSON export')
 page.screenshot(path=str(p/'preview.png'),full_page=True)
 print('PASS browser screenshot')
 browser.close()
