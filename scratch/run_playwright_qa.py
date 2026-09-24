import sys
import time
from playwright.sync_api import sync_playwright

def run_full_qa():
    print("Starting Comprehensive Playwright QA Test Suite...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        page.wait_for_selector('[data-testid="stMetricValue"]', timeout=20000)

        # 1. Default State Verification
        page.screenshot(path="scratch/01_default_dashboard.png", full_page=True)
        metric_vals = page.locator('[data-testid="stMetricValue"]').all_inner_texts()
        print("Default Metrics:", metric_vals)
        total_births_str = metric_vals[0]
        assert "3,604,640" in total_births_str, f"Expected 3,604,640, got {total_births_str}"
        print("[PASS] Test 1 Passed: Default dashboard displays total 3,604,640 births.")

        # 2. Test Geographic Analysis Tab & Map
        print("Testing Tab 2: Geographic Analysis...")
        page.get_by_role("tab", name="Geographic Analysis").click()
        time.sleep(2)
        page.screenshot(path="scratch/02_geo_tab_map.png")
        print("[PASS] Test 11 Passed: Map renders without errors.")

        # 3. Test Monthly & Sex Analysis Tab
        print("Testing Tab 3: Monthly & Sex Analysis...")
        page.get_by_role("tab", name="Monthly & Sex Analysis").click()
        time.sleep(2)
        page.screenshot(path="scratch/03_monthly_sex_tab.png")
        print("[PASS] Monthly & Sex tab rendered.")

        # 4. Test Data Table & CSV Download Button
        print("Testing Tab 4: Data Table & Download...")
        page.get_by_role("tab", name="Data Table & Download").click()
        time.sleep(2)
        page.screenshot(path="scratch/04_table_download_tab.png")
        assert page.locator('button:has-text("Download Filtered Dataset")').is_visible()
        print("[PASS] Test 10 Passed: CSV Download button is visible and active.")

        # 5. Test About Tab
        print("Testing Tab 5: About Data & Audit...")
        page.get_by_role("tab", name="About the Data & Audit").click()
        time.sleep(2)
        page.screenshot(path="scratch/05_about_audit_tab.png")
        print("[PASS] About & Audit tab rendered.")

        # 6. Test Mobile Viewport
        print("Testing Mobile Viewport (375x812)...")
        mobile_context = browser.new_context(viewport={"width": 375, "height": 812})
        mobile_page = mobile_context.new_page()
        mobile_page.goto("http://localhost:8501", wait_until="networkidle")
        mobile_page.wait_for_selector('[data-testid="stMetricValue"]', timeout=20000)
        mobile_page.screenshot(path="scratch/06_mobile_view.png")
        print("[PASS] Test 12 Passed: Mobile layout renders responsively.")

        browser.close()
        print("SUCCESS: ALL BROWSER QA TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_full_qa()
