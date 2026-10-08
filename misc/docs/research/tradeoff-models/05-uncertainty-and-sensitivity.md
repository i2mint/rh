# Uncertainty propagation, sensitivity analysis and uncertainty display for interactive tradeoff models

Scope: a generic tool that renders a mesh of variables linked by simple 1–3-parameter relations, with sliders, where some inputs are known facts and others are assumptions or unknowns given as ranges. First use: an experimental-design dashboard for a camera-based measurement campaign, where the question is which unknown's range moves a target output (for example signal-to-noise per measured colour) the most. Constraint: each slider update must recompute in well under ~100 ms in the browser.

## Summary of actionable findings

- **Propagate with one fixed Monte Carlo sample, drawn once and reused on every slider move** (common random numbers), stratified by Latin hypercube or a scrambled Sobol sequence. Common random numbers make the difference between two settings reflect the settings rather than sampling noise [1]; LHS and Sobol points cover the input box more evenly than plain random draws [2][3]. Guesstimate instead draws a fresh 5000-sample set after every edit [4], which (by inference, not measured) makes outputs jitter.
- **Cost is not the bottleneck.** A 20-node formula mesh over 5000 samples evaluated in under 1 ms in a quick Node benchmark (section 2; measured on one laptop, indicative only), so live propagation and live first-order sensitivity are affordable at N = 2000–10 000.
- **Answer "which unknown matters most" with global, not one-at-a-time, measures.** Estimate first-order indices live from the same sample ("given data" estimators [5]) and show a scatterplot of the output against each input; offer total-order Sobol indices (N(k+2) runs [6]) on demand. Keep a tornado diagram only as a familiar entry point, because one-at-a-time designs leave most of the input space unexplored [7].
- **For the key output show a quantile dotplot** (about 20–50 dots), which led lay users to near-optimal decisions [8]; add hypothetical outcome plots (animated draws) for comparisons between two or three outputs [9]. Avoid bare error bars, which even researchers misread [10][11].
- **Keep intervals and distributions distinct.** When an unknown has a range but no defensible distribution, a uniform prior is an assumption, not a fact; probability bounds analysis (p-boxes) carries "range only" inputs honestly alongside distributional ones [12].

## 1. Terminology

- **Aleatory vs epistemic uncertainty**: natural variability vs lack of knowledge; the split is a modelling choice that decides which uncertainties more data could reduce [13]. Ferson and Ginzburg call these *variability* and *incertitude* and argue they need different propagation methods [14]. In this tool, sensor noise is aleatory; an unknown quantum efficiency or illumination level given as a range is epistemic.
- **Metrology (GUM)**: *standard uncertainty* (a standard deviation), *combined standard uncertainty*, *sensitivity coefficients* (partial derivatives), *coverage interval* and *coverage factor* [15]; the Monte Carlo supplement adds *propagation of distributions* [16].
- **Uncertainty analysis** asks how uncertain an output is; **sensitivity analysis** asks which inputs that uncertainty comes from [7]. *Factor prioritisation* (which input, if fixed, would reduce output variance most) and *factor fixing* (which inputs can be frozen) are the two standard settings, answered by first-order and total-order indices respectively [17].
- **Deep uncertainty**: parties do not know or cannot agree on the model, the probability distributions of its inputs, or how to value outcomes [18][19]. See section 6.

## 2. Propagation methods

| Method | Gives | Cost per update | Use when |
|---|---|---|---|
| Interval arithmetic [20] | Guaranteed bounds | ~2× a point evaluation | Inputs known only as ranges; need a hard worst case |
| First-order Taylor / delta method, GUM law of propagation [15] | Mean and standard uncertainty | One gradient (k+1 evaluations by finite differences, or automatic differentiation) | Near-linear model, small relative uncertainties, roughly Gaussian output |
| Monte Carlo, GUM S1 [16] | Full output distribution | N evaluations | Nonlinear model, skewed or bounded output, any input distribution |
| LHS / quasi-Monte Carlo (Sobol) [2][3] | Same as Monte Carlo, lower error for the same N | N evaluations | Always preferable to plain random draws for a fixed sample |
| Probability bounds analysis / p-boxes [12] | Upper and lower CDFs | Several Monte Carlo or interval passes | Mix of ranges (no distribution) and distributions |

