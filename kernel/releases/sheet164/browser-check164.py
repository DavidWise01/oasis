from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parent
html=(BASE/'index.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':920},accept_downloads=True)
    page.set_content(html,wait_until='load')
    passed=0
    for button in page.locator('#bars button').all():
        button.click()
        assert page.locator('#detail .num').inner_text().endswith('/s')
        passed+=1
    for k in ('holdout','crash','effects'):
        page.locator('#'+k).click()
        assert len(page.locator('#detail').inner_text())>40
        passed+=1
    with page.expect_download() as dl:
        page.locator('#export').click()
    assert dl.value.suggested_filename=='SHEET164-benchmark-export.json'
    passed+=1
    page.screenshot(path=str(BASE/'preview.png'),full_page=True)
    browser.close()
(BASE/'browser-check.log').write_text(f'SHEET164 CHROMIUM {passed}/{passed} PASS\n')
print(f'SHEET164 CHROMIUM {passed}/{passed} PASS')
