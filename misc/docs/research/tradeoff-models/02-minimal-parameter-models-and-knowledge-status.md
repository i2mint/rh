# Minimal-parameter phenomenological models and how to show knowledge status

Research note for a generic tool that renders interactive tradeoff models: variables linked by simple parametric relations, where moving one slider updates the rest, every parameter is interpretable, and the same model can later be fitted to data. First use: an experimental-design dashboard for a print → phone capture → upload → analyse measurement campaign. Companion in-house reading, not repeated here: prior elicitation from observable quantities, PreliZ and SHELF [1]; epistemic state, open-world defaults and provenance records [2].

## Summary of actionable findings

- **Build every relation from a small library of 1–3-parameter shape primitives, and parametrise each by quantities a person can picture**: half-life or 1/e length instead of a rate, midpoint x50 plus 10–90 % width instead of a slope, "value at a reference point" instead of a raw coefficient. Expected-value parametrisations are also the ones that make nonlinear fits behave close to linearly [3], and orthogonal parameters decouple during inference [4].
- **Few parameters are usually enough.** Multi-parameter models are "sloppy": their behaviour is governed by a few stiff parameter combinations, with sensitivities spread over many decades [5][6][7]. Fit to the observables, report predictions rather than parameter values, and check identifiability before fitting [8].
- **Positive, vaguely known quantities get a log-scale slider and a lognormal default entered as a 90 % range, `a to b`**, the Squiggle convention [9] (Guesstimate uses `[p5, p95]` [10]). A decay time known only to two orders of magnitude is then simply `1 to 100` in its unit.
- **Tag every quantity on two separate axes**: its *role* (law, design choice, device property, assumption, unknown) and its *evidence level* (measured, estimated, assumed, guessed, unknown). Ground the evidence axis in the NUSAP pedigree matrix [11] and the GRADE levels [12]; let the IPCC ladder (ambiguous → sign → order of magnitude → range → likelihood → distribution) decide which widget a quantity gets [13].
- **Encode the evidence level redundantly**: a text badge, solid lines for measured and dashed for assumed (dashing was the style users preferred [14]), and fuzziness or blur for spread. Do not rely on colour saturation or hue alone: both rated "unacceptable" for intuitiveness [15]. Pair any verbal likelihood with its number, because lay readers misread verbal terms [16].
- **Rank what to measure next with a sensitivity × pedigree "diagnostic diagram"** [17]: a parameter that is both influential and weakly evidenced is the next experiment.

## 1. Terminology, and why few parameters are enough

A **phenomenological model** represents only the observable properties of its target, without postulating hidden mechanisms. The definition is contested, since many such models still borrow theoretical laws [18]. A **constitutive relation** is a material- or device-specific relation between physical quantities (Hooke's law, Ohm's law) [19]; most of the primitives below play that role inside a larger model. A **reduced-order model** (ROM) is a cheaper model derived from a high-fidelity one, for example by projection onto a low-dimensional subspace [20]. A **surrogate** (metamodel) stands in for expensive evaluations or simulations, and is built, validated and refined from samples [21]. The tool described here sits closest to the phenomenological/constitutive end: hand-chosen forms with interpretable parameters, not black-box surrogates.

**Sloppy models.** Gutenkunst et al. examined a collection of published systems-biology models and found that all of them had sensitivity eigenvalues spread roughly evenly over many decades. Collective fits leave many individual parameters poorly constrained while still giving tight predictions, so modellers should "focus on predictions rather than on parameters" [5]. Transtrum, Sethna and colleagues generalised this result with an information geometry, in which the Fisher information is a metric on model space, and argue that the same mechanism explains why simple effective theories work [6][7]. Their **manifold boundary approximation method** removes one parameter at a time by taking a limit at the model manifold's boundary (for example a rate going to 0 or ∞), which yields simpler models that are still physically interpretable [22]. Practical consequence (our inference): a 2-parameter primitive whose parameters are the stiff combinations, such as an amplitude and a characteristic scale, often captures what a detailed mechanistic model would. Box's "since all models are wrong the scientist must be alert to what is importantly wrong" is the matching attitude [23].

**Identifiability.** A parameter can be *structurally* non-identifiable (functionally related to others) or *practically* non-identifiable (the data cannot pin it down). The profile likelihood detects both, and its results can guide experimental planning and model reduction [8]. Example (derived): if every capture happens at t ≪ τ, the decay is indistinguishable from a straight line, so τ cannot be identified and the design should add a late capture.

