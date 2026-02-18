"""Record a demo video of the Architecture Review Agent using the microservices banking scenario."""

import asyncio
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

SCENARIO_FILE = Path(__file__).resolve().parent.parent / "scenarios" / "microservices_banking.yaml"
VIDEO_DIR = Path(__file__).resolve().parent.parent / "screenshots"
OUTPUT_VIDEO = VIDEO_DIR / "microservices_banking_demo.mp4"


async def smooth_scroll(page, target: int, steps: int = 8, delay_ms: int = 80):
    """Smoothly scroll to a target Y position."""
    current = await page.evaluate("window.scrollY")
    step = (target - current) / steps
    for _ in range(steps):
        current += step
        await page.evaluate(f"window.scrollTo(0, {int(current)})")
        await page.wait_for_timeout(delay_ms)
    await page.evaluate(f"window.scrollTo(0, {target})")


async def main():
    scenario_content = SCENARIO_FILE.read_text(encoding="utf-8")
    VIDEO_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        # 1. Navigate to the app
        print("1. Opening app...")
        await page.goto("http://localhost:5173")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)

        # 2. Paste the microservices banking scenario
        print("2. Pasting microservices banking scenario...")
        textarea = page.locator("textarea")
        await textarea.click()
        await textarea.fill(scenario_content)
        await page.wait_for_timeout(1500)

        # 3. Scroll down to show the textarea content and Review button
        await smooth_scroll(page, 200)
        await page.wait_for_timeout(1000)

        # 4. Click Review Architecture
        print("3. Clicking Review Architecture...")
        await page.get_by_role("button", name="Review Architecture").click()
        await page.wait_for_timeout(500)

        # 5. Wait for results (banking scenario takes longer due to more components)
        print("4. Waiting for analysis results...")
        await page.wait_for_selector("text=Executive Summary", timeout=45000)
        await page.wait_for_timeout(1000)

        # 6. Scroll smoothly to Executive Summary
        print("5. Showing Executive Summary...")
        await smooth_scroll(page, 420)
        await page.wait_for_timeout(2500)

        # 7. Diagram tab — wait for PNG blob to load then scroll into view
        print("6. Diagram tab — PNG preview...")
        await page.get_by_role("button", name="Diagram").click()
        await page.wait_for_timeout(500)
        await smooth_scroll(page, 620)
        # Wait up to 6 s for the PNG blob URL to appear in the img src
        await page.wait_for_selector(".diagram-container img[src^='blob:']", timeout=6000)
        await page.wait_for_timeout(2500)

        # 8. Risks tab
        print("7. Risks tab...")
        # Risks button text includes the count e.g. "Risks (7)"
        await page.locator(".tabs button", has_text="Risks").click()
        await page.wait_for_timeout(500)
        await smooth_scroll(page, 560)
        await page.wait_for_timeout(2000)
        # Scroll further to reveal more risk rows
        await smooth_scroll(page, 900)
        await page.wait_for_timeout(2000)

        # 9. Components tab
        print("8. Components tab...")
        await page.locator(".tabs button", has_text="Components").click()
        await page.wait_for_timeout(500)
        await smooth_scroll(page, 560)
        await page.wait_for_timeout(2000)
        # Scroll to reveal more component rows
        await smooth_scroll(page, 950)
        await page.wait_for_timeout(2000)

        # 10. Recommendations tab
        print("9. Recommendations tab...")
        await page.locator(".tabs button", has_text="Recommendations").click()
        await page.wait_for_timeout(500)
        await smooth_scroll(page, 560)
        await page.wait_for_timeout(2000)
        # Scroll to reveal more recommendations
        await smooth_scroll(page, 950)
        await page.wait_for_timeout(2000)

        # 11. Return to Diagram tab and scroll back to top
        print("10. Back to diagram, scroll to top...")
        await page.locator(".tabs button", has_text="Diagram").click()
        await page.wait_for_timeout(500)
        await smooth_scroll(page, 0)
        await page.wait_for_timeout(2000)

        # Capture the temp video path before closing
        video_path = await page.video.path()
        print(f"Temp video path: {video_path}")

        await context.close()
        await browser.close()

    # Rename / overwrite the final output file
    shutil.move(str(video_path), str(OUTPUT_VIDEO))
    print(f"Done! Demo video saved to: {OUTPUT_VIDEO}")
    return str(OUTPUT_VIDEO)


if __name__ == "__main__":
    asyncio.run(main())
