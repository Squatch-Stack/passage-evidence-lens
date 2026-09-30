#!/usr/bin/env python3
"""HTTP negative controls for public and local preview modes."""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def get(base: str, path: str, headers: dict | None = None) -> tuple[int, dict, bytes]:
    request = urllib.request.Request(base + path, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", default="http://127.0.0.1:8777")
    parser.add_argument("--local", default="http://127.0.0.1:8778")
    parser.add_argument("--skip-local", action="store_true")
    args = parser.parse_args()
    status, headers, page = get(args.public, "/")
    assert status == 200 and b"Passage Evidence Lens" in page
    assert "default-src 'none'" in headers["Content-Security-Policy"]
    assert headers["Referrer-Policy"] == "no-referrer"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert "Access-Control-Allow-Origin" not in headers
    assert get(args.public, "/api/evidence?ref=Luke.11.10")[0] == 403
    assert get(args.public, "/api/evidence?ref=Luke.11.10%27%20OR%201=1")[0] == 400
    assert get(args.public, "/sources/private.xml")[0] == 404
    assert get(args.public, "/%2e%2e/%2e%2e/etc/passwd")[0] == 404
    assert get(args.public, "/", {"Host": "unexpected.example"})[0] == 403
    if not args.skip_local:
        assert get(args.local, "/api/evidence?ref=Luke.11.10", {"Sec-Fetch-Site": "cross-site"})[0] == 403
        status, _, body = get(args.local, "/api/evidence?ref=Luke.11.10")
        data = json.loads(body)
        assert status == 200 and data["state"] == "indexed_transcription"
        assert [item["hand"] for item in data["corrections"]] == [None, "ca"]
        assert get(args.local, "/api/evidence?ref=Gen.1.1")[0] == 200
    print(json.dumps({"status": "passed", "checks": 13 if not args.skip_local else 9,
                      "boundary": "Local research text is loopback-only and explicit opt-in"}))


if __name__ == "__main__":
    main()
