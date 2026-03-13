#!/usr/bin/env python3
"""
Migrate markdown files in a directory in-place with syntax transformations
(MkDocs → remark/MDX directives).

Usage:
    python docs/migrate.py path/to/source
"""

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent  # docs/
MKDOCS_YML = SCRIPT_DIR / "mkdocs.yml"  # docs/mkdocs.yml

# Language identifier renames applied to all fence opening lines.
LANG_ALIASES: dict[str, str] = {
    "shellSession": "console",
}


# ---------------------------------------------------------------------------
# Nav title lookup
# ---------------------------------------------------------------------------


def parse_nav_titles(mkdocs_yml: Path) -> dict:
    """
    Scan the nav: section of mkdocs.yml for entries of the form
        - Some Title: path/to/file.md
    and return a dict mapping Path("path/to/file.md") → "Some Title".
    Bare path entries (no explicit title) are ignored.
    """
    nav_re = re.compile(r"^\s*-\s+(.+?):\s+(\S+\.md)\s*$")
    titles: dict = {}
    try:
        text = mkdocs_yml.read_text(encoding="utf-8")
    except FileNotFoundError:
        return titles

    in_nav = False
    for line in text.splitlines():
        if re.match(r"^nav:\s*$", line):
            in_nav = True
            continue
        if in_nav:
            # A non-indented, non-blank, non-list line signals the end of nav:
            if line and line[0] not in (" ", "\t", "-") and line.strip():
                in_nav = False
                continue
            m = nav_re.match(line)
            if m:
                titles[Path(m.group(2).strip())] = m.group(1).strip()
    return titles


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def title_from_filename(stem: str) -> str:
    """Generate a title from a filename stem (dashes→spaces, title-case)."""
    return stem.replace("-", " ").replace("_", " ").title()


