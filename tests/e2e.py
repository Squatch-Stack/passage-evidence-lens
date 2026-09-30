#!/usr/bin/env python3
"""End-to-end keyboard, narrow-screen, rights and source-link checks."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", default="http://127.0.0.1:8777")
    parser.add_argument("--local", default="http://127.0.0.1:8778")
    parser.add_argument("--screenshots", default="")
    parser.add_argument("--skip-local", action="store_true")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        binary = os.environ.get("CHROME_BIN")
        browser = playwright.chromium.launch(executable_path=binary or None, headless=True)
        output = Path(args.screenshots) if args.screenshots else None
        if output:
            output.mkdir(parents=True, exist_ok=True)
        for name, width, height in [("desktop", 1440, 900), ("mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(args.public, wait_until="networkidle")
            assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
            assert page.get_by_text("Source link only").is_visible()
            assert page.get_by_role("link", name="Sponsor Squatch Stack").get_attribute("href") == "https://github.com/sponsors/Squatch-Stack"
            assert page.get_by_role("link", name="One-time tip on Ko-fi").get_attribute("rel") == "noopener noreferrer"
            page.get_by_role("tab", name="Corrections").click()
            assert "No correction text is bundled" in page.locator("#panel-corrections").inner_text()
            page.get_by_role("tab", name="Source").click()
            assert "source record" in page.locator("#panel-source").inner_text().lower()
            page.get_by_role("tab", name="Integration").click()
            assert "source_link_only" in page.locator("#panel-integration").inner_text()
            page.get_by_role("tab", name="Integration").press("Home")
            assert page.get_by_role("tab", name="Reading").get_attribute("aria-selected") == "true"
            page.locator("#ref-input").fill("Matt.7.8")
            page.get_by_role("button", name="Open passage").click()
            assert page.locator("#detail-ref").inner_text() == "Matt.7.8"
            assert "book=33&chapter=7&verse=8" in page.locator("#official-link").get_attribute("href")
            page.locator("#ref-input").fill("../../private")
            page.get_by_role("button", name="Open passage").click()
            assert "bounded study" in page.locator("#status").inner_text()
            assert page.locator("#detail-ref").inner_text() == "Matt.7.8"
            assert not errors, errors
            if output:
                page.screenshot(path=str(output / f"public-{name}.png"), full_page=True)
            page.close()
        if not args.skip_local:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(args.local + "/?ref=Luke.11.10&mode=local", wait_until="networkidle")
            page.get_by_text("Local verified XML").wait_for()
            page.get_by_role("tab", name="Corrections").click()
            assert page.get_by_text("Correction · ca").is_visible()
            page.get_by_role("tab", name="Source").click()
            assert "sinaiticus-" in page.locator("#panel-source").inner_text()
            assert not errors, errors
            if output:
                page.screenshot(path=str(output / "local-evidence.png"), full_page=True)
            page.close()
        browser.close()
    print(json.dumps({"status": "passed", "public_viewports": [1440, 390],
                      "features": ["reference", "all tabs", "keyboard", "external links", "rights boundary"] + ([] if args.skip_local else ["local correction"])}))


if __name__ == "__main__":
    main()
