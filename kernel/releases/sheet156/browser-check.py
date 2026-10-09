#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
html=(root/'index.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':960},accept_downloads=True)
    page.set_content(html,wait_until='domcontentloaded')
    buttons=page.locator('#choices button')
    assert buttons.count()==11,buttons.count()
    for i in range(11):
        buttons.nth(i).click()
        assert buttons.nth(i).get_attribute('aria-pressed')=='true',i
        assert page.locator('#detail').inner_text().strip(),i
        assert len(page.locator('#trace').inner_text())>30,i
        print('CHROMIUM PASS',i+1,buttons.nth(i).inner_text())
    buttons.first.click()
    page.screenshot(path=str(root/'preview.png'),full_page=True)
    with page.expect_download() as info: page.locator('#export').click()
    d=info.value
    assert d.suggested_filename.endswith('.json')
    payload=d.path().read_text()
    assert 'oasis.sheet156.svg.case.v1' in payload
    print('CHROMIUM PASS JSON export');print('CHROMIUM PASS screenshot');browser.close()
