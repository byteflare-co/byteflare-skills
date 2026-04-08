"""Project structure auto-discovery script.

Takes a project root as an argument and outputs information about
specification candidates, source code structure, IaC files,
build systems, etc. in JSON format.

Usage:
    python discover_project.py /path/to/project
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def discover_spec_files(root: Path) -> list[dict]:
    """Detect specification document candidate files."""
    patterns = [
        "docs/**/*.md",
        "spec/**/*.md",
        "specification/**/*.md",
        "specifications/**/*.md",
        "doc/**/*.md",
        "documents/**/*.md",
        "wiki/**/*.md",
        "design/**/*.md",
        "*.md",  # Root-level md files (README, etc.)
    ]
    results = []
    seen = set()
    for pattern in patterns:
        for f in sorted(root.glob(pattern)):
            if f.name.startswith(".") or "__pycache__" in str(f):
                continue
            rel = str(f.relative_to(root))
            if rel in seen:
                continue
            seen.add(rel)
            # Parse heading structure
            headings = _extract_headings(f)
            results.append({
                "path": rel,
                "headings": headings,
                "size_bytes": f.stat().st_size,
            })
    return results


def _extract_headings(md_file: Path) -> list[dict]:
    """Extract heading structure from Markdown file."""
    headings = []
    try:
        text = md_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return headings
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            if title:
                headings.append({"level": level, "title": title})
    return headings


def discover_source_code(root: Path) -> dict:
    """Detect source code structure."""
    language_extensions = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".jsx": "JavaScript (React)",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".swift": "Swift",
        ".kt": "Kotlin",
    }
    ignore_dirs = {
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
        ".next", ".nuxt", "target", "vendor", ".terraform",
        "coverage", ".coverage", "htmlcov", "egg-info",
    }

    lang_counts: dict[str, int] = {}
    source_dirs: list[str] = []
    entry_points: list[str] = []
    shared_modules: list[str] = []

    # Scan top-level directories
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in ignore_dirs:
            continue
        # Check if directory contains source code
        has_source = False
        for ext in language_extensions:
            if list(d.rglob(f"*{ext}")):
                has_source = True
                break
        if has_source:
            source_dirs.append(d.name)

    # Count files by language (top 3 levels only, for performance)
    for f in root.rglob("*"):
        if any(part in ignore_dirs for part in f.parts):
            continue
        if f.is_file() and f.suffix in language_extensions:
            lang = language_extensions[f.suffix]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # Entry point candidates
    entry_point_patterns = [
        "main.py", "app.py", "index.py", "handler.py", "wsgi.py",
        "index.js", "index.ts", "app.js", "app.ts", "server.js", "server.ts",
        "main.go", "main.rs", "Main.java", "Program.cs",
        "manage.py", "setup.py",
    ]
    for pattern in entry_point_patterns:
        for f in root.rglob(pattern):
            if any(part in ignore_dirs for part in f.parts):
                continue
            entry_points.append(str(f.relative_to(root)))

    # Shared module candidates (lib/, shared/, common/, utils/, layer/, etc.)
    shared_patterns = [
        "lib", "shared", "common", "utils", "helpers", "core",
        "lambda_layer", "layer", "packages", "internal",
    ]
    for name in shared_patterns:
        d = root / name
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file() and f.suffix in language_extensions:
                    if any(part in ignore_dirs for part in f.parts):
                        continue
                    shared_modules.append(str(f.relative_to(root)))

    # Determine primary language
    primary_language = None
    if lang_counts:
        primary_language = max(lang_counts, key=lang_counts.get)

    return {
        "primary_language": primary_language,
        "language_file_counts": lang_counts,
        "source_directories": sorted(source_dirs),
        "entry_points": sorted(entry_points),
        "shared_modules": sorted(shared_modules),
    }


def discover_iac(root: Path) -> list[dict]:
    """Detect IaC (Infrastructure as Code) files."""
    iac_indicators = [
        ("terraform", "Terraform", "*.tf"),
        ("cdk", "AWS CDK", "*.ts"),
        ("cloudformation", "CloudFormation", "*.yml"),
        ("kubernetes", "Kubernetes", "*.yml"),
        ("k8s", "Kubernetes", "*.yml"),
        ("helm", "Helm", "*.yaml"),
        ("pulumi", "Pulumi", "*.*"),
    ]
    results = []
    seen_dirs = set()

    # Directory-based detection
    for dir_name, iac_type, pattern in iac_indicators:
        d = root / dir_name
        if d.is_dir() and dir_name not in seen_dirs:
            seen_dirs.add(dir_name)
            files = sorted(str(f.relative_to(root)) for f in d.glob(pattern) if f.is_file())
            results.append({
                "type": iac_type,
                "directory": dir_name,
                "files": files[:20],  # Max 20 entries
            })

    # File-based detection
    single_file_indicators = [
        ("docker-compose.yml", "Docker Compose"),
        ("docker-compose.yaml", "Docker Compose"),
        ("Dockerfile", "Docker"),
        ("serverless.yml", "Serverless Framework"),
        ("serverless.yaml", "Serverless Framework"),
        ("template.yaml", "SAM"),
        ("template.yml", "SAM"),
        ("samconfig.toml", "SAM"),
    ]
    for filename, iac_type in single_file_indicators:
        f = root / filename
        if f.is_file():
            results.append({
                "type": iac_type,
                "directory": ".",
                "files": [filename],
            })

    return results


def discover_build_system(root: Path) -> list[dict]:
    """Detect build systems and package managers."""
    indicators = [
        ("Makefile", "Make"),
        ("package.json", "npm/Node.js"),
        ("pyproject.toml", "Python (pyproject)"),
        ("setup.py", "Python (setuptools)"),
        ("setup.cfg", "Python (setuptools)"),
        ("requirements.txt", "Python (pip)"),
        ("Pipfile", "Python (pipenv)"),
        ("poetry.lock", "Python (poetry)"),
        ("uv.lock", "Python (uv)"),
        ("go.mod", "Go"),
        ("Cargo.toml", "Rust"),
        ("pom.xml", "Java (Maven)"),
        ("build.gradle", "Java (Gradle)"),
        ("build.gradle.kts", "Kotlin (Gradle)"),
        ("Gemfile", "Ruby (Bundler)"),
        ("composer.json", "PHP (Composer)"),
        ("CMakeLists.txt", "CMake"),
        ("justfile", "Just"),
        ("Taskfile.yml", "Task"),
    ]
    results = []
    for filename, system_type in indicators:
        f = root / filename
        if f.is_file():
            results.append({
                "type": system_type,
                "file": filename,
            })
    return results


def discover_test_structure(root: Path) -> dict:
    """Detect test structure."""
    test_dirs = []
    test_files_count = 0
    test_patterns = ["test_*.py", "*_test.py", "*.test.js", "*.test.ts",
                     "*.spec.js", "*.spec.ts", "*_test.go", "*Test.java"]

    # Test directories
    for name in ["tests", "test", "spec", "__tests__", "test_*"]:
        for d in root.glob(name):
            if d.is_dir():
                test_dirs.append(str(d.relative_to(root)))

    # Test file count
    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".terraform"}
    for pattern in test_patterns:
        for f in root.rglob(pattern):
            if any(part in ignore_dirs for part in f.parts):
                continue
            test_files_count += 1

    # Test configuration files
    test_configs = []
    config_files = [
        "pytest.ini", "pyproject.toml", "setup.cfg",  # pytest
        "jest.config.js", "jest.config.ts",  # jest
        "vitest.config.ts", "vitest.config.js",  # vitest
        ".mocharc.yml", ".mocharc.json",  # mocha
    ]
    for name in config_files:
        if (root / name).is_file():
            test_configs.append(name)

    return {
        "test_directories": sorted(test_dirs),
        "test_files_count": test_files_count,
        "test_config_files": test_configs,
    }


def discover_claude_config(root: Path) -> dict:
    """Get CLAUDE.md and existing skill information."""
    claude_md = root / "CLAUDE.md"
    claude_md_content = None
    language = None

    if claude_md.is_file():
        try:
            text = claude_md.read_text(encoding="utf-8")
            claude_md_content = text[:3000]  # Preview only
            # Detect language tag
            import re
            match = re.search(r"<language>(.*?)</language>", text)
            if match:
                language = match.group(1)
        except (UnicodeDecodeError, OSError):
            pass

    # Also check global CLAUDE.md language setting
    global_claude_md = Path.home() / ".claude" / "CLAUDE.md"
    if language is None and global_claude_md.is_file():
        try:
            text = global_claude_md.read_text(encoding="utf-8")
            import re
            match = re.search(r"<language>(.*?)</language>", text)
            if match:
                language = match.group(1)
        except (UnicodeDecodeError, OSError):
            pass

    # Existing skills
    skills_dir = root / ".claude" / "skills"
    existing_skills = []
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file():
                existing_skills.append(d.name)

    return {
        "has_claude_md": claude_md.is_file(),
        "claude_md_preview": claude_md_content,
        "detected_language": language,
        "existing_skills": existing_skills,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python discover_project.py <project_root>", file=sys.stderr)
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = {
        "project_root": str(root),
        "project_name": root.name,
        "spec_files": discover_spec_files(root),
        "source_code": discover_source_code(root),
        "iac": discover_iac(root),
        "build_system": discover_build_system(root),
        "tests": discover_test_structure(root),
        "claude_config": discover_claude_config(root),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
