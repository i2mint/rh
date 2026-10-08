# Fitting few-parameter tradeoff models to pilot data, honestly

For a generic tool that renders interactive tradeoff models (variables linked by 1–3-parameter relations, one slider per parameter) whose parameters start as human guesses and are later fitted to pilot data, with the UI showing prior → posterior. Running example: a camera measurement campaign fitting a falloff length scale (blank-sheet capture), a decay time (frame time series) and a noise floor (swatches of different sizes). Prior elicitation, the prior/likelihood/posterior overlay, power-scaling sensitivity, effective-sample-size display and the conjugate fast path are covered in-house and not repeated [1], [2].

## Summary of actionable findings

- **Treat each slider as a prior, not just a widget.** Its default becomes the optimiser's starting value, its range becomes both an optimiser bound and (via elicitation) a prior; never let a fitter fall back to its own defaults (SciPy's `curve_fit` starts every parameter at 1 unless told otherwise) [3], [1].
- **For 1–2 parameters, compute the posterior on a grid in the browser**; it is exact up to grid resolution, needs no sampler, and gives the prior → posterior picture for free [4]. Use the Laplace approximation, then PyMC/NumPyro/Stan, only as dimension or non-Gaussianity grows [5], [6], [7].
- **Report intervals from the profile likelihood, not only from the covariance matrix**: the covariance is a linear approximation that can mislead near bounds and for multi-exponential models, close to the camera use cases; a flat or one-sided profile is the identifiability alarm [3], [8], [9].
- **Ship four honesty signals with every fitted value**: posterior contraction (how much the data narrowed the guess), a parameter-correlation warning, data-support shading on the slider (the range the pilot actually covered), and a provenance record (dataset, date, method, model form) [10], [11], [12].
- **Keep the human's guessed form by default.** Use GAMs or symbolic regression to *check* it (large residual structure ⇒ discrepancy) rather than to replace it; discovered forms lose the parameters' physical meaning and recover exact laws unreliably under noise [13], [14].
- **Design the pilot from the guesses.** Locally D-optimal designs place measurements where the model is most sensitive to each parameter: for an exponential decay, near t = 0, near t ≈ τ_guess and at the far tail (derivation below) [15], [16].
- **Pool across devices only with a weakly informative prior on the between-device spread**; with few devices that prior strongly shapes the result, so elicit it and show it like any other slider [17].

## 1. Standard terminology

| Term | Meaning in this tool | Source |
|---|---|---|
| Calibration | Adjusting model parameters so model output matches observations | [18] |
| Nonlinear least squares (NLS) | Minimise the sum of squared residuals of a model nonlinear in its parameters | [19] |
| Profile likelihood | Likelihood of one parameter with the others re-optimised at each value | [9], [8] |
| Structural / practical non-identifiability | Parameters functionally related (flat profile, any data) / poorly constrained by *these* data (profile does not close at the confidence threshold) | [9] |
| Sloppiness | Fisher-information eigenvalues spread over many decades: few stiff combinations, many sloppy ones | [20], [21] |
| Prior / posterior predictive check | Simulate data from prior / posterior and compare with expectations / observations | [7], [22] |
| Posterior contraction | 1 − posterior variance / prior variance: how much the data taught us | [10] |
| Partial pooling | Hierarchical model: per-group parameters shrink toward a shared mean by an amount learned from the data | [17] |
| Model discrepancy | Systematic difference between reality and the model at the true parameters | [18], [14] |
| Locally optimal design | Design that is optimal at a guessed parameter value | [16], [15] |
| D-optimality | Choose design points to maximise det of the Fisher information (minimise confidence-ellipsoid volume) | [23], [24] |

## 2. Nonlinear least squares: the fast "fitted" path

