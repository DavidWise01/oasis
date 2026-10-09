#!/usr/bin/env python3
"""Headless interaction regression for the standalone SVG test viewer."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
p=Path(__file__).resolve().parent
names=['healthy','reordered','forged','crash','missing','conflict','partition','replay']
with sync_playwright() as w:
    browser=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1320,'height':930},accept_downloads=True)
    page.set_content((p/'index.html').read_text(encoding='utf-8'),wait_until='load')
    assert page.locator('h1').inner_text().startswith('Paginated')
    for name in names:
        page.locator(f'button[data-scenario="{name}"]').click()
        assert page.locator(f'button[data-scenario="{name}"]').get_attribute('aria-pressed')=='true'
        assert page.locator('#scenario-result').inner_text()
        print('PASS chromium scenario',name)
    page.locator('button[data-scenario="healthy"]').click()
    with page.expect_download() as event: page.locator('#export').click()
    download=event.value
    assert download.suggested_filename=='sheet158-healthy.json'
    content=json.loads(Path(download.path()).read_text())
    assert content['schema']=='oasis.sheet158.dashboard.v1' and content['certified'] is True
    print('PASS chromium JSON export')
    page.screenshot(path=str(p/'preview.png'),full_page=True)
    print('PASS chromium screenshot')
    browser.close()
