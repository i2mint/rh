# Model representation and spec formats for interactive tradeoff models

Scope: how to write down *variables + relations + parameters + uncertainty + provenance* as tool-neutral data (YAML/JSON) that a Python backend and a JS/TS frontend can both consume, to drive slider-and-diagram tradeoff dashboards that can later be fitted to data. First consumer: an experimental-design dashboard for a camera-based measurement campaign.

## Summary (actionable)

- **Adopt no existing standard wholesale; borrow field names.** The closest matches are heavy XML standards (SBML, CellML, FMI, XMILE, Modelica) built for simulation, not for sliders-plus-diagrams. A ~10-field YAML spec that borrows their vocabulary is cheaper than any of them, and each field below names its donor.
- **The model is a DAG of named expressions (meshed's "node name = argument name" convention), not a cyclic mesh.** Bidirectionality ("what exposure gives 1 px of blur?") is a *query* on the DAG, solved by 1-D bracketed root-finding over the variable's declared range; an optional `inverse:` expression is the fast path; symbolic solving runs only at authoring time in Python.
- **Expressions: a whitelisted arithmetic subset in mathjs syntax**, parsed by mathjs in JS and by SymPy (with `convert_xor`) or a small `ast` whitelist in Python. Never `eval` a spec string: SymPy's `parse_expr` and numexpr have both been `eval`-based.
- **Uncertainty: percentile-parametrised distributions** (`{lognormal: {p5, p95}}`, the Squiggle/Guesstimate "90% interval" idiom), which sidesteps the per-library parametrisation traps.
- **Parameters borrow PEtab** (`scale: lin|log|log10`, bounds, nominal value, `estimate` flag, prior type) plus PROV-O-style `fitted_from`; variable `kind` borrows influence-diagram node types (decision / chance / deterministic / value).
- **Units: strings validated by Pint in Python, carried by mathjs units in JS, normalised to canonical units at load**; QUDT/UCUM identifiers are optional annotations, not the working syntax.
- **Author the schema once in Zod** and export JSON Schema with `z.toJSONSchema()` for the Python side; this matches the existing frontend stack and rh's RJSF-based widgets.

## 1. Representations and the terminology they supply

**Graphical-model family.** Causal DAGs encode "X directly influences Y" as arrows and are read for interventions (`do(x)`) as well as association [1]. Bayesian networks attach a conditional distribution to each node of a DAG [2]. Influence diagrams (decision networks) add node *types*: decision nodes (chosen), chance nodes (uncertain), deterministic nodes (functions of their parents) and a value node (the objective) [3]; the same lineage gives "value of information", the expected gain from resolving a chance node before deciding [4]. This node-type vocabulary is exactly what a tradeoff dashboard needs to decide which variables become sliders (decision), which become distributions (chance), which are computed (deterministic) and which are optimised (value).

**System dynamics.** Stocks (accumulations), flows (rates) and auxiliaries (algebraic helpers) are integrated over time; causal loop diagrams (CLDs) annotate each arrow with a polarity (+/−) and each loop as reinforcing or balancing [5], [6]. XMILE (OASIS standard, 2015) serialises `stock`, `flow`, `aux` and graphical functions (`gf`), with optional `units`, per-variable documentation, `<view>` sections, and input devices such as sliders and knobs [7]. Python tooling: PySD translates Vensim and XMILE files into Python modules [8]; JS/browser: Simlin compiles a Rust engine to WebAssembly (Apache-2.0) [9]. A static tradeoff model is the degenerate case with only auxiliaries; the CLD polarity idea is worth borrowing as an edge hint for diagrams.

**Bidirectional constraint systems.** Sussman and Steele's constraint networks propagate values through a network in whichever direction the known values determine, so one relation serves several computations [10]; ThingLab brought this to interactive graphical simulation [11]; Cassowary solves linear equality/inequality constraints with strength hierarchies incrementally, for UI layout [12]; Radul and Sussman's propagators generalise this to cells that accumulate partial information from autonomous propagators [13]. Lenses formalise a bidirectional transformation as a `get` plus a `put`, with round-trip laws [14]. In simulation tooling the same split appears as acausal equation-based modelling (Modelica: "No particular variable needs to be solved for manually", the tool decides [15]) versus causal block diagrams with fixed input/output ports (Simulink [16]).

**Spreadsheets and reactive recomputation.** A spreadsheet is a dependency graph recomputed incrementally; Mokhov et al. model Excel as one point in a design space of build systems (dynamic dependencies, restarting scheduler) [17]; Adapton is a general demand-driven incremental computation scheme [18]. Observable's runtime is the closest JS analogue to rh: variables "akin to a cell in a spreadsheet" that recompute from their inputs, but "circular inputs are not allowed" [19]. Excel's Goal Seek is the canonical bidirectional query: it "works only with one variable input value", and multi-input goals go to Solver [20].

**When bidirectionality is needed, and the cheapest way to provide it.** It is needed whenever the user's natural question is phrased as a target on an output ("how many items fit in 2 TB?", "what exposure keeps blur under 1 px?"). Three mechanisms, cheapest first in engineering cost:

| Mechanism | How | Cost / limits |
|---|---|---|
| Numerical 1-D root-finding on the DAG | Pin all inputs but one, solve `f(x) − target = 0` on the variable's declared `range` with bisection or Brent's method | Needs a sign change on the bracket [21]; works for any expression or function ref, in both languages, with no extra spec. Roughly 20–60 forward evaluations per solve (estimate) — negligible for small models. Multi-input targets become optimisation (Solver territory). |
| Declared explicit inverse | `inverse: {n_items: "storage / (shots * image_bytes)"}` on a relation (the lens `put`) | Exact and instant; costs authoring effort and can drift from the forward expression unless checked. rh's cyclic mesh is effectively this pattern. |
| Symbolic solve | SymPy solves the expression for the free symbol at authoring time, then prints the inverse to JS with `jscode` [22] and to NumPy with `lambdify` [23] | Python-only at authoring time; fails or branches for non-invertible expressions; good as a generator of `inverse:` entries, not as a runtime dependency. |

Recommendation: keep the spec **acyclic**; implement Goal-Seek-style root-finding as a generic frontend/backend service (a "pin and solve" UI gesture), and let `inverse:` override it when present. This keeps meshed's DAG semantics intact and avoids having to define what a cycle means.

## 2. Spec formats compared

Coverage key: V variables, R relations/expressions, P parameters, U units, Rg ranges/defaults, D distributions, Pv provenance/evidence, UI view hints. Verbosity is an estimate (relative to the YAML in §4).

| Format | Covers | Verbosity | Python / JS tooling | Licence | Verdict |
|---|---|---|---|---|---|
| PMML 4.4 [24], [25] | V, R (transformations), P (fitted model), Rg (`Interval`, `Value`), Pv (Header, build task) | High (XML) | sklearn2pmml (AGPL-3.0) [26]; no mainstream JS | Open spec (DMG) | Avoid: built for scoring trained ML models. |
| SBML L3 [27] + SBO [28] + MIRIAM [29] + distrib [30] | V (species, parameters with `constant`), R (MathML rules), P, U (`unitDefinition`), D (distrib package), Pv (RDF annotations with MIRIAM qualifiers, `sboTerm`) | Very high (XML + MathML) | libSBML (LGPL) [31]; libsbmljs [32] | Open spec | Borrow: `constant` flag, ontology-term annotation slot, `id`/`name` split. The distrib package was accepted in 2020 but libSBML/JSBML list only prototype support [30]. |
| PEtab [33], [34] | P (bounds, nominal value, `estimate`, priors), Pv (measurement tables), UI (visualisation table) | Low (TSV + YAML) | libpetab-python (MIT) | Open | **Borrow directly**: `parameterScale` (`lin`/`log`/`log10`), `lowerBound`/`upperBound`, `nominalValue`, `estimate`, prior types (`normal`, `logNormal`, `uniform`, `laplace`, …). |
| CellML 2.0 [35] | V (mandatory `units` on every variable, optional `initial_value` [36]), R (MathML), U | High (XML) | libCellML (Apache-2.0) [37] | Open | Borrow "every variable has a unit". No distribution construct found. |
| Modelica [15] | V, R (acausal equations), P, U, Rg (`Real` has `quantity, unit, displayUnit, min, max, start, fixed, nominal` … [38]) | Medium (own language) | OpenModelica (OSMC-PL); Modelica Standard Library BSD-3 | Spec freely distributable | Borrow the attribute names `unit`, `displayUnit`, `min`, `max`, `start`, `nominal`. Avoid as a format (needs a compiler). |
| FMI 3.0 / FMU [39] | V with `causality` (`input`, `output`, `parameter`, `local`, …), `variability`, `start`, `min`, `max`, units; R only as compiled binaries or C sources in a ZIP | Medium (XML) | FMPy (BSD-2) [40]; no JS runtime | CC BY-SA 4.0 doc, BSD-2 code | Borrow `causality`. Avoid as a format: the relations are opaque code. |
| Simulink [16] | V, R (causal blocks), P, UI | n/a (proprietary files) | MATLAB only | Proprietary | Avoid. |
| XMILE 1.0 [7] | V, R (infix equations, `IF THEN ELSE`), U, Rg, D (`NORMAL`, `LOGNORMAL` sampling functions only), Pv (per-variable documentation), UI (views, sliders, knobs, graphs) | High (XML) | PySD [8]; Simlin (wasm) [9] | OASIS (open) | Borrow: separation of model from `views`, input-device vocabulary, `gf` lookup tables. |
| PyMC graph [41] / Stan [42], [43] / NumPyro [44] | V, R, P, D (rich); graphs rendered from code (`model_to_graphviz`, `render_model` with distribution annotations) | Low (code) | Python (PyMC Apache-2.0, Stan BSD-3, NumPyro Apache-2.0) | Open | Borrow as **fitting backends** (`fit_with`), not as the spec: the model is code, not data. No unit or provenance fields found. |
| Guesstimate [45] | V, R (formulas "processed with Math.js"), D (a range is a 90% interval; normal default, uniform optional), Monte Carlo with 5000 samples | Very low | JS app | MIT | Borrow the 90%-interval input idiom and the mathjs precedent. |
| Squiggle [46], [47] | V, R, D (`5 to 10` = lognormal with p5=5, p95=10; `normal({p5,p95})`, `beta`, `mixture`, …) | Very low (own language) | JS/TS (MIT) | MIT | Borrow the percentile parametrisation (`{p5, p95}`); avoid the language (JS-only evaluator). |
| Causal [48], [49] | V, R (natural-language formulas), D (ranges, Monte Carlo) | Low (app) | SaaS, now part of Lucanet | Proprietary | Ideas only (readable formula names). |
| Excel named ranges [50], [20] | V (names), R (formulas), bidirectional query (Goal Seek) | Low | not assessed | Proprietary product | Borrow "names, not cell addresses" and Goal Seek as the bidirectional UX. |
| Observable [19] | V, R (reactive cells), UI (inputs) | Low (JS) | JS runtime (ISC) | ISC | Borrow the runtime model for the frontend; acyclic by design. |
| Pint / UCUM / QUDT [51], [52], [53] | U only | n/a | Pint (BSD-3); ucum-lhc for JS [54]; QUDT as RDF | Pint BSD-3; UCUM copyright Regenstrief (licence terms not verified); QUDT CC BY 4.0 | Use Pint strings as working syntax; UCUM/QUDT IDs as optional annotations. |

## 3. Expression language and units

| Option | Python | JS | Safety | Fit |
|---|---|---|---|---|
| mathjs syntax [55] | SymPy `parse_expr` with `convert_xor` (treats `^` as power) [56], or an `ast` whitelist | mathjs | mathjs parses to a tree and has not used `eval` since v4, but warns of possible unknown holes and recommends disabling `import`, `createUnit`, `evaluate`, `parse` and running in a worker [57]. SymPy's `parse_expr` "uses `eval`, and thus shouldn't be used on unsanitized input" [56]. | **Recommended** (with a function whitelist). Guesstimate's precedent [45]. |
| SymPy → JS printing | `lambdify` to NumPy [23] | `jscode` emits `Math.pow`/`Math.sin` code [22] | Generated code, so trusted at authoring time only | Good codegen path for rh's `functions_spec`. |
| numexpr [58] | fast array evaluation | none | `evaluate` was `eval`-based; CVE-2023-39631 (9.8) [59] | Avoid as the spec parser; fine as a vectorised backend for trusted, already-validated expressions. |
| CEL [60], [61] | cel-python (Apache-2.0) [62] | cel-js (MIT) [63] | "Non-Turing complete, and only accesses data provided by the host" [60] | Strong for constraints/predicates; thin math library. |
| JSON Logic [64] | json-logic-py | json-logic-js | Rules are data, no side effects | Too verbose for formulas; viable for constraints if expressions must be pure JSON. |
| DMN FEEL [65] | limited | limited | Business-rules standard | Avoid (tooling mostly Java). |

Recommended subset: numbers, identifiers (`[A-Za-z_][A-Za-z0-9_]*`, valid in both languages and in meshed, excluding reserved words), `+ − * / ^`, unary minus, parentheses, comparison operators (constraints only), and a whitelist such as `sqrt exp log log10 log2 abs min max floor ceil round sin cos tan atan2 clip`. Inputs of a relation are the expression's free symbols, so no separate input list is needed (meshed's convention made automatic).