**Tools.** `scipy.optimize.curve_fit` returns best-fit values and an approximate covariance `pcov` (errors = `sqrt(diag(pcov))`); by default (`absolute_sigma=False`) it rescales `pcov` so the reduced χ² is 1, i.e. it trusts residual scatter over stated measurement errors [3]. With a rank-deficient Jacobian, method `lm` returns an all-`inf` `pcov` while `trf`/`dogbox` use a pseudoinverse, and a large condition number of `pcov` "may indicate that results are unreliable" [3]: surface that, never swallow it. `scipy.optimize.least_squares` adds robust losses (`soft_l1`, `huber`, `cauchy`, `arctan`) for a few corrupted frames and returns the Jacobian needed in §6 [25]. lmfit's named `Parameter` objects (`value`, `min`, `max`, `vary`, expressions) map one-to-one onto slider metadata [26].

**Slider → fit mapping.** Slider default → `p0` / `Parameter.value`; slider range → `bounds` / `min`, `max`. lmfit enforces bounds by a MINUIT-style sine/square-root transformation of an unbounded internal variable, and warns that when the best fit sits very close to a bound the uncertainty and correlations "may not be reliable" [27]. In the UI, a fitted value pinned at a slider end should therefore read "data push past your range", never as a precise estimate.

**Covariance vs profile intervals.** lmfit's `conf_interval()` computes profile-likelihood intervals (fix one parameter, re-optimise the others, find where χ² rises by the F-test threshold); its documentation says the covariance-based error is usually adequate but fails for cases such as a sum of exponentials, where the true intervals are asymmetric, and near bounds [8]. `conf_interval2d()` gives a Δχ² grid for a pair of parameters, i.e. the correlation contour to draw [8]. Profile likelihood is also the standard identifiability diagnostic [9]; pyPESTO provides it for black-box Python models [28]. With ≤ 3 parameters, profile every one and show asymmetric intervals.

## 3. Bayesian updating of a few parameters

**Grid approximation (browser-native).** With 1–2 parameters, evaluate prior × likelihood on a grid and normalise; McElreath teaches it as the first, most transparent method and notes it scales poorly with the number of parameters, motivating quadratic (Laplace) approximation and MCMC [4]. Estimate (not benchmarked): a 200 × 200 grid with 50 observations is 2 million residual evaluations, well within an interactive budget in plain JavaScript; a 3-parameter 100³ grid is ~10⁸ evaluations at the same n and should move to a Web Worker or a server. The grid also gives marginals, intervals and the joint contour directly, so the slider can show the posterior as a density strip behind the thumb.

**Closed form.** Conjugate updates are the in-house fast path [1], [2], but they cover proportions and means, not length scales or decay times inside exponentials, which is why the grid matters here.

**Laplace approximation.** A Gaussian at the posterior mode with covariance from the Hessian: CmdStan's `laplace` method samples a normal approximation centred at the mode in unconstrained space [6], and `pymc_extras.fit_laplace` does the same for PyMC models, warning that it may not suit strongly skewed or multimodal posteriors [5]. Approximating on the log scale of positive parameters (log L, log τ), as Stan's unconstrained space does, keeps the approximation inside the valid range [6].

**Full MCMC.** PyMC [29], NumPyro (JAX, composable effects, fast NUTS) [30] and Stan via CmdStanPy (which exposes sample, optimize, variational, laplace and pathfinder) [31], [32]. Bambi adds a formula interface on PyMC for linear and generalised linear (mixed) models [33], so it fits a relation only after linearisation (e.g. log intensity linear in distance); the nonlinear forms here need PyMC/NumPyro/Stan directly. Store results in ArviZ `InferenceData` so prior, posterior and predictive groups travel together [34], [2].

**Prior and posterior predictive checks.** Gelman et al.'s workflow puts prior predictive simulation before fitting and posterior predictive checking after, with model expansion and comparison as normal steps, not failures [7]; Gabry et al. give the corresponding plots [22]. In this tool: the prior predictive is the curve band the sliders imply *before* data ("your guesses predict this falloff profile"); the posterior predictive is the band after, overlaid on the pilot points.

