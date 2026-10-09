from playwright.sync_api import sync_playwright
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'index.html').read_text()
lines=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':1000})
 page.set_content(text,wait_until='load')
 assert page.locator('#scenarios button').count()==8
 for i in range(8):
  b=page.locator('#scenarios button').nth(i)
  b.click()
  assert b.get_attribute('aria-pressed')=='true'
  assert page.locator('#status').inner_text().strip()
  lines.append(f'PASS scenario {i+1} {page.locator("#label").inner_text()}')
 with page.expect_download() as d:page.locator('#export').click()
 download=d.value
 assert download.suggested_filename=='sheet157-scenario.json'
 lines.append('PASS scenario JSON export')
 page.locator('#scenarios button').first.click()
 page.screenshot(path=str(root/'preview.png'),full_page=True)
 lines.append('PASS Chromium screenshot')
 browser.close()
(root/'browser-test.log').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
