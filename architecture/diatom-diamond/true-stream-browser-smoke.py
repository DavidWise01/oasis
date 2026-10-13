from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path(__file__).parent
url=(p/'true-stream-threejs-v1.4.html').resolve().as_uri()
with sync_playwright() as w:
 browser=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--disable-gpu','--no-sandbox'])
 page=browser.new_page(viewport={'width':1280,'height':840},device_scale_factor=1)
 page.set_content((p/'true-stream-threejs-v1.4.html').read_text(), wait_until='load')
 page.wait_for_timeout(600)
 assert '5,275' in page.locator('#rate').inner_text()
 assert page.locator('#choices button').count()==8
 page.get_by_role('button',name='sustained 100k').click()
 assert '5,562' in page.locator('#rate').inner_text()
 assert '3,125' in page.locator('#stat').inner_text()
 page.get_by_role('button',name='slow sink 20k').click()
 assert '626 / 625' in page.locator('#details').inner_text()
 assert page.locator('#fallback').evaluate('(e)=> e.width>100')
 page.screenshot(path=str(p/'true-stream-preview.png'),full_page=True)
 print('PASS: 8 selectable scenarios, 100k case, slow-sink backpressure, offline render')
 browser.close()