**Interval arithmetic** propagates [lo, hi] bounds through each operation [20]. Its known weakness is the *dependency problem*: each occurrence of a variable is treated as independent, so x − x on [0, 1] evaluates to [−1, 1] instead of 0, and algebraically equal forms give different widths [20]. For a small mesh, evaluating the formulas at the corners of the input box (2^k points) gives exact bounds when the output is monotone in each input; this is our reasoning, not a sourced result, and fails for non-monotone relations.

**Delta method (GUM)**: the law of propagation of uncertainty combines sensitivity coefficients with input standard uncertainties [15]. GUM Supplement 1 states the conditions under which this is valid for nonlinear models (continuous differentiability, independent and Gaussian inputs in any significant higher-order terms, negligible omitted terms) and recommends Monte Carlo otherwise [16]. Ratios such as signal over noise with wide input ranges are exactly the case where it breaks, so treat it as a quick readout, not the default.

**Monte Carlo**: GUM S1 notes that M = 10^6 trials often gives a 95 % coverage interval correct to one or two significant digits [16] — that is a precision target for certification, not for a dashboard. Interactive tools use far fewer: Guesstimate uses 5000 samples per calculation [4]; Squiggle's default sample count is 1000 [21]. For dashboard medians and 5–95 % bands, N = 2000–10 000 is a reasonable range (estimate; tails beyond the 1st/99th percentile need more).

**Common random numbers**: draw the input sample once, as uniforms u ∈ [0,1]^k, and on each slider move only re-map u through the new input ranges (e.g. lo + u·(hi − lo), or an inverse CDF). The output then moves smoothly and the change between two settings is not swamped by resampling noise; this is the variance-reduction argument for common random numbers [1]. Use a seeded PRNG so the sample is reproducible (stdlib-js provides seedable generators [22]).

**Stratified and quasi-random sampling**: Latin hypercube sampling stratifies each input's marginal [2]; quasi-Monte Carlo sequences such as Sobol's have error that decays close to O(1/N) (up to log factors) against O(1/√N) for random sampling, for smooth enough integrands [3]. Joe and Kuo publish the standard direction numbers for generating Sobol points [23]. Either can be precomputed once as the fixed u-matrix.

**Probability bounds analysis**: a p-box is a pair of CDFs that bound the unknown true CDF; an interval is the widest p-box and a precise distribution is a zero-width one, so both kinds of inputs live in one calculus [12][24]. This answers "the unknown is somewhere in [a, b], I will not claim it is uniform". It is more expensive and harder to explain; a lighter alternative for a dashboard is a *double loop*: sweep the range-only inputs over a small grid (outer loop) and run Monte Carlo over the distributional inputs (inner loop), then show the envelope (our suggestion, following the variability/incertitude split of [14]).

**Browser cost (measured, indicative)**: a 20-node chain of 1–3-parameter formulas (products, ratios, square roots, logs) over Float64Arrays, plus a sort for quantiles, took a median of 0.16 ms at N = 1000, 0.79 ms at N = 5000, 3.1 ms at N = 20 000 and 17 ms at N = 100 000 (Node 23 on one Apple M1 Max laptop; a phone may be several times slower). A Saltelli design for k = 6 inputs and base N = 1024 (8192 rows) took 1.2 ms. Implementation note: store samples as one typed array per variable and evaluate column-wise; keep it off the main thread (Web Worker) only if N or the mesh grows by an order of magnitude.

### Libraries

| Library | Language | What it offers |
|---|---|---|
| SALib [25] | Python | Sobol, Morris, eFAST, RBD-FAST, delta (given-data), PAWN, DGSM, HDMR; samplers |
| uncertainties [26] | Python | Linear (first-order) error propagation with automatic derivatives and correlation tracking |
| mcerp / soerp [27] | Python | Monte Carlo with Latin hypercube and correlation enforcement / second-order moments propagation |
| chaospy [28] | Python | Polynomial chaos expansions, quasi-random samplers, distributions |
| OpenTURNS [29] | Python/C++ | Full uncertainty-quantification stack: distributions, copulas, LHS/QMC, Sobol indices, metamodels |
| pba [24] | Python | Probability bounds analysis: intervals, p-boxes |
| Squiggle [21] | JS/TS | Language for sample-based estimates; default 1000 samples |
| simple-statistics [30] | JS | Quantiles, descriptive statistics, regression |
| jStat [31] | JS | Distribution PDFs, CDFs, inverse CDFs |
| stdlib-js [22] | JS/TS | Seedable PRNGs, distributions, statistics |