## 2. A catalogue of shape primitives

Notation: *A* is an amplitude (output units), *x* the input. "Log" means the slider and prior should live on a log scale; positive scale parameters are the standard case, because the scale-invariant (Jeffreys) prior for a scale parameter is uniform in its logarithm [24], and multiplicative effects produce lognormal variation [25]. Ranges marked *est.* are our engineering estimates for the first use, not sourced values.

| Primitive | Interpretable form | Parameters (units, scale) | Choose when / first use |
|---|---|---|---|
| Exponential decay / kernel | A·exp(−r/λ) = A·2^(−r/r½) | λ 1/e length or τ time (log); r½ = λ ln 2 (derived) | Memoryless loss or spread: fading over time, neighbour bleed with a sharp-edged kernel. Decay time known to two decades: `τ: 1 to 100` (est.) |
| Gaussian kernel | A·exp(−r²/2σ²) | σ (length, log), FWHM ≈ 2.355σ (derived) | Blur or point-spread with a smooth core. 2-D Gaussian approximations of optical PSFs are very accurate [26]; print optical dot gain is described by the paper's own PSF [27] |
| Power law | y_ref·(x/x_ref)^p | p (dimensionless, linear); y_ref value at a chosen x_ref | Scaling laws; inverse square is p = −2 for a point source [28] |
| Off-axis falloff | lamp over a page: (1+(r/h)²)^(−3/2), i.e. cos³θ; camera: cos⁴θ | h lamp height or f focal length (length, log) | Illumination across a sheet: inverse square plus Lambert cosine gives cos³ for a horizontal plane (derived from [28]); natural lens vignetting follows the cos⁴ law approximately [29][30] |
| Quadratic vignetting | 1 − v·(r/r_c)² | v = fractional drop at the corner r_c (linear, 0–0.5 est.) | Small-angle limit of both falloffs above (derived: cos³ → 1 − 1.5(r/h)², cos⁴ → 1 − 2(r/f)²); empirical vignetting is fitted as 1 + α₂r² + α₄r⁴ + α₆r⁶ [30], and v is its first term |
| Michaelis–Menten | A·x/(K + x) | A ceiling; K half-saturation point (log) | Saturating response with no threshold [31] |
| Linear-then-saturating | g·x/(1 + g·x/A) | g initial slope; A ceiling (log both) | Same curve as Michaelis–Menten with K = A/g (derived), but parametrised by the two things one sees: initial gain and ceiling. Best default for "linear until it saturates" sensor or ink response |
| Hill | A·xⁿ/(x50ⁿ + xⁿ) | x50 (log); n steepness (est. 0.5–4) | Sigmoidal saturation [32]; x90/x10 = 81^(1/n) (derived), so n = 1 spans 81×, n = 2 spans 9× |
| First-order approach | A·(1 − exp(−t/τ)) | τ (log); t63 = τ, t90 ≈ 2.3τ, t95 ≈ 3τ (derived) | Charging, warm-up, ink drying, exposure build-up |
| Logistic threshold | A/(1 + exp(−(x − x50)/s)) | x50 midpoint; w = 10–90 % width = 2s·ln 9 ≈ 4.39s (derived) | Pass/fail detectability, threshold effects; system dynamics offers a generalised logistic as an analytic replacement for table functions [33] |
| Averaging with floor | σ_N = √(σ²/N + σ_f²) | σ single-sample noise; σ_f floor; knee N* = (σ/σ_f)² (derived) | Averaging pixels or frames. EMVA 1288 separates temporal noise from fixed-pattern nonuniformity precisely by averaging frames [34]; systematic errors likewise do not average away (derived). Allan deviation falls as τ^(−1/2) under white noise, then goes flat at the flicker floor [35] |
| Linear with offset | y_ref + b·(x − x_ref) | value at a reference point, and slope | Default when the data cover a narrow range |
| Arrhenius / log-linear | k_ref·exp(−(E_a/R)(1/T − 1/T_ref)) | k_ref (log) at T_ref; E_a | Temperature-dependent rates [36]; centring on T_ref decorrelates the two parameters (derived) |

**Reparametrisations, and why they matter twice.** (1) *Sliders*: a person can say "the corner is about 20 % darker" or "half the signal is gone after a day", but not "v = 0.0031 mm⁻²". (2) *Fitting*: in a documented dose-response example, replacing a raw coefficient by the LD50 and by the expected response at a chosen dose cut the parameter skewness from 1.92 to about −0.06, and brought parameter-effects curvature below its critical value. Intrinsic curvature is unchanged by any reparametrisation [3]. Parameters that are orthogonal in the Fisher-information sense can be inferred almost independently [4], which is also what makes independent sliders feel independent. The "interior reference point" versions of the system-dynamics equations [33] are the same idea.

