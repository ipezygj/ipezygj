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

**[How the Choice of Sign Inventory Moves the Statistics of an Undeciphered Script](https://doi.org/10.5281/zenodo.22057706)**
Three published readings of one rongorongo corpus move the entropy statistic 4.1 times
further than the structure it exists to detect — including the ligature artefact my own
metric produced before I caught it. `10.5281/zenodo.22057706` (concept DOI, resolves to
the current version) · code:
**[rongorongo-catalogue-audit](https://github.com/ipezygj/rongorongo-catalogue-audit)**

**[What a Transit-Search Threshold Does When There Is Nothing to Find](https://doi.org/10.5281/zenodo.22344440)**
A measured null distribution for the box-least-squares detection statistic on Kepler
photometry. About one planetless star in ten clears the literature threshold on a single
quarter; the confirmed hot Jupiter used as a control ranks sixth, behind five stars with
nothing in them; and requiring the period to repeat across quarters removes 86% of the
noise and none of the stellar variability — because what survives is not noise.
`10.5281/zenodo.22344440`

**[How Much of a Published Figure Is the Catalogue?](https://doi.org/10.5281/zenodo.22345205)**
A whole-catalogue census of the 1,410 human microRNA entries no curation supports. They
carry 12.2% of the literature, not the two thirds their share of the catalogue suggests —
and 570 of them fail all four annotation criteria while the same test fails none of the
506 curated entries. Both of my own framings died on the way, in opposite directions.
`10.5281/zenodo.22345205`

**[A Pre-Registered Configuration Test for the Göbekli Tepe Pillar 43 "Date Stamp"](https://doi.org/10.5281/zenodo.22139090)**
A stated failure criterion, filed before the test. `10.5281/zenodo.22139090`

**[How Much of a Published Statistic Belongs to the Choice Upstream of It](https://doi.org/10.5281/zenodo.22162050)**
The method behind the audits below, stated once: name the coding decision, assemble the
codings other people published, recompute the statistic *and its null* under each, and
report the movement against the effect the statistic exists to detect. Six worked cases
across epigraphy, astronomy, archaeoastronomy, two leaderboards and clinical variant
prediction — two of which return less than the audit set out to find — and a catalogue
of the five ways the procedure misleads, each an error I made running it.
`10.5281/zenodo.22162050`

### Audits — code, data, and the reproduction

**[dataco-late-delivery-audit](https://github.com/ipezygj/dataco-late-delivery-audit)**
Logistics ML's favourite number — ~97% accuracy at predicting late deliveries — is
the label's own algebra. Leaked vs. clean reproduction (100% / 97.5% / 69%) and a
census of 65 public works, 28 of them verifiably leaked. `10.5281/zenodo.22342749`

**[swebench-rank-audit](https://github.com/ipezygj/swebench-rank-audit)**
How much of a leaderboard ranking survives its own sampling error. Paired-resolution
audit across four SWE-bench splits and MTEB. `10.5281/zenodo.22342751`

**[preregistered-miss](https://github.com/ipezygj/preregistered-miss)**
A preregistered hidden-test prediction, the miss that refuted it, and every number's
receipt. Published because it failed. `10.5281/zenodo.22342755`

**[eval-integrity](https://github.com/ipezygj/eval-integrity)**
Eight audits of public AI evaluation datasets — AlpacaEval, GPQA, LiveCodeBench,
MT-Bench and three RewardBench analyses — each recomputed from raw data.
`10.5281/zenodo.22343058`

**[ControlBattery](https://github.com/ipezygj/ControlBattery)**
The statistics a control battery relies on, proved in Lean 4 rather than asserted.
`10.5281/zenodo.22342753`

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
