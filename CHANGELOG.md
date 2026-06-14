# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-06-14

First public release.

### Changed
- **Renamed `fable-mode` → `modelharness`** (model-agnostic brand). Command
  namespaces are now `/modelharness:goal|verify|retro`; the behavioral core lives
  at `core/modelharness-core.md`. This is a breaking change for anyone who used
  the pre-release command names.
- Rebuilt the README around the benchmark story: shields badges, an SVG hero
  chart generated from the frozen CSV, and a paired per-model results table.

### Added
- `bench/stats.py` — paired per-task analysis with 95% confidence intervals,
  reporting which deltas are statistically significant vs within run-to-run
  noise. The Opus 4.8 cost (−12.0%) and time (−16.5%) wins clear zero; Fable 5
  gets a significant speed-up; Sonnet 4.6 and Haiku 4.5 land within noise and
  are never significantly worse.
- `bench/chart.py` — regenerates the hero chart SVG from the results CSV.
- `bench/GRADING.md` — self-contained record of the two grader corrections made
  during capture, each with diff and rationale.
- `docs/dev/publish-checklist.md` — release-time checklist.

### Fixed
- Removed leaked local filesystem paths from tracked files; internal planning
  artifacts (`docs/superpowers/`) are no longer part of the published repo.

## [0.2.1] — 2026-06-12

### Added
- `fable-plugin` configuration, completing the harness-universality matrix:
  8 configurations × 17 tasks × 3 reps = **408 runs**. Confirms the harness
  helps (or does not hurt) every one of the four Claude models tested.

## [0.2.0] — 2026-06-12

### Added
- Sonnet 4.6 and Haiku 4.5 model configurations and dynamic report columns,
  expanding the comparison from one model to four.

### Fixed
- Regraded affected reps after the two grader corrections (see `bench/GRADING.md`).

## [0.1.0] — 2026-06-11

Initial benchmark capture.

### Added
- Zero-config Claude Code plugin: SessionStart hook injecting a ≈910-token
  behavioral core, three on-demand skills, a fresh-context verifier agent, and
  three optional commands.
- Benchmark harness (`bench/`): 17 agentic-coding tasks across six categories
  (bugfix, feature, refactor, long-horizon, hard, continuity), hidden binary
  grading, reference solutions, and a reproducible runner.

[0.3.0]: https://github.com/vitaliikapliuk/modelharness/releases/tag/v0.3.0
[0.2.1]: https://github.com/vitaliikapliuk/modelharness/releases/tag/v0.2.1
[0.2.0]: https://github.com/vitaliikapliuk/modelharness/releases/tag/v0.2.0
[0.1.0]: https://github.com/vitaliikapliuk/modelharness/releases/tag/v0.1.0
