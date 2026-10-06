"""Check public repository artifacts using the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRECTORIES = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
    ".mypy_cache", "dist", "build", "htmlcov",
}
REQUIRED_FILES = (
    "README.md", "LICENSE", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md",
    "CODE_OF_CONDUCT.md", "NOTICE.md", "docs/architecture.md",
    "docs/memory-contract.md",
    ".gitignore", ".github/CODEOWNERS", ".github/dependabot.yml",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/workflows/repository-checks.yml",
)
SECRET_PATTERNS = (
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
)
CONTENT_DIAGNOSTIC_CODES = (
    "github-token-signature", "provider-token-signature", "private-key-signature",
    "personal-filesystem-path",
)
LINK_PATTERN = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.+?)(?:\s+#+)?$")


def repository_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink requires explicit review: {relative}")
        if path.is_file():
            files.append(path)
    return sorted(files)


def markdown_prose(text: str) -> str:
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            character = marker.group(1)[0]
            if fence is None:
                fence = character
            elif character == fence:
                fence = None
            lines.append("")
        else:
            lines.append(line if fence is None else "")
    if fence is not None:
        raise ValueError("Unclosed Markdown code fence")
    return "\n".join(lines)


def heading_ids(text: str) -> set[str]:
    result = set()
    counts: dict[str, int] = {}
    for line in markdown_prose(text).splitlines():
        heading = HEADING_PATTERN.match(line)
        if not heading:
            continue
        label = re.sub(r"<[^>]*>", "", heading.group(1)).strip().lower()
        label = re.sub(r"[^\w\s-]", "", label, flags=re.UNICODE).replace(" ", "-")
        count = counts.get(label, 0)
        counts[label] = count + 1
        result.add(label if count == 0 else f"{label}-{count}")
    return result


def check_markdown(path: Path, text: str) -> list[str]:
    problems = []
    relative = path.relative_to(ROOT)
    try:
        prose = markdown_prose(text)
    except ValueError as error:
        return [f"{relative}: {error}"]
    for raw in LINK_PATTERN.findall(prose):
        target = raw.strip().split(' "', 1)[0].strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not destination.is_relative_to(ROOT):
            problems.append(f"{relative}: local link escapes the repository")
        elif not destination.exists():
            problems.append(f"{relative}: missing local link {target}")
        elif parsed.fragment and destination.suffix == ".md":
            anchors = heading_ids(destination.read_text(encoding="utf-8"))
            if unquote(parsed.fragment) not in anchors:
                problems.append(f"{relative}: missing heading in local link {target}")
    return problems


def check_public_file(path: Path, text: str | None) -> list[str]:
    relative = path.relative_to(ROOT)
    problems = []
    private_names = {".hermes", ".omh", ".optchat", "runtime-data", "private", "backups"}
    if path.name == "build-optchat-hermes.md":
        problems.append(f"{relative}: private implementation assignment")
    if any(part in private_names for part in relative.parts):
        problems.append(f"{relative}: private runtime directory")
    if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
        problems.append(f"{relative}: environment/credential file")
    if path.suffix in {".db", ".sqlite", ".sqlite3", ".pem", ".key", ".p12", ".pfx"} or path.name.endswith(("-wal", "-shm")):
        problems.append(f"{relative}: private database/key artifact")
    if text is not None:
        for rule_index, pattern in enumerate(SECRET_PATTERNS):
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                code = CONTENT_DIAGNOSTIC_CODES[rule_index]
                problems.append(f"{relative}:{line}: {code}; value suppressed")
    return problems


def check_workflow(path: Path, text: str) -> list[str]:
    problems = []
    relative = path.relative_to(ROOT)
    for match in re.finditer(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", text, re.MULTILINE):
        action = match.group(1).strip("\"'")
        if action.startswith("./"):
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-f]{40}", action):
            problems.append(f"{relative}: action must use an immutable full commit SHA")
    return problems


def main() -> int:
    problems = [f"Missing required artifact: {name}" for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    try:
        files = repository_files()
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    markdown_count = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = None
        problems.extend(check_public_file(path, text))
        if text is not None and path.suffix == ".md":
            markdown_count += 1
            problems.extend(check_markdown(path, text))
        if text is not None and path.parent == ROOT / ".github/workflows":
            problems.extend(check_workflow(path, text))
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "files": len(files), "markdown_files": markdown_count, "scope": "Repository artifacts and public hygiene"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
