# Tradeoffs, budgets and value of information: how to show them and which unknown to measure first

Research note for a generic tradeoff-model tool: variables linked by simple 1–3-parameter relations, sliders on design knobs, device facts, assumptions and unknowns given as ranges. First use: experimental design for a camera-based measurement campaign (print → capture → upload → analyse) under upload-bandwidth, operator-time and material budgets, with objectives such as signal-to-noise per measured item, items covered per megabyte uploaded, and unbiased comparisons. Value of information for question selection in general (active learning, EIG, EVPI, VoI − cost > 0) is already covered in-house [1]; this note does not repeat it and concentrates on the multi-objective, budget and pilot-study side.

## Summary of actionable findings

- **Compute VOI on the Monte Carlo sample the sliders already need.** Sample the unknowns from their ranges once; EVPI is a one-line formula over that sample, and per-parameter EVPPI is one regression per parameter (the Strong–Oakley–Brennan method) [2][3]. For ~5 unknowns, 4 designs and 10,000 draws this took about 6 ms in NumPy (measured estimate, §3.3): cheap enough to recompute on every slider move.
- **The pilot ranking is "EVSI − cost", not "most uncertain parameter first".** Turn each bar into a named pilot experiment, estimate its expected value of sample information by simulating the pilot's data, and subtract the pilot's cost (ENBS) [4][5]. Expect most parameters to be worth ~0 to measure, and the valuable ones to be ones nobody is currently measuring (Hubbard's measurement inversion) [6].
- **Show "would it flip the decision?" next to the VOI bar.** Flip probability alone overstates sensitivity because it ignores how much is lost when the decision flips [7]; showing both makes VOI legible.
- **Budgets: hard constraints with visible slack by default; penalties only through an explicit exchange constant.** These are Ashby's three textbook strategies (trade-off plot, all-but-one-as-constraint, penalty function with an exchange constant) [8]. Slack bars plus shadow prices answer "what is this budget costing us?" [9].
- **Views: a 2-D trade-off plot with infeasible regions greyed, plus a brushed scatterplot matrix; parallel coordinates only as a secondary filter.** Scatter plots beat parallel coordinates for reading linear relations [10], and with many objectives almost everything becomes non-dominated [11]. Vega-Lite does brushed SPLOMs declaratively [12]; HiPlot is archived [13].
- **When the ranges themselves are contested, add a regret / satisficing view** (robust decision making) rather than trusting a single expected value [14][15].

## 1. Multi-objective tradeoffs: what to compute and what to draw

**Pareto dominance.** Design A dominates B if it is no worse on every objective and strictly better on at least one; the non-dominated set is the Pareto front, which Ashby's materials-selection teaching calls the *trade-off surface* [8]. In Python, `pymoo` provides multi-objective algorithms, constraint handling and visualisation [16], and `paretoset` returns a Boolean non-dominated mask over a pandas DataFrame, with per-column min/max sense and a `"diff"` column for computing fronts separately within categories (e.g. per camera model) [17]. When designs are a handful of discrete options plus slider settings, the front can simply be computed on a grid; the optimiser is only needed for large continuous design spaces.

**Too many objectives flatten the front.** The share of mutually non-dominated solutions rises quickly as objectives are added [11], so a front over five objectives tells the team little. Ashby's practical answer is to keep two objectives on the plot and turn the rest into constraints ("OK if budget limit") [8]; the same group noted that trade-off surfaces are straightforward for two objectives but need new visualisation tools beyond two [18].

**Parallel coordinates** (Inselberg) map each variable to a vertical axis and each design to a polyline [19]. A survey of user evaluations finds they give a good overview, are easier to learn than novices expect (SQL experts finished tasks 43% faster than with SQL), and are good for clusters and brushing, but are *outperformed by scatter plots for reading linear correlation*; most research effort has gone into fighting clutter by reordering or reducing axes and polylines [10][20]. Meta's HiPlot is the usual drop-in parallel-coordinates viewer for Python and CSV, but its repository was archived in March 2024 [13]. **Scatterplot matrices with linked brushing** are a showcase of Vega-Lite's interaction grammar and take a few dozen lines of JSON [12]; Observable Plot is the lighter grammar-of-graphics alternative for single views [21].

**Design by shopping.** The term is attributed to Balling (1999); the original WCSMO-3 paper could not be verified online. Its best-documented implementation is the ARL Trade Space Visualizer: generate many designs automatically, then let the decision-maker browse glyph plots and scatter matrices with brushing, set bounds on performance variables, apply preference shading and display the Pareto frontier, and pick a design once their preferences have formed [22]. This matches the target tool closely. The more formal relative is **interactive multi-objective optimisation**, in which the decision-maker states reference points or classifies objectives at each iteration; DESDEO is the open-source Python framework for it (NIMBUS and others, both scalarisation-based and evolutionary methods) [23].

**Scenario comparison and decision matrices.** For a few named options, a *consequences table* (alternatives as rows, objectives as columns) is the standard device. Hammond, Keeney and Raiffa's *even swaps* method works on that table, trading one objective against another until columns or rows can be eliminated [24]. It is a good fit for the moment the team must commit, after the shopping phase.

## 2. Budgets and constraints

**Three formulations**, all in one Ashby lecture [8]:

1. *Trade-off plot, choose by eye.* Show the non-dominated designs and let judgment pick.
2. *All but one objective as constraints.* Ashby calls this "cheating" in general but "OK if budget limit". This is the natural reading of upload bandwidth, operator time and material, which are real budgets.
3. *Penalty function* `Z = C + α·m`, with α an **exchange constant** (how much of objective 1 you would give up for one unit of objective 2). Contours of Z are straight lines on a linear-scale trade-off plot, and the optimum is the point with the lowest Z.

Optimisation libraries mirror this. pymoo writes constraints as `g(x) ≤ 0` and offers feasibility-first, penalty, constraint-violation-as-objective, ε-constraint and repair strategies [25]. Deb's feasibility rules (feasible beats infeasible; among infeasible designs, smaller violation wins) avoid having to tune a penalty weight [26]. **Recommendation for the tool:** keep budgets as hard constraints, show them as **budget bars** that fill as knobs move, and **grey out infeasible regions** in every trade-off view (the "bounds on performance variables" and preference shading of design-by-shopping [22]). Offer a single utility only when the team writes down its exchange constants explicitly.

**Slack and shadow price.** Slack is budget minus usage. The useful companion number is the **shadow price**: under convex duality, a large optimal multiplier λᵢ means the optimum degrades a lot if constraint i is tightened, and a small one means loosening it gains little [9]. A budget bar can therefore carry "slack left" *and* "what one more unit would buy". A constraint with slack has a zero multiplier, which is complementary slackness [9].

**Goal-seek.** "What distance gives SNR ≥ 10?" is the inverse of one relation. Excel's Goal Seek solves exactly this one-input inversion and sends multi-input cases to Solver [27]. With 1–3-parameter monotone relations the inverse is usually closed-form or a bisection; for several knobs at once it becomes a constrained optimisation (§2 above).

**Linked sliders over ranges.** Bret Victor's *reactive documents* (Tangle) embed a live model in the text so a reader can drag a number and watch the consequences [28]. Guesstimate does the same with uncertainty: an input written `[25,35]` is a 90% interval, and 5,000 Monte Carlo samples propagate through the formulas [29]. Together they are the interaction model this tool needs, and the Monte Carlo sample they produce is the input to everything in §3.

## 3. Value of information: which unknown to measure first

### 3.1 Concepts and terminology

Decision-analytic VOI goes back to Howard's *Information Value Theory* (1966), which argued that information must be valued through the decision's economic consequences rather than through Shannon entropy alone [30], and to Raiffa and Schlaifer's preposterior analysis [31]. Health economics turned it into routine practice; the ISPOR task force reports are the reference for terminology and good practice [32]:

- **Net benefit** NB(d, θ): the value of design *d* if the unknowns are θ, in one currency (here, for example, operator-hour-equivalents, using exchange constants as in §2).
- **EVPI**: expected value of perfect information about all unknowns. It is an upper bound on what any study can be worth.
- **EVPPI**: EVPI for one parameter or a group of parameters ("partial").
- **EVSI**: the expected value of a *specific study* of a given design and size [33].
- **ENBS** = EVSI − study cost: run the pilot only if it is positive [4].

Tools: the SAVI web app computes EVPI and EVPPI from the probabilistic-sensitivity-analysis (PSA) sample alone, without re-running the model [34]; the R package `voi` (Jackson, Heath et al.) offers EVPI, EVPPI, EVSI and ENBS with several estimation methods behind one interface [4]; Jackson et al. 2022 is the compact methods review [35].

### 3.2 Worked formulas from a Monte Carlo sample

Draw θ⁽¹⁾…θ⁽ᴺ⁾ from the ranges (the same draws that drive the uncertainty bands on the sliders) and evaluate NB(d, θ⁽ⁿ⁾) for each of the D designs: an N × D matrix.

- Current best design and value: `V₀ = max_d (1/N) Σₙ NB(d, θ⁽ⁿ⁾)`.
- **EVPI** `= (1/N) Σₙ max_d NB(d, θ⁽ⁿ⁾) − V₀` (choose after seeing θ, minus choose now) [33].
- **EVPPI for φ = θᵢ** (or a group) `= E_φ[ max_d E_{θ|φ} NB(d, θ) ] − V₀`. The nested expectation is the expensive part; Strong, Oakley and Brennan replace it with a regression: fit `ĝ_d(φ) ≈ E[NB(d,θ) | φ]` by regressing column d of the NB matrix on φ⁽ⁿ⁾ (a GAM, or a Gaussian process for groups of parameters), then `EVPPI ≈ (1/N) Σₙ max_d ĝ_d(φ⁽ⁿ⁾) − V₀`. It reuses the existing sample and was more efficient than two-level Monte Carlo in their case studies [2]. A comparative review found this regression approach the best on accuracy, run time and ease of implementation [3].
- **EVSI for a pilot**: simulate the pilot's data Xⁿ ~ p(X | θ⁽ⁿ⁾), reduce it to a low-dimensional summary T(Xⁿ) (for example the pilot's estimated SNR), and regress NB on T instead of on φ. The only extra ingredient is a simulator of the pilot's data [34]; four practical EVSI methods (regression, importance sampling, Gaussian approximation, moment matching) are compared in [5].

