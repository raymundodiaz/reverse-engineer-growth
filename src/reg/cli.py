"""Reverse Engineer Growth — CLI v0."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_CTA_URL = "https://iac.ventaja.com.mx/"
DEFAULT_CTA_LABEL = "Medir IAC gratis (~8 min)"


class _HomeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.h1: list[str] = []
        self.h2: list[str] = []
        self._h_level: int | None = None
        self._buf: list[str] = []
        self.meta_desc = ""
        self.links: list[str] = []
        self.ctas: list[str] = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2"):
            self._h_level = int(tag[1])
            self._buf = []
        elif tag == "meta" and (ad.get("name") or "").lower() == "description":
            self.meta_desc = ad.get("content", "") or ""
        elif tag == "a":
            href = ad.get("href") or ""
            text_hint = ad.get("aria-label") or ""
            self.links.append(href)
            if text_hint:
                self.ctas.append(text_hint.strip())

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2") and self._h_level:
            text = " ".join("".join(self._buf).split())
            if text:
                (self.h1 if self._h_level == 1 else self.h2).append(text[:300])
            self._h_level = None
            self._buf = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._h_level:
            self._buf.append(data)


def _fetch(url: str, timeout: int = 25) -> tuple[str, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ReverseEngineerGrowth/0.1 (+https://ventaja.com.mx)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        final = res.geturl()
        raw = res.read()
        charset = res.headers.get_content_charset() or "utf-8"
        try:
            text = raw.decode(charset, errors="replace")
        except LookupError:
            text = raw.decode("utf-8", errors="replace")
        return final, text


def _domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or "unknown"


def _guess_icp(title: str, h1: list[str], h2: list[str], body_len: int) -> tuple[str, str]:
    blob = " ".join([title] + h1 + h2).lower()
    if any(w in blob for w in ("multi", "sedes", "enterprise", "erp", "sla", "compliance", "nIIF", "esg")):
        return "scale", "Language hints multi-site / enterprise / compliance (proxy only)."
    if any(w in blob for w in ("automat", "proceso", "sistema", "operaci", "escala", "indicador")):
        return "system", "Language hints systems / ops / scale transition (proxy only)."
    if body_len > 8000 or len(h2) > 8:
        return "system", "Heavy site narrative; default system-led until human corrects."
    return "unknown", "Insufficient public signal; do not invent."


def _scorecard(h1: list[str], h2: list[str], ctas: list[str], title: str) -> dict:
    cta_n = len(ctas) + sum(1 for h in h2 if any(x in h.lower() for x in ("solicitar", "demo", "diagn", "probar", "agendar")))
    focus = "weak" if cta_n >= 8 or len(h2) > 12 else ("mixed" if cta_n >= 4 else "strong")
    offer = "mixed"
    if h1:
        offer = "strong" if len(h1[0]) < 180 else "mixed"
    return {
        "offer_clarity": {"status": offer, "note": (h1[0][:160] if h1 else title) or "no h1"},
        "owner_dependence_proxy": {"status": "unknown", "note": "Needs human/call; not inferred from homepage alone."},
        "demand_engine": {"status": "unknown", "note": "v0 does not score ads libraries; optional later."},
        "conversion_friction": {
            "status": "mixed" if cta_n else "unknown",
            "note": f"CTA-like signals counted≈{cta_n} (noisy HTML parse).",
        },
        "proof_trust": {"status": "unknown", "note": "Logos/cases not classified in v0 fetch."},
        "focus_vs_menu": {
            "status": focus,
            "note": "Many H2/CTA-like nodes → menu risk; few → clearer door.",
        },
        "system_vs_tactics": {
            "status": "mixed",
            "note": "Homepage copy only; tactics salad needs deeper evidence.",
        },
    }


def _lever_draft(icp: str, focus_status: str, h1: str) -> dict:
    """Conservative open harness — human must confirm."""
    if focus_status == "weak":
        return {
            "lever": "Entry door diluted: too many offers/CTAs compete before one growth constraint is named.",
            "not_this": "More traffic, more ads, or more AI features on the same confused door.",
            "yes_this": "One primary offer + proof path; everything else behind the first win.",
            "anti_moves": [
                "Scale paid acquisition before a single primary CTA/offer wins.",
                "Add another product line to the homepage hero.",
            ],
            "confidence": "low-medium",
            "rule": "IF multi-CTA/menu heavy THEN focus/offer-clarity lever",
        }
    if icp == "system":
        return {
            "lever": "Growth likely constrained by system clarity (process/governance/offer mechanism) more than raw awareness — validate with IAC + human map.",
            "not_this": "Another loose tactic pack (CRM/ads/course) without naming the bottleneck.",
            "yes_this": "Diagnose the dominant constraint; sequence three moves max.",
            "anti_moves": ["Pitch a full marketing stack before diagnosis."],
            "confidence": "low",
            "rule": "system archetype default — human confirm",
        }
    return {
        "lever": f"Insufficient automatic certainty. Public headline signal: {h1[:120] or 'n/a'}. Run IAC + human lever map.",
        "not_this": "Pretending a full growth audit from a homepage scrape.",
        "yes_this": "Collect system evidence; name one constraint with a human in the loop.",
        "anti_moves": ["Ship a 10-tactic PDF from thin public data."],
        "confidence": "low",
        "rule": "fallback",
    }


def _write_run(out_dir: Path, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evidence.json").write_text(json.dumps(payload["evidence"], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "scorecard.json").write_text(json.dumps(payload["scorecard"], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "unknowns.md").write_text(
        "# Unknowns\n\n" + "\n".join(f"- {u}" for u in payload["unknowns"]) + "\n",
        encoding="utf-8",
    )
    ev_lines = ["# Evidence (L4)\n"]
    for e in payload["evidence"]["items"]:
        ev_lines.append(f"- **{e['id']}** · {e['title']} · `{e.get('url','')}`")
        if e.get("note"):
            ev_lines.append(f"  - {e['note']}")
    (out_dir / "evidence.md").write_text("\n".join(ev_lines) + "\n", encoding="utf-8")

    L = payload["lever"]
    S = payload["system"]
    cta_url = payload["cta"]["url"]
    cta_label = payload["cta"]["label"]
    readout = f"""# Growth readout — {payload['brand']}

