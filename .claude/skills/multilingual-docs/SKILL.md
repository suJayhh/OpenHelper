# Multilingual Documentation Generator

When the user asks to write or update documentation, perform the following steps:

1. Ask the user for the target repository path: "What is the absolute path to the target repository you want me to work on?"
2. Ask which documentation needs updating (README, CONTRIBUTING, API docs, inline comments, or all).
3. Ask whether to write directly or preview first.
4. Load the instructions from `core/prompts/multilingual-docs.md` and follow them exactly.
5. Use `core/templates/doc-section-en-zh.md` as the default section format.
6. Inspect existing docs in the target repo to understand the current bilingual pattern.
7. Produce documentation in parallel EN/ZH blocks unless the repo already uses a different pattern.
