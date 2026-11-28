---
name: accessible-visual-verification
description: Verify document page bounds for users who cannot see them.
version: 0.1.0
author: Julian Dreykorn (mimocomputer), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [accessibility, blind, screen-reader, vision, pdf, verification]
    category: productivity
    related_skills: [pdf]
---

# Accessible Visual Verification

Confirm where content starts and stops in a document (PDF, scanned booklet, image
set) on behalf of a user who cannot look at it — "split this score/report into
per-item files, but I cannot reliably see where each item begins and ends". The
user delegates the *sight* to you and verifies the result from your stated
evidence, so the evidence is part of the deliverable, not a footnote to it.

Does not cover full-screen terminal programs (ncurses/dialog/whiptail/debconf).
There the surface is an emulated pty screen and the question is where the
terminal cursor sits, not what a rendered page looks like.

## When to Use

- The user is blind or cannot inspect a rendered document, and a boundary,
  figure or layout must be settled before you split, quote or archive it.
- You are about to hand back files cut at boundaries that only you have seen.
- Don't use it for machine-readable structure: when a text index, table of
  contents or embedded outline answers the question, use that instead of vision.

## Prerequisites

- The `pdf` skill's prerequisites: its helper scripts (`scripts/pdf_read.py`,
  `scripts/pdf_page_image.py`) and the shared documents interpreter. Set `PY`
  exactly as that skill's Prerequisites block does, then run every helper below
  as `"$PY" scripts/...`.
- `vision_analyze` to read a rendered page.

## Procedure

1. **Find an authoritative index first.** Extract text with `scripts/pdf_read.py
   --text` and look for a table of contents, an index, or a printed page-number
   scheme. Done when you can name the ground truth that every `vision_analyze`
   call will be checked against — do not rely on vision alone while a text index
   exists.
2. **Render the candidate range at a modest DPI** — 100 is enough for layout and
   title recognition, 300 only when fine text must be read:

   ```bash
   "$PY" scripts/pdf_page_image.py --pages 1-20 --dpi 100 --out-dir <preview-dir>
   ```

   Done when every page you intend to judge exists as an image.
3. **Verify both ends of every range with `vision_analyze`, not just the start.**
   - The opening page: title text and printed page number, matched against the index.
   - The closing page: an explicit terminal marker — a double bar line, "Fine", a
     blank system, trailing whitespace — not merely a page that looks like a
     plausible ending. A climax with a rallentando and no final barline is a
     false stop; check one page further before trusting the boundary.
   Cross-check the printed page number *in the graphic* against the index, never
   against the file's own 1-based page count, which front matter shifts apart.
4. **Batch independent `vision_analyze` calls in one turn.** Checking page 6 and
   page 17 has no dependency, so do not serialize them one call per turn.
5. **Report the evidence, not only the artifacts.** Give the page-range-to-item
   mapping you used (both file page numbers and printed page numbers when they
   differ), name what you deliberately excluded — covers, licence pages, blanks —
   and why. This is what lets the user, or a sighted third party, spot-check the
   result without re-deriving it.
6. **Flag genuine ambiguity instead of guessing.** When no title, no closing cue
   and no index entry agree, say so and present the alternatives; never pick the
   more plausible split and present it as fact.

## Pitfalls

- **One `vision_analyze` call per boundary is not enough.** A description that
  reads like an ending (rallentando, diminuendo) can be wrong when the double bar
  line is on the next page. Require an explicit terminal marker, or check one page
  further.
- **Printed page numbers routinely differ from file page indices** (cover, licence
  and back matter). Report both when they disagree.
- **Re-inspect the final artifact after corrections.** An earlier preview does not
  verify the delivered version; re-render the affected pages whenever spacing,
  font size or page dimensions changed.
- **Distinguish text bounds from glyph metrics.** Audit prose and directions per
  text span rather than as one page block: music-font boxes, especially stretched
  braces, can extend outside the page while the ink stays inside. Inspect the
  rendered symbol before calling a bound clipped, and never present a
  text-bounds pass as a full graphical collision test.
- **Never ask the user whether page X looks right.** They cannot check it — that
  is the whole task. Cite the index entry, the title match or the terminal marker.

## Verification

- Every delivered boundary names its file page number and printed page number,
  the index entry it matched where one exists, and the closing cue that proved
  the end.
- The reported mapping accounts for every page of the source: assigned to an item
  or explicitly excluded.
- Anything you could not confirm is listed as unresolved, not dropped or guessed.
