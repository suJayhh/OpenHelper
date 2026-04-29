# Multilingual Documentation Generator

This skill is invoked when the user requests documentation updates inside the OpenHand Control Center.

## Instruction Chain

1. Read `AGENTS.md` in the repo root for Control Center rules.
2. Read `core/prompts/multilingual-docs.md` for the documentation protocol.
3. Read `core/templates/doc-section-en-zh.md` for the default section format.
4. Execute the AskUserQuestion flow to establish the target repo, doc scope, and write mode.
5. Inspect existing docs in the target repo for bilingual conventions.
6. Produce or update documentation in parallel EN/ZH blocks.
7. Preview or write directly based on user preference.

## Overrides

- Always verify that EN and ZH versions convey identical technical meaning.
- Preserve the repo's existing bilingual pattern if one exists.