<sub>Reverse Engineer Growth v0.1 · Ventaja · MIT · {payload['generated']} · confidence lever: **{L['confidence']}**</sub>

**ICP archetype (proxy):** `{payload['icp']['code']}` — {payload['icp']['note']}

**CTA:** [{cta_label}]({cta_url})

---

## 1. System sketch (from public page)

| Stage | Note |
|---|---|
| Attraction | {S['attraction']} |
| Conversion | {S['conversion']} |
| Delivery | {S['delivery']} |
| Retention | {S['retention']} |
| Cash / decision | {S['cash']} |

**Flow:** {S['flow_one_liner']}

---

## 2. One lever (hypothesis — human must confirm)

> **Lever:** {L['lever']}

| | |
|---|---|
| **Not this (symptom)** | {L['not_this']} |
| **Yes this (mechanism)** | {L['yes_this']} |
| **Harness rule** | {L['rule']} |

**Anti-moves**
"""
    for a in L["anti_moves"]:
        readout += f"\n- {a}"
    readout += f"""

---

## 3. Growth scorecard (coarse)

"""
    for k, v in payload["scorecard"].items():
        readout += f"- **{k}**: `{v['status']}` — {v['note']}\n"

    readout += f"""
---

## 4. Placement hint

Default open-source path: **IAC** (system number), not a tactic pack.  
Paid lever audit / diagnosis is a separate product when a decider is present.

---

## 5. Next step

1. Run **[IAC]({cta_url})** with the decision-maker.  
2. If the number and the story match a real constraint, book a human growth-lever map.  
3. If not: **nothing** — do not sell theater.

