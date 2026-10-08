# Explorable explanations, reactive documents, and which control fits which relation

Research note for a generic tool that renders small, fiddlable parametric models of tradeoffs (variables linked by simple relations; inputs that update everything downstream; a diagram of the relations), to be fitted to data later. First intended use: an experimental-design tradeoff dashboard for a camera-based measurement campaign (print a test sheet, capture it with a phone, upload, analyse) under budgets such as upload bandwidth, operator time and material. Written 2026-10-08.

## Summary of actionable findings

- Build the dashboard as a **reactive document** in Bret Victor's original sense: an argument whose assertions are backed by an explorable computational model, not "an article with interactive pictures"; Victor's 2024 postscript says the former is what he meant all along [1].
- The default numeric control should be a **number with units plus a slider or scrub handle**, log-scaled when the quantity spans orders of magnitude, with the consequence shown next to it and a "step up the ladder" plot of the output against that input with the current point marked [2], [3], [4].
- Add **persistent locks and solve-for** (Victor's Scrubbing Calculator, spreadsheet Goal Seek): this is the largest functional gap relative to rh, whose propagator only pins the variable being edited and needs hand-written inverse functions [5], [6], [7].
- Represent uncertain parameters as **intervals** that feed a **tornado chart**; budgets as **threshold indicators**; discrete designs as **scenarios compared side by side**; two conflicting objectives as a **Pareto scatter** [8], [9], [10].
- The evidence that interactivity improves understanding is **thin and mixed**: readers use widgets that are central to the message, but many (mobile readers especially) never touch secondary controls, so the key conclusion must be readable in the static view [11], [12], [13].
- Keep recomputation well under half a second per change; an added 500 ms delay measurably reduced exploration in a controlled study [14].
- Every slider needs a keyboard path and a non-drag alternative (typing or clicking) to meet accessibility guidance [15], [16].

## 1. The lineage, and what each piece contributes

**Bret Victor.** *Explorable Explanations* (March 2011) names three ideas: a *reactive document* "allows the reader to play with the author's assumptions and analyses, and see the consequences"; an *explorable example* "makes the abstract concrete"; *contextual information* lets the reader "learn related material just-in-time, and cross-check the author's claims" [1]. *Up and Down the Ladder of Abstraction* (October 2011) argues that "the most powerful way to gain insight into a system is by moving between levels of abstraction": stepping up abstracts over a variable by letting it range over all its values, stepping down picks one concrete value to explain a pattern [2]. *Tangle* is "a JavaScript library for creating reactive documents" (canonical example: cookies × 50 = calories, inside a sentence) [17]. The *Scrubbing Calculator* (May 2011) defines **scrubbing** as "dragging horizontally on the value" and adds **locks**: "an unlocked number is free to adjust itself to whatever makes the equation hold" [5]. *Kill Math* (2011) calls "Mathematics, as currently practiced, ... a command line" and asks for concrete, visual tools [18]; *Media for Thinking the Unthinkable* (2013) argues for several linked representations of a system rather than ones "designed for the medium of paper" [19]. In a 2024 postscript Victor says the term now seems to mean "any article with interactive pictures", that most such articles are pedagogical, "and that's not really what I was going for"; he meant "a written argument whose assertions are backed by explorable computational models" [1]. A tradeoff dashboard is exactly that case.

**Nicky Case.** *How I Make Explorable Explanations* (2017) gives a three-step recipe: start with a question the reader cares about, move up the ladder of abstraction from a concrete interactive experience, and end with a question, usually via a "Sandbox Mode" that "allows the student to go beyond the teacher" [20]. The explorabl.es hub collects such work as "a hub for learning through play" [21]. *LOOPY* lets anyone "model systems by simply drawing circles & arrows" and then play with what-if questions; it is public domain [22], and is the closest prior art for an editable relation diagram.

**Idyll and its follow-ups (Conlen and Heer).** Idyll is a "compile-to-the-web" markup language for interactive articles, with reader-driven events and a structured interface to JavaScript components (UIST 2018) [23]. *Idyll Studio* (UIST 2021) adds a structured graphical editor, evaluated with 18 participants [24]. Conlen, Kale and Heer (EuroVis 2019) instrumented three published Idyll articles and analysed over 50,000 reader sessions, comparing desktop and mobile [25]; the detailed results are in Conlen's dissertation and are summarised in section 2 [12].

**Observable.** In Observable notebooks an input declared with `viewof` can be referenced in any cell, "and the cell will run whenever the input changes" [26]. Observable Inputs provides button, checkbox, toggle, radio, range, select, text, table and search inputs; `Inputs.range` accepts a non-linear `transform` (passing `Math.log` supplies the inverse automatically), and `Inputs.number` is the same control with the slider suppressed [3]. Observable Plot is "a concise API for exploratory data visualization implementing a layered grammar of graphics" [27], a natural target for the linked plots in section 4.

**Distill.** Olah and Carter's *Research Debt* (2017) defines research debt as "the accumulation of missing interpretive labor" and names distillation as its remedy, citing explorable explanations as reimagining "what an essay can be" [28]. Distill is now "on an indefinite hiatus" [29]. Its 2020 survey, Hohman, Conlen, Heer and Chau's *Communicating with Interactive Articles*, surveys the evidence [11].

**Other systems.** Mavo (Verou, Zhang and Karger, UIST 2016) extends HTML so that non-programmers turn static mockups into data-driven apps; 20 study participants did so fairly quickly [30]; Verou's 2024 thesis adds Formula², a reactive expression language for novices [31]. Apparatus (originally developed by Toby Schachman) is "a hybrid graphics editor and programming environment for creating interactive diagrams" [32]. The *New York Times* rent-versus-buy calculator (2014 rebuild, updated in 2024) lays out all assumptions as sliders in one vertical column and reports a single headline number, the break-even rent [33], [34]; the claim that each slider carried a small curve of the result versus that input could not be verified from an accessible source. *Seeing Theory* (Brown University) pairs a short explanation with a manipulable chart for each probability concept [35]; Setosa's *Explained Visually* is "an experiment in making hard ideas intuitive", inspired by Victor [36].

## 2. Does interactivity improve understanding? The evidence, including null results

Hohman et al. state plainly: "There is limited empirical evaluation of the effectiveness of interactive articles" [11].

Supportive: dynamic queries (sliders that filter a live display) let 18 students answer questions significantly faster than two form-fill-in interfaces [37]. Asking readers to predict data before seeing it, then showing the gap, improved recall and comprehension over a control group, even with little prior knowledge [38]. PhET's simulation research credits *implicit scaffolding* ("affordances, constraints, cueing, and feedback") for productive exploration, refined over 125 simulations and more than 600 student interviews [39].

Null or disconfirming: adding introductory stories to exploratory visualizations did not increase exploration in three field experiments, "contrary to the authors' hypotheses" [13]. In a randomised study of 152 students learning functions, both dynamic conditions beat static pictures, but interactive (drag a point) and non-interactive animation did not differ significantly [40]. Hohman et al. report a study that found no engagement difference between step-based and scroll-based interactive layouts, and the *New York Times*' observation that "only a fraction of readers interact with non-static content" [11]. Educational psychology warns that minimally guided exploration is less effective than guided instruction for novices; the benefit of guidance recedes only with high prior knowledge [41].

In the wild: across three instrumented articles, readers engaged most with widgets central to the narrative; when details sat behind a click, roughly half of desktop readers and 38% of mobile readers who reached the end clicked; mobile readers spent 23–52% of desktop median time, used fewer features but still followed the narrative, leading Conlen to recommend that "the narrative is intact and comprehensible even if a reader chooses not to engage with the interactive widgets" [12].

Reading for this tool (inference, not a finding): interaction pays when the reader is asking a question the model answers (a tradeoff decision is such a case), when the interactive element is the point rather than a garnish, and when there is guidance; it does not pay as decoration.

## 3. What makes them understandable: principles

1. **Immediate, incremental, reversible feedback.** Direct manipulation means continuous representation of the objects of interest and "rapid, incremental, reversible actions whose effects ... are visible immediately" [42]; latency cuts exploration (section 6) [14].
2. **Show the consequence next to the control.** The reactive-document pattern puts the changed number inside the sentence that interprets it [1], [17].
3. **Reader-controlled abstraction.** Offer both the concrete case (current values) and the step up (sweep one variable, plot the family of outcomes) [2]; start concrete and climb [20].
4. **Defaults that tell a story, then release.** Segel and Heer's *martini glass* structure runs an author-driven sequence first and then opens up to free exploration [43]; Case opens with a question [20]; prediction prompts before revealing results improve recall [38]. For a dashboard: ship with a sensible baseline design and two or three named presets.
5. **Constraints and locks.** Let the reader fix what they cannot change (a budget, a deadline) and solve for the rest [5]; spreadsheets call this Goal Seek (one input) and Solver (several inputs, with constraints) [6], [9].
6. **Scenarios.** Name and compare whole configurations; spreadsheets separate Scenarios (many variables, up to 32 values) from Data Tables (one or two variables, many values) [9].
7. **Annotation and context.** Give each quantity a unit, a one-line meaning and its source or assumption, just in time [1]; cue rather than instruct [39].
8. **Never hide the conclusion behind an interaction.** The static view must carry the main message [12].

## 4. UI element → relation or variable type → pitfalls

| Element | Fits | Pitfalls |
|---|---|---|
| Slider, linear | Bounded continuous input where the approximate value matters more than the exact one [4] | Imprecise in dense ranges; fingers hide labels; hard for users with motor difficulties [4]; needs arrow/Home/End keys and `aria-valuetext` for readable values [15]; needs a single-pointer, non-drag alternative [16] |
| Slider, log scale | Quantities spanning orders of magnitude (replicate count, file size, bandwidth); supported directly via a `transform` [3] | Labels must show real values, not exponents; zero is not representable, so a floor must be chosen (design note) |
| Scrubbable inline number | Assumptions embedded in prose ("we capture **12** sheets per hour") [5], [17] | Affordance is invisible unless styled (Victor underlines adjustable values) [1]; not keyboard-accessible unless given the slider role [15] |
| Number input with units | Exact values: budgets, targets, measured constants; "tap or type" when precision matters [4] | Gives no sense of range; pair with a slider (Observable's range input shows both) [3] |
| Dropdown / segmented control | Discrete design options (phone model, print layout, file format) | A dropdown hides the alternatives; information hidden behind a click is often never seen [12]; for two to five options prefer a segmented control or a scenario table |
| Toggle | Boolean capability flags (flash on, on-device compression) | Must take effect immediately; label states what "on" means, not a question [44] |
| Range (interval) slider | Uncertain parameters to be fitted later (throughput, failure rate); feeds sensitivity analysis [8] | Readers may treat the interval as hard bounds; sampled-outcome displays (hypothetical outcome plots) beat error bars for some judgements [45] |
| Linked plot (output vs one input, current point marked) | "Stepping up" on one variable [2]; linking highlights the same item across views [46] | Shows a one-dimensional slice with everything else held fixed; Lotov's decision maps use collections of two-objective slices to show more [10] |
| Small multiples | Comparing a curve across a discrete option, all panels on the same scale and axes [47] | Unshared scales mislead; panel count grows multiplicatively |
| Tornado chart | Ranking which uncertain input moves an output most; compact for many variables [8] | One-at-a-time ranges ignore interactions; a spider plot shows more detail for few variables, and Eschenbach recommends using both [8] |
| Pareto-front scatter | Two conflicting objectives (cost vs precision); Interactive Decision Maps visualise the Pareto frontier as collections of two-objective slices [10] | Beyond two or three objectives needs slices or decision maps [10] |
| Scenario comparison table | Named whole configurations side by side [9] | Hides the shape between scenarios; pair with a linked plot |
| Traffic-light / threshold indicator | Budget constraints (upload time under the window, material under stock); bullet graphs encode qualitative ranges as intensities of one hue [48] | Colour alone fails accessibility; add text or icon [49] |
| Node-link diagram with live values | Showing which relations an edit propagated through; Excel's tracer arrows for precedents and dependents [50]; LOOPY's circles and arrows [22]; multiple linked representations [19] | No controlled evaluation of live dependency graphs for comprehension was found; estimated to clutter beyond a few dozen nodes (estimate) |
| Lock / solve-for (goal seek) | "What must X be for Y to hit target?" [5], [6] | Goal Seek varies one input; several need a solver with constraints [9]; may have no or multiple solutions, which the UI must report (design note) |

## 5. Standard terminology

*Explorable explanation*, *reactive document*, *explorable example*, *contextual information* [1]; *ladder of abstraction* [2]; *scrubbing* and *locked/unlocked numbers* [5]; *interactive article* [11]; *research distillation* [28]; *direct manipulation* [42]; *dynamic query* [37]; *brushing and linking* [46]; *what-if analysis*, *scenario*, *data table*, *goal seek*, *solver* [9], [6]; *sensitivity analysis*, *tornado diagram*, *spider plot* [8]; *Pareto frontier*, *interactive decision maps* [10]; *martini glass* narrative structure [43]; *implicit scaffolding* [39]; *hypothetical outcome plots* [45]; *small multiples* [47]; *bullet graph* [48].

## 6. Important things not asked about

- **Accessibility.** The ARIA slider pattern requires role, current/min/max values, a label, arrow, Home and End keys, and `aria-valuetext` when the raw number is not meaningful [15]. WCAG 2.2 criterion 2.5.7 requires a single-pointer alternative to dragging [16]; WCAG 1.4.1 forbids colour as the only carrier of meaning [49].
- **Recompute latency.** In Liu and Heer's study an added 500 ms delay reduced user activity and dataset coverage, and early exposure to delay depressed later performance even at low latency [14]. For a few-parameter model this argues for client-side recomputation; for a fitted or simulated model, precompute grids or cache.
- **Server round trips.** Streamlit re-executes the script on every widget interaction, mitigated with caching, forms and fragments [51]; that is fine for a few closed-form relations but is the main latency risk for a dagapp-based renderer.
- **Mobile.** Mobile readers spend much less time and use fewer features [12], and finger occlusion makes sliders worse on phones [4]; a single vertical column with the headline result pinned is the safe layout (design note).

## 7. How this maps onto rh and dagapp (gaps only)

rh already builds reactive HTML from a variable mesh with cyclic dependencies, name-based widget conventions (`slider_`, `readonly_`, ...) and JSON-Schema field overrides [52]; dagapp already builds Streamlit apps from meshed DAGs with per-input `num`/`slider` types and slider ranges [53]. What the findings add:

- **Locks and solve-for.** rh's propagator runs a fixed-point iteration over all functions (at most 50 passes) and never overwrites the variable just edited [7]. That is an implicit, one-variable lock; bidirectionality still requires the author to write each inverse. A persistent lock set plus a numeric solver for the unlocked variable would deliver the Scrubbing-Calculator and Goal-Seek behaviour [5], [6]. The same loop silently stops after 50 passes, so non-convergence of a cycle is invisible to the reader [7]; it should be reported.
- **Richer conventions.** Units, log scale, interval (uncertain) inputs, and threshold metadata are not among the README's conventions [52]; each maps to a row of the table in section 4.
- **Views beyond the form.** Linked output-versus-input plots, tornado, Pareto scatter, scenario table and a live relation diagram (the mesh already is the graph) are absent from both READMEs [52], [53].
- **Prose with scrubbable numbers.** Neither package renders values inside a sentence [52], [53]; that is the Tangle/Idyll pattern [17], [23].
- **Fitting.** rh's relations are JavaScript strings [52], dagapp's are Python functions [53]. Recommendation (not a finding): keep one model specification (variables, units, ranges or priors, relations) as the single source of truth, fit its parameters in Python, and let both renderers consume it.

## REFERENCES

1. [Explorable Explanations — Bret Victor, 2011](https://worrydream.com/ExplorableExplanations/)
2. [Up and Down the Ladder of Abstraction — Bret Victor, 2011](https://worrydream.com/LadderOfAbstraction/)
3. [Observable Inputs (README and API reference) — Observable, n.d.](https://github.com/observablehq/inputs)
4. [Slider Design: Rules of Thumb — Aurora Harley, Nielsen Norman Group, 2015](https://www.nngroup.com/articles/gui-slider-controls/)
5. [Scrubbing Calculator — Bret Victor, 2011](https://worrydream.com/ScrubbingCalculator/)
6. [Use Goal Seek to find the result you want by adjusting an input value — Microsoft Support, n.d.](https://support.microsoft.com/en-us/excel/use-goal-seek-to-find-the-result-you-want-by-adjusting-an-input-value)
7. [rh source, rh/generators/html.py (MeshPropagator.propagate) — i2mint, n.d.](https://github.com/i2mint/rh/blob/master/rh/generators/html.py)
8. [Spiderplots versus Tornado Diagrams for Sensitivity Analysis (Interfaces 22(6):40-46) — Ted G. Eschenbach, 1992](https://doi.org/10.1287/inte.22.6.40)
9. [Introduction to What-If Analysis — Microsoft Support, n.d.](https://support.microsoft.com/en-us/excel/introduction-to-what-if-analysis)
10. [Interactive Decision Maps: Approximation and Visualization of Pareto Frontier — Alexander V. Lotov, Vladimir A. Bushenkov, Georgy K. Kamenev, 2004](https://doi.org/10.1007/978-1-4419-8851-5)
11. [Communicating with Interactive Articles (Distill) — Fred Hohman, Matthew Conlen, Jeffrey Heer, Duen Horng Chau, 2020](https://distill.pub/2020/communicating-with-interactive-articles/)
12. [Authoring and Publishing Interactive Articles (PhD dissertation, University of Washington), ch. 7 — Matthew Conlen, 2021](https://digital.lib.washington.edu/researchworks/items/5d615042-1f87-433e-9f04-1e2554a8bc97/full)
13. [Storytelling in Information Visualizations: Does it Engage Users to Explore Data? (CHI 2015) — Jeremy Boy, Françoise Detienne, Jean-Daniel Fekete, 2015](https://hal-imt.archives-ouvertes.fr/hal-01133595)
14. [The Effects of Interactive Latency on Exploratory Visual Analysis (IEEE TVCG / InfoVis) — Zhicheng Liu, Jeffrey Heer, 2014](https://idl.uw.edu/papers/latency)
15. [Slider Pattern, ARIA Authoring Practices Guide — W3C WAI, n.d.](https://www.w3.org/WAI/ARIA/apg/patterns/slider/)
16. [Understanding SC 2.5.7: Dragging Movements (WCAG 2.2) — W3C WAI, 2023](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements)
17. [Tangle: a JavaScript library for reactive documents — Bret Victor, 2011](https://worrydream.com/Tangle/)
18. [Kill Math — Bret Victor, 2011](https://worrydream.com/KillMath/)
19. [Media for Thinking the Unthinkable — Bret Victor, 2013](https://worrydream.com/MediaForThinkingTheUnthinkable/)
20. [How I Make Explorable Explanations — Nicky Case, 2017](https://blog.ncase.me/how-i-make-an-explorable-explanation/)
21. [Explorable Explanations (hub) — Nicky Case and contributors, n.d.](https://explorabl.es/)
22. [LOOPY: a tool for thinking in systems — Nicky Case, n.d.](https://ncase.me/loopy/)
23. [Idyll: A Markup Language for Authoring and Publishing Interactive Articles on the Web (UIST 2018) — Matt Conlen, Jeffrey Heer, 2018](https://idl.uw.edu/papers/idyll)
24. [Idyll Studio: A Structured Editor for Authoring Interactive & Data-Driven Articles (UIST 2021) — Matt Conlen, Megan Vo, Alan Tan, Jeffrey Heer, 2021](https://idl.uw.edu/papers/idyll-studio)
25. [Capture & Analysis of Active Reading Behaviors for Interactive Articles on the Web (EuroVis 2019) — Matthew Conlen, Alex Kale, Jeffrey Heer, 2019](https://idl.uw.edu/papers/idyll-analytics)
26. [Observable Inputs (notebook documentation) — Observable, n.d.](https://observablehq.com/documentation/inputs/overview)
27. [Observable Plot (repository) — Observable, n.d.](https://github.com/observablehq/plot)
28. [Research Debt (Distill) — Chris Olah, Shan Carter, 2017](https://distill.pub/2017/research-debt/)
29. [About Distill — Distill editors, n.d.](https://distill.pub/about)
30. [Mavo: Creating Interactive Data-Driven Web Applications by Authoring HTML (UIST 2016) — Lea Verou, Amy X. Zhang, David R. Karger, 2016](https://people.csail.mit.edu/karger/Papers/mavo.pdf)
31. [Languages and Systems to Democratize Development of Data-Driven Web Applications (PhD thesis, MIT) — Lea Verou, 2024](https://phd.verou.me/whole/)
32. [Apparatus — Toby Schachman, 2015](http://aprt.us/)
33. [New, Even Better New York Times Buy vs. Rent Calculator — Seattle Bubble, 2014](https://seattlebubble.com/blog/2014/05/23/new-even-better-new-york-times-buy-vs-rent-calculator/)
34. [Is It Better to Rent or Buy? (calculator, current version; paywalled, not fetched) — The New York Times, 2024](https://www.nytimes.com/interactive/2024/upshot/buy-rent-calculator.html)
35. [Seeing Theory: teaching statistics through interactive web-based visualizations — Brown CS Blog, 2018](https://blog.cs.brown.edu/2018/01/22/seeing-theory-teaching-statistics-through-interactive-web-based-visualizations/)
36. [Explained Visually — Setosa, n.d.](https://setosa.io/ev/)
37. [Dynamic Queries for Information Exploration: An Implementation and Evaluation (CHI 1992) — Christopher Ahlberg, Christopher Williamson, Ben Shneiderman, 1992](https://lccd.umiacs.umd.edu/node/17103)
38. [Explaining the Gap: Visualizing One's Predictions Improves Recall and Comprehension of Data (CHI 2017) — Yea-Seul Kim, Katharina Reinecke, Jessica Hullman, 2017](https://idl.uw.edu/papers/explaining-the-gap)
39. [Implicit scaffolding in interactive simulations: Design strategies to support multiple educational goals — Noah S. Podolefsky, Emily B. Moore, Katherine K. Perkins, 2013](https://arxiv.org/abs/1306.6544)
40. [Learning the Concept of Function With Dynamic Visualizations (Frontiers in Psychology 11) — Tobias Rolfes, Jürgen Roth, Wolfgang Schnotz, 2020](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00693/full)
41. [Why Minimal Guidance During Instruction Does Not Work (Educational Psychologist 41(2)) — Paul A. Kirschner, John Sweller, Richard E. Clark, 2006](https://doi.org/10.1207/s15326985ep4102_1)
42. [Direct Manipulation: A Step Beyond Programming Languages (IEEE Computer 16(8)) — Ben Shneiderman, 1983](https://doi.org/10.1109/MC.1983.1654471)
43. [Narrative Visualization: Telling Stories with Data (IEEE InfoVis) — Edward Segel, Jeffrey Heer, 2010](https://idl.uw.edu/papers/narrative)
44. [Toggle-Switch Guidelines — Alita Kendrick, Nielsen Norman Group, 2018](https://www.nngroup.com/articles/toggle-switch-guidelines/)
45. [Hypothetical Outcome Plots Outperform Error Bars and Violin Plots for Inferences about Reliability of Variable Ordering (PLOS ONE) — Jessica Hullman, Paul Resnick, Eytan Adar, 2015](https://doi.org/10.1371/journal.pone.0142444)
46. [Brushing Scatterplots (Technometrics 29(2)) — Richard A. Becker, William S. Cleveland, 1987](https://doi.org/10.1080/00401706.1987.10488204)
47. [Small multiple — Wikipedia, n.d.](https://en.wikipedia.org/wiki/Small_multiple)
48. [Bullet graph — Wikipedia, n.d.](https://en.wikipedia.org/wiki/Bullet_graph)
49. [Understanding SC 1.4.1: Use of Color (WCAG 2.2) — W3C WAI, 2023](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
50. [Display the relationships between formulas and cells — Microsoft Support, n.d.](https://support.microsoft.com/en-us/excel/display-the-relationships-between-formulas-and-cells)
51. [App model summary — Streamlit documentation, n.d.](https://docs.streamlit.io/get-started/fundamentals/summary)
52. [rh: Reactive Html Framework (README) — i2mint, n.d.](https://github.com/i2mint/rh)
53. [dagapp (README) — i2mint, n.d.](https://github.com/i2mint/dagapp)