**Bayesian experimental design** values information differently: the **expected information gain** EIG(ξ) = E[log p(y | θ, ξ) − log p(y | ξ)], the mutual information between parameters and outcome for design ξ (Lindley 1956) [36], is the standard criterion when the aim is to learn θ rather than to make a fixed decision [37]. Chaloner and Verdinelli show how it sits inside a decision-theoretic framework [37], and Rainforth et al. review modern estimators, which are typically nested Monte Carlo and much costlier than the EVPPI regression [38]. **Use EVPPI/EVSI to choose the pilot that most improves the campaign decision, and EIG when the deliverable is the parameter estimate itself** (for example a published SNR curve).

### 3.3 How cheap is it? (measured estimate)

A toy model with 5 normal unknowns, 4 contested designs, linear net benefit and N = 10,000 draws, computed in NumPy on a laptop (estimate; not a benchmark): EVPI took about 0.2 ms; all five single-parameter EVPPIs by quartic least-squares regression took about 6 ms. The results show two textbook effects:

| parameter | EVPPI | share of draws where the decision flips |
|---|---|---|
| θ₁ | 0.23 | 0.41 |
| θ₂ | 0.33 | 0.72 |
| θ₃ | 0.24 | 0.44 |
| θ₄ | 0.01 | 0.13 |
| θ₅ | 0.07 | 0.29 |

