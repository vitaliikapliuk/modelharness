# Publish checklist (run at GitHub release time)

1. Create GitHub repo `modelharness` under `vitaliikapliuk`; push branch; default branch = the release branch.
2. About line: "Make every model cheaper or better. Zero-config behavioral harness for Claude Code, with a reproducible 408-run benchmark."
3. Topics: claude-code, claude-code-plugin, benchmark, llm-harness, agent-harness, opus, sonnet, haiku, fable.
4. Confirm the README install block points at the real account (`vitaliikapliuk/modelharness` — already filled).
5. Social preview: screenshot the rendered README first screen (or the v22 mockup) to `assets/social-preview.png`, upload in Settings → Social preview.
6. Run `docs/dev/manual-smoke-test.md` (all 6 checks — note names: `/modelharness:verify`, install `modelharness@modelharness`).
7. Tag `v0.3.0` (rename = breaking change for command namespaces); release notes: the 408-run table + harness-lift summary.
8. Launch posts (r/ClaudeAI, X) — lead with the paired chart image.
9. Stretch (later): GitHub Pages interactive leaderboard from results-v*.csv.