For the browser, the minimum stack is a seeded PRNG plus inverse CDFs (stdlib-js or jStat) and quantiles (simple-statistics). Python libraries are for offline checks, e.g. validating browser Sobol indices against SALib.

## 3. Sensitivity analysis

**One-at-a-time (OAT), tornado and spider plots.** A tornado diagram swings each input between its low and high value with the others at baseline and sorts the bars; a spider plot draws output against each input's percentage change. Eschenbach calls them complementary: the tornado summarises many inputs at once, the spider gives more detail on a few, including break-even points [32]. Their shared failure: they measure effects around one baseline point, so they miss interactions and nonlinearity elsewhere in the box, and the result depends on the baseline chosen. Saltelli et al. found that 42 % of highly cited papers they reviewed did not explore the input space properly, typically by moving along one-dimensional corridors [7]; Campolongo et al. note that local OAT remained the common practice despite better screening methods being available [33].

**Elementary effects (Morris screening).** Morris samples r random OAT trajectories across the whole input box, at a cost of r(k+1) runs, and summarises each input's elementary effects by their mean and spread [34]. Campolongo et al. introduced μ*, the mean of the *absolute* elementary effects, so that effects of opposite sign do not cancel, plus a space-filling choice of trajectories [33]. High μ* means influential; high σ means nonlinear or interacting. This is a good "screening" view when k grows past ten or so.

**Variance-based (Sobol) indices.** The first-order index S_i is the share of output variance explained by input i alone; the total index S_Ti includes all its interactions [35]. S_i answers *which unknown, if pinned down, would reduce output variance most* — exactly the experimental-design question — and S_Ti answers *which unknowns can safely be left as ranges* [17]. The Saltelli/Jansen design estimates both at N(k+2) runs [6]. Standard Sobol indices assume independent inputs [17].

**Given-data estimators.** First-order indices (and moment-independent measures) can be estimated from an existing Monte Carlo sample without a special design, at a cost independent of the number of inputs [5]; SALib implements this as its delta method [25]. For the dashboard this means the same fixed sample that draws the uncertainty band can also rank the unknowns on every slider move.

**Scatterplots.** Plotting the output against each input over the Monte Carlo sample is the recommended first look in the Primer [17]: a visible trend means a strong first-order effect, a fan shape means interaction. Small-multiple scatterplots are cheap to render from the existing sample and are the most honest single view for non-experts.

**What runs live vs precomputed** (estimates from the benchmark above): live on every slider move — Monte Carlo band, quantile dotplot, scatterplots, given-data first-order indices; live on demand (a button, or on slider release) — Saltelli total-order indices with N around 1000–4000; offline or precomputed — bootstrap confidence intervals on indices, p-box envelopes over many range combinations, and anything with k beyond a few dozen.

## 4. Visualising uncertainty for non-experts

**Why it is often left out.** Hullman surveyed 90 visualisation authors and interviewed 13 designers: they say uncertainty matters yet routinely omit it; the paper's rhetorical model argues that showing uncertainty reduces the degrees of freedom viewers have in the inferences they draw [36]. Padilla, Kay and Hullman's review identifies frequency framing as a recurring winner and describes *attribute substitution*: viewers swap hard uncertainty information for an easier attribute [37]. Joslyn and Savelli name the *deterministic construal error*: lay users read an uncertainty display as a deterministic quantity, a failure that studies can hide by telling participants up front what the display means [38].

**Hypothetical outcome plots (HOPs).** Animated frames, each one draw from the distribution. Users made much more accurate judgments about two or three quantities with HOPs than with error bars or violin plots [9], and untrained observers judged trends in weak-evidence data better with HOPs than with static aggregate displays [39]. Costs: they need time to show a representative set of draws and impose counting load [37]. A fixed sample gives the HOP frames for free.

**Quantile dotplots.** Proposed for mobile transit predictions, they draw a distribution as a small number of equally likely dots, so a probability is read by counting [40]. In an incentivised bus-catching experiment, a 50-dot quantile dotplot brought decisions to about 97 % of optimal payoff, 5 points better than no uncertainty display, with CDF plots nearly as good and text intervals worse [8].