**Showing prior → posterior to non-experts.** ArviZ's `plot_dist_comparison` draws prior and posterior on separate and shared axes, useful when one is much tighter than the other [35]; `plot_dot` draws quantile dotplots [36], which reduced the variance of lay users' probability estimates relative to density plots in Kay et al.'s study [37]. A compact per-parameter display is an *interval shrinkage bar*: the prior 90% interval as a pale bar, the posterior interval as a dark bar inside it, labelled with the posterior contraction 1 − σ²_post/σ²_prior [10]. Schad et al.'s contraction-vs-z-score diagnostic also classifies outcomes: low contraction means poorly identified; high contraction with a large shift away from the prior signals prior–data conflict or overfitting [10].

## 4. Partial pooling across devices

When the same parameter (e.g. the noise floor) varies per phone, a hierarchical model estimates per-device values that shrink toward a shared mean. Gelman's analysis of group-level variance priors shows serious problems with the popular inverse-gamma(ε, ε) "noninformative" prior, recommends a uniform prior on the between-group standard deviation, and recommends the half-t family when the number of groups is small; in his J = 3 example the uniform prior "is too weak" and a proper half-Cauchy works better [17]. Stan's guide recommends the non-centred parameterisation when there are not many groups or the data constrain them weakly [38]. For this tool: with a handful of devices, pool (it stabilises per-device estimates) but expose the between-device spread as its own slider with an elicited prior, and draw shrinkage arrows (unpooled → pooled estimate) so the borrowing is visible; Bambi's `(1 | device)` covers linearisable cases [33]. No source found giving a minimum number of groups for nonlinear models; treat "about 5 devices before the spread is data-driven" as an unverified heuristic.

## 5. Discovering the relation's form

**Symbolic regression.** PySR searches expression space with a multi-population evolutionary algorithm and returns a loss–complexity front [39]; its default `model_selection="best"` picks the highest "score" (negated derivative of log-loss with respect to complexity) among equations within 1.5× of the best loss, and it can softly enforce physical units via `X_units`/`y_units` [40]. AI Feynman exploits physics-inspired structure (units, symmetries, separability) [41]. SRBench found AI Feynman recovered exact noise-free Feynman equations 53% of the time but was overtaken by other methods once noise exceeded 0.01, and the best real-world method "struggles to recover" ground-truth forms despite near-perfect test scores [13]. With a few dozen noisy pilot points, expect a plausible-looking but non-unique formula.

**SINDy** fits sparse combinations of candidate terms to time derivatives to identify governing equations [42]; PySINDy implements it with noise-robust variants [43]. It suits the frame time series: it can confirm that dy/dt ≈ −(y − y∞)/τ is the sparsest adequate model, i.e. that the guessed exponential is right.

**GAMs** are the interpretable middle ground: smooth per-variable functions with penalised wiggliness [44]; pyGAM supports monotonic and convex/concave constraints, which encode "falloff is decreasing" without fixing the form [45], [46]. A GAM fitted next to the guessed curve is a cheap discrepancy detector.

**Model comparison.** AIC [47] and BIC [48] penalise parameter count; AICc corrects AIC for small samples [49]. For Bayesian fits, PSIS-LOO and WAIC estimate out-of-sample predictive accuracy, with PSIS-LOO more robust [50], [51]; the Pareto k̂ diagnostic flags observations for which the estimate is unreliable (current threshold min(1 − 1/log₁₀ S, 0.7)) [52], [53]. With ~10–30 points these criteria are noisy; use them to rank 2–3 candidate forms, not to search.

**When not to replace the guessed form.** Keep it when its parameters carry meaning someone will act on (a length scale in millimetres, a decay time in seconds), when the alternative wins only by a small information-criterion margin, or when the decision depends on extrapolation. Brynjarsdóttir and O'Hagan show that fitting a structurally wrong model yields biased, over-confident parameters, and that modelling the discrepancy flexibly fixes in-range prediction but recovers true parameters only with realistic priors on the discrepancy [14]. A discovered form trades that problem for one with no physical prior at all.

## 6. Honesty issues and how the UI should surface them

