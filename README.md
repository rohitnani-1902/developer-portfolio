# Chitirala Rohit — Developer Portfolio

A responsive static portfolio connecting nine AI and educational market-simulation projects.

## Live portfolio

[Open the portfolio](https://rohit-developer-portfolio.vercel.app/) — hosted on Vercel, with automatic deployment from `main`.

## Run it

Open `index.html` in a modern browser. Case studies use relative links and work locally or on a static host. No dependencies, API keys, or build step are required. Open a featured case study and choose **Open live demo**, or open a local `demos/*.html` file. Other projects can be run by downloading their linked repositories.

## Featured case studies

| Project | Technical focus | Case study |
| --- | --- | --- |
| Sift AI — RAG Document Intelligence | Local ingestion, passage ranking, extractive answers with evidence | [Read](case-studies/sift-ai.html) |
| VectorTest — Quant Backtesting Engine | Seeded price generation, moving averages, equity and drawdown calculations | [Read](case-studies/vectortest.html) |
| Paperfolio — Paper Trading Dashboard | Order validation, account state, weighted cost and journaling | [Read](case-studies/paperfolio.html) |

Each page includes a problem statement, architecture, repeatable demo steps, implementation outcomes, current limits, and direct links to source, setup documentation, and a source ZIP.

These three were selected after comparing the READMEs and implementations of all nine linked projects: they show the clearest multi-stage computation or state transitions. Outcomes describe implemented behavior; no user-impact, model-quality, or real-market performance claims are implied. VectorTest now uses distinct strategies and consistent fee-adjusted metrics; its remaining execution assumptions are documented explicitly.

## All projects

- [RAG Document Intelligence](https://github.com/rohitnani-1902/rag-document-intelligence)
- [Matchwise — AI Resume Matcher](https://github.com/rohitnani-1902/ai-resume-matcher)
- [VibeLens — Multilingual Sentiment Analyzer](https://github.com/rohitnani-1902/multilingual-sentiment-analyzer)
- [SignalDeck — Market News Sentiment Radar](https://github.com/rohitnani-1902/market-news-sentiment-radar)
- [ThesisFrame — AI Stock Research Assistant](https://github.com/rohitnani-1902/ai-stock-research-assistant)
- [RuleCraft — Trading Strategy Copilot](https://github.com/rohitnani-1902/trading-strategy-copilot)
- [VectorTest — Quant Backtesting Engine](https://github.com/rohitnani-1902/quant-backtesting-engine)
- [Paperfolio — Paper Trading Dashboard](https://github.com/rohitnani-1902/paper-trading-dashboard)
- [RiskCanvas — Portfolio Risk Analytics](https://github.com/rohitnani-1902/portfolio-risk-analytics)

## Structure and maintenance

- `index.html`: original responsive nine-card hub, AI / Markets / Systems filters, and focus section.
- `case-studies/*.html`: standalone static case studies using the hub's existing colors, typography, and responsive styling.
- `demos/*.html`: runnable copies of the three featured projects; Sift escapes imported text and filenames before HTML display.
- Each selected card retains its direct repository link alongside the case-study link.
- Update case-study evidence and review dates when a linked implementation changes. Keep future extensions separate from current capabilities.
- All market projects use fictional or generated data and are educational prototypes.

## Validation

Check all four filters, open every case study from its card, follow the return link, and verify relative links when serving from a subdirectory. Compare documented demo steps with the linked source. The case-study pages require no JavaScript.

Vanilla HTML, CSS, and JavaScript. Part of [Rohit's GitHub profile](https://github.com/rohitnani-1902).


## Atlas AI Studio

Three new workspaces: [Research Desk](https://rohit-developer-portfolio.vercel.app/projects/atlas-ai/#research), [Code Lens](https://rohit-developer-portfolio.vercel.app/projects/atlas-ai/#code), and [Ops Flow](https://rohit-developer-portfolio.vercel.app/projects/atlas-ai/#ops). Public previews provide backend-powered local analysis, browser-saved results and Markdown exports. Model generation is integrated but requires provider credit and a privately configured backend; successful real-model generation is not yet verified.

See [architecture, setup and limitations](atlas-ai/README.md). Fourteen backend checks and browser verification cover the three example workflows. Run tests with `python -m unittest discover -s atlas-ai/tests -p "test_*.py" -v`.
