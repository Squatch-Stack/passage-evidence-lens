# Security and performance model

The hosted package is static and contains no credentials or user accounts. It fetches only its own four-row reference catalog. External links use `noopener noreferrer`; referrer policy is `no-referrer`. All evidence text is inserted with `textContent`, never HTML. The catalog accepts only canonical references and the official manuscript URL pattern. No third-party script, font, image, analytics, or package runs in the browser.

`dev_server.py` binds to `127.0.0.1`, serves a fixed route allowlist, and denies unexpected Host headers and cross-site API fetches. Text access additionally requires `LENS_LOCAL_TEXT=1` plus an external SQLite index and lock file. It checks the indexed XML member hash, validates the reference, caps correction count and text size, and returns only a bounded response. It emits CSP, nosniff, no-referrer, no-store, CORP and frame-denial headers. This adapter is a local evaluation service, not a public data API.

Security limits: a malicious local process can reach another process's loopback service; the local mode is not a multi-user access-control system. A public institutional integration needs the host's own authentication, rights policy, rate limits, CSP and audit process. Neither the static UI nor the local adapter claims to verify manuscript content independently of its pinned source.

Performance target: no framework runtime, external asset, continuous animation or polling. The reference catalog is tiny; tab changes only replace small DOM fragments. Run `tests/profile.py` to measure browser heap, DOM nodes, resource transfer, load time, and the Python preview server's RSS on the target machine. Results are measurements, not guaranteed budgets on every browser.
