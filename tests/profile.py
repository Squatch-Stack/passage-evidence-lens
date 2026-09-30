#!/usr/bin/env python3
"""Measure browser work and server RSS; report observed values without inventing budgets."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time

from playwright.sync_api import sync_playwright


def metric(session, name: str) -> float:
    return next(item["value"] for item in session.send("Performance.getMetrics")["metrics"] if item["name"] == name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8777/")
    parser.add_argument("--server-pid", type=int)
    parser.add_argument("--iterations", type=int, default=300)
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.environ.get("CHROME_BIN") or None, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        session = page.context.new_cdp_session(page)
        session.send("Performance.enable")
        start = time.perf_counter()
        page.goto(args.url, wait_until="networkidle")
        loaded_ms = round((time.perf_counter() - start) * 1000, 1)
        session.send("HeapProfiler.collectGarbage")
        baseline = metric(session, "JSHeapUsedSize")
        baseline_nodes = metric(session, "Nodes")
        samples = []
        for index in range(args.iterations):
            page.locator("#ref-input").fill("Luke.11.9" if index % 2 else "Matt.7.7")
            page.get_by_role("button", name="Open passage").click()
            page.get_by_role("tab", name="Corrections").click()
            page.get_by_role("tab", name="Source").click()
            if (index + 1) % 100 == 0:
                session.send("HeapProfiler.collectGarbage")
                samples.append({"iterations": index + 1,
                                "heap_mib": round(metric(session, "JSHeapUsedSize") / 1048576, 3),
                                "dom_nodes": metric(session, "Nodes")})
        session.send("HeapProfiler.collectGarbage")
        final = metric(session, "JSHeapUsedSize")
        final_nodes = metric(session, "Nodes")
        resources = page.evaluate("performance.getEntriesByType('resource').map(x => ({name:x.name.split('/').pop(), bytes:x.transferSize}))")
        browser.close()
    rss_kib = None
    if args.server_pid:
        result = subprocess.run(["ps", "-p", str(args.server_pid), "-o", "rss="], capture_output=True, text=True, check=True)
        rss_kib = int(result.stdout.strip())
    print(json.dumps({"loaded_ms": loaded_ms, "js_heap_baseline_mib": round(baseline / 1048576, 3),
                      "js_heap_after_iterations_mib": round(final / 1048576, 3),
                      "heap_growth_kib": round((final - baseline) / 1024, 1),
                      "dom_nodes_baseline": baseline_nodes, "dom_nodes_after_iterations": final_nodes,
                      "samples": samples,
                      "resource_transfer_bytes": sum(item["bytes"] for item in resources),
                      "resources": resources, "preview_server_rss_kib": rss_kib}))


if __name__ == "__main__":
    main()
