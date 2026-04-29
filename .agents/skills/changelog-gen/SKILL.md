# Changelog Generator

This skill is invoked when the user requests changelog updates inside the OpenHand Control Center.

## Instruction Chain

1. Read `AGENTS.md` in the repo root for Control Center rules.
2. Read `core/prompts/changelog-generator.md` for the changelog protocol.
3. Execute the AskUserQuestion flow to establish the target repo, version range, output mode, and bilingual preference.
4. Collect git history with `git -C <TARGET_PATH> log` and `git -C <TARGET_PATH> diff`.
5. Categorize commits and produce the formatted entry.
6. Append to `CHANGELOG.md` or output standalone based on user preference.

## Overrides

- Breaking changes must appear first in the entry.
- Issue/PR references should use `#N` format and link correctly.
