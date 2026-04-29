## PR Review: Granular Auto-Approval Rules (like Claude Code)

**Branch:** `feat/granular-auto-approval` → `main`  
**Reviewer:** OpenHand CLI Agent  
**Date:** 2026-04-29

---

### Summary

This PR introduces a well-architected "AFK mode" (away-from-keyboard) that decouples non-interactive execution from the existing YOLO mode. It adds glob-pattern-based auto-approval rules, workspace directory exemptions, and comprehensive test coverage. The change is substantial (100 files, +273/-86) but the intent is clear and the implementation is mostly clean. The main concern is a breaking config rename without migration logic.

---

### Intent Groups

- **Feature Additions**
  - `src/kimi_cli/soul/dynamic_injections/afk_mode.py` — New AFK mode injection provider.
  - `src/kimi_cli/soul/slash.py` — New `/afk` slash command.
  - `src/kimi_cli/config.py` — `default_auto_approve_actions` and `auto_approve_workspace_dirs` config fields.
  - `src/kimi_cli/soul/approval.py` — Glob pattern matching for auto-approved actions.
- **Refactoring**
  - `src/kimi_cli/soul/approval.py` — Split `auto_approve_actions` into exact-set vs. pattern-list for performance.
  - `src/kimi_cli/soul/kimisoul.py` — Replaced `YoloModeInjectionProvider` with `AfkModeInjectionProvider`; added `is_auto_approve`, `is_afk`, `is_subagent` properties.
  - `src/kimi_cli/soul/dynamic_injections/yolo_mode.py` — Removed (functionality merged into AFK mode).
- **Tests**
  - `tests/core/test_approval_runtime.py` — Approval source timeout behavior.
  - `tests/core/test_afk_injection.py` — AFK prompt injection coverage.
  - `tests/core/test_slash_afk.py` — `/afk` and `/yolo` slash command tests.
  - `tests/core/test_config.py` — Config validation for new fields.
- **Chores / Dependencies**
  - `pyproject.toml`, `uv.lock` — Dependency bumps.
  - `docs/en/*`, `docs/zh/*` — Documentation updates for new config options.

---

### Detailed Feedback

#### 🔴 Critical

1. **`src/kimi_cli/config.py` (L199-L206)**  
   The rename of `skip_yolo_prompt_injection` → `skip_afk_prompt_injection` is a breaking change for existing user configs. Users with the old key in their `config.toml` will encounter a Pydantic validation error on next startup.  
   **Recommendation:** Add an alias or migration step. Pydantic's `AliasChoices` can handle this gracefully:
   ```python
   skip_afk_prompt_injection: bool = Field(
       default=False,
       validation_alias=AliasChoices("skip_afk_prompt_injection", "skip_yolo_prompt_injection"),
       ...
   )
   ```

#### 🟡 Warning

1. **`src/kimi_cli/soul/approval.py` (L117-L120)**  
   `is_yolo_flag()` is redundant with `is_yolo()`. Both return the exact same value. This adds surface area without benefit.  
   **Recommendation:** Remove `is_yolo_flag()` and use `is_yolo()` everywhere. If the intent was to distinguish from `is_auto_approve()`, rename it to something explicit like `is_explicit_yolo()`.

2. **`src/kimi_cli/soul/kimisoul.py` (L354-L359)**  
   `ExitPlanMode` is now bound to `self._approval.is_afk` instead of `self._approval.is_yolo`. This changes behavior for users who previously used YOLO without AFK. Verify this is intentional — plan mode exit previously required explicit yolo, now any afk state suffices.

3. **`src/kimi_cli/soul/dynamic_injections/afk_mode.py` (L54-L58)**  
   The provider only injects when `soul.is_afk_flag` is True, ignoring `runtime_afk`. This means `--afk` (invocation-only) may not receive the system prompt reminder on the first turn.  
   **Recommendation:** Consider injecting for both `is_afk_flag` and `is_runtime_afk`, or document why runtime-afk is intentionally excluded.

#### ⚪ Info

1. **`src/kimi_cli/soul/approval.py` (L75-L82)**  
   Nice optimization separating exact matches from glob patterns. The `_GLOB_SPECIAL_RE` pre-check avoids `fnmatch` overhead for the common case.

2. **`src/kimi_cli/soul/slash.py` (L122-L142)**  
   The UX copy for `/afk` toggle is clear and informative. The conditional messaging based on yolo/afk overlap state is a good touch.

3. **`tests/core/test_approval_runtime.py`**  
   Good parametrization over `foreground_turn` and `background_agent` approval sources. The indefinite wait test is a valuable regression guard.

4. **`src/kimi_cli/config.py` (L295-L375)**  
   The new `_DEFAULT_CONFIG_TEMPLATE` with inline comments and examples is excellent for onboarding. Consider adding a comment header with the config file URL for discoverability.

---

### Action Items

- [ ] Add `validation_alias` or migration logic for `skip_yolo_prompt_injection` → `skip_afk_prompt_injection`.
- [ ] Remove or rename redundant `is_yolo_flag()` method.
- [ ] Confirm `ExitPlanMode` binding change from `is_yolo` to `is_afk` is intentional.
- [ ] Evaluate whether `runtime_afk` should trigger the AFK system prompt injection.
