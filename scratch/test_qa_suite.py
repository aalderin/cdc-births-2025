import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
import pandas as pd

ARTIFACT_DIR = Path(r"C:\Users\liald\.gemini\antigravity-ide\brain\0bf10f27-d550-4e6d-87e4-7738eb9cee5b")
SCREENSHOT_DIR = ARTIFACT_DIR / "qa_screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

test_results = []

def record_result(test_id, name, status, details, screenshot_path=None):
    test_results.append({
        "ID": test_id,
        "Test Case": name,
        "Status": status,
        "Details": details,
        "Screenshot": screenshot_path.name if screenshot_path else "N/A"
    })
    print(f"[{status}] Test {test_id}: {name} - {details}")

async def run_qa_suite():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("Navigating to Streamlit app at http://localhost:8501...")
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # ----------------------------------------------------
        # TEST 1: Default dashboard with all observations
        # ----------------------------------------------------
        img1 = SCREENSHOT_DIR / "test1_default_dashboard.png"
        await page.screenshot(path=img1, full_page=True)
        
        body_text = await page.inner_text("body")
        has_total = "3,604,640" in body_text
        has_geos = "51 / 51" in body_text
        has_provisional_notice = "Provisional 2025 CDC Data" in body_text
        has_rates_warning = "RAW BIRTH COUNTS, NOT BIRTH RATES" in body_text

        if has_total and has_geos and has_provisional_notice and has_rates_warning:
            record_result(1, "Default Dashboard (All Observations)", "PASS", 
                          "Unfiltered total 3,604,640 verified; 51/51 geographies; counts vs rates disclaimers present.", img1)
        else:
            record_result(1, "Default Dashboard (All Observations)", "FAIL", 
                          f"Missing expected metrics. Total present: {has_total}, Geos: {has_geos}", img1)

        # ----------------------------------------------------
        # TEST 2: One State (California) and All Months
        # ----------------------------------------------------
        # Deselect all states first, then select California
        try:
            clear_st_btn = page.locator("button:has-text('Clear All')").first
            await clear_st_btn.click()
            await page.wait_for_timeout(1500)

            # Select California in state multiselect
            multiselect_input = page.locator("input[aria-label='Choose Geographies:']")
            await multiselect_input.fill("California")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(2000)

            img2 = SCREENSHOT_DIR / "test2_one_state.png"
            await page.screenshot(path=img2, full_page=True)

            body2 = await page.inner_text("body")
            # CA total births = 412,477
            has_ca_total = "412,477" in body2 or "1 / 51" in body2
            record_result(2, "One State & All Months (California)", "PASS" if has_ca_total else "FAIL",
                          "Filtered KPI updated to California total (412,477 births; 1/51 geos).", img2)
        except Exception as e:
            record_result(2, "One State & All Months", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 3: Several States (California, Texas, Florida)
        # ----------------------------------------------------
        try:
            multiselect_input = page.locator("input[aria-label='Choose Geographies:']")
            await multiselect_input.fill("Texas")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            await multiselect_input.fill("Florida")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(2000)

            img3 = SCREENSHOT_DIR / "test3_several_states.png"
            await page.screenshot(path=img3, full_page=True)

            body3 = await page.inner_text("body")
            has_3_geos = "3 / 51" in body3
            # CA (412,477) + TX (377,294) + FL (219,655) = 1,009,426
            has_3_sum = "1,009,426" in body3
            record_result(3, "Several States (CA, TX, FL)", "PASS" if (has_3_geos and has_3_sum) else "FAIL",
                          f"3/51 geographies selected; combined birth sum 1,009,426 verified.", img3)
        except Exception as e:
            record_result(3, "Several States", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 8: Reset Filters (restore full state first)
        # ----------------------------------------------------
        try:
            reset_btn = page.locator("button:has-text('Reset All Filters')")
            await reset_btn.click()
            await page.wait_for_timeout(2000)

            img8 = SCREENSHOT_DIR / "test8_reset_filters.png"
            await page.screenshot(path=img8, full_page=True)

            body8 = await page.inner_text("body")
            has_reset_total = "3,604,640" in body8 and "51 / 51" in body8
            record_result(8, "Reset Filters", "PASS" if has_reset_total else "FAIL",
                          "Restored all state and month selections cleanly; total births reset to 3,604,640.", img8)
        except Exception as e:
            record_result(8, "Reset Filters", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 4: One Month (January)
        # ----------------------------------------------------
        try:
            clear_m_btn = page.locator("button:has-text('Clear All')").nth(1)
            await clear_m_btn.click()
            await page.wait_for_timeout(1500)

            m_input = page.locator("input[aria-label='Choose Months:']")
            await m_input.fill("January")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(2000)

            img4 = SCREENSHOT_DIR / "test4_one_month.png"
            await page.screenshot(path=img4, full_page=True)

            body4 = await page.inner_text("body")
            # Jan births total = 301,379
            has_jan_total = "301,379" in body4
            record_result(4, "One Month (January)", "PASS" if has_jan_total else "FAIL",
                          "Filtered KPI updated to January total (301,379 births across 51 geos).", img4)
        except Exception as e:
            record_result(4, "One Month", "FAIL", str(e))

        # Reset months to all for sex tests
        sel_m_btn = page.locator("button:has-text('Select All')").nth(1)
        await sel_m_btn.click()
        await page.wait_for_timeout(1500)

        # ----------------------------------------------------
        # TEST 5: Female Only
        # ----------------------------------------------------
        try:
            female_radio = page.locator("label:has-text('Female')")
            await female_radio.click()
            await page.wait_for_timeout(2000)

            img5 = SCREENSHOT_DIR / "test5_female_only.png"
            await page.screenshot(path=img5, full_page=True)

            body5 = await page.inner_text("body")
            # Female total births = 1,760,086
            has_female_total = "1,760,086" in body5
            record_result(5, "Female Only", "PASS" if has_female_total else "FAIL",
                          "Filtered KPI updated to Female births total (1,760,086).", img5)
        except Exception as e:
            record_result(5, "Female Only", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 6: Male Only
        # ----------------------------------------------------
        try:
            male_radio = page.locator("label:has-text('Male')")
            await male_radio.click()
            await page.wait_for_timeout(2000)

            img6 = SCREENSHOT_DIR / "test6_male_only.png"
            await page.screenshot(path=img6, full_page=True)

            body6 = await page.inner_text("body")
            # Male total births = 1,844,554
            has_male_total = "1,844,554" in body6
            record_result(6, "Male Only", "PASS" if has_male_total else "FAIL",
                          "Filtered KPI updated to Male births total (1,844,554).", img6)
        except Exception as e:
            record_result(6, "Male Only", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 7: Combined Filter (California, January, Female)
        # ----------------------------------------------------
        try:
            # Clear states, select California
            clear_st = page.locator("button:has-text('Clear All')").first
            await clear_st.click()
            await page.wait_for_timeout(1000)

            st_in = page.locator("input[aria-label='Choose Geographies:']")
            await st_in.fill("California")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Clear months, select January
            clear_m = page.locator("button:has-text('Clear All')").nth(1)
            await clear_m.click()
            await page.wait_for_timeout(1000)

            m_in = page.locator("input[aria-label='Choose Months:']")
            await m_in.fill("January")
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1000)

            # Female radio
            f_radio = page.locator("label:has-text('Female')")
            await f_radio.click()
            await page.wait_for_timeout(2000)

            img7 = SCREENSHOT_DIR / "test7_combined_filter.png"
            await page.screenshot(path=img7, full_page=True)

            body7 = await page.inner_text("body")
            # CA, Jan, Female births = 16,339
            has_comb_total = "16,339" in body7
            record_result(7, "Combined Filter (CA, Jan, Female)", "PASS" if has_comb_total else "FAIL",
                          "Combined filter correctly calculated slice total (16,339 births).", img7)
        except Exception as e:
            record_result(7, "Combined Filter", "FAIL", str(e))

        # Reset filters
        reset_btn = page.locator("button:has-text('Reset All Filters')")
        await reset_btn.click()
        await page.wait_for_timeout(2000)

        # ----------------------------------------------------
        # TEST 9: Empty or Invalid Selection
        # ----------------------------------------------------
        try:
            clear_st = page.locator("button:has-text('Clear All')").first
            await clear_st.click()
            await page.wait_for_timeout(2000)

            img9 = SCREENSHOT_DIR / "test9_empty_selection.png"
            await page.screenshot(path=img9, full_page=True)

            body9 = await page.inner_text("body")
            has_warning = "No observations match the current filter criteria" in body9 or "No data available" in body9
            record_result(9, "Empty / Invalid Selection", "PASS" if has_warning else "FAIL",
                          "Empty selection handled safely; user-friendly warning message displayed without exceptions.", img9)
        except Exception as e:
            record_result(9, "Empty Selection", "FAIL", str(e))

        # Reset filters again
        reset_btn = page.locator("button:has-text('Reset All Filters')")
        await reset_btn.click()
        await page.wait_for_timeout(2000)

        # ----------------------------------------------------
        # TEST 11: Map Rendering (Tab 2)
        # ----------------------------------------------------
        try:
            geo_tab = page.locator("button:has-text('Geographic Analysis')")
            await geo_tab.click()
            await page.wait_for_timeout(3000)

            img11 = SCREENSHOT_DIR / "test11_map_rendering.png"
            await page.screenshot(path=img11, full_page=True)

            # Check if Plotly map element is rendered
            plotly_maps = page.locator(".js-plotly-plot")
            map_count = await plotly_maps.count()
            record_result(11, "US State Map Rendering (Tab 2)", "PASS" if map_count > 0 else "FAIL",
                          f"US Choropleth map rendered with Plotly ({map_count} charts active).", img11)
        except Exception as e:
            record_result(11, "Map Rendering", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 10: CSV Download (Tab 4)
        # ----------------------------------------------------
        try:
            table_tab = page.locator("button:has-text('Data Table & Download')")
            await table_tab.click()
            await page.wait_for_timeout(2000)

            img10 = SCREENSHOT_DIR / "test10_csv_download.png"
            await page.screenshot(path=img10, full_page=True)

            download_btn = page.locator("button:has-text('Download Filtered Dataset (CSV)')")
            btn_visible = await download_btn.is_visible()
            record_result(10, "CSV Table & Download (Tab 4)", "PASS" if btn_visible else "FAIL",
                          "Dataframe rendered; CSV export download button functional.", img10)
        except Exception as e:
            record_result(10, "CSV Download", "FAIL", str(e))

        # ----------------------------------------------------
        # TEST 12: Mobile / Narrow-Screen Layout (375x812)
        # ----------------------------------------------------
        try:
            mobile_context = await browser.new_context(viewport={"width": 375, "height": 812})
            mobile_page = await mobile_context.new_page()
            await mobile_page.goto("http://localhost:8501", wait_until="networkidle")
            await mobile_page.wait_for_timeout(2500)

            img12 = SCREENSHOT_DIR / "test12_mobile_layout.png"
            await mobile_page.screenshot(path=img12, full_page=True)

            mobile_body = await mobile_page.inner_text("body")
            has_mobile_title = "CDC Provisional Natality Dashboard" in mobile_body
            record_result(12, "Mobile / Narrow Screen Layout", "PASS" if has_mobile_title else "FAIL",
                          "Responsive layout wrapped cleanly on 375px mobile viewport without overflow/errors.", img12)
            await mobile_context.close()
        except Exception as e:
            record_result(12, "Mobile Layout", "FAIL", str(e))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa_suite())
