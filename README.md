# Reverse Engineer Growth

**[Ventaja](https://ventaja.com.mx)** · MIT

> Paste a company. Get the **growth constraint** — one lever, not forty tactics.  
> Not an ad library dump. Not “steal their Meta creatives.”

```bash
pip install -e .
reg https://example.com
# → ./reg-out/<domain>-<date>/readout.md
```

**Default CTA:** measure the system with **[IAC](https://iac.ventaja.com.mx/)** (Índice de Automatización de Crecimiento).

---

## Why this exists

Everyone ships **marketing OSINT**: ads, pixels, SEO theater.

Almost nobody ships **growth done properly**:

- market before marketing  
- system before tactics  
- **one** dominant constraint  
- anti-goals  
- diagnosis before media spend  

**Reverse Engineer Growth** reads a business the way a growth operator should:  
attraction → conversion → delivery → retention → cash — then names **one lever** and what **not** to do.

Inspired in spirit by tools like REM (marketing teardown), but the unit of analysis is the **growth system**, and the judgment layer is Ventaja’s criterion (open principles + harness; dense L3 stays productized).

---

## What you get

| Artifact | Meaning |
|---|---|
| `evidence.md` | Public facts + sources (L4) |
| `readout.md` | 1-page growth map: ICP archetype, system sketch, **1 lever**, anti-moves |
| `scorecard.json` | Growth dimensions (offer, owner-dependence proxies, demand engine, focus, proof) — **not** an ads scorecard |
| `unknowns.md` | What we couldn’t see |

**Evals (harness):** exactly one lever · has “not this / yes this” · ≥1 anti-move · ICP classified · no 10-tactic laundry list · no “run more ads” without a mechanism.

---

## Quick start

```bash
cd reverse-engineer-growth
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
reg https://energymaster.co/mx/
open reg-out/*/readout.md
```

Optional: point CTA in config (default IAC):

```bash
export REG_CTA_URL=https://iac.ventaja.com.mx/
export REG_CTA_LABEL="Medir IAC gratis"
```

---

## Not this / Yes this

| Not this | Yes this |
|---|---|
| Longest-running ads = “winners” | Longest-running ads ≠ growth if the **system** is broken |
| Channel scorecard as the product | **Constraint + one lever** as the product |
| Steal the playbook | Don’t steal tactics — find the lever |
| CTA: buy UGC / more creatives | CTA: **[IAC](https://iac.ventaja.com.mx/)** → diagnosis if it fits |

---

## Open vs closed

| Open (this repo) | Closed (Ventaja product) |
|---|---|
| CLI, schemas, public principles | Dense L3 maxims, pricing, full IAC instrument |
| Growth harness v0 | Paid **Auditoría de palancas** / Diagnóstico |
| Example readouts | Live placement: Autopsia · Forensa · Atlavier · Consigliere |

Built and maintained in the **[Ventaja](https://ventaja.com.mx)** line of work (Forward Deployed Growth · criterion packaged).

---

## Pipeline (ICM)

```
intake → evidence (L4) → ICP archetype → system map
      → ONE lever (L3 rules) → anti-moves → placement hint → CTA (IAC)
```

Details: [`harness/v0/`](harness/v0/) · principles: [`PRINCIPLES.md`](PRINCIPLES.md)

---

## License

[MIT](LICENSE) · **Badge / attribution: Ventaja** — see [NOTICE](NOTICE).

---

## Links

- IAC: https://iac.ventaja.com.mx/  
- Ventaja: https://ventaja.com.mx  
- Design canon (internal): 2Brain `Proyectos/Repo growth-lever — diseño v0.md`