**Identifiability.** A flat profile means a structural non-identifiability (e.g. amplitude × gain appear only as a product); a profile that does not rise above the threshold on one side means the data cannot bound it [9]. Sloppy models fit and predict well while individual parameters stay poorly constrained [20], [21]; the honest display is then "this combination is known, the parts are not". UI: grey out or hatch the slider of a non-identified parameter and show the identified combination.

**Correlation and reparametrisation.** Orthogonal parametrisations make nuisance parameters approximately independent of the one of interest [54]; Bates and Watts distinguish intrinsic nonlinearity from parameter-effects curvature that a better parametrisation removes [19]. Illustration (my computation, not from a source): for y = A·e^(−t/τ) with ten points only in t ∈ [5τ, 8τ], corr(Â, τ̂) ≈ −0.996; with points in [0, 3τ] it is ≈ −0.59. Re-referencing the amplitude to the middle of the observed window (an orthogonalising reparametrisation in the sense of [54]) removes most of it. UI: warn above |ρ| ≈ 0.9 (heuristic) and draw the 2-D contour.

**Overfitting with few points.** AICc exists because AIC under-penalises when the sample is small relative to the parameter count, and its correction term grows sharply as n approaches that count [49]; no source found for a universal points-per-parameter rule, so show n and p side by side rather than hide a threshold, and prefer the prior-regularised posterior over the raw NLS fit when n is small [7].

**Extrapolation.** Predictions outside the convex hull of the data depend more on model assumptions than on evidence [11]; leverage (hat-matrix diagonal, average p/n) measures how far a design point is from the data's centre, and the Jacobian replaces X for nonlinear fits [55], [19]. UI: shade each slider's input-variable track over the range the pilot covered; when the user moves an *input* slider outside it, switch the curve to dashed and widen the band, and in multi-input views test convex-hull membership [11].

**Model discrepancy.** Kennedy and O'Hagan's calibration adds an explicit discrepancy term δ(x), often a Gaussian process, to y = η(x, θ) + δ(x) + ε [18]; it is confounded with θ unless δ has a realistic prior [14]. For a slider tool a lighter version suffices: show residuals vs input and flag structure (a GAM fit to residuals that is clearly non-flat) [44].

**Provenance.** Every fitted value should carry: dataset identifier and hash, capture date, model form and version, method (NLS / grid / NUTS), prior used, and fit date. W3C PROV-O provides the entity–activity–agent vocabulary [12] and the FAIR principles call for rich metadata and provenance [56]. UI: a "fitted from pilot P on date D by method M" badge on each slider, with "revert to guess".

## 7. Designing the pilot so parameters are identifiable

Fisher information I(θ) = Jᵀ J / σ² (J = sensitivities of predictions to parameters) bounds achievable precision; D-optimal design maximises det I, minimising the joint confidence-region volume [23], [21]. For nonlinear models I depends on the unknown θ, so designs are *locally* optimal at a guess [16], [15]; Bayesian design averages the criterion over the prior instead [24], [57] — and the human's slider priors are exactly that prior. Pyomo.DOE approximates the Fisher information for model-based design in Python [23].

Worked results for the running examples (my derivations, numerically checked; not from a cited source):

- *Decay time*, y = A·e^(−t/τ): the 2-point D-optimal design is t = 0 and t = τ_guess. With an unknown baseline, y = b + A·e^(−t/τ), it is t = 0, t ≈ τ_guess and the longest feasible time.
- *Noise floor*, var(N) = σ²_floor + σ²_px / N for swatches of N pixels: linear in 1/N, so the D-optimal design uses the smallest and the largest swatch; the floor is identifiable only if the largest swatch is past the crossover N* = σ²_px / σ²_floor.
- *Falloff length scale*: as for the decay, sample near r = 0, near r ≈ L_guess, and far enough out to pin the background.

UI: before the pilot, show the predicted interval shrinkage bars for the proposed design (simulate data from the prior, fit, report expected contraction); after the pilot, re-run with the posterior to plan the next round.

## 8. Recommended workflow: from "guess" to "fitted"