**Error bars.** Among 473 published researchers, many misjudged how error bars relate to statistical significance and did not distinguish standard-error bars from confidence intervals [10]. Bar-plus-error-bar charts encourage an in-or-out reading; gradient plots (opacity encodes density) and violin plots did better on inferential tasks [11].

**Fan charts, cones and ensembles.** Spiegelhalter et al. review fan charts, spaghetti plots and cones and note that experimental evidence on how they are understood is limited [41]. For hurricane forecasts, the visual properties of the display changed non-experts' decisions [42]; salient features of a summary cone led people to read its width as storm size, while an ensemble of tracks prompted readings closer to the underlying distribution [43]. Lesson for any band that widens: label it as a range of possible values, not as the size of something, or show draws instead of an outline.

**Frequency framing and icon arrays.** Probabilities stated as natural frequencies ("3 in 20") improve Bayesian reasoning without instruction [44]; icon arrays were tested as a remedy for low numeracy in medical risk communication [45].

## 5. Recommendations for a slider-driven tradeoff dashboard

1. **Input controls encode their epistemic status.** Known facts get a single-thumb slider; assumptions and unknowns get a two-thumb range slider (optionally with a third "best guess" thumb). Visual distinction follows the aleatory/epistemic and variability/incertitude split [13][14].
2. **One fixed sample, re-mapped on every move** (section 2). N = 5000 by default; LHS or scrambled Sobol for the u-matrix [2][23]; outputs then move without jitter [1].
3. **Every output node shows a band, not just a point**: median plus a 50 % and 90 % interval as a gradient strip [11]; the band updates live while a thumb is dragged.
4. **The target output gets a quantile dotplot** with 20–50 dots and a threshold line (e.g. the minimum acceptable SNR), so "how many in 50 fall short" is read by counting [8][44].
5. **A "which unknown matters" panel**: bars of first-order indices from the live sample [5], with a toggle to compute total-order indices [6]; clicking a bar opens the output-vs-input scatterplot [17]. Show a tornado only as a labelled "around the current point" view [32][7].
6. **Per-colour comparison** (e.g. SNR for each measured colour channel): small multiples sharing one axis, with an optional HOP mode that animates the same draws across all panels, so viewers see which channel falls short together [9][39].
7. **Say what the band means in words**, in frequency terms ("in 45 of 50 simulated campaigns SNR stays above 10"), to counter the deterministic construal error [38][44].
8. **"Range only" honesty switch**: when an unknown has no defensible distribution, show the min-max envelope across its range (double loop or p-box) alongside the Monte Carlo band [12].

## 6. Not asked about, but relevant

- **Deep uncertainty and decision methods.** When the distributions themselves are contested, the decision-making-under-deep-uncertainty literature recommends looking for strategies that perform acceptably across many plausible futures rather than optimising an expected value: Robust Decision Making, dynamic adaptive planning, info-gap decision theory and engineering options analysis [19][18]. Info-gap asks how far the unknowns can deviate from a best guess before a requirement fails — a natural "robustness margin" readout for an experimental design [46].
- **Scenario discovery.** Run the model over the whole input box, flag the runs that fail a requirement, and use a box-finding algorithm (PRIM) to describe the input region where failure concentrates [47]. For the campaign this turns "SNR is too low in 12 % of runs" into "SNR is too low when exposure is below X and illumination below Y". The EMA Workbench implements exploratory modelling, scenario discovery and robust decision making in Python [48].
- **Value of information.** A first-order Sobol index is the expected share of output variance removed by pinning that one unknown [17]; that is the quantitative case for which calibration measurement to run first.

## REFERENCES

