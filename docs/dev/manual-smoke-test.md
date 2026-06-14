# Manual smoke test — run before every release

1. In Claude Code: `/plugin marketplace add <path-to-local-clone>`
   then `/plugin install modelharness@modelharness`. Restart Claude Code.
2. Open a NEW session in any project. Without typing anything fable-related, ask:
   "What behavioral rules are you operating under in this session?"
   EXPECTED: the answer references modelharness patterns (grounded progress, etc.) —
   proves the SessionStart hook injected the core with zero user action.
3. Ask for a deliberately vague large task ("make this project better").
   EXPECTED: Claude starts a spec interview (goal/constraints/definition of done)
   instead of immediately editing files — proves auto task-intake.
4. Give a small multi-step coding task in a scratch repo.
   EXPECTED: Claude states a definition of done up front and runs real checks
   during the work — proves self-verification triggering.
5. Run `/modelharness:verify` after the task. EXPECTED: verifier subagent dispatched,
   structured verdict returned.
6. With the superpowers plugin also enabled, repeat step 2.
   EXPECTED: both plugins' contexts present, no errors at session start.
Record results in the release PR description.
