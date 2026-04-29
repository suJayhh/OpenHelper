#!/usr/bin/env python3
"""
validate-skills.py

Validates all SKILL.md files across CLI adapter directories.
Checks:
- YAML frontmatter with 'name' and 'description' fields
- No duplicate skill names
- Referenced core prompts exist
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SKILL_GLOBS = [
    ".kimi/skills/*",
    ".claude/skills/*",
    ".gemini/skills/*",
    ".agents/skills/*",
]
CORE_PROMPTS = PROJECT_ROOT / "core" / "prompts"


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    result = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            result[key.strip()] = val.strip()
    return result


def validate_skill_file(path: Path) -> list[str]:
    """Validate a single SKILL.md file. Returns list of errors."""
    errors = []
    content = path.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)

    if fm is None:
        errors.append(f"Missing or malformed YAML frontmatter")
        return errors

    if "name" not in fm:
        errors.append("Missing 'name' in frontmatter")
    if "description" not in fm:
        errors.append("Missing 'description' in frontmatter")

    # Check for core prompt references
    for match in re.finditer(r"core/prompts/([\w\-]+\.md)", content):
        prompt_name = match.group(1)
        prompt_path = CORE_PROMPTS / prompt_name
        if not prompt_path.exists():
            errors.append(f"Referenced core prompt not found: core/prompts/{prompt_name}")

    return errors


def main() -> int:
    all_errors = []
    names_seen = {}

    for glob_pattern in SKILL_GLOBS:
        for skill_dir in PROJECT_ROOT.glob(glob_pattern):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            rel_path = skill_file.relative_to(PROJECT_ROOT)
            errors = validate_skill_file(skill_file)

            # Check for duplicate names
            content = skill_file.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            if fm and "name" in fm:
                name = fm["name"]
                # Check for duplicates within the same CLI adapter only
                adapter = str(rel_path).split("/")[0]
                adapter_names = names_seen.setdefault(adapter, {})
                if name in adapter_names:
                    errors.append(
                        f"Duplicate skill name '{name}' within {adapter} (also in {adapter_names[name]})"
                    )
                else:
                    adapter_names[name] = rel_path

            if errors:
                all_errors.append((rel_path, errors))

    if all_errors:
        print("Validation failed!")
        for rel_path, errors in all_errors:
            print(f"\n{rel_path}")
            for err in errors:
                print(f"  - {err}")
        return 1
    else:
        print(f"All skills valid. Checked {len(names_seen)} skill(s).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