def get_frontmatter_end(lines: list[str]) -> int:
    """Return the line index *after* the closing --- of YAML frontmatter, or 0."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def has_h1(lines: list[str]) -> bool:
    """Check whether the file contains at least one level-1 heading (not inside a code block)."""
    in_code = False
    open_char = "`"
    open_len = 3
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")

    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
        elif not in_code:
            if re.match(r"^# ", line) or line.rstrip() == "#":
                return True
    return False


# ---------------------------------------------------------------------------
# Step 2: fix missing spaces in headings (e.g. `#Text` → `# Text`)
# ---------------------------------------------------------------------------


def fix_heading_spaces(lines: list[str]) -> list[str]:
    result = []
    in_code = False
    open_char = "`"
    open_len = 3
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")

    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
            result.append(line)
        elif not in_code:
            m = re.match(r"^(#{1,6})([^#\s])(.*)", line)
            if m:
                line = m.group(1) + " " + m.group(2) + m.group(3) + "\n"
            result.append(line)
        else:
            result.append(line)
    return result


# ---------------------------------------------------------------------------
# Step 3: transform code-fence syntax-highlighting attributes
# ---------------------------------------------------------------------------


def _transform_fence_line(line: str) -> str:
    """
    Convert:
      ```{.nix title="foo.nix" hl_lines="2 3-7"}  →  ```nix [foo.nix] {2,3-7}
      ```nix title="foo.nix" hl_lines="2 3-7"     →  ```nix [foo.nix] {2,3-7}
      ```nix {hl_lines="2 4-6"}                   →  ```nix {2,4-6}
      ```hl_lines="2"                              →  ```text {2}
      ```{.console, .no-copy}                      →  ```console
      ```{ .bash .annotate .no-copy .nohighlight}  →  ```bash
      ```{.no-copy}                                →  ```
    """
    m = re.match(r"^(\s*(?:`{3,}|~{3,}))(.*?)$", line.rstrip())
    if not m:
        return line
    backticks = m.group(1)
    rest = m.group(2).strip()

    has_hl = "hl_lines" in rest
    has_title = "title=" in rest
    # Detect class-only brace notation: {.class1 .class2 ...}
    # (no = assignments, no quoted values → just CSS-style class names)
    is_class_brace = rest.startswith("{") and "=" not in rest and '"' not in rest
    if not has_hl and not has_title and not is_class_brace:
        return line  # nothing to transform

    # Extract title
    title = None
    tm = re.search(r'\btitle="([^"]*)"', rest)
    if tm:
        title = tm.group(1)

    # Extract hl_lines, convert spaces to commas
    hl_lines = None
    hm = re.search(r'\bhl_lines="([^"]*)"', rest)
    if hm:
        hl_lines = re.sub(r"\s+", ",", hm.group(1).strip())

    # Extract language.
    # First, blank out quoted values so we don't accidentally harvest words
    # from paths inside title="~/.config/..." etc.
    rest_no_quotes = re.sub(r'"[^"]*"', '""', rest)

    # Prefer .lang notation (class-style), skipping non-language classes
    lang = None
    skip_classes = {"no", "annotate", "copy", "nohighlight"}
    for dl in re.findall(r"\.([a-zA-Z][a-zA-Z0-9_]*)", rest_no_quotes):
        if dl not in skip_classes:
            lang = dl
            break

    # Fall back to bare language word at the start (before any space, {, or =)
    if lang is None:
        bm = re.match(r"^([a-zA-Z][a-zA-Z0-9_]*)\b", rest)
        if bm and bm.group(1) not in ("title", "hl_lines"):
            lang = bm.group(1)

    # If still no language but we have hl_lines or title, default to "text".
    # A meta string must not appear without a language identifier.
    # For class-only patterns with no recognizable language, keep bare fence.
    if lang is None and (has_hl or has_title):
        lang = "text"

    # Apply language aliases
    if lang is not None:
        lang = LANG_ALIASES.get(lang, lang)

    # Build new fence suffix
    parts: list[str] = []
    if lang:
        parts.append(lang)
    if title:
        parts.append(f"[{title}]")
    if hl_lines:
        parts.append(f"{{{hl_lines}}}")

    new_rest = " ".join(parts)
    return backticks + new_rest + "\n"


def rename_fence_langs(lines: list[str]) -> list[str]:
    """
    On fence opening lines: apply LANG_ALIASES renames and remove any
    stray space between the fence characters and the language identifier.
    E.g. ``` nix → ```nix,  ```shellSession → ```console.
    """
    # Allow optional whitespace between fence chars and lang
    open_re = re.compile(r"^(\s*(?:`{3,}|~{3,}))\s*([a-zA-Z][a-zA-Z0-9_]*)(.*)$")
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    in_code = False
    open_char = "`"
    open_len = 3
    result: list[str] = []
    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
                m = open_re.match(line.rstrip())
                if m:
                    new_lang = LANG_ALIASES.get(m.group(2), m.group(2))
                    line = m.group(1) + new_lang + m.group(3) + "\n"
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
        result.append(line)
    return result


def transform_embeds(lines: list[str]) -> list[str]:
    """
    Convert code blocks whose only content is an --8<-- snippet include:
        ```nix [foo.nix] {2}
          --8<-- "docs/code-examples/bar.nix"
        ```
    into:
        ```nix [foo.nix] {2} embed=bar.nix
        ```
    The docs/code-examples/ prefix is stripped from the path.
    If the resulting path contains a space, it is quoted: embed="the path".
    """
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    embed_re = re.compile(r'^\s*--8<--\s+"([^"]+)"\s*$')

    result: list[str] = []
    in_code = False
    open_char = "`"
    open_len = 3
    open_line_idx = -1
    content_lines: list[str] = []

    for line in lines:
        fm = fence_re.match(line)

        if fm and not in_code:
            # Opening fence
            fence_str = fm.group(2)
            in_code = True
            open_char = fence_str[0]
            open_len = len(fence_str)
            open_line_idx = len(result)
            content_lines = []
            result.append(line)
            continue

        if in_code:
            stripped = line.strip()
            is_closer = (
                fm
                and stripped
                and all(c == open_char for c in stripped)
                and len(stripped) >= open_len
            )
            if is_closer:
                in_code = False
                non_blank = [cl for cl in content_lines if cl.strip()]
                if len(non_blank) == 1:
                    em = embed_re.match(non_blank[0])
                    if em:
                        path = em.group(1)
                        # Strip docs/code-examples/ prefix
                        path = re.sub(r"^docs/code-examples/", "", path)
                        # Append embed= to opening fence line
                        opening = result[open_line_idx].rstrip("\n")
                        if " " in path:
                            opening += f' embed="{path}"'
                        else:
                            opening += f" embed={path}"
                        result[open_line_idx] = opening + "\n"
                        # Closing fence only – content removed
                        result.append(line)
                        continue
                # Not an embed block – flush collected content
                result.extend(content_lines)
                result.append(line)
            else:
                content_lines.append(line)
            continue

        # Outside code block
        result.append(line)

    # Unclosed code block – flush remaining content
    if in_code:
        result.extend(content_lines)

    return result


def transform_code_fences(lines: list[str]) -> list[str]:
    """Transform opening fence lines; leave content and closing fences untouched."""
    result: list[str] = []
    in_code = False
    open_char = "`"
    open_len = 3
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")

    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
                result.append(_transform_fence_line(line))
            else:
                # Closing fence: only fence chars, at least as many as opening
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
                result.append(line)
        else:
            result.append(line)

    return result


# ---------------------------------------------------------------------------
# Step 4: transform admonition blocks (??? and !!!)
# ---------------------------------------------------------------------------


def transform_admonitions(lines: list[str]) -> list[str]:
    """
    Convert:
      ??? info "Title"       →  :::admonition[Title]{type=info collapsible}
      ???+ info "Title"      →  :::admonition[Title]{type=info collapsible open}
      !!! info "Title"       →  :::admonition[Title]{type=info}
      ??? tip                →  :::admonition[Tip]{type=tip collapsible}
    Block content (indented 4 spaces relative to marker) is de-indented.
    Block closes with :::.
    """
    result: list[str] = []
    i = 0
    admon_re = re.compile(r'^(\s*)(\?\?\?\+|\?\?\?|!!!)\s*(\w+)(?:\s+"([^"]*)")?\s*$')

    while i < len(lines):
        line = lines[i]
        m = admon_re.match(line.rstrip())
        if m:
            indent = m.group(1)  # leading whitespace of the marker
            marker = m.group(2)  # ???, ???+, or !!!
            admon_type = m.group(3).lower()
            admon_title = m.group(4)  # None if no quoted title

            # Derive title
            if admon_title is None:
                admon_title = m.group(3).capitalize()
            else:
                # Strip markdown bold markers from title
                admon_title = re.sub(r"\*+", "", admon_title)

            if marker == "???":
                collapsible = " collapsible"
            elif marker == "???+":
                collapsible = " collapsible open"
            else:
                collapsible = ""
            result.append(
                f"{indent}:::admonition[{admon_title}]"
                f"{{type={admon_type}{collapsible}}}\n"
            )
            i += 1

            # Determine actual content indentation from the first non-blank line
            content_indent = indent + "    "  # default: 4 extra spaces
            for j in range(i, min(i + 10, len(lines))):
                if lines[j].strip():
                    raw = lines[j]
                    n = len(raw) - len(raw.lstrip())
                    if n > len(indent):
                        content_indent = raw[:n]
                    break

            # Collect indented content lines
            while i < len(lines):
                cl = lines[i]
                if cl.strip() == "":
                    # Blank line: include only if more indented content follows
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == "":
                        j += 1
                    if j < len(lines) and lines[j].startswith(content_indent):
                        result.append("\n")
                        i += 1
                    else:
                        break
                elif cl.startswith(content_indent):
                    # De-indent by exactly content_indent, keep marker indent
                    result.append(indent + cl[len(content_indent) :])
                    i += 1
                else:
                    break

            result.append(f"{indent}:::\n")
        else:
            result.append(line)
            i += 1

    return result


# ---------------------------------------------------------------------------
# Step 5: transform tab blocks (=== "Name")
# ---------------------------------------------------------------------------


def transform_tabs(lines: list[str]) -> list[str]:
    """
    Convert:
      === "Tab A"
          content A
      === "Tab B"
          content B
    to:
      ::::tabs
      :::tab[Tab A]
      content A
      :::
      :::tab[Tab B]
      content B
      :::
      ::::
    Handles arbitrary indentation levels for nested usage.
    """
    result: list[str] = []
    i = 0
    tab_re = re.compile(r'^(\s*)=== "(.*?)"')

    while i < len(lines):
        line = lines[i]
        m = tab_re.match(line.rstrip())
        if m:
            indent = m.group(1)
            content_indent = indent + "    "
            tab_re_exact = re.compile(r"^" + re.escape(indent) + r'=== "(.*?)"')

            result.append(f"{indent}::::tabs\n")

            while i < len(lines):
                tm = tab_re_exact.match(lines[i].rstrip())
                if not tm:
                    break
                tab_name = tm.group(1)
                # Strip bold markers (**text** → text)
                tab_name = re.sub(r"\*+", "", tab_name)
                result.append(f"{indent}:::tab[{tab_name}]\n")
                i += 1

                # Collect tab content lines
                while i < len(lines):
                    cl = lines[i]
                    if cl.strip() == "":
                        # Include blank only if more content (not next tab) follows
                        j = i + 1
                        while j < len(lines) and lines[j].strip() == "":
                            j += 1
                        if j < len(lines) and lines[j].startswith(content_indent):
                            result.append("\n")
                            i += 1
                        else:
                            break
                    elif cl.startswith(content_indent):
                        result.append(indent + cl[len(content_indent) :])
                        i += 1
                    else:
                        break

                result.append(f"{indent}:::\n")

                # Skip blank lines between tabs
                while i < len(lines) and lines[i].strip() == "":
                    i += 1

            result.append(f"{indent}::::\n")
        else:
            result.append(line)
            i += 1

    return result


# ---------------------------------------------------------------------------
# Step 5b: fix directive colon counts for nesting
# ---------------------------------------------------------------------------


def fix_directive_colons(lines: list[str]) -> list[str]:
    """
    Adjust colon counts so each containing directive uses exactly one more
    colon than its deepest direct child directive.  Leaf directives use 3.

    Example:  :::admonition wrapping ::::tabs wrapping :::tab
    becomes:  :::::admonition wrapping ::::tabs wrapping :::tab
    """
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    open_re = re.compile(r"^(\s*)(:{3,})(\w)")  # :::word  – opener
    close_re = re.compile(r"^(\s*)(:{3,})\s*$")  # :::     – closer

    # — Phase 1: parse directive tree (skip code blocks) —
    in_code = False
    open_char = "`"
    open_len = 3
    stack: list[dict] = []
    roots: list[dict] = []

    for i, line in enumerate(lines):
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
            continue
        if in_code:
            continue

        om = open_re.match(line.rstrip())
        cm = close_re.match(line.rstrip())

        if om and not cm:
            stack.append({"open": i, "close": None, "children": []})
        elif cm:
            if stack:
                node = stack.pop()
                node["close"] = i
                if stack:
                    stack[-1]["children"].append(node)
                else:
                    roots.append(node)

    # — Phase 2: compute colon counts bottom-up —
    def compute(node: dict) -> int:
        if not node["children"]:
            node["colons"] = 3
        else:
            child_max = max(compute(c) for c in node["children"])
            node["colons"] = child_max + 1
        return node["colons"]

    for r in roots:
        compute(r)

    # — Phase 3: collect line → new colon count —
    adjustments: dict[int, int] = {}

    def collect(node: dict) -> None:
        adjustments[node["open"]] = node["colons"]
        if node["close"] is not None:
            adjustments[node["close"]] = node["colons"]
        for c in node["children"]:
            collect(c)

    for r in roots:
        collect(r)

    # — Phase 4: rewrite —
    result: list[str] = []
    for i, line in enumerate(lines):
        if i in adjustments:
            new_n = adjustments[i]
            om = open_re.match(line.rstrip())
            cm = close_re.match(line.rstrip())
            if om and not cm:
                indent = om.group(1)
                rest_after_colons = line.rstrip()[len(indent) + len(om.group(2)) :]
                line = indent + ":" * new_n + rest_after_colons + "\n"
            elif cm:
                indent = cm.group(1)
                line = indent + ":" * new_n + "\n"
        result.append(line)

    return result


# ---------------------------------------------------------------------------
# Step 6: remove duplicate h1 headings
# ---------------------------------------------------------------------------


def remove_duplicate_h1(lines: list[str]) -> list[str]:
    """Keep only the first h1 heading; remove all subsequent ones.
    Skips lines inside code fences."""
    found_first = False
    in_code = False
    open_char = "`"
    open_len = 3
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    result: list[str] = []
    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
            result.append(line)
            continue
        if not in_code:
            m = re.match(r"^# (.+)", line.rstrip())
            if m:
                if found_first:
                    continue
                found_first = True
        result.append(line)
    return result


# ---------------------------------------------------------------------------
# Step 7: transform relative .md links to absolute /docs/ paths
# ---------------------------------------------------------------------------


def _resolve_link(base_dir: Path, current_file: Path, rel_link: str) -> str:
    """Resolve a relative .md link to an absolute /docs/… path."""
    # Split off any anchor fragment
    anchor = ""
    base = rel_link
    if "#" in rel_link:
        base, fragment = rel_link.split("#", 1)
        anchor = "#" + fragment

    if not base.endswith(".md"):
        return rel_link

    # Resolve relative to the file's directory inside base_dir
    current_dir = current_file.parent
    resolved = (base_dir / current_dir / base).resolve()
    source_abs = base_dir.resolve()

    try:
        rel = resolved.relative_to(source_abs)
    except ValueError:
        # Can't resolve to /docs/ path, but still strip .md
        return re.sub(r"\.md(#|$)", r"\1", rel_link)

    without_md = rel.with_suffix("")
    # foo/index → foo
    if without_md.name == "index":
        without_md = without_md.parent
    # Ensure forward slashes (important on Windows, harmless on Unix)
    path_str = "/".join(without_md.parts)
    return f"/docs/{path_str}{anchor}"


def transform_links(lines: list[str], base_dir: Path, current_file: Path) -> list[str]:
    """Replace relative .md links with absolute /docs/ paths.
    Skips lines inside code fences.
    Handles multi-line links where [text\\n...](url.md) spans lines."""
    # Match ](url) — the URL part is always on one line, even for multi-line links
    url_re = re.compile(r"\]\(([^)]+\.md(?:#[^)]*)?)\)")
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    in_code = False
    open_char = "`"
    open_len = 3
    result: list[str] = []

    def replace(m: re.Match) -> str:
        link = m.group(1)
        # Skip absolute and external links
        if link.startswith(("http://", "https://", "/", "mailto:")):
            return m.group(0)
        new_link = _resolve_link(base_dir, current_file, link)
        return f"]({new_link})"

    for line in lines:
        fm = fence_re.match(line)
        if fm:
            fence_str = fm.group(2)
            if not in_code:
                in_code = True
                open_char = fence_str[0]
                open_len = len(fence_str)
            else:
                stripped = line.strip()
                if (
                    stripped
                    and all(c == open_char for c in stripped)
                    and len(stripped) >= open_len
                ):
                    in_code = False
            result.append(line)
        elif in_code:
            result.append(line)
        else:
            new_line = url_re.sub(replace, line)
            # clan_inventory.md: MkDocs uses #tags_1 for the duplicate "tags" heading
            if current_file == Path("reference/options/clan_inventory.md"):
                new_line = new_line.replace("#tags_1)", "#tags)")
            result.append(new_line)

    return result


# ---------------------------------------------------------------------------
# Step 8: strip indentation from code fences not inside a list item
# ---------------------------------------------------------------------------


def strip_non_list_fence_indent(lines: list[str]) -> list[str]:
    """
    After all block transformations, code fences that ended up indented because
    they were inside a ::: container (admonition/tab) should NOT be indented
    unless they genuinely sit inside a list item in that container's scope.

    Strategy:
    - Maintain a stack of list-context frames, one per ::: block level.
    - Each frame records the content-indents of currently-active list items
      within that block level.
    - Opening ::: directives push a fresh (empty) frame; closing ::: pop one.
    - A list marker updates the innermost frame.
    - A non-blank, non-list line at indent N trims the innermost frame of
      entries whose content_indent > N (those list items are closed).
    - A code fence at indent M with no active list item satisfying
      content_indent ≤ M is stripped: M leading spaces are removed from the
      opening fence, every content line, and the matching closing fence.
    """
    fence_re = re.compile(r"^(\s*)(`{3,}|~{3,})")
    list_re = re.compile(r"^(\s*)([-*+]|\d+[.)]) ")
    open_dir_re = re.compile(r"^(\s*):{3,}\w")  # :::word  – opening directive
    close_dir_re = re.compile(r"^(\s*):{3,}\s*$")  # ::: or :::: alone – closer

    in_code = False
    open_char = "`"
    open_len = 3
    strip_indent = 0  # > 0 means current block is being stripped by this many cols

    # Stack of list-context frames (list of active content_indent values).
    # The bottom frame is the file-level context.
    contexts: list[list[int]] = [[]]

    result: list[str] = []

    for line in lines:
        fm = fence_re.match(line)

        if fm and not in_code:
            # ── Opening code fence ──────────────────────────────────────────
            fence_str = fm.group(2)
            open_char = fence_str[0]
            open_len = len(fence_str)
            fence_indent = len(fm.group(1))
            in_code = True

            current_lists = contexts[-1]
            in_list = fence_indent > 0 and any(
                ci <= fence_indent for ci in current_lists
            )

            in_directive = len(contexts) > 1
            if fence_indent > 0 and not in_list and not in_directive:
                strip_indent = fence_indent
                result.append(line[fence_indent:])
            else:
                strip_indent = 0
                result.append(line)

        elif in_code:
            # ── Inside code block ───────────────────────────────────────────
            stripped_content = line.strip()
            is_closer = (
                stripped_content
                and all(c == open_char for c in stripped_content)
                and len(stripped_content) >= open_len
            )
            if is_closer:
                in_code = False

            if strip_indent:
                lead = len(line) - len(line.lstrip())
                remove = min(strip_indent, lead)
                result.append(line[remove:])
                if is_closer:
                    strip_indent = 0
            else:
                result.append(line)

        else:
            # ── Outside code block ──────────────────────────────────────────
            is_open_dir = bool(open_dir_re.match(line.rstrip()))
            is_close_dir = bool(close_dir_re.match(line.rstrip()))
            lm = list_re.match(line)

            if is_open_dir and not is_close_dir:
                # Push a fresh list-context frame for this ::: block
                contexts.append([])

            elif is_close_dir:
                # Pop the innermost frame (keep at least the global one)
                if len(contexts) > 1:
                    contexts.pop()

            elif lm:
                # List item: record its content_indent in the current frame
                content_indent = len(lm.group(0))
                current = contexts[-1]
                # Replace any entries at the same or deeper content level
                while current and current[-1] >= content_indent:
                    current.pop()
                current.append(content_indent)

            elif line.strip():
                # Non-blank, non-list, non-directive line: close list items
                # whose content_indent exceeds this line's indentation.
                line_indent = len(line) - len(line.lstrip())
                contexts[-1] = [ci for ci in contexts[-1] if ci <= line_indent]
                if line_indent == 0:
                    contexts[-1].clear()

            result.append(line)

    return result


# ---------------------------------------------------------------------------
# Main transformation pipeline
# ---------------------------------------------------------------------------


def transform_file(
    base_dir: Path,
    source_path: Path,
    dest_path: Path,
    nav_titles: dict = None,
) -> None:
    with open(source_path, encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    # Ensure trailing newline
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"

    rel_path = source_path.relative_to(base_dir)

    # Step 1: add h1 title if missing
    if not has_h1(lines):
        # Prefer the explicit nav title; fall back to filename-derived title
        if nav_titles and rel_path in nav_titles:
            title = nav_titles[rel_path]
        else:
            stem = source_path.stem
            if stem == "index" and source_path.parent != base_dir:
                stem = source_path.parent.name
            title = title_from_filename(stem)
        fm_end = get_frontmatter_end(lines)
        insert = [f"# {title}\n", "\n"]
        lines = lines[:fm_end] + insert + lines[fm_end:]

    # Step 2: fix heading spaces
    lines = fix_heading_spaces(lines)

    # Step 3: transform code-fence attributes
    lines = transform_code_fences(lines)

    # Step 3b: rename language identifiers (e.g. shellSession → console)
    lines = rename_fence_langs(lines)

    # Step 3c: convert --8<-- snippet includes to embed= meta
    lines = transform_embeds(lines)

    # Step 4: transform admonitions (multiple passes to handle nesting)
    for _ in range(5):
        new = transform_admonitions(lines)
        if new == lines:
            break
        lines = new

    # Step 5: transform tab blocks
    lines = transform_tabs(lines)

    # Step 5b: fix directive colon counts for nesting
    lines = fix_directive_colons(lines)

    # Step 6: remove duplicate h1 headings
    lines = remove_duplicate_h1(lines)

    # Step 7: strip indentation from code fences not inside list items
    lines = strip_non_list_fence_indent(lines)

    # Step 8: transform relative links (code-fence and inline-code aware)
    lines = transform_links(lines, base_dir, rel_path)

    content = "".join(lines)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>", file=sys.stderr)
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    if not target_dir.exists():
        print(f"Error: directory '{target_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    nav_titles = parse_nav_titles(MKDOCS_YML)

    md_files = sorted(target_dir.rglob("*.md"))
    written = 0
    for source_path in md_files:
        rel = source_path.relative_to(target_dir)
        print(f"  {rel}")
        transform_file(target_dir, source_path, source_path, nav_titles=nav_titles)
        written += 1

    print(f"\nDone. {written} files transformed in '{target_dir}/'.")


if __name__ == "__main__":
    main()