(EVPI = 0.73.) **EVPPIs are not additive**: here they sum to 0.88, more than the EVPI, which is why BCEA's info-rank plot warns against reading the bars as shares [39]. And θ₅ flips the decision in 29% of draws yet is worth little, because the flips happen where the designs are nearly tied. That is Felli and Hazen's argument for EVPI over flip probability [7]. For real use, swap the polynomial for a GAM or GP, as in the original method [2].

### 3.4 Cheap proxies, and their failure modes

- **Sensitivity × reducibility** (how much the output moves across the range × how much a feasible pilot could narrow the range). This is a heuristic (labelled as such); it ignores whether the movement changes the decision, which is exactly what EVPI adds [7].
- **Expected decision change**: does knowing θᵢ flip the chosen design? Felli and Hazen show that flip-based measures overstate sensitivity because they ignore the payoff difference [7]. Keep it as a *display*, not a ranking.
- **Measurement inversion**: Hubbard reports that the economic value of measuring a variable is usually inversely proportional to the attention it already gets, and that in his analyses the vast majority of variables had information value of zero [6][40]. Practical consequence: before running a pilot, compute VOI; the parameter the team is keen to measure is often not the valuable one.

## 4. Visualising VOI for a team

1. **Per-parameter VOI bars**: EVPPI (absolute, or as a fraction of EVPI) sorted descending, the "info-rank" plot that BCEA describes as a tornado plot built on EVPPI [39]. Put EVPI as a reference line.
2. **Decision-flip strips**: for each top parameter, plot the fitted ĝ_d(φ) curves against φ. Where the curves cross are the thresholds at which the best design changes, the classical threshold-proximity view [7]. Shade the parameter's prior range behind them. A probability-each-design-is-best curve, which SAVI produces in its cost-effectiveness acceptability form [34], is the aggregate version.
3. **Pilot cards**: each bar links to a named pilot ("capture 30 prints at three distances", "upload 50 items at two compression levels") showing its EVSI, its cost in the same currency, and **ENBS = EVSI − cost**, sorted by ENBS [4][5]. A parameter with high EVPPI but no affordable pilot is shown as such, not hidden.
4. **Re-run after each pilot**: update the ranges, recompute (milliseconds, §3.3), and show the bars shrinking. Hubbard's Applied Information Economics loop is to repeat until the value of further information is ~0 [6].