Units: mathjs supports unit values, arithmetic and `to` conversion inside expressions, plus `createUnit` [66]; Pint does the same in Python [51]. Their unit names differ at the edges, so the robust pattern is: units live on variables (not inside expressions), Pint validates dimensional consistency of every relation at load, and both runtimes evaluate expressions on numbers already converted to a canonical unit per dimension, converting back to `display_unit` at the UI edge (the Modelica `unit`/`displayUnit` split [38]). UCUM is designed for unambiguous machine exchange of units and has case-sensitive and case-insensitive code sets [52]; QUDT supplies quantity-kind URIs [53]. Both belong in an optional `quantity_kind`/annotation slot.

## 4. Recommended minimal schema

```yaml
spec: tradeoff-model/0.1
id: capture_campaign
title: Capture campaign tradeoffs
variables:
  n_items:        {kind: decision, unit: "1",  default: 500, range: [50, 5000], scale: log, step: 1, title: Items to capture}
  shots_per_item: {kind: decision, unit: "1",  default: 4,   range: [1, 20], step: 1}
  exposure:       {kind: decision, unit: ms,   default: 4,   range: [0.5, 50], scale: log}
  megapixels:     {kind: decision, unit: "1",  default: 12,  range: [2, 50]}
  speed:          {kind: chance,   unit: mm/s, distribution: {lognormal: {p5: 2, p95: 20}}, status: assumed}
  pixel_pitch:    {kind: known,    unit: mm,   default: 0.05, status: measured, source: calibration_2026_09}
  storage_budget: {kind: known,    unit: GB,   default: 2000}
  blur:           {kind: derived,  unit: px}
  image_bytes:    {kind: derived,  unit: B}
  storage:        {kind: derived,  unit: GB}
  capture_time:   {kind: derived,  unit: h}
parameters:
  bytes_per_pixel: {unit: B, default: 0.4, range: [0.05, 3], scale: log, estimate: true,
                    prior: {lognormal: {p5: 0.2, p95: 1.0}}, fit_with: file_size_log, fitted_from: null}
  seconds_per_shot: {unit: s, default: 3, estimate: true, prior: {normal: {p5: 2, p95: 5}}}
relations:
  blur:         {expr: "speed * exposure / pixel_pitch", signs: {speed: "+", exposure: "+", pixel_pitch: "-"}}
  image_bytes:  {expr: "megapixels * 1e6 * bytes_per_pixel"}
  storage:      {expr: "n_items * shots_per_item * image_bytes",
                 inverse: {n_items: "storage / (shots_per_item * image_bytes)"}}
  capture_time: {fn: "campaign_models.capture_time"}   # function ref; inputs = its argument names
constraints:
  - {expr: "blur <= 1", label: Sharp enough, kind: hard}
  - {expr: "storage <= storage_budget", kind: budget}
objectives:
  - {minimize: capture_time}
  - {minimize: blur}
views:
  - {kind: sliders, vars: [n_items, shots_per_item, exposure, megapixels]}
  - {kind: graph, direction: LR, show_signs: true}
  - {kind: scatter, x: capture_time, y: blur, sweep: exposure}   # tradeoff curve
provenance:
  file_size_log: {kind: dataset, uri: "store://measurements/file_sizes", generated_at: 2026-10-01}
```