**Combining primitives.** Most first-use relations are products or sums of these factors. For example, measured value ≈ response(ink) × illumination(r) × (1 − bleed(gap/σ)) + noise(N). Each factor has 1–2 parameters, so the whole dashboard stays near 8–12 parameters (est.).

## 3. Practice from estimation, dimensional analysis and system dynamics

**Fermi estimation.** Weinstein and Adam make useful ballpark estimates by splitting hard problems into small, separately estimable factors [37]. Mahajan's toolkit adds dimensional analysis, easy cases, lumping, picture proofs, successive approximation and analogy [38]. "Easy cases" are the limits where a primitive degenerates (λ → 0 or ∞), the same limits MBAM uses to remove parameters [22]. **Buckingham's π theorem** [39] reduces a relation among n dimensional variables to one among dimensionless groups, typically n minus the number of independent dimensions. Example (derived): bleed between swatches depends on the gap g and the kernel width σ only through g/σ, so one slider replaces two.

**System dynamics.** Sterman's textbook gives a whole chapter to forming nonlinear relationships [40], conventionally as *table functions* (graphical lookup curves) that can take almost any shape. Ríos-Ocampo and Gary argue for replacing them with six analytic forms (generalised logistic, exponential, modified exponential, quadratic, logarithmic, power), each with an interior reference point, because analytic forms are easier to sensitivity-test and to communicate [33]. That is the same move as the catalogue above. Keep a table function as the escape hatch when no primitive fits.

**Guesstimate-style inputs.** Guesstimate (Gooen, 2015) is a spreadsheet in which any cell can hold a distribution, written `[p5, p95]` and propagated by in-browser Monte Carlo [10]. Squiggle, its successor language from the Quantified Uncertainty Research Institute, defines `5 to 10` as shorthand for a lognormal with 5th percentile 5 and 95th percentile 10, rejecting non-positive bounds [9]. Causal, now part of Lucanet [41], offered the same pattern for business spreadsheets: a range per input assumption, Monte Carlo ranges on the outputs [42]. Lognormal is the right default for positive quantities built from multiplicative effects [25]. Bret Victor's *reactive documents* (with his Tangle library) are the closest UI precedent for "drag one number, watch the others update" inside prose [43].

**Calibration.** Unaided assessors are overconfident, and their distributions are too narrow: 20–50 % of true values fell outside stated 1 %–99 % ranges, and training helps only to a limited extent [44]. Hubbard's calibration training uses the equivalent-bet test (prefer your range or a 90 % wheel?), tests each bound separately, and gives repeated feedback [45]; the claimed half-day effect is his own and was not independently verified here. Elicit observable quantities, and elicit extremes before the centre [1].

## 4. Representing and displaying knowledge status

**Standards to borrow from.**

- *NUSAP* (Funtowicz and Ravetz) qualifies every quantity by Numeral, Unit, Spread, Assessment and Pedigree [46]. Its pedigree matrix scores proxy representation, empirical basis, methodological rigour and validation from 0 to 4; empirical basis, for example, runs from "controlled experiments, large-sample direct measurement" (4) down to "crude speculation" (0) [11]. Van der Sluijs et al. combine pedigree with sensitivity in a *diagnostic diagram* to rank uncertainties, and extend pedigree to model assumptions [17].
- *IPCC AR5* separates **confidence** (five qualifiers, very low to very high, from evidence × agreement, not to be read probabilistically) from **likelihood** (calibrated terms: very likely = 90–100 %, likely = 66–100 %, and so on). It asks authors to choose a presentation by knowledge level: A, ambiguous → no confidence, explain; B, sign known; C, order of magnitude; D, range; E, likelihood; F, full distribution. It also requires a traceable account and an evaluation of structural uncertainty [13].
- *GRADE* rates quality of evidence from high to very low, displayed as one to four symbols [12][47].
- *W3C PROV* gives the provenance vocabulary: Entity, Activity, Agent; wasGeneratedBy, used, wasDerivedFrom, wasAttributedTo [48]. The in-house design adds an open-world default (absence means UNKNOWN, never "no"), plus separate confidence dimensions per fact [2].
- Van der Bles et al. distinguish *direct* uncertainty (about the number itself, nine expressions from a full distribution down to denial) from *indirect* uncertainty (quality of the evidence behind it) [47]. This is the same split as spread versus pedigree.

