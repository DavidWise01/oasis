from playwright.sync_api import sync_playwright
from pathlib import Path
page_html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    page.set_content(page_html,wait_until='domcontentloaded')
    names=['certified','inclusion','extension','crash','rollback','forged','order','tls']
    for name in names:
        page.locator(f'button[data-id="{name}"]').click()
        assert page.locator('button.active').get_attribute('data-id')==name
        assert page.locator('#state b').count()==1
        print('PASS browser scenario',name)
    with page.expect_download() as event:page.locator('#export').click()
    download=event.value
    assert download.suggested_filename=='SHEET161-benchmark.json'
    print('PASS browser benchmark JSON export')
    page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
    print('PASS browser screenshot')
    browser.close()