---

*Not a substitute for a paid audit. Map opens the door; it does not replace judgment.*
"""
    (out_dir / "readout.md").write_text(readout, encoding="utf-8")
    (out_dir / "meta.json").write_text(
        json.dumps(
            {
                "tool": "reverse-engineer-growth",
                "version": "0.1.0",
                "badge": "Ventaja",
                "cta": payload["cta"],
                "input": payload["input"],
                "final_url": payload["final_url"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def run(url: str, out_root: Path) -> Path:
    if not re.match(r"^https?://", url):
        url = "https://" + url
    try:
        final, html = _fetch(url)
    except urllib.error.URLError as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        sys.exit(2)

    p = _HomeParser()
    try:
        p.feed(html)
    except Exception:
        pass
    title = " ".join(p.title.split()) or _domain(final)
    brand = _domain(final).split(".")[0].capitalize()

    # crude CTA harvest from visible link texts already limited; also scan buttons-ish
    raw_lower = html.lower()
    for pat in ("diagnóstico", "diagnostico", "solicitar", "agendar", "demo", "prueba", "empezar", "medir"):
        if pat in raw_lower:
            p.ctas.append(pat)

    icp_code, icp_note = _guess_icp(title, p.h1, p.h2, len(html))
    score = _scorecard(p.h1, p.h2, p.ctas, title)
    lever = _lever_draft(icp_code, score["focus_vs_menu"]["status"], p.h1[0] if p.h1 else title)

    import os

    cta_url = os.environ.get("REG_CTA_URL", DEFAULT_CTA_URL)
    cta_label = os.environ.get("REG_CTA_LABEL", DEFAULT_CTA_LABEL)

    evidence_items = [
        {"id": "E1", "title": "Document title", "url": final, "note": title},
        {"id": "E2", "title": "H1", "url": final, "note": " | ".join(p.h1) or "(none)"},
        {"id": "E3", "title": "H2 sample", "url": final, "note": " | ".join(p.h2[:8]) or "(none)"},
        {"id": "E4", "title": "Meta description", "url": final, "note": p.meta_desc or "(none)"},
    ]

    unknowns = [
        "Paid media libraries not queried in v0",
        "Owner-dependence not knowable from homepage alone",
        "Revenue, CAC, conversion rates unknown",
        "ICP archetype is a proxy — human confirm",
        "Lever confidence is low until human map / IAC",
    ]

    system = {
        "attraction": "Public site narrative only (v0).",
        "conversion": f"CTA-like noise≈{len(set(p.ctas))}; primary door unclear if menu-heavy.",
        "delivery": "Not visible from homepage scrape.",
        "retention": "Not visible from homepage scrape.",
        "cash": "Pricing page / sales motion not fully classified in v0.",
        "flow_one_liner": "Visit site → many possible CTAs → ? (human must complete).",
    }

    payload = {
        "brand": brand,
        "input": url,
        "final_url": final,
        "generated": str(date.today()),
        "icp": {"code": icp_code, "note": icp_note},
        "evidence": {"items": evidence_items},
        "scorecard": score,
        "lever": lever,
        "system": system,
        "unknowns": unknowns,
        "cta": {"url": cta_url, "label": cta_label, "code": "iac"},
    }

    out_dir = out_root / f"{_domain(final)}-{date.today().isoformat()}"
    _write_run(out_dir, payload)
    return out_dir


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        prog="reg",
        description="Reverse Engineer Growth — one lever, not forty tactics (Ventaja).",
    )
    ap.add_argument("url", help="Company URL or domain")
    ap.add_argument(
        "-o",
        "--out",
        default="reg-out",
        help="Output root directory (default: ./reg-out)",
    )
    args = ap.parse_args(argv)
    out = run(args.url, Path(args.out))
    print(f"✓ wrote {out}")
    print(f"  readout: {out / 'readout.md'}")
    print(f"  CTA: {DEFAULT_CTA_URL}")


if __name__ == "__main__":
    main()