| Stage | What happens | Library (Python / browser) | What the UI shows |
|---|---|---|---|
| 1. Guess | Human sets default + range per parameter; range → prior | PreliZ `maxent` [1] / jStat | Slider with prior band; prior-predictive curve band [7] |
| 2. Design | Choose pilot points maximising expected information under the prior | NumPy + simulation; Pyomo.DOE for larger cases [23] | Proposed points on the curve; predicted shrinkage bars |
| 3. Quick fit | NLS from slider default within slider bounds; robust loss | `least_squares` / lmfit [25], [26] | Best-fit curve over data; residual strip |
| 4. Honest intervals | Profile likelihood per parameter; correlation; identifiability | lmfit `conf_interval`, pyPESTO [8], [28] | Asymmetric intervals; hatched non-identified sliders; 2-D contour |
| 5. Posterior | Grid (1–2 params) or Laplace / NUTS (3+, hierarchical) | JS grid; PyMC / NumPyro / CmdStanPy [29], [30], [32] | Prior → posterior shrinkage bar, contraction %, quantile dotplot [36] |
| 6. Check | Posterior predictive check; residual GAM; compare 2–3 forms by LOO/AICc | ArviZ, pyGAM, PySR as a check [34], [46], [39] | Predictive band over data; "form looks adequate / structured residuals" flag |
| 7. Pool | Per-device hierarchical model when ≥ 2 devices | PyMC / Bambi [33] | Shrinkage arrows per device; between-device spread slider |
| 8. Publish | Record provenance; freeze fitted prior for next round | PROV-style record [12] | Badge (dataset, date, method); data-support shading on input sliders [11] |

## REFERENCES