**Proposed taxonomy (our synthesis of the above).**

| Axis | Values | Maps to |
|---|---|---|
| Role | law/fact · **design choice** (a decision variable we set: swatch size, gap, number of shots) · device/material property (fixed but unmeasured: paper PSF, sensor floor) · environment (lighting, temperature) · modelling assumption (the choice of primitive itself) · unknown | IPCC "structural uncertainty" [13]; NUSAP assumptions [17] |
| Evidence | measured (this setup) · estimated (literature, analogous data) · assumed (stated for convenience) · guessed (elicited) · unknown (open-world default) | NUSAP empirical basis 4→0 [11]; GRADE high → very low [12]; open-world default [2] |
| Spread | number · range `a to b` · distribution | IPCC C/D/F [13]; van der Bles direct-uncertainty scale [47] |
| Provenance | source, fit or elicitation activity, who, when | PROV [48] |

Design choices are not uncertain, so render them as plain controls. Unknowns are distributions, so render them as range sliders. Mixing the two semantics on one widget is the most likely source of confusion (our inference). Let the IPCC ladder choose the widget: B → sign toggle, C → log slider snapping to decades, D → `a to b` range slider, F → distribution editor.

**Visual encodings, with the evidence on how people read them.**

- MacEachren et al. tested visual variables for ordinal uncertainty on point symbols. Fuzziness, location and value (lighter = less certain) were "good"; arrangement, size and transparency were "acceptable"; saturation, hue, orientation and shape were "unacceptable", which is notable because saturation is often recommended. Only one direction of each mapping read as intuitive [15].
- Boukhelifa et al. compared blur, dashing, grayscale and sketchiness on lines. Sketchiness was as intuitive as blur, but participants subjectively *preferred dashing* [14]. So: solid = measured or fitted, dashed = assumed or estimated, dotted or sketchy = guessed (our mapping). Hatching was not tested in these studies; we found no direct evidence for it, and treat it as a convention for "extrapolated beyond data". It is closest to MacEachren's "arrangement" variable.
- Verbal probability terms are read inconsistently: IPCC "very likely" was read as about 65–75 % rather than ≥ 90 %, and adding numbers narrows the gap [16][47]. About half of respondents took the top of a range as the correct value, while a best estimate or density shape helped [47]. Show a range with its central value, and a word with its number.
- For output distributions, quantile dotplots reduced the variance of lay probability estimates about 1.15-fold compared with density plots [49].
- Communicating uncertainty does not necessarily reduce trust, though effects vary by person and format [47].

Concrete badge: `M` / `E` / `A` / `G` / `?` plus a 0–4 pedigree pip, with a click-through to the PROV record. Never let colour carry the status alone.

## 5. Important things not asked about

- **Prior predictive checks**: simulate the *observable* (the captured image values) from the current slider ranges and show it. Prior predictive simulation is one of the visual checks of the Bayesian workflow [50], and it turns elicitation into judging data, which non-experts do better [1].
- **Sensitivity before precision**: the diagnostic diagram [17] and Hubbard's value-of-information argument [45] both say to measure the parameters that are influential *and* weakly evidenced first; Hubbard also reports a "measurement inversion", in which the variables that most need measuring are the ones measured least [45]. A tornado-style sensitivity display next to the pedigree badges does this in the UI.
- **The form is an assumption too**: tag the chosen primitive (cos³ versus quadratic, exponential versus Gaussian kernel) as a modelling assumption, and where cheap, let the user switch forms and compare predictions. IPCC asks for structural uncertainty to be estimated explicitly [13], and polynomial vignetting models extrapolate badly outside the fitted region [30].
- **Predict, don't over-interpret parameters**: with sloppy models, report prediction bands; parameter error bars can be huge even when predictions are tight [5].
- **Known physics for the first use**: the "neighbour bleed" of printed swatches has a literature of its own. Optical dot gain (the Yule–Nielsen effect) comes from light scattering sideways inside the paper and is described by the paper's point-spread function [51][27]. Camera noise has a standard model separating temporal noise from fixed-pattern nonuniformity [34].

## REFERENCES

