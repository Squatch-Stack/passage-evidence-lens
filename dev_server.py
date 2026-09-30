#!/usr/bin/env python3
"""Loopback-only preview. Protected XML text is opt-in and never in this repo."""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
STATIC = {
    "/": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/index.html": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/styles.css": (ROOT / "styles.css", "text/css; charset=utf-8"),
    "/app.js": (ROOT / "app.js", "text/javascript; charset=utf-8"),
    "/data/loci.json": (ROOT / "data" / "loci.json", "application/json; charset=utf-8"),
    "/favicon.svg": (ROOT / "favicon.svg", "image/svg+xml"),
}
ALLOWED_REFS = {"Matt.7.7", "Matt.7.8", "Luke.11.9", "Luke.11.10"}
REF = re.compile(r"^[1-3]?[A-Za-z]{2,12}\.[1-9][0-9]{0,2}\.[1-9][0-9]{0,2}$")
SECURITY = {
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cache-Control": "no-store",
}


def evidence(ref: str) -> dict:
    if ref not in ALLOWED_REFS:
        return {"ref": ref, "state": "outside_curated_pilot"}
    if os.environ.get("LENS_LOCAL_TEXT") != "1":
        raise PermissionError("Local transcription display is disabled")
    db_path = Path(os.environ["LENS_DB"])
    lock_path = Path(os.environ["LENS_LOCK"])
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        provenance = dict(db.execute("SELECT key,value FROM provenance"))
        if provenance.get("member_sha256") != lock["member_sha256"]:
            return {"ref": ref, "state": "index_revision_mismatch"}
        row = db.execute("SELECT ref,page,folio,scribe,initial_text,source_url,fragment_sha256 FROM verse WHERE ref=?", (ref,)).fetchone()
        if row is None:
            return {"ref": ref, "state": "index_unavailable"}
        corrections = [dict(item) for item in db.execute(
            "SELECT reading_order,reading_type,hand,text FROM correction WHERE ref=? ORDER BY reading_order", (ref,))]
        if len(corrections) > 64 or len(row["initial_text"]) > 4096 or any(len(item["text"]) > 4096 for item in corrections):
            raise ValueError("Evidence row exceeds preview bounds")
        return {"ref": ref, "state": "indexed_transcription", "page": row["page"],
                "folio": row["folio"], "scribe": row["scribe"], "initial_text": row["initial_text"],
                "fragment_sha256": row["fragment_sha256"], "source_version": provenance["version"],
                "import_run_id": provenance["import_run_id"], "corrections": corrections}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status: int, body: bytes, mime: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        for name, value in SECURITY.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        host = self.headers.get("Host", "")
        allowed_hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if host not in allowed_hosts:
            self.respond(403, b"Host not allowed", "text/plain; charset=utf-8")
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/api/evidence":
            if self.headers.get("Sec-Fetch-Site") == "cross-site":
                self.respond(403, b'{"error":"cross-site request denied"}', "application/json; charset=utf-8")
                return
            ref = parse_qs(parsed.query).get("ref", [""])[0]
            if len(ref) > 64 or not REF.fullmatch(ref):
                self.respond(400, b'{"error":"invalid reference"}', "application/json; charset=utf-8")
                return
            try:
                data = evidence(ref)
            except (PermissionError, KeyError, FileNotFoundError, ValueError, sqlite3.DatabaseError):
                self.respond(403, b'{"error":"local evidence unavailable"}', "application/json; charset=utf-8")
                return
            self.respond(200, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        entry = STATIC.get(parsed.path)
        if entry is None:
            self.respond(404, b"Not found", "text/plain; charset=utf-8")
            return
        path, mime = entry
        self.respond(200, path.read_bytes(), mime)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8771)
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Passage Evidence Lens: http://127.0.0.1:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