1. [Bayesian prior elicitation for Beta distributions: a practical survey (in-house, thorwhalen/ba misc/docs/resources) — Whalen T., 2026](https://github.com/thorwhalen/ba/blob/main/misc/docs/resources/Bayesian%20prior%20elicitation%20for%20Beta%20distributions-%20a%20practical%20survey.md)
2. [Design lessons from nine statistical libraries for building ba (in-house, thorwhalen/ba misc/docs/resources) — Whalen T., 2026](https://github.com/thorwhalen/ba/blob/main/misc/docs/resources/Design%20Lessons%20from%20Nine%20Statistical%20Libraries%20for%20Building%20ba.md)
3. [scipy.optimize.curve_fit (documentation) — SciPy developers, accessed 2026](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)
4. [Statistical Rethinking: A Bayesian Course with Examples in R and Stan, 2nd ed. — McElreath R., 2020](https://xcelab.net/rm/)
5. [pymc_extras.inference.fit_laplace (documentation) — PyMC developers, accessed 2026](https://www.pymc.io/projects/extras/en/latest/generated/pymc_extras.inference.fit_laplace.html)
6. [CmdStan User's Guide: Laplace sampling — Stan Development Team, accessed 2026](https://mc-stan.org/docs/cmdstan-guide/laplace_sample_config.html)
7. [Bayesian Workflow — Gelman A., Vehtari A., Simpson D., et al., 2020](https://arxiv.org/abs/2011.01808)
8. [lmfit: Calculation of confidence intervals (documentation) — Newville M., et al., accessed 2026](https://lmfit.github.io/lmfit-py/confidence.html)
9. [Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood — Raue A., Kreutz C., Maiwald T., et al., 2009](https://doi.org/10.1093/bioinformatics/btp358)
10. [Toward a principled Bayesian workflow in cognitive science — Schad D.J., Betancourt M., Vasishth S., 2021](https://doi.org/10.1037/met0000275) (preprint: [arXiv:1904.12765](https://arxiv.org/abs/1904.12765))
11. [The dangers of extreme counterfactuals — King G., Zeng L., 2006](https://doi.org/10.1093/pan/mpj004)
12. [PROV-O: The PROV Ontology (W3C Recommendation) — Lebo T., Sahoo S., McGuinness D. (eds.), 2013](https://www.w3.org/TR/prov-o/)
13. [Contemporary symbolic regression methods and their relative performance — La Cava W., Orzechowski P., Burlacu B., et al., 2021](https://arxiv.org/abs/2107.14351)
14. [Learning about physical parameters: the importance of model discrepancy — Brynjarsdóttir J., O'Hagan A., 2014](https://doi.org/10.1088/0266-5611/30/11/114007)
15. [Design of experiments in non-linear situations — Box G.E.P., Lucas H.L., 1959](https://doi.org/10.1093/biomet/46.1-2.77) (full text not accessed; cited at title/bibliographic level)
16. [Locally optimal designs for estimating parameters — Chernoff H., 1953](https://doi.org/10.1214/aoms/1177728915) (full text not accessed; cited at title level)
17. [Prior distributions for variance parameters in hierarchical models — Gelman A., 2006](https://doi.org/10.1214/06-BA117A)
18. [Bayesian calibration of computer models — Kennedy M.C., O'Hagan A., 2001](https://doi.org/10.1111/1467-9868.00294)
19. [Nonlinear Regression Analysis and Its Applications — Bates D.M., Watts D.G., 1988](https://doi.org/10.1002/9780470316757)
20. [Universally sloppy parameter sensitivities in systems biology models — Gutenkunst R.N., Waterfall J.J., Casey F.P., et al., 2007](https://doi.org/10.1371/journal.pcbi.0030189)
21. [Perspective: Sloppiness and emergent theories in physics, biology, and beyond — Transtrum M.K., Machta B.B., Brown K.S., et al., 2015](https://doi.org/10.1063/1.4923066)
22. [Visualization in Bayesian workflow — Gabry J., Simpson D., Vehtari A., Betancourt M., Gelman A., 2019](https://doi.org/10.1111/rssa.12378)
23. [Pyomo.DOE: An open-source package for model-based design of experiments in Python — Wang J., Dowling A.W., 2022](https://doi.org/10.1002/aic.17813)
24. [Bayesian experimental design: a review — Chaloner K., Verdinelli I., 1995](https://doi.org/10.1214/ss/1177009939)
25. [scipy.optimize.least_squares (documentation) — SciPy developers, accessed 2026](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
26. [LMFIT: Non-linear least-squares minimization and curve-fitting for Python — Newville M., Otten R., Nelson A., et al., 2025 (Zenodo)](https://doi.org/10.5281/zenodo.598352)
27. [lmfit: Bounds implementation (documentation) — Newville M., et al., accessed 2026](https://lmfit.github.io/lmfit-py/bounds.html)
28. [pyPESTO: a modular and scalable tool for parameter estimation for dynamic models — Schälte Y., Fröhlich F., Jost P.J., et al., 2023](https://doi.org/10.1093/bioinformatics/btad711) (profile likelihoods listed in the [project README](https://github.com/ICB-DCM/pyPESTO))
29. [PyMC: a modern, and comprehensive probabilistic programming framework in Python — Abril-Pla O., Andreani V., Carroll C., et al., 2023](https://doi.org/10.7717/peerj-cs.1516)
30. [Composable effects for flexible and accelerated probabilistic programming in NumPyro — Phan D., Pradhan N., Jankowiak M., 2019](https://arxiv.org/abs/1912.11554)
31. [Stan: A probabilistic programming language — Carpenter B., Gelman A., Hoffman M.D., et al., 2017](https://doi.org/10.18637/jss.v076.i01)
32. [CmdStanPy (documentation) — Stan Development Team, accessed 2026](https://mc-stan.org/cmdstanpy/)
33. [Bambi: A simple interface for fitting Bayesian linear models in Python — Capretto T., Piho C., Kumar R., et al., 2022](https://doi.org/10.18637/jss.v103.i15)
34. [ArviZ: a unified library for exploratory analysis of Bayesian models in Python — Kumar R., Carroll C., Hartikainen A., Martin O., 2019](https://doi.org/10.21105/joss.01143)
35. [arviz.plot_dist_comparison (documentation) — ArviZ developers, accessed 2026](https://arviz.readthedocs.io/en/latest/api/generated/arviz.plot_dist_comparison.html)
36. [arviz.plot_dot (documentation) — ArviZ developers, accessed 2026](https://arviz.readthedocs.io/en/latest/api/generated/arviz.plot_dot.html)
37. [When(ish) is my bus? User-centered visualizations of uncertainty in everyday, mobile predictive systems — Kay M., Kola T., Hullman J.R., Munson S.A., 2016](https://doi.org/10.1145/2858036.2858558)
38. [Stan User's Guide: Efficiency tuning — hierarchical models and the non-centered parameterization — Stan Development Team, accessed 2026](https://mc-stan.org/docs/stan-users-guide/efficiency-tuning.html)
39. [Interpretable machine learning for science with PySR and SymbolicRegression.jl — Cranmer M., 2023](https://arxiv.org/abs/2305.01582)
40. [PySR API reference — Cranmer M., et al., accessed 2026](https://ai.damtp.cam.ac.uk/pysr/api)
41. [AI Feynman: A physics-inspired method for symbolic regression — Udrescu S.-M., Tegmark M., 2020](https://doi.org/10.1126/sciadv.aay2631)
42. [Discovering governing equations from data by sparse identification of nonlinear dynamical systems — Brunton S.L., Proctor J.L., Kutz J.N., 2016](https://doi.org/10.1073/pnas.1517384113)
43. [PySINDy: A comprehensive Python package for robust sparse system identification — Kaptanoglu A.A., de Silva B.M., Fasel U., et al., 2022](https://doi.org/10.21105/joss.03994)
44. [Generalized Additive Models: An Introduction with R, 2nd ed. — Wood S.N., 2017](https://doi.org/10.1201/9781315370279) (R package [mgcv](https://cran.r-project.org/package=mgcv))
45. [A tour of pyGAM (documentation) — pyGAM developers, accessed 2026](https://pygam.readthedocs.io/en/latest/notebooks/tour_of_pygam.html)
46. [pyGAM: Generalized additive models in Python — Servén D., Brummitt C., et al., 2018– (Zenodo)](https://doi.org/10.5281/zenodo.1208723)
47. [A new look at the statistical model identification — Akaike H., 1974](https://doi.org/10.1109/TAC.1974.1100705)
48. [Estimating the dimension of a model — Schwarz G., 1978](https://doi.org/10.1214/aos/1176344136)
49. [Regression and time series model selection in small samples — Hurvich C.M., Tsai C.-L., 1989](https://doi.org/10.1093/biomet/76.2.297)
50. [Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC — Vehtari A., Gelman A., Gabry J., 2017](https://doi.org/10.1007/s11222-016-9696-4)
51. [Asymptotic equivalence of Bayes cross validation and widely applicable information criterion in singular learning theory — Watanabe S., 2010](https://www.jmlr.org/papers/v11/watanabe10a.html)
52. [loo: Diagnostics for Pareto smoothed importance sampling (documentation) — Stan Development Team, accessed 2026](https://mc-stan.org/loo/reference/pareto-k-diagnostic.html)
53. [Pareto smoothed importance sampling — Vehtari A., Simpson D., Gelman A., Yao Y., Gabry J., 2024](https://www.jmlr.org/papers/v25/19-556.html)
54. [Parameter orthogonality and approximate conditional inference — Cox D.R., Reid N., 1987](https://doi.org/10.1111/j.2517-6161.1987.tb01422.x)
55. [The hat matrix in regression and ANOVA — Hoaglin D.C., Welsch R.E., 1978](https://doi.org/10.1080/00031305.1978.10479237)
56. [The FAIR guiding principles for scientific data management and stewardship — Wilkinson M.D., Dumontier M., Aalbersberg I.J., et al., 2016](https://doi.org/10.1038/sdata.2016.18)
57. [A review of modern computational algorithms for Bayesian optimal design — Ryan E.G., Drovandi C.C., McGree J.M., Pettitt A.N., 2016](https://doi.org/10.1111/insr.12107)