1. [Bayesian prior elicitation for Beta distributions: a practical survey — Whalen, in-house (thorwhalen/ba, misc/docs/resources/), 2026](https://github.com/thorwhalen/ba/blob/main/misc/docs/resources/Bayesian%20prior%20elicitation%20for%20Beta%20distributions-%20a%20practical%20survey.md)
2. [Building a candidate-knowledge system: elicitation, active questioning, epistemic state, and a personal knowledge store — Whalen, in-house (thorwhalen/hired, misc/docs/research/elicitation-and-knowledge-store.md), 2026](https://github.com/thorwhalen/hired/blob/main/misc/docs/research/elicitation-and-knowledge-store.md)
3. [Affecting Curvature through Parameterization (NLIN example, following Ratkowsky's Handbook of Nonlinear Regression Models, 1990) — SAS Institute, SAS/STAT User's Guide](https://support.sas.com/documentation/cdl/en/statug/63962/HTML/default/statug_nlin_sect037.htm)
4. [Parameter Orthogonality and Approximate Conditional Inference — Cox & Reid, 1987](https://doi.org/10.1111/j.2517-6161.1987.tb01422.x)
5. [Universally Sloppy Parameter Sensitivities in Systems Biology Models — Gutenkunst et al., 2007](https://pmc.ncbi.nlm.nih.gov/articles/PMC2000971)
6. [Sloppiness and Emergent Theories in Physics, Biology, and Beyond — Transtrum, Machta, Brown, Daniels, Myers & Sethna, 2015](https://arxiv.org/abs/1501.07668)
7. [Parameter Space Compression Underlies Emergent Theories and Predictive Models — Machta, Chachra, Transtrum & Sethna, 2013](https://arxiv.org/abs/1303.6738)
8. [Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood — Raue et al., 2009](https://pubmed.ncbi.nlm.nih.gov/19505944)
9. [Squiggle documentation: Dist (the `to` shorthand) — Quantified Uncertainty Research Institute, accessed 2026](https://www.squiggle-language.com/docs/Api/Dist)
10. [Guesstimate: An app for making decisions with confidence (intervals) — Gooen, 2015](https://forum.nunosempere.com/posts/Bt4nkCGHKBkDk97mn/guesstimate-an-app-for-making-decisions-with-confidence)
11. [NUSAP (pedigree matrix) — PBL Netherlands Environmental Assessment Agency, Guidance on Uncertainty Assessment and Communication](https://leidraad.pbl.nl/tools/32)
12. [GRADE: an emerging consensus on rating quality of evidence and strength of recommendations — Guyatt et al., 2008](https://www.bmj.com/content/336/7650/924)
13. [Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties — Mastrandrea et al., 2010](https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf)
14. [Evaluating Sketchiness as a Visual Variable for the Depiction of Qualitative Uncertainty — Boukhelifa, Bezerianos, Isenberg & Fekete, 2012](https://www.aviz.fr/Research/UncertaintySketchy)
15. [Visual Semiotics & Uncertainty Visualization: An Empirical Study — MacEachren et al., 2012](https://geography.wisc.edu/cartography/projects/publications/MacEachrenEtAl_2012_TVCG.pdf)
16. [Improving Communication of Uncertainty in the Reports of the Intergovernmental Panel on Climate Change — Budescu, Broomell & Por, 2009](https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.2009.02284.x/)
17. [Combining Quantitative and Qualitative Measures of Uncertainty in Model-Based Environmental Assessment: The NUSAP System — van der Sluijs et al., 2005](https://dspace.library.uu.nl/handle/1874/386039)
18. [Models in Science — Frigg & Hartmann, Stanford Encyclopedia of Philosophy, 2006, rev. 2025](https://plato.stanford.edu/entries/models-science/)
19. [Constitutive equation — Wikipedia, accessed 2026](https://en.wikipedia.org/wiki/Constitutive_equation)
20. [A Survey of Projection-Based Model Reduction Methods for Parametric Dynamical Systems — Benner, Gugercin & Willcox, 2015](https://dspace.mit.edu/handle/1721.1/100939)
21. [Engineering Design via Surrogate Modelling: A Practical Guide — Forrester, Sóbester & Keane, 2008](https://www.wiley-vch.de/de/fachgebiete/ingenieurwesen/engineering-design-via-surrogate-modelling-978-0-470-06068-1)
22. [Model Reduction by Manifold Boundaries — Transtrum & Qiu, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4425275)
23. [Science and Statistics — Box, 1976](https://doi.org/10.1080/01621459.1976.10480949)
24. [Jeffreys prior — Wikipedia, accessed 2026](https://en.wikipedia.org/wiki/Jeffreys_prior)
25. [Log-normal Distributions across the Sciences: Keys and Clues — Limpert, Stahel & Abbt, 2001](https://www.statpower.net/Content/MLRM/Readings/LimpertStahelAbt2007.pdf)
26. [Gaussian approximations of fluorescence microscope point-spread function models — Zhang, Zerubia & Olivo-Marin, 2007](https://doi.org/10.1364/AO.46.001819)
27. [Optical Dot Gain in a Halftone Print — Rogers, 1997](https://library.imaging.org/jist/articles/41/6/art00015)
28. [Point-by-Point Method — Lighting Design and Simulation Knowledgebase (Schorsch), accessed 2026](http://www.schorsch.com/en/kbase/glossary/point-by-point.html)
29. [Vignetting — Wikipedia, accessed 2026](https://en.wikipedia.org/wiki/Vignetting)
30. [Vignette and Exposure Calibration and Compensation — Goldman & Chen, 2005](https://grail.cs.washington.edu/projects/vignette/)
31. [The original Michaelis constant: translation of the 1913 Michaelis–Menten paper — Johnson & Goody, 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3381512)
32. [The Hill equation and the origin of quantitative pharmacology — Gesztelyi et al., 2012](https://doi.org/10.1007/s00407-012-0098-5)
33. [Using analytical equations to represent nonlinear relationships — Ríos-Ocampo & Gary, 2022](https://strathprints.strath.ac.uk/89750)
34. [EMVA 1288 (summary of the sensor-characterisation standard) — Imatest, accessed 2026](https://imatest.com/imaging/emva-1288)
35. [Handbook of Frequency Stability Analysis (NIST SP 1065) — Riley, 2008](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication1065.pdf)
36. [Arrhenius equation — IUPAC Compendium of Chemical Terminology (Gold Book)](https://goldbook.iupac.org/terms/view/A00446)
37. [Guesstimation: Solving the World's Problems on the Back of a Cocktail Napkin — Weinstein & Adam, 2008](https://press.princeton.edu/books/paperback/9780691129495/guesstimation)
38. [Street-Fighting Mathematics (course and open textbook) — Mahajan, 2008/2010](https://ocw.mit.edu/courses/18-098-street-fighting-mathematics-january-iap-2008/)
39. [On Physically Similar Systems; Illustrations of the Use of Dimensional Equations — Buckingham, 1914](https://doi.org/10.1103/PhysRev.4.345)
40. [Business Dynamics: Systems Thinking and Modeling for a Complex World — Sterman, 2000](https://www.mheducation.com.sg/business-dynamics-systems-thinking-and-modeling-for-a-complex-world-int-l-ed-9780071179898-asia)
41. [Causal (now part of Lucanet) — Causal, accessed 2026](https://www.causal.app/)
42. [Causal Scenarios (Monte Carlo add-on for Google Sheets) — Causal, Google Workspace Marketplace, accessed 2026](https://workspace.google.com/marketplace/app/causal_scenarios/383280853562)
43. [Explorable Explanations — Victor, 2011](https://worrydream.com/ExplorableExplanations/)
44. [Calibration of probabilities: The state of the art to 1980 — Lichtenstein, Fischhoff & Phillips, 1982](https://www.cambridge.org/core/books/abs/judgment-under-uncertainty/calibration-of-probabilities-the-state-of-the-art-to-1980/9F0C9EC2997AEEB6DDDB304C2F935A16)
45. [How to Measure Anything: Finding the Value of Intangibles in Business, 3rd ed. — Hubbard, 2014](https://www.oreilly.com/library/view/-/9781118836446/)
46. [Uncertainty and Quality in Science for Policy — Funtowicz & Ravetz, 1990 (Wikipedia entry)](https://en.wikipedia.org/wiki/Uncertainty_and_Quality_in_Science_for_Policy)
47. [Communicating uncertainty about facts, numbers and science — van der Bles et al., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6549952)
48. [PROV-DM: The PROV Data Model — Moreau & Missier (eds.), W3C, 2013](https://www.w3.org/TR/prov-dm/)
49. [When(ish) is My Bus? User-centered Visualizations of Uncertainty in Everyday, Mobile Predictive Systems — Kay, Kola, Hullman & Munson, 2016](https://idl.uw.edu/papers/when-ish-is-my-bus)
50. [Visualization in Bayesian workflow — Gabry, Simpson, Vehtari, Betancourt & Gelman, 2019](https://arxiv.org/abs/1709.01449)
51. [Dot gain — Wikipedia, accessed 2026](https://en.wikipedia.org/wiki/Dot_gain)
