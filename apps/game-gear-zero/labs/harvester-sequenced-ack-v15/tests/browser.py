import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text()

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width':1500,'height':1050},accept_downloads=True)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.set_content(HTML, wait_until='load')
        assert await page.locator('#hallGrid .hallrail').count() == 19
        assert await page.evaluate('FiveGyro.version') == '15.0-harvester-sequenced-ack-gating'
        await page.click('#hNext')
        await page.click('#mAdvance128')
        for _ in range(5):
            await page.click('#hNext')
        assert await page.evaluate('FiveGyro.harvester().phase') == 'SECURED'
        await page.click('#pipeLoad')
        await page.click('#pipeIn')
        assert await page.evaluate('FiveGyro.dual().txId') == 1
        await page.click('#pipeOut')
        assert await page.evaluate('FiveGyro.pipe().phase') == 'HELD'
        assert await page.evaluate('FiveGyro.pipe().egress') == 0
        await page.click('#dualTicks16')
        assert await page.evaluate('FiveGyro.dualEngine.evaluate(FiveGyro.dual()).acksB') == 5
        await page.click('#pipeResume')
        await page.click('#pipeOut')
        assert await page.evaluate('FiveGyro.integrity().delivered') == '01337AB4FF'
        assert await page.evaluate('FiveGyro.pipe().egress') == 1
        await page.click('#dualReplayA')
        await page.click('#dualTick')
        assert await page.evaluate("FiveGyro.dual().receipts.some(r=>r.kind==='REPLAY_PACKET_REJECTED')")
        await page.click('#pipeClear')
        await page.locator('#dualAckModeB').select_option('DROP_ONE')
        await page.locator('#pipeHex').fill('ABCDE12345')
        await page.click('#pipeLoad')
        await page.click('#pipeIn')
        await page.click('#dualTicks16')
        gate=await page.evaluate('FiveGyro.dualEngine.evaluate(FiveGyro.dual())')
        assert gate['bitsB'] == 40 and gate['acksB'] == 4 and not gate['ready'], gate
        await page.click('#pipeOut')
        assert await page.evaluate('FiveGyro.pipe().phase') == 'HELD'
        assert await page.evaluate('FiveGyro.pipe().egress') == 1
        await page.locator('#dualAckModeB').select_option('NORMAL')
        await page.click('#dualRetryB')
        assert await page.evaluate('FiveGyro.dualEngine.evaluate(FiveGyro.dual()).acksB') == 0
        await page.click('#dualTicks16')
        assert await page.evaluate('FiveGyro.dualEngine.evaluate(FiveGyro.dual()).ready')
        await page.click('#pipeResume')
        await page.click('#pipeOut')
        assert await page.evaluate('FiveGyro.pipe().egress') == 2
        async with page.expect_download() as download:
            await page.click('#pipeExport')
        assert (await download.value).suggested_filename == 'harvester-v15-ack-receipts.json'
        mobile = await browser.new_page(viewport={'width':430,'height':930},is_mobile=True,has_touch=True)
        mobile.on('pageerror', lambda e: errors.append('mobile '+str(e)))
        await mobile.set_content(HTML,wait_until='load')
        assert await mobile.locator('#dualBoard').count() == 1
        assert await mobile.locator('#dualAckA').count() == 1
        assert not errors, errors
        print('PASS Chromium ACK gating, replay hold, resend, JSON and mobile')
        await browser.close()

asyncio.run(run())
