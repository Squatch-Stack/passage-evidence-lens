# Passage Evidence Lens

An **independent, unofficial interface study** for finding a manuscript passage, reading its sourced transcription, seeing correction hands, and opening the institution's source record. It is designed as a small contribution or companion for the Codex Sinaiticus Project's ongoing portal renewal, not as a replacement for its institutional service.

The code is MIT-licensed and has no runtime package dependencies. `data/loci.json` contains four passage labels and official deep links. This repository distributes **no manuscript images, XML transcription, translation text, folio metadata, or copies of the existing website**. The manuscript-looking artwork is original CSS. The local research adapter is opt-in and binds to loopback; its external SQLite file is never included in this repository.

## Run

```sh
python3 dev_server.py --port 8777
```

Open `http://127.0.0.1:8777/?ref=Luke.11.10`. The public mode is link-only. It is also deployable as static files on GitHub Pages: `index.html`, `styles.css`, `app.js`, `favicon.svg`, and `data/loci.json`.

To connect an **existing, separately licensed local research index** for end-to-end evaluation, set `LENS_LOCAL_TEXT=1`, `LENS_DB` to its SQLite file, and `LENS_LOCK` to its pinned source lock; then open `?ref=Luke.11.10&mode=local`. This preview remains bound to `127.0.0.1`. Do not publish that local mode or its generated screenshots as a hosted transcription without an asset-specific rights decision.

## What is proven

- Four source-linked references; keyboard-operable tabs for reading, corrections, source trail, and integration.
- A loopback adapter that shows a main reading, correction hands, folio locator and exact import ID from a pinned external source index.
- Content Security Policy, no external scripts or fonts, no tracking, no cross-origin API access, strict URL/ref validation, and no arbitrary file serving.
- Responsive layout and automated browser/security/profile checks under `tests/`.

## Rights and relationship

The [Codex Sinaiticus Project](https://codexsinaiticus.org/en/) is the source of record. Its [XML transcription](https://codexsinaiticus.org/en/project/transcription_download.aspx) is CC BY-NC-SA 3.0; [electronic images and some metadata](https://codexsinaiticus.org/en/copyright.aspx) have separate institutional conditions. This MIT license covers only the independently written interface code. See [DATA_POLICY.md](DATA_POLICY.md) and [INTEGRATION.md](INTEGRATION.md). This study has no endorsement from the project's partner institutions.

## Funding

[Squatch Stack GitHub Sponsors](https://github.com/sponsors/Squatch-Stack) and [Ko-fi](https://ko-fi.com/squatchstack) support Squatch Stack's independent open tooling and maintenance. They are not fundraising channels for the manuscript institutions. Patreon is intentionally omitted from the site and `FUNDING.yml` until its current URL is verified. Sponsorship does not expand the rights to redistribute project XML or images.

## Contribution path

The [Leipzig University Library redevelopment](https://www.ub.uni-leipzig.de/forschungsbibliothek/projekte/projekte-chronologisch-alle/codex-sinaiticus) already targets mobile accessibility, IIIF and reusable code. The proposed handoff is a small, tested passage dossier component with a typed evidence adapter and source/rights rules. Institutional integration would start with their preferred API, license and contribution process. No claim is made that this code is part of their portal.
