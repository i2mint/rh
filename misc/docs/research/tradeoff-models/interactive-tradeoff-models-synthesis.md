# Interactive tradeoff models: synthesis

*2026-10-08 · scope: explorable explanations and UI elements, minimal-parameter phenomenological models, model representation and spec formats, fitting to data, uncertainty and sensitivity, tradeoff and value-of-information visualisation · requested for: a generic fleet tool that renders human-understandable, interactive models of tradeoffs (variables linked by simple parametric relations, sliders that update everything downstream, diagrams of the relations), fiddlable now and fittable to data later. First use: an experimental-design dashboard for a camera-based measurement campaign (print a test sheet → capture with a phone → upload → analyse) under bandwidth, operator-time and material budgets.*

This is the cross-cutting synthesis of six theme reports in this folder. Each section below points to its theme report, which holds the detail and the primary sources. References here are numbered for this document only.

## Summary and recommendation

1. **Write the model as data, not code**: one small, versioned YAML/JSON spec of variables, relations, constraints, objectives, pilots and views, with every variable carrying a *kind* (its knowledge status), a unit, a default, a range and a scale. No existing standard fits as-is; the spec borrows field names from PEtab, Modelica/FMI, influence diagrams, Squiggle and PROV [1], [2], [3], [4], [5]. The proposal is in the Recommendations section.
2. **Keep the relation graph acyclic** (meshed's "node name = argument name" convention) and provide bidirectionality as a *query*: the user locks variables and asks to solve for one, which is a bracketed 1-D root-find over its declared range, with an optional declared `inverse` as the fast path. This is Victor's Scrubbing Calculator and Excel's Goal Seek, and it is the largest gap in the in-house renderer rh, whose cyclic mesh needs a hand-written inverse per direction [6], [7], [8].
3. **Build every relation from 1–3-parameter shape primitives parametrised by things a person can picture**: a 1/e length or half-life instead of a rate, a midpoint and 10–90 % width instead of a slope, a value at a reference point instead of a raw coefficient. The same reparametrisations make nonlinear fits better behaved, and "sloppy model" theory explains why few parameters usually suffice [9], [10], [11].
4. **Draw one fixed Monte Carlo sample of the uncertain inputs and reuse it for everything**: the uncertainty bands, the sensitivity ranking, the value-of-information bars and the hypothetical-outcome frames. Re-map the same uniforms on every slider move (common random numbers), so curves do not jitter. In the theme benchmarks, 5,000 draws through a 20-node formula mesh took under 1 ms in Node, and five single-parameter EVPPIs over 10,000 draws took about 6 ms in NumPy, so all of it can run live [12], [13], [14]. These timings come from one laptop and are indicative only.
5. **Answer "which pilot should we run first" with value of information, not with "which parameter is most uncertain"**: rank named pilot experiments by expected value of sample information minus cost (ENBS), show "would it flip the decision?" next to each bar, and expect most parameters to be worth nothing to measure [14], [15], [16]. One regression per parameter on the shared sample gives both the first-order Sobol index and the EVPPI, so the sensitivity panel and the VOI panel are one computation with two readouts [12], [17].
6. **Treat each slider as a prior.** The default is the fitter's starting value, the range is its bound and the prior. For 1–2 parameters, compute the posterior on a grid in the browser and show prior → posterior as an interval-shrinkage bar. Report profile-likelihood intervals, correlation warnings, the range the data covered and provenance with every fitted value [18], [19], [20].
7. **Never let a guess look like a measurement**: a text badge plus a line style (solid = measured or fitted, dashed = assumed, dotted = guessed) on every value and curve, never colour alone. Saturation and hue tested as unintuitive for uncertainty, and dashing was the style users preferred [21], [22].
8. **The conclusion must survive without interaction.** The evidence that interactivity improves understanding is thin and mixed, and many readers never touch secondary controls. Ship a baseline design and two or three named presets, and pin the headline result [23], [24].

## What already exists (in-house)

- **i2mint/rh** (this repo): builds a reactive HTML app from a `mesh_spec` (target → inputs), JS `functions_spec` and `initial_values`; it allows cyclic dependencies, chooses widgets from name prefixes, and accepts JSON-Schema field overrides. It is the natural renderer for this spec once it gains units, log scales, interval inputs, locks + solve, and output views; gaps are listed in [6] §7.
- **i2mint/meshed**: a DAG of Python functions in which node names are argument names. The spec's `relations` compile to a `meshed.DAG` one-to-one [1] §4.
- **i2mint/dagapp**: Streamlit apps from meshed DAGs. It is a second surface over the same DAG, but every widget change re-runs the script on the server, which is the main latency risk [6] §6.
- **thorwhalen/ba**: research on prior elicitation (elicit observable quantities; PreliZ, SHELF) [25]; the theme reports build on it and do not repeat it.
- **thorwhalen/hired**: research on epistemic state, open-world defaults and value of information for question selection [26].
- Nothing in the fleet already covered explorable-model UI, phenomenological model catalogues, spec formats, sensitivity analysis or VOI for experiments; those are new here.

## Theme digests

### 1. Explorable explanations and UI elements → [01-explorable-explanations-and-ui-elements.md](01-explorable-explanations-and-ui-elements.md)

Victor's 2024 postscript says that by "explorable explanation" he meant "a written argument whose assertions are backed by explorable computational models", which is what a tradeoff dashboard is [27]. The working principles are immediate and reversible feedback, the consequence shown next to the control, reader-controlled steps up and down the ladder of abstraction (sweep one variable and plot the family of outcomes), story-first defaults then free exploration (the "martini glass"), locks and solve-for, named scenarios, and just-in-time annotation [6]. Recompute well under 500 ms; an added half-second of latency measurably reduced exploration [6]. Sliders need keyboard and non-drag alternatives (WCAG 2.5.7) [6].

### 2. Minimal-parameter models and knowledge status → [02-minimal-parameter-models-and-knowledge-status.md](02-minimal-parameter-models-and-knowledge-status.md)

A catalogue of 13 primitives with interpretable parametrisations: exponential and Gaussian kernels, power law, cos³/cos⁴ off-axis falloff and its quadratic small-angle limit, Michaelis–Menten, linear-then-saturating, Hill, first-order approach, logistic threshold, averaging with a floor √(σ²/N + σ_f²), linear around a reference point, and Arrhenius. Dimensional analysis (Buckingham π) removes parameters, for example a bleed that depends on gap and kernel width only through gap/width. Positive, vaguely known quantities get a log slider and a lognormal `a to b` 90 % range (the Squiggle convention) [4]. Knowledge status has two axes, *role* and *evidence*, grounded in NUSAP pedigree, GRADE and the IPCC ladder (sign → order of magnitude → range → distribution), and the ladder picks the widget [9].

### 3. Representation and spec formats → [03-model-representation-and-spec-formats.md](03-model-representation-and-spec-formats.md)

The theme report surveys and grades 15 formats. SBML, CellML, FMI, XMILE, Modelica and PMML are too heavy or built for other jobs, and PPLs (PyMC, Stan, NumPyro) are fitting back-ends, not specs. Borrow PEtab's parameter fields (`scale: lin|log`, bounds, nominal, `estimate`, prior), influence-diagram node types, Modelica's `unit`/`displayUnit`/`min`/`max`/`start`, Squiggle percentile distributions, and PROV-O for `fitted_from`. Expressions use a whitelisted mathjs subset, parsed by mathjs in JS and by a small `ast` whitelist or SymPy in Python; never `eval` a spec string (numexpr's CVE-2023-39631 came from exactly that). Units live on variables and are validated by Pint at load; evaluation runs on canonical units [1]. Author the schema once in Zod and export JSON Schema for Python [1].

### 4. Fitting to data → [04-fitting-to-data.md](04-fitting-to-data.md)

The path runs NLS (lmfit, which maps one-to-one onto slider metadata) → profile-likelihood intervals → a grid posterior (1–2 parameters, in the browser) or Laplace/NUTS (more parameters, hierarchical) → posterior predictive check → residual GAM as a discrepancy detector. Keep the human's guessed form by default: symbolic regression (PySR) and SINDy *check* the form; they should not replace it. With a few dozen noisy points they return plausible but non-unique formulas [18]. Pool across devices with a weakly informative half-t prior on the between-device spread [18]. Design the pilot from the guesses (locally D-optimal). For a decay, measure at t = 0, t ≈ τ_guess and the longest feasible time. For a noise floor, use the smallest and the largest swatch, and the largest must pass the crossover N* = (σ/σ_f)² [18].

### 5. Uncertainty and sensitivity → [05-uncertainty-and-sensitivity.md](05-uncertainty-and-sensitivity.md)

Use one fixed LHS or scrambled-Sobol sample (N ≈ 5,000) and re-map it on every move. Every output shows a median with a 50/90 % gradient band, and the target output gets a 20–50-dot quantile dotplot with a threshold line, read by counting ("45 of 50 simulated campaigns clear SNR 10") [12]. Rank unknowns with given-data first-order Sobol indices plus output-vs-input scatterplots. Use a tornado chart only when labelled "around the current point", because one-at-a-time designs miss interactions, and 42 % of highly cited sensitivity analyses explored the input space badly [12]. An input known only as a range is not uniform: show the min–max envelope (a double loop or a p-box) next to the Monte Carlo band [12].

### 6. Tradeoffs, budgets and VOI → [06-tradeoffs-budgets-and-value-of-information.md](06-tradeoffs-budgets-and-value-of-information.md)

Show tradeoffs as a 2-D trade-off plot with infeasible regions greyed out, plus a brushed scatterplot matrix (Vega-Lite). Use parallel coordinates only as a secondary filter, since scatter plots beat them for reading relations [14]. Budgets stay hard constraints, drawn as budget bars with slack and a shadow price ("what one more unit would buy"). Collapse them into a single utility only with written-down exchange constants (Ashby) [14]. The VOI formulas over the shared sample are: EVPI = mean of per-draw max − max of means; EVPPI by one regression per parameter (Strong–Oakley–Brennan); EVSI by regressing on a simulated pilot summary. EVPPIs are not additive, and flip probability alone overstates importance [14]. When the ranges themselves are contested, add a satisficing view: the share of draws in which every threshold is met [14].

## Recommendations

### A. Minimal model-spec schema (`tradeoff-model/0.1`)

```yaml
spec: tradeoff-model/0.1
id: capture_campaign
variables:            # every input, parameter and output, one table (excerpt)
  sensor_px:  {kind: fact,       unit: px,  default: 4000}
  r:          {kind: design,     unit: mm,  default: 160, range: [0, 160], label: Offset from centre}
  distance:   {kind: design,     unit: cm,  default: 22,  range: [8, 50], label: Camera distance}
  phone:      {kind: device,     options: [phone_a, phone_b], default: phone_a}
  hfov:       {kind: fact,       unit: deg, default: 69, source: datasheet_x}
  falloff_k:  {kind: assumption, default: 3.5, range: [3, 4], fit_with: blank_sheet}
  decay_time: {kind: unknown,    unit: s,  dist: {lognormal: {p5: 0.01, p95: 10}}, scale: log, fit_with: burst_pilot}
  snr:        {kind: derived}
relations:            # target: {expr | fn, form, inverse?}; inputs = free symbols
  px_per_mm:  {expr: "sensor_px / (2 * distance * 10 * tan(hfov * pi / 360))", form: law}
  corner_rel: {expr: "cos(atan(r / (distance * 10))) ^ falloff_k", form: assumed}
constraints: [{expr: "upload_hours <= upload_budget_h", kind: budget}]
objectives:  [{maximize: snr}, {minimize: upload_hours}]
pilots:               # VOI ties each unknown to an experiment and its cost
  blank_sheet: {informs: [falloff_k], cost: {operator_h: 0.5}}
views: [{sliders: [distance, phone]}, {graph: {signs: true}}, {pareto: [snr, upload_hours]}]
provenance: {datasheet_x: {kind: source, uri: "..."}}
```

The field list, and where each field comes from:

| Field | Values / meaning | Borrowed from |
|---|---|---|
| `kind` | `design` (a knob we choose) · `device` (a discrete property per instance or scenario) · `fact` (known, sourced) · `assumption` (believed within a range) · `unknown` (structure known, magnitude not; wide range) · `derived` (computed) | influence-diagram decision / chance / deterministic nodes [1]; the five-tag practice of the first use; IPCC ladder for which widget [9] |
| `evidence` (optional) | `measured` · `estimated` · `assumed` · `guessed`, or a 0–4 pedigree score | NUSAP pedigree, GRADE [9] |
| `unit`, `display_unit` | Pint-parseable strings | Modelica `unit` / `displayUnit` [1] |
| `default`, `range`, `step`, `options` | slider start, bounds, increment, discrete choices | Modelica/FMI `start`/`min`/`max`; JSON Schema [1] |
| `scale` | `lin` / `log` (sliders, priors and fitting share it) | PEtab `parameterScale` [2] |
| `dist` | one family, parametrised by percentiles (`p5`, `p95`) | Squiggle / Guesstimate 90 % intervals [4] |
| `expr` / `fn` | mathjs-subset expression or a dotted function reference; the inputs are the free symbols | SBML assignment rules; meshed [1] |
| `form` | `law` (the form is established) or `assumed` (the form itself is a modelling assumption) | IPCC structural uncertainty [9] |
| `inverse` | explicit solve for a named input | lens `put` [1] |
| `signs` | edge polarity for the diagram | causal loop diagrams [1] |
| `fit_with`, `fitted_from` | the pilot or dataset that will fit it; the record of the fit that did (dataset, date, method, prior) | PROV-O `used` / `wasDerivedFrom` [5]; PEtab `estimate` [2] |
| `constraints` | `hard` / `budget` predicates, drawn as greyed regions and budget bars | Cassowary strengths; Ashby [1], [14] |
| `objectives` | `minimize` / `maximize`; two or more give a Pareto view | influence-diagram value node; tradespace exploration [1] |
| `pilots` | `informs`, `cost`, optional `simulate` function (needed for EVSI) | ENBS = EVSI − cost [15] |
| `views` | presentation only, never semantics | XMILE `views`; RJSF `uiSchema` [1] |

Rules: the spec is acyclic; at most three parameters per relation; every `assumption` or `unknown` has a `range` or `dist` and should have a `fit_with`; a variable that has been fitted gets `fitted_from` and changes its evidence, not its kind. The spec is versioned from the first file.

### B. UI element per relation and variable type

| Relation or variable type | Primary element | Companion | Pitfall to avoid |
|---|---|---|---|
| `design`, continuous | number with unit + slider (log if it spans more than about a decade) | linked mini-plot of the key output against it, current point marked | a linear slider over orders of magnitude |
| `design`, discrete (2–5 options) | segmented control, or named presets | scenario table side by side | a dropdown hides the alternatives |
| `device` | toggle or dropdown | a banner when it disables something (e.g. a capability absent) | silent consequences |
| `fact` | read-only number with badge and source link | none | presenting it as adjustable |
| `assumption` / `unknown` | range slider (two thumbs, optional best-guess thumb) with evidence badge and `fit_with` link | after fitting: posterior strip behind the thumb, data-support shading | showing a single precise value |
| 1-input shape relation (falloff, saturation, decay) | small curve plot with its 1–3 parameter handles | pilot data points and residuals once fitted; dashed beyond the data | hiding the form behind a number |
| output, single value | number + 50/90 % gradient band | text in frequencies ("45 of 50") | bare error bars |
| target output vs threshold | quantile dotplot (20–50 dots) with threshold line | hypothetical-outcome animation across panels | a cone read as a size |
| budget | budget bar with slack and shadow price | traffic-light text label | colour-only status |
| "what input gives this output?" | lock + solve (goal seek) on the output | report no or multiple solutions | silent non-convergence |
| two objectives | Pareto scatter, infeasible greyed | presets plotted as labelled points | more than three objectives on one front |
| more than two objectives | brushed scatterplot matrix | parallel coordinates as a filter | parallel coordinates as the main view |
| which unknown matters | first-order index bars from the shared sample | output-vs-input scatter on click; tornado labelled "around current point" | one-at-a-time ranking as the answer |
| which pilot to run | VOI bars (EVPPI, or ENBS per pilot card) | decision-flip curves; EVPI reference line | ranking by flip probability alone |
| the model's structure | node-link graph with signs and live values; highlight what an edit changed | prose with scrubbable numbers for the narrative | more than a few dozen nodes on one canvas (estimate) |

### C. Fitting and VOI workflow

1. **Guess.** Write the spec. Every `assumption` and `unknown` gets a range or a `p5`/`p95`, elicited as observable quantities where possible [25]. Show the prior predictive band.
2. **Propagate.** Draw one fixed LHS or Sobol sample (N ≈ 5,000) and re-map it on slider moves. Bands, dotplots and scatterplots come from it.
3. **Rank.** Regress each output on each unknown over the sample. The explained-variance share is the first-order index; with a decision attached, the same regression gives the EVPPI.
4. **Choose a pilot.** Each unknown points to the pilots that inform it. Simulate each pilot's data from the sample and compute EVSI by regression on its summary statistic, then rank pilots by ENBS = EVSI − cost. Place the pilot's measurement points D-optimally at the current guess (decay: t = 0, τ, and the longest time).
5. **Fit.** NLS from the slider defaults within the slider bounds, then profile-likelihood intervals. Use a grid posterior for 1–2 parameters, or Laplace/NUTS beyond that or when pooling per device.
6. **Check.** Posterior predictive band over the data, a residual GAM for structure, and 2–3 candidate forms compared by AICc or LOO. Run PySR or SINDy only as a check on the form.
7. **Publish.** Write `fitted_from` (dataset id and hash, date, method, prior) and shade the data-support range on the input sliders. Dash curves outside it. Show the prior → posterior shrinkage bar and the contraction percentage.
8. **Loop.** Recompute VOI with the posteriors and stop running pilots when every ENBS ≤ 0.

## Open questions

- No controlled study was found on whether a live dependency graph helps people understand a model; treat the node-link view as a navigation aid and test it with users.
- Whether rh should grow these features or a new TS renderer (zodal + zustand) should consume the spec is an architecture decision for the build, not settled here. Both can consume the same spec.
- Minimum number of devices for partial pooling of a nonlinear parameter: no source found; "about five" is an unverified heuristic.
- Balling's 1999 "design by shopping" paper could not be checked online; the theme report cites the documented implementation instead.
- The benchmarks (browser propagation, NumPy EVPPI) were run once on one laptop; re-measure on a phone before relying on live recomputation at N = 5,000.

## Where this is used

The recommendations are distilled into the agent skill `tradeoff-models` (spec schema, shape-primitive catalogue, UI element table, fitting and VOI workflow), which cites this folder.

## REFERENCES

1. [Model representation and spec formats for interactive tradeoff models — theme report 03, this folder, 2026](03-model-representation-and-spec-formats.md)
2. [PEtab data format specification v1 — PEtab developers, 2026](https://petab.readthedocs.io/en/latest/v1/documentation_data_format.html)
3. [Modelica Language Specification, ch. 4: predefined types — Modelica Association, 2026](https://specification.modelica.org/master/class-predefined-types-and-declarations.html)
4. [Squiggle: Distribution Creation — Quantified Uncertainty Research Institute, 2026](https://www.squiggle-language.com/docs/Guides/DistributionCreation)
5. [PROV-O: The PROV Ontology — W3C, 2013](https://www.w3.org/TR/prov-o/)
6. [Explorable explanations, reactive documents, and which control fits which relation — theme report 01, this folder, 2026](01-explorable-explanations-and-ui-elements.md)
7. [Scrubbing Calculator — Victor B, 2011](https://worrydream.com/ScrubbingCalculator/)
8. [Use Goal Seek to find the result you want by adjusting an input value — Microsoft, n.d.](https://support.microsoft.com/en-us/office/use-goal-seek-to-find-the-result-you-want-by-adjusting-an-input-value-320cb99e-f4a4-417f-b1c3-4f369d6e66c7)
9. [Minimal-parameter phenomenological models and how to show knowledge status — theme report 02, this folder, 2026](02-minimal-parameter-models-and-knowledge-status.md)
10. [Universally Sloppy Parameter Sensitivities in Systems Biology Models — Gutenkunst RN et al., 2007](https://doi.org/10.1371/journal.pcbi.0030189)
11. [Parameter Orthogonality and Approximate Conditional Inference — Cox DR, Reid N, 1987](https://doi.org/10.1111/j.2517-6161.1987.tb01422.x)
12. [Uncertainty propagation, sensitivity analysis and uncertainty display for interactive tradeoff models — theme report 05, this folder, 2026](05-uncertainty-and-sensitivity.md)
13. [Some Guidelines and Guarantees for Common Random Numbers — Glasserman P, Yao DD, 1992](https://doi.org/10.1287/mnsc.38.6.884)
14. [Tradeoffs, budgets and value of information — theme report 06, this folder, 2026](06-tradeoffs-budgets-and-value-of-information.md)
15. [voi: Expected Value of Information (R package vignette) — Jackson C, Heath A, et al., 2024](https://cran.r-project.org/web/packages/voi/vignettes/voi.html)
16. [How to Measure Anything, 3rd ed. — Hubbard DW, 2014](https://oreilly.com/library/view/how-to-measure/9781118836446)
17. [Estimating multiparameter partial expected value of perfect information from a probabilistic sensitivity analysis sample: a nonparametric regression approach — Strong M, Oakley JE, Brennan A, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4819801)
18. [Fitting few-parameter tradeoff models to pilot data, honestly — theme report 04, this folder, 2026](04-fitting-to-data.md)
19. [Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood — Raue A et al., 2009](https://doi.org/10.1093/bioinformatics/btp358)
20. [Toward a principled Bayesian workflow in cognitive science — Schad DJ, Betancourt M, Vasishth S, 2021](https://doi.org/10.1037/met0000275)
21. [Visual Semiotics & Uncertainty Visualization: An Empirical Study — MacEachren AM et al., 2012](https://geography.wisc.edu/cartography/projects/publications/MacEachrenEtAl_2012_TVCG.pdf)
22. [Evaluating Sketchiness as a Visual Variable for the Depiction of Qualitative Uncertainty — Boukhelifa N, Bezerianos A, Isenberg T, Fekete J-D, 2012](https://www.aviz.fr/Research/UncertaintySketchy)
23. [Communicating with Interactive Articles — Hohman F, Conlen M, Heer J, Chau DH, 2020](https://distill.pub/2020/communicating-with-interactive-articles/)
24. [Authoring and Publishing Interactive Articles (PhD dissertation), ch. 7 — Conlen M, 2021](https://digital.lib.washington.edu/researchworks/items/5d615042-1f87-433e-9f04-1e2554a8bc97/full)
25. [Bayesian prior elicitation for Beta distributions: a practical survey — in-house, thorwhalen/ba, 2026](https://github.com/thorwhalen/ba/blob/main/misc/docs/resources/Bayesian%20prior%20elicitation%20for%20Beta%20distributions-%20a%20practical%20survey.md)
26. [Building a candidate-knowledge system: elicitation, active questioning, epistemic state — in-house, thorwhalen/hired, 2026](https://github.com/thorwhalen/hired/blob/main/misc/docs/research/elicitation-and-knowledge-store.md)
27. [Explorable Explanations (with 2024 postscript) — Victor B, 2011](https://worrydream.com/ExplorableExplanations/)