| Field | Meaning | Borrowed from |
|---|---|---|
| map key (`id`) | identifier valid in Python, JS and as a meshed node / argument name | SBML `id`; meshed convention |
| `title`, `description` | human label and help text | JSON Schema [67]; XMILE documentation [7] |
| `kind` | `decision` / `chance` / `known` / `derived`; objectives listed separately | influence-diagram node types [3]; FMI `causality` [39] |
| `status` | knowledge status: `measured` / `assumed` / `estimated` / `fitted` | GUM Type A vs Type B evaluation [68]; PEtab `estimate` [34] |
| `unit`, `display_unit` | canonical and display units, Pint-parseable | Modelica `unit`/`displayUnit` [38]; CellML [35] |
| `range`, `default`, `step` | slider bounds, start value, increment | Modelica/FMI `min`/`max`/`start`; JSON Schema `minimum`/`maximum`/`default`/`multipleOf` [67]; PMML `Interval` [25] |
| `scale` | `lin` / `log` / `log10` for sliders and for fitting | PEtab `parameterScale` [34] |
| `distribution` | one family with percentile or native parameters | Squiggle/Guesstimate 90% intervals [46], [45]; SBML distrib [30] |
| `relations.<target>.expr` / `.fn` | expression in the §3 subset, or a dotted function reference; inputs implied | SBML assignment rules [27]; meshed / rh `functions_spec` |
| `inverse` | explicit solve for a named input | lens `put` [14] |
| `signs` | edge polarity for diagrams and sanity checks | causal loop diagrams [6] |
| `parameters.*.estimate`, `prior` | fixed vs to-be-fitted; prior for fitting | PEtab [34] |
| `fit_with`, `fitted_from` | dataset a fit will use; record of the fit that set the value | PROV-O `used` / `wasDerivedFrom` [69] |
| `constraints` (`hard`, `soft`, `budget`) | feasibility predicates, shaded on sliders | Cassowary strengths [12]; CEL-style predicates [60] |
| `objectives` | `minimize`/`maximize` targets; several → Pareto front | influence-diagram value node [3]; tradespace exploration [70] |
| `views` | presentation only, never semantics | XMILE `views` and input devices [7]; RJSF `uiSchema` (used by rh) |
| `annotations` (optional) | ontology URIs per variable (QUDT quantity kind, domain terms) | SBML `sboTerm` + MIRIAM RDF [28], [29]; QUDT [53] |

