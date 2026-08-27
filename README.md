## Ilpo Väätäinen

**I measure whether reported numbers survive their own error.**

Benchmark accuracies, leaderboard ranks, backtest Sharpes, deployment claims — they
are published as point estimates, stripped of the uncertainty that produced them. My
work is to recompute them from the raw data, attach the interval, and report what is
left standing. Sometimes the answer is that the number holds. Sometimes the ranking
was sampling noise, or the accuracy was the label's own algebra handed back.

Finland · remote · Finnish (native), English (professional)

---

### Published

**[The Benchmark Number Is Not the Deployment Number](https://doi.org/10.5281/zenodo.22109473)**
Rank collapse and base-rate collapse, measured across four domains.
`10.5281/zenodo.22109473`

**[The Catalogue Is the Instrument](https://doi.org/10.5281/zenodo.22124423)**
How the choice of sign inventory moves the statistics of an undeciphered script
(rongorongo) — including the ligature artefact my own metric produced before I
caught it. `10.5281/zenodo.22124423` · code:
**[rongorongo-catalogue-audit](https://github.com/ipezygj/rongorongo-catalogue-audit)**

### Audits — code, data, and the reproduction

**[dataco-late-delivery-audit](https://github.com/ipezygj/dataco-late-delivery-audit)**
Logistics ML's favourite number — ~97% accuracy at predicting late deliveries — is
the label's own algebra. Leaked vs. clean reproduction (100% / 97.5% / 69%) and a
census of 65 public works, 28 of them verifiably leaked.

**[swebench-rank-audit](https://github.com/ipezygj/swebench-rank-audit)**
How much of a leaderboard ranking survives its own sampling error. Paired-resolution
audit across four SWE-bench splits and MTEB.

**[preregistered-miss](https://github.com/ipezygj/preregistered-miss)**
A preregistered hidden-test prediction, the miss that refuted it, and every number's
receipt. Published because it failed.

**[ControlBattery](https://github.com/ipezygj/ControlBattery)** — Lean 4 · mathlib
The statistics a control battery rests on, proved rather than asserted: Šidák never
exceeds Bonferroni, and Bonferroni's union bound needs no independence assumption.
Kernel-checked, and CI rejects any proof resting on `sorry`.

### Merged upstream

**[pmorissette/ffn](https://github.com/pmorissette/ffn)** — `calc_deflated_sharpe_ratio`
and `calc_expected_max_sharpe` (Bailey & López de Prado), plus the follow-up fix for
a series with no dispersion.

**[uber/causalml](https://github.com/uber/causalml)** — bootstrap confidence intervals
for `auuc_score()` and `qini_score()`.

**[hummingbot/hummingbot](https://github.com/hummingbot/hummingbot)** — Hyperliquid auth
silently accepting wrong private keys; the KuCoin perpetual trade-stream topic and
timestamp field; a Vertex testnet WebSocket URL.

### Built end to end (source private — happy to walk through it live)

**Ranger Sovereign Vault** — delta-neutral funding-arbitrage vault deployed to Solana
mainnet; honourable mention, 2026 hackathon.
**Babble Parenting** — a published parenting app: sound recording, feeding timers,
calendar, memory storage.
**Chimera** — event-driven trading automation: real-time market data, risk controls,
parallel strategy testing.

---

### How I work

I direct AI tooling (Claude) through design, implementation and analysis, and I operate
what I build. Every number on this page was recomputed from raw data before it was
written down, and where the artefact is public the recomputation is public with it.

**ipezygj2@gmail.com**