1. [Some Guidelines and Guarantees for Common Random Numbers — Glasserman P, Yao DD, 1992](https://doi.org/10.1287/mnsc.38.6.884)
2. [A Comparison of Three Methods for Selecting Values of Input Variables in the Analysis of Output from a Computer Code — McKay MD, Beckman RJ, Conover WJ, 1979](https://doi.org/10.1080/00401706.1979.10489755)
3. [Monte Carlo and quasi-Monte Carlo methods — Caflisch RE, 1998](https://doi.org/10.1017/S0962492900002804)
4. [Guesstimate app (README: 5000 samples per input after each change) — Guesstimate project, 2015](https://github.com/getguesstimate/guesstimate-app)
5. [Global sensitivity measures from given data — Plischke E, Borgonovo E, Smith CL, 2013](https://doi.org/10.1016/j.ejor.2012.11.047)
6. [Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index — Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S, 2010](https://doi.org/10.1016/j.cpc.2009.09.018)
7. [Why so many published sensitivity analyses are false: A systematic review of sensitivity analysis practices — Saltelli A, Aleksankina K, Becker W, et al., 2019](https://doi.org/10.1016/j.envsoft.2019.01.012) (open preprint: [arXiv:1711.11359](https://arxiv.org/abs/1711.11359))
8. [Uncertainty Displays Using Quantile Dotplots or CDFs Improve Transit Decision-Making — Fernandes M, Walls L, Munson S, Hullman J, Kay M, 2018](https://doi.org/10.1145/3173574.3173718)
9. [Hypothetical Outcome Plots Outperform Error Bars and Violin Plots for Inferences about Reliability of Variable Ordering — Hullman J, Resnick P, Adar E, 2015](https://doi.org/10.1371/journal.pone.0142444)
10. [Researchers misunderstand confidence intervals and standard error bars — Belia S, Fidler F, Williams J, Cumming G, 2005](https://doi.org/10.1037/1082-989X.10.4.389)
11. [Error Bars Considered Harmful: Exploring Alternate Encodings for Mean and Error — Correll M, Gleicher M, 2014](https://doi.org/10.1109/TVCG.2014.2346298)
12. [Constructing Probability Boxes and Dempster-Shafer Structures (SAND2002-4015) — Ferson S, Kreinovich V, Ginzburg L, Myers DS, Sentz K, 2003](https://doi.org/10.2172/809606)
13. [Aleatory or epistemic? Does it matter? — Der Kiureghian A, Ditlevsen O, 2009](https://doi.org/10.1016/j.strusafe.2008.06.020)
14. [Different methods are needed to propagate ignorance and variability — Ferson S, Ginzburg LR, 1996](https://doi.org/10.1016/S0951-8320%2896%2900071-3)
15. [Evaluation of measurement data — Guide to the expression of uncertainty in measurement (JCGM 100:2008) — Joint Committee for Guides in Metrology, 2008](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)
16. [Evaluation of measurement data — Supplement 1 to the GUM: Propagation of distributions using a Monte Carlo method (JCGM 101:2008), clauses 5.8 and 7.2 — Joint Committee for Guides in Metrology, 2008](https://www.bipm.org/documents/20126/2071204/JCGM_101_2008_E.pdf)
17. [Global Sensitivity Analysis: The Primer — Saltelli A, Ratto M, Andres T, Campolongo F, Cariboni J, Gatelli D, Saisana M, Tarantola S, 2008](https://doi.org/10.1002/9780470725184)
18. [Shaping the Next One Hundred Years: New Methods for Quantitative, Long-Term Policy Analysis — Lempert RJ, Popper SW, Bankes SC, 2003](https://www.rand.org/pubs/monograph_reports/MR1626.html)
19. [Decision Making under Deep Uncertainty: From Theory to Practice (open access) — Marchau VAWJ, Walker WE, Bloemen PJTM, Popper SW (eds), 2019](https://doi.org/10.1007/978-3-030-05252-2)
20. [Introduction to Interval Analysis — Moore RE, Kearfott RB, Cloud MJ, 2009](https://doi.org/10.1137/1.9780898717716)
21. [Squiggle: defaultSampleCount in packages/squiggle-lang/src/magicNumbers.ts — Quantified Uncertainty Research Institute, accessed 2026](https://github.com/quantified-uncertainty/squiggle/blob/main/packages/squiggle-lang/src/magicNumbers.ts) (site: [squiggle-language.com](https://www.squiggle-language.com/))
22. [stdlib: a standard library for JavaScript and Node.js — stdlib project, accessed 2026](https://stdlib.io/)
23. [Sobol sequence generator and direction numbers — Joe S, Kuo FY, 2008](https://web.maths.unsw.edu.au/~fkuo/sobol/)
24. [Probability bounds analysis for Python — Gray N, Ferson S, De Angelis M, Gray A, de Oliveira FB, 2022](https://doi.org/10.1016/j.simpa.2022.100246) (docs: [pba-for-python](https://pba-for-python.readthedocs.io/))
25. [SALib: An open-source Python library for Sensitivity Analysis — Herman J, Usher W, 2017](https://doi.org/10.21105/joss.00097) (docs: [salib.readthedocs.io](https://salib.readthedocs.io/))
26. [uncertainties: a Python package for calculations with uncertainties — Lebigot EO, accessed 2026](https://uncertainties.readthedocs.io/)
27. [mcerp: Monte Carlo error propagation — Lee AD, accessed 2026](https://github.com/eggzec/mcerp) (companion: [soerp](https://github.com/eggzec/soerp))
28. [Chaospy: An open source tool for designing methods of uncertainty quantification — Feinberg J, Langtangen HP, 2015](https://doi.org/10.1016/j.jocs.2015.08.008)
29. [OpenTURNS: open source initiative for the treatment of uncertainties — OpenTURNS consortium, accessed 2026](https://openturns.github.io/www/)
30. [simple-statistics — MacWright T, accessed 2026](https://simple-statistics.github.io/)
31. [jStat: JavaScript statistical library — jStat project, accessed 2026](https://jstat.github.io/)
32. [Spiderplots versus Tornado Diagrams for Sensitivity Analysis — Eschenbach TG, 1992](https://doi.org/10.1287/inte.22.6.40)
33. [An effective screening design for sensitivity analysis of large models — Campolongo F, Cariboni J, Saltelli A, 2007](https://doi.org/10.1016/j.envsoft.2006.10.004)
34. [Factorial Sampling Plans for Preliminary Computational Experiments — Morris MD, 1991](https://doi.org/10.1080/00401706.1991.10484804)
35. [Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates — Sobol' IM, 2001](https://doi.org/10.1016/S0378-4754%2800%2900270-6)
36. [Why Authors Don't Visualize Uncertainty — Hullman J, 2019](https://doi.org/10.1109/TVCG.2019.2934287) (open preprint: [arXiv:1908.01697](https://arxiv.org/abs/1908.01697))
37. [Uncertainty Visualization — Padilla L, Kay M, Hullman J, 2021](https://doi.org/10.1002/9781118445112.stat08296)
38. [Visualizing Uncertainty for Non-Expert End Users: The Challenge of the Deterministic Construal Error — Joslyn S, Savelli S, 2021](https://doi.org/10.3389/fcomp.2020.590232)
39. [Hypothetical Outcome Plots Help Untrained Observers Judge Trends in Ambiguous Data — Kale A, Nguyen F, Kay M, Hullman J, 2019](https://doi.org/10.1109/TVCG.2018.2864909)
40. [When (ish) is My Bus? User-centered Visualizations of Uncertainty in Everyday, Mobile Predictive Systems — Kay M, Kola T, Hullman J, Munson S, 2016](https://doi.org/10.1145/2858036.2858558)
41. [Visualizing Uncertainty About the Future — Spiegelhalter D, Pearson M, Short I, 2011](https://doi.org/10.1126/science.1191181)
42. [Non-expert interpretations of hurricane forecast uncertainty visualizations — Ruginski IT, Boone AP, Padilla LM, Liu L, et al., 2016](https://doi.org/10.1080/13875868.2015.1137577)
43. [Effects of ensemble and summary displays on interpretations of geospatial uncertainty data — Padilla LM, Ruginski IT, Creem-Regehr SH, 2017](https://doi.org/10.1186/s41235-017-0076-1)
44. [How to improve Bayesian reasoning without instruction: Frequency formats — Gigerenzer G, Hoffrage U, 1995](https://doi.org/10.1037/0033-295X.102.4.684)
45. [Using icon arrays to communicate medical risks: Overcoming low numeracy — Galesic M, Garcia-Retamero R, Gigerenzer G, 2009](https://doi.org/10.1037/a0014474)
46. [Info-Gap Decision Theory: Decisions Under Severe Uncertainty (2nd ed.) — Ben-Haim Y, 2006](https://doi.org/10.1016/B978-0-12-373552-2.X5000-0)
47. [Thinking inside the box: A participatory, computer-assisted approach to scenario discovery — Bryant BP, Lempert RJ, 2010](https://doi.org/10.1016/j.techfore.2009.08.002)
48. [The Exploratory Modeling Workbench: An open source toolkit for exploratory modeling, scenario discovery, and (multi-objective) robust decision making — Kwakkel JH, 2017](https://doi.org/10.1016/j.envsoft.2017.06.054)