Mapping onto the in-house components: each relation is a meshed node whose name is the target and whose arguments are the free symbols, so `relations` compiles to a `meshed.DAG` (expressions become small generated functions, `fn` refs are imported); rh's `mesh_spec` is `{target: free_symbols}`, its `functions_spec` is the expression printed to JS (mathjs or SymPy `jscode`), and its `field_overrides` are the variable's `title`/`range`/`default` as JSON Schema keywords; dagapp is a second (Streamlit) surface over the same DAG. On the TS side, the schema is authored in Zod and exported with `z.toJSONSchema()` (stable), while `z.fromJSONSchema()` is still experimental [71], so Zod should be the single source of truth.

## 5. Terminology and points not asked about

- **Terms worth adopting**: decision / chance / deterministic / value node [3]; exogenous vs endogenous variables [1]; causality and variability (FMI) [39]; *tradespace exploration* and Pareto front for "models of tradeoffs" [70]; *global sensitivity analysis* for "which slider matters" [72].
- **Sensitivity views are cheap and high-value.** A tornado or Sobol view answers "which assumption should we measure first", the value-of-information question [4]; SALib (MIT) implements Sobol, Morris, FAST and other methods, and needs only names and bounds, which `variables` already holds [73], [72].
- **Distribution parametrisation is a trap.** SciPy's `lognorm` uses shape `s` and `scale = exp(mu)` [74], Squiggle uses `lognormal(mu, sigma)` or percentiles [46], PEtab has separate `logNormal` and `parameterScaleNormal` [34]. Percentiles are the only parametrisation that reads the same in every library and to a human.
- **Cycles.** rh permits cyclic meshes; Observable forbids them [19]; constraint systems define them by solving [10], [12]. A spec that permits cycles must also define which value wins; keeping the spec acyclic and treating "solve for x" as a query avoids this.
- **Security is a spec property.** If specs can come from users or LLMs, the expression subset is the attack surface; the numexpr CVE came precisely from an LLM tool passing generated math to an `eval`-based evaluator [59].
- **Version the spec** (`spec: tradeoff-model/0.1`) from the first file, as the standards above do (SBML levels and versions, PEtab's versioned YAML problem file, FMI's versioned model description) [27], [34], [39].
- Not verified: UCUM's licence terms (the copyright notice is visible, the terms section was not read); whether mathjs offers a symbolic equation solver (not checked); Stan/NumPyro unit support (none found in the reference material read).

