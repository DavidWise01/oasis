from pathlib import Path
from playwright.sync_api import sync_playwright
html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':1320,'height':1100},accept_downloads=True)
    page.set_content(html,wait_until='domcontentloaded')
    buttons=page.locator('[data-scenario]')
    assert buttons.count()==8
    for i in range(8):
        buttons.nth(i).click()
        assert page.locator('[aria-pressed="true"]').count()==1
        assert page.locator('#scenario-index').inner_text().endswith('/ 08')
        assert ('DENIED' in page.locator('#event-state').inner_text()) == (i>=3)
    with page.expect_download() as event:
        page.locator('#export').click()
    assert event.value.suggested_filename=='sheet152-recovery.json'
    assert page.evaluate('window.__lastExport.scenario')=='recovery'
    page.locator('[data-scenario="normal"]').click()
    page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
    b.close()
    print('PASS 8 scenarios + JSON export + screenshot (10 checks)')
