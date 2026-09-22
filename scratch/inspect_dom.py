import asyncio
from playwright.async_api import async_playwright

async def inspect_dom():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_selector('[data-testid="stMetricValue"]', timeout=15000)
        
        labels = await page.locator('[data-testid="stMetricLabel"]').all_inner_texts()
        values = await page.locator('[data-testid="stMetricValue"]').all_inner_texts()
        print("Metrics:", list(zip(labels, values)))
        
        sidebar = page.locator('[data-testid="stSidebar"]')
        buttons = await sidebar.locator('button').all_inner_texts()
        print("Sidebar Buttons:", buttons)
        
        multiselects = await sidebar.locator('[data-testid="stMultiSelect"]').all_inner_texts()
        print("Multiselects count:", len(multiselects))
        
        radios = await sidebar.locator('[data-testid="stRadio"]').all_inner_texts()
        print("Radios:", radios)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_dom())