## 5. Things not asked about but important

- **Deep uncertainty.** VOI trusts the ranges. When the ranges are themselves disputed, the decision-making-under-deep-uncertainty (DMDU) toolkit applies: Robust Decision Making iterates "propose strategies → find the futures where each fails → weigh the hedges" [14]; the open-access DMDU book covers RDM, adaptive pathways, info-gap and engineering options [41]; and the Python EMA Workbench implements exploratory modelling and PRIM scenario discovery ("in which region of the ranges does design A fail?") [42].
- **Regret and satisficing.** *Minimax regret* (Savage 1951) picks the design whose worst shortfall against the best design in hindsight is smallest [43]. *Satisficing* (Simon 1955) accepts the first option that meets aspiration levels [44]. A water-planning comparison found that robustness definitions change which alternative wins, and recommended an elicited multivariate *satisficing* measure: the share of scenarios in which every threshold (for example SNR ≥ 10 *and* bandwidth within budget) is met [15]. That number fits naturally next to the budget bars.
- **Unbiased comparisons are a design constraint, not an objective.** Balanced or randomised assignment of items to conditions is better expressed as a hard constraint on the design space than traded against throughput. This is a recommendation, without a specific source.

## REFERENCES

1. [Building a candidate-knowledge system: elicitation, active questioning, epistemic state, and a personal knowledge store (in-house research note; repo thorwhalen/hired, misc/docs/research/elicitation-and-knowledge-store.md) — thorwhalen/hired, 2026](https://github.com/thorwhalen/hired/blob/main/misc/docs/research/elicitation-and-knowledge-store.md)
2. [Estimating multiparameter partial expected value of perfect information from a probabilistic sensitivity analysis sample: a nonparametric regression approach — Strong M, Oakley JE, Brennan A, 2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4819801)
3. [A Review of Methods for Analysis of the Expected Value of Information — Heath A, Manolopoulou I, Baio G, 2017](https://ideas.repec.org/a/sae/medema/v37y2017i7p747-758.html)
4. [voi: Expected Value of Information (R package overview vignette) — Jackson C, Heath A, et al., 2024](https://cran.r-project.org/web/packages/voi/vignettes/voi.html)
5. [Computing the Expected Value of Sample Information Efficiently: Practical Guidance and Recommendations for Four Model-Based Methods — Kunst N, Wilson ECF, Glynn D, et al., 2020](https://www.ispor.org/publications/journals/value-in-health/abstract/Volume-23--Issue-6/Computing-the-Expected-Value-of-Sample-Information-Efficiently--Practical-Guidance-and-Recommendations-for-Four-Model-Based-Methods)
6. [How to Measure Anything (summary of Hubbard's book) — Muehlhauser L, 2013](https://www.lesswrong.com/posts/ybYBCK9D7MZCcdArB/how-to-measure-anything)
7. [Sensitivity Analysis and the Expected Value of Perfect Information — Felli JC, Hazen GB, 1998](https://ideas.repec.org/a/sae/medema/v18y1998i1p95-109.html)
8. [Objectives in conflict: trade-off methods and penalty functions (lecture unit) — Ashby MF, 2025](https://ansys.synopsys.com/content/dam/web/academic/education-resources/2025r1/objectives-in-conflict-lecture-unit-pptobjen25.pdf)
9. [Duality (EE364a lecture slides for Convex Optimization, ch. 5: perturbation and sensitivity analysis) — Boyd S, Vandenberghe L, n.d.](https://web.stanford.edu/class/ee364a/lectures/duality.pdf)
10. [Evaluation of Parallel Coordinates: Overview, Categorization and Guidelines for Future Research — Johansson J, Forsell C, 2016](https://itn-web.it.liu.se/~jimjo94/papers/Johansson_Forsell_CAMERA_READY_FINAL.pdf)
11. [What if we Increase the Number of Objectives? Theoretical and Empirical Implications for Many-objective Optimization — Allmendinger R, Jaszkiewicz A, Liefooghe A, Tammer C, 2021](https://arxiv.org/abs/2106.03275)
12. [Vega-Lite: A Grammar of Interactive Graphics — Satyanarayan A, Moritz D, Wongsuphasawat K, Heer J, 2017](https://idl.uw.edu/papers/vega-lite)
13. [HiPlot: High-dimensional interactive plotting (repository, archived 2024) — Haziza D, Rapin J, Synnaeve G, 2020](https://github.com/facebookresearch/hiplot)
14. [A General, Analytic Method for Generating Robust Strategies and Narrative Scenarios — Lempert RJ, Groves DG, Popper SW, Bankes SC, 2006](https://doi.org/10.1287/mnsc.1050.0472)
15. [How Should Robustness Be Defined for Water Systems Planning under Change? — Herman JD, Reed PM, Zeff HB, Characklis GW, 2015](https://ascelibrary.com/doi/10.1061/%28ASCE%29WR.1943-5452.0000509)
16. [pymoo: Multi-Objective Optimization in Python — Blank J, Deb K, 2020](https://arxiv.org/abs/2002.04504)
17. [paretoset: Compute the Pareto (non-dominated) set (documentation) — tommyod, 2025](https://paretoset.readthedocs.io/)
18. [A new approach to multi-criteria material selection in engineering design — Sirisalee P, Parks GT, Clarkson PJ, Ashby MF, 2003](https://www.designsociety.org/publication/23910/A+NEW+APPROACH+TO+MULTI-CRITERIA+MATERIAL+SELECTION+IN+ENGINEERING+DESIGN)
19. [The plane with parallel coordinates — Inselberg A, 1985](https://doi.org/10.1007/BF01898350)
20. [State of the Art of Parallel Coordinates — Heinrich J, Weiskopf D, 2013](https://diglib.eg.org/handle/10.2312/conf.EG2013.stars.095-116)
21. [Observable Plot (documentation) — Observable, n.d.](https://observablehq.com/plot/)
22. [Multidimensional visualization and its application to a design by shopping paradigm — Stump G, Simpson TW, Yukish M, Bennett L, 2002](https://pure.psu.edu/en/publications/multidimensional-visualization-and-its-application-to-a-design-by-2)
23. [DESDEO: The Modular and Open Source Framework for Interactive Multiobjective Optimization — Misitano G, Saini BS, Afsar B, Shavazipour B, Miettinen K, 2021](https://jyx.jyu.fi/handle/123456789/78657)
24. [Even Swaps: A Rational Method for Making Trade-offs — Hammond JS, Keeney RL, Raiffa H, 1998](https://scholars.duke.edu/publication/780184)
25. [Constraint Handling (pymoo documentation) — pymoo developers, n.d.](https://pymoo.org/constraints/index.html)
26. [An efficient constraint handling method for genetic algorithms — Deb K, 2000](https://repository.ias.ac.in/9407)
27. [Use Goal Seek to find the result you want by adjusting an input value — Microsoft, n.d.](https://support.microsoft.com/en-us/excel/use-goal-seek-to-find-the-result-you-want-by-adjusting-an-input-value)
28. [Explorable Explanations — Victor B, 2011](https://worrydream.com/ExplorableExplanations/)
29. [Guesstimate app (README) — Gooen O et al., 2015](https://github.com/getguesstimate/guesstimate-app)
30. [Information Value Theory — Howard RA, 1966](https://doi.org/10.1109/TSSC.1966.300074)
31. [Applied Statistical Decision Theory — Raiffa H, Schlaifer R, 1961 (Wiley Classics reprint 2000)](https://www.wiley-vch.de/en/areas-interest/mathematics-statistics/applied-statistical-decision-theory-978-0-471-38349-9)
32. [Value of Information Analysis for Research Decisions—An Introduction: Report 1 of the ISPOR Value of Information Analysis Emerging Good Practices Task Force — Fenwick E, Steuten L, Knies S, et al., 2020](https://www.ispor.org/heor-resources/good-practices/article/value-of-information-analysis-for-research-decisions-an-introduction)
33. [Expected Value of Sample Information Calculations in Medical Decision Modeling — Ades AE, Lu G, Claxton K, 2004](https://ideas.repec.org/a/sae/medema/v24y2004i2p207-227.html)
34. [SAVI – Sheffield Accelerated Value of Information (web app) — Strong M, Oakley JE, Brennan A, et al., 2025](https://savi.shef.ac.uk/)
35. [Value of Information Analysis in Models to Inform Health Policy — Jackson CH, Baio G, Heath A, Strong M, Welton NJ, Wilson ECF, 2022](https://research-information.bris.ac.uk/en/publications/value-of-information-analysis-in-models-to-inform-health-policy/)
36. [On a Measure of the Information Provided by an Experiment — Lindley DV, 1956](https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-27/issue-4/On-a-Measure-of-the-Information-Provided-by-an-Experiment/10.1214/aoms/1177728069.full)
37. [Bayesian Experimental Design: A Review — Chaloner K, Verdinelli I, 1995](https://projecteuclid.org/euclid.ss/1177009939)
38. [Modern Bayesian Experimental Design — Rainforth T, Foster A, Ivanova DR, Bickford Smith F, 2024 (preprint 2023)](https://arxiv.org/abs/2302.14545)
39. [info.rank: Information-rank plot (BCEA R package reference manual) — Baio G, et al., n.d.](https://search.r-project.org/CRAN/refmans/BCEA/html/info.rank.html)
40. [How to Measure Anything: Finding the Value of Intangibles in Business, 3rd ed. — Hubbard DW, 2014](https://oreilly.com/library/view/how-to-measure/9781118836446)
41. [Decision Making under Deep Uncertainty: From Theory to Practice — Marchau VAWJ, Walker WE, Bloemen PJTM, Popper SW (eds), 2019](https://library.oapen.org/handle/20.500.12657/22900)
42. [The Exploratory Modeling Workbench: An open source toolkit for exploratory modeling, scenario discovery, and (multi-objective) robust decision making — Kwakkel JH, 2017](https://doi.org/10.1016/j.envsoft.2017.06.054)
43. [The Theory of Statistical Decision — Savage LJ, 1951](https://doi.org/10.1080/01621459.1951.10500768)
44. [A Behavioral Model of Rational Choice — Simon HA, 1955](https://doi.org/10.2307/1884852)