## REFERENCES

1. [Causal diagrams for empirical research — Pearl, 1995](https://doi.org/10.1093/biomet/82.4.669)
2. [Probabilistic Graphical Models: Principles and Techniques — Koller & Friedman, 2009](https://mitpress.mit.edu/9780262013192/probabilistic-graphical-models/)
3. [Influence Diagrams — Howard & Matheson, 2005 (reprint of 1981 report)](https://doi.org/10.1287/deca.1050.0020)
4. [Information Value Theory — Howard, 1966](https://doi.org/10.1109/tssc.1966.300074)
5. [System dynamics—a personal view of the first fifty years — Forrester, 2007](https://doi.org/10.1002/sdr.382)
6. [System Dynamics Modeling: Tools for Learning in a Complex World — Sterman, 2001](https://doi.org/10.2307/41166098)
7. [XMILE Version 1.0, OASIS Standard — Chichakly, Baxter, Eberlein et al. (eds.), 2015](https://docs.oasis-open.org/xmile/xmile/v1.0/xmile-v1.0.html)
8. [PySD documentation — SDXorg, 2026](https://pysd.readthedocs.io/en/master/)
9. [Simlin: system dynamics model editor and simulator — Powers, 2026](https://github.com/bpowers/simlin)
10. [Constraints—A language for expressing almost-hierarchical descriptions — Sussman & Steele, 1980](https://doi.org/10.1016/0004-3702(80)90032-6)
11. [The Programming Language Aspects of ThingLab, a Constraint-Oriented Simulation Laboratory — Borning, 1981](https://doi.org/10.1145/357146.357147)
12. [The Cassowary linear arithmetic constraint solving algorithm — Badros, Borning & Stuckey, 2001](https://doi.org/10.1145/504704.504705)
13. [The Art of the Propagator — Radul & Sussman, 2009](https://dspace.mit.edu/handle/1721.1/44215)
14. [Combinators for bidirectional tree transformations: a linguistic approach to the view-update problem — Foster, Greenwald, Moore, Pierce & Schmitt, 2007](https://doi.org/10.1145/1232420.1232424)
15. [Modelica Language Specification — Modelica Association, 2026](https://specification.modelica.org/master/)
16. [Simulink — MathWorks, 2026](https://www.mathworks.com/products/simulink.html)
17. [Build systems à la carte — Mokhov, Mitchell & Peyton Jones, 2018](https://doi.org/10.1145/3236774)
18. [Adapton: composable, demand-driven incremental computation — Hammer, Phang, Hicks & Foster, 2014](https://doi.org/10.1145/2594291.2594324)
19. [Observable Runtime — Observable, 2026](https://github.com/observablehq/runtime)
20. [Use Goal Seek to find the result you want by adjusting an input value — Microsoft, 2026](https://support.microsoft.com/en-us/office/use-goal-seek-to-find-the-result-you-want-by-adjusting-an-input-value-320cb99e-f4a4-417f-b1c3-4f369d6e66c7)
21. [scipy.optimize.brentq — SciPy developers, 2026](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.brentq.html)
22. [SymPy printing: JavaScript code printer (jscode) — SymPy Development Team, 2026](https://docs.sympy.org/latest/modules/printing.html)
23. [SymPy lambdify — SymPy Development Team, 2026](https://docs.sympy.org/latest/modules/utilities/lambdify.html)
24. [PMML 4.4.1 General Structure — Data Mining Group, 2019](https://dmg.org/pmml/v4-4-1/GeneralStructure.html)
25. [PMML 4.4.1 Data Dictionary — Data Mining Group, 2019](https://dmg.org/pmml/v4-4-1/DataDictionary.html)
26. [sklearn2pmml — JPMML, 2026](https://github.com/jpmml/sklearn2pmml)
27. [The Systems Biology Markup Language (SBML): Language Specification for Level 3 Version 2 Core — Hucka et al., 2019](https://doi.org/10.1515/jib-2019-0021)
28. [Controlled vocabularies and semantics in systems biology — Courtot et al., 2011](https://doi.org/10.1038/msb.2011.77)
29. [Minimum information requested in the annotation of biochemical models (MIRIAM) — Le Novère et al., 2005](https://doi.org/10.1038/nbt1156)
30. [SBML Level 3 Package: Distributions, Version 1, Release 1 — Smith et al., 2020](https://sbml.org/documents/specifications/level-3/version-1/distrib/)
31. [libSBML — SBML Team, 2026](https://github.com/sbmlteam/libsbml)
32. [libsbmljs—Enabling web-based SBML tools — Medley et al., 2020](https://doi.org/10.1016/j.biosystems.2020.104150)
33. [PEtab—Interoperable specification of parameter estimation problems in systems biology — Schmiester et al., 2021](https://doi.org/10.1371/journal.pcbi.1008646)
34. [PEtab data format specification v1 — PEtab developers, 2026](https://petab.readthedocs.io/en/latest/v1/documentation_data_format.html)
35. [CellML 2.0 — Clerx et al., 2020](https://doi.org/10.1515/jib-2020-0021)
36. [CellML 2.0 specification, §2.8 The variable element — CellML Editorial Board, 2020](https://cellml-specification.readthedocs.io/en/latest/reference/formal_and_informative/specB08.html)
37. [libCellML — CellML, 2026](https://github.com/cellml/libcellml)
38. [Modelica Language Specification, ch. 4: Classes, Predefined Types, and Declarations — Modelica Association, 2026](https://specification.modelica.org/master/class-predefined-types-and-declarations.html)
39. [Functional Mock-up Interface Specification 3.0 — Modelica Association Project FMI, 2022](https://fmi-standard.org/docs/3.0/)
40. [FMPy — Dassault Systèmes, 2026](https://github.com/CATIA-Systems/FMPy)
41. [pymc.model_graph.model_to_graphviz — PyMC developers, 2026](https://docs.pymc.io/en/stable/api/model/generated/pymc.model_graph.model_to_graphviz.html)
42. [Stan: A Probabilistic Programming Language — Carpenter et al., 2017](https://doi.org/10.18637/jss.v076.i01)
43. [Stan Reference Manual — Stan Development Team, 2026](https://mc-stan.org/docs/reference-manual/)
44. [NumPyro utilities: render_model — Pyro developers, 2026](https://num.pyro.ai/en/stable/utilities.html)
45. [Guesstimate app (source and README) — Getguesstimate, 2026](https://github.com/getguesstimate/guesstimate-app)
46. [Squiggle: Distribution Creation — Quantified Uncertainty Research Institute, 2026](https://www.squiggle-language.com/docs/Guides/DistributionCreation)
47. [Squiggle repository — Quantified Uncertainty Research Institute, 2026](https://github.com/quantified-uncertainty/squiggle)
48. [Causal (now part of Lucanet) — Causal, 2026](https://www.causal.app/)
49. [Causal Scenarios add-on listing — Google Workspace Marketplace, 2026](https://workspace.google.com/marketplace/app/causal_scenarios/383280853562)
50. [Define and use names in formulas — Microsoft, 2026](https://support.microsoft.com/en-us/office/define-and-use-names-in-formulas-4d0f13ac-53b7-422e-afd2-abd7ff379c64)
51. [Pint documentation — Grecco et al., 2026](https://pint.readthedocs.io/en/stable/)
52. [The Unified Code for Units of Measure, v2.2 — Schadow & McDonald, 2024](https://ucum.org/ucum)
53. [QUDT public repository (CC BY 4.0) — QUDT.org, 2026](https://github.com/qudt/qudt-public-repo)
54. [ucum-lhc: UCUM validation and conversion in JavaScript — NLM Lister Hill Center, 2026](https://github.com/lhncbc/ucum-lhc)
55. [math.js: Expression parsing and evaluation — de Jong et al., 2026](https://mathjs.org/docs/expressions/parsing.html)
56. [SymPy parsing (parse_expr, transformations) — SymPy Development Team, 2026](https://docs.sympy.org/latest/modules/parsing.html)
57. [math.js: Expression security — de Jong et al., 2026](https://mathjs.org/docs/expressions/security.html)
58. [NumExpr — PyData, 2026](https://github.com/pydata/numexpr)
59. [CVE-2023-39631 — NIST National Vulnerability Database, 2023](https://nvd.nist.gov/vuln/detail/CVE-2023-39631)
60. [Common Expression Language — Google, 2026](https://cel.dev/)
61. [CEL specification repository — cel-expr, 2026](https://github.com/google/cel-spec)
62. [cel-python — Cloud Custodian, 2026](https://github.com/cloud-custodian/cel-python)
63. [cel-js — Bachmann, 2026](https://github.com/marcbachmann/cel-js)
64. [JsonLogic — Wadhams, 2026](https://jsonlogic.com/)
65. [Decision Model and Notation (DMN) — Object Management Group, 2026](https://www.omg.org/dmn/)
66. [math.js: Units — de Jong et al., 2026](https://mathjs.org/docs/datatypes/units.html)
67. [Understanding JSON Schema: Numeric types — JSON Schema, 2026](https://json-schema.org/understanding-json-schema/reference/numeric)
68. [Evaluation of measurement data — Guide to the expression of uncertainty in measurement (JCGM 100:2008) — JCGM, 2008](https://www.bipm.org/en/doi/10.59161/JCGM100-2008E)
69. [PROV-O: The PROV Ontology — W3C, 2013](https://www.w3.org/TR/prov-o/)
70. [The Tradespace Exploration Paradigm — Ross & Hastings, 2005](https://doi.org/10.1002/j.2334-5837.2005.tb00783.x)
71. [Zod: JSON Schema — Zod, 2026](https://zod.dev/json-schema)
72. [Global Sensitivity Analysis: The Primer — Saltelli et al., 2007](https://doi.org/10.1002/9780470725184)
73. [SALib: Sensitivity Analysis Library in Python — SALib developers, 2026](https://salib.readthedocs.io/en/latest/)
74. [scipy.stats.lognorm — SciPy developers, 2026](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html)
