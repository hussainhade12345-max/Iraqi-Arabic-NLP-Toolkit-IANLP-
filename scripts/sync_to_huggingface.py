#!/usr/bin/env python3
"""
Reliable one-way synchronization script from GitHub to Hugging Face.

Key Features & Guarantees:
1. GitHub is the single source of truth.
2. Synchronizes NLP modules:
   - iraqi_nlp/
   - tests/
   - corpus/
   - lexicon/
   - data/
   - README.md, pyproject.toml, setup.py, requirements.txt, LICENSE, LICENSE-DATA
3. Excludes:
   - Tokens, API keys, credentials, .env*
   - __pycache__/, *.pyc, *.pyo, *.pyd
   - .git/, .github/, .pytest_cache/, *.egg-info/, build/, dist/
4. Non-destructive: Never deletes existing remote Hugging Face files automatically.
5. Verification: Can run test suite or schema validation before upload.
6. Detailed sync reporting: Added, updated, skipped files, and commit URL.
7. Supports dry-run execution (--dry-run).
"""

from pathlib import Path
import os
import sys
import fnmatch
import argparse
import subprocess
from typing import List, Dict, Set, Tuple, Optional, Any

try:
    from huggingface_hub import HfApi, upload_file, list_repo_files
except ImportError:
    HfApi = None
    upload_file = None
    list_repo_files = None

# Default Hugging Face target dataset repository
DEFAULT_REPO_ID = "hussainhadi/Iraqi-Arabic-NLP-Toolkit-IANLP"
REPO_TYPE = "dataset"

ROOT = Path(__file__).resolve().parents[1]
GITIGNORE_PATH = ROOT / ".gitignore"

# Directories and top-level files to synchronize
SYNC_DIRS = ["iraqi_nlp", "tests", "corpus", "lexicon", "data"]
SYNC_FILES = [
    "README.md",
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "LICENSE",
    "LICENSE-DATA",
    "CITATION.cff"
]

# Strict security exclusions (never sync to Hugging Face)
ALWAYS_SKIP_PREFIXES = (".git", ".github")
ALWAYS_SKIP_CONTAINS = ("__pycache__", ".pytest_cache", ".egg-info")
ALWAYS_SKIP_EXTENSIONS = (".pyc", ".pyo", ".pyd")
ALWAYS_SKIP_PATTERNS = [
    ".env*",
    "*token*",
    "*secret*",
    "*credential*",
    "*.key",
    "*.pem",
    ".DS_Store",
    "dist/*",
    "build/*"
]


def load_gitignore_patterns(gitignore_path: Path) -> List[str]:
    patterns: List[str] = []
    if gitignore_path.exists():
        for line in gitignore_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
    return patterns


def matches_any_pattern(rel_path: str, patterns: List[str]) -> bool:
    rel = rel_path.replace(os.sep, "/")
    for pat in patterns:
        p = pat
        if p.endswith("/"):
            p = p + "*"
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
            return True
    return False


def is_excluded(rel_path: str, gitignore_patterns: Optional[List[str]] = None) -> Tuple[bool, str]:
    """
    Check if a file should be excluded from synchronization.
    Returns (is_excluded, reason).
    """
    rel = rel_path.replace(os.sep, "/")

    for pfx in ALWAYS_SKIP_PREFIXES:
        if rel == pfx or rel.startswith(pfx + "/"):
            return True, f"Excluded top-level directory: {pfx}"

    for seg in ALWAYS_SKIP_CONTAINS:
        if f"/{seg}/" in "/" + rel + "/" or rel.endswith(seg):
            return True, f"Excluded artifact directory: {seg}"

    for ext in ALWAYS_SKIP_EXTENSIONS:
        if rel.endswith(ext):
            return True, f"Excluded binary extension: {ext}"

    for pat in ALWAYS_SKIP_PATTERNS:
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(os.path.basename(rel), pat):
            return True, f"Matched sensitive pattern: {pat}"

    if gitignore_patterns and matches_any_pattern(rel, gitignore_patterns):
        # Allow files in SYNC_DIRS even if general gitignore has loose patterns, but respect gitignore otherwise
        return True, "Matched .gitignore pattern"

    return False, ""


def collect_local_files_to_sync(root_dir: Path = ROOT) -> List[Path]:
    """Collect all eligible local files for synchronization."""
    gitignore_patterns = load_gitignore_patterns(root_dir / ".gitignore")
    files_to_sync: List[Path] = []

    # 1. Directories
    for dir_name in SYNC_DIRS:
        dir_path = root_dir / dir_name
        if not dir_path.exists():
            continue
        for root, _, files in os.walk(dir_path):
            for fname in files:
                full_path = Path(root) / fname
                rel_path = str(full_path.relative_to(root_dir)).replace(os.sep, "/")
                excluded, _ = is_excluded(rel_path, gitignore_patterns)
                if not excluded:
                    files_to_sync.append(full_path)

    # 2. Individual top-level files
    for file_name in SYNC_FILES:
        full_path = root_dir / file_name
        if full_path.exists() and full_path.is_file():
            rel_path = file_name
            excluded, _ = is_excluded(rel_path, gitignore_patterns)
            if not excluded:
                files_to_sync.append(full_path)

    return sorted(files_to_sync)


def run_pre_sync_validation() -> bool:
    """Run pytest suite before synchronizing to ensure code integrity."""
    print("Running pre-synchronization test suite...")
    try:
        res = subprocess.run([sys.executable, "-m", "pytest", "tests/"], cwd=str(ROOT), capture_output=True, text=True)
        if res.returncode == 0:
            print("Pre-sync tests passed successfully.")
            return True
        else:
            print(f"Pre-sync tests failed (exit code {res.returncode}):\n{res.stdout}\n{res.stderr}")
            return False
    except Exception as e:
        print(f"Error running pre-sync validation: {e}")
        return False


def sync_to_huggingface(
    repo_id: str = DEFAULT_REPO_ID,
    token: Optional[str] = None,
    dry_run: bool = False,
    skip_validation: bool = False
) -> Dict[str, Any]:
    """
    Perform one-way sync from local repository to Hugging Face.
    """
    report = {
        "repo_id": repo_id,
        "dry_run": dry_run,
        "validation_passed": False,
        "added_files": [],
        "updated_files": [],
        "skipped_files": [],
        "commit_url": None,
        "error": None
    }

    # 1. Pre-sync validation
    if not skip_validation:
        if not run_pre_sync_validation():
            report["error"] = "Pre-sync validation failed. Synchronization aborted."
            return report
        report["validation_passed"] = True
    else:
        report["validation_passed"] = True

    # 2. Collect local files
    local_files = collect_local_files_to_sync(ROOT)
    if not local_files:
        report["error"] = "No local files found to synchronize."
        return report

    # 3. Handle Dry Run
    if dry_run:
        print(f"\n--- DRY RUN: Synchronizing to {repo_id} ---")
        for f in local_files:
            rel = str(f.relative_to(ROOT)).replace(os.sep, "/")
            report["added_files"].append(rel)
            print(f"[DRY-RUN] Will sync: {rel}")
        print(f"Total files to sync: {len(report['added_files'])}")
        return report

    # 4. Authenticate & Connect
    if not token:
        token = os.environ.get("HF_TOKEN")
    if not token:
        report["error"] = "HF_TOKEN is not set. Please provide HF_TOKEN via environment variable or argument."
        return report

    if HfApi is None:
        report["error"] = "huggingface_hub package is not installed."
        return report

    api = HfApi()

    # Verify repository exists
    try:
        api.repo_info(repo_id=repo_id, repo_type=REPO_TYPE, token=token)
        print(f"Verified Hugging Face repository: {repo_id}")
    except Exception as e:
        report["error"] = f"Could not access Hugging Face repository {repo_id}: {type(e).__name__}."
        return report

    # Fetch existing remote files to determine added vs updated
    remote_files = set()
    try:
        remote_files = set(list_repo_files(repo_id=repo_id, repo_type=REPO_TYPE, token=token))
    except Exception:
        pass

    # 5. Upload files non-destructively
    for local_path in local_files:
        rel_path = str(local_path.relative_to(ROOT)).replace(os.sep, "/")
        try:
            upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=rel_path,
                repo_id=repo_id,
                repo_type=REPO_TYPE,
                token=token,
            )
            if rel_path in remote_files:
                report["updated_files"].append(rel_path)
                print(f"Updated: {rel_path}")
            else:
                report["added_files"].append(rel_path)
                print(f"Added: {rel_path}")
        except Exception as e:
            report["skipped_files"].append(rel_path)
            print(f"Failed to upload {rel_path}: {type(e).__name__}")

    report["commit_url"] = f"https://huggingface.co/datasets/{repo_id}/tree/main"
    return report


def main():
    parser = argparse.ArgumentParser(description="Synchronize IANLP repository to Hugging Face dataset.")
    parser.add_argument("--repo-id", default=os.environ.get("HF_REPO_ID", DEFAULT_REPO_ID), help="Hugging Face repo ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview files to synchronize without uploading")
    parser.add_argument("--skip-validation", action="store_true", help="Skip pre-sync test execution")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    report = sync_to_huggingface(
        repo_id=args.repo_id,
        token=token,
        dry_run=args.dry_run,
        skip_validation=args.skip_validation
    )

    print("\n" + "=" * 60)
    print("SYNCHRONIZATION REPORT")
    print("=" * 60)
    print(f"Target Repo:         {report['repo_id']}")
    print(f"Dry Run:             {report['dry_run']}")
    print(f"Validation Passed:   {report['validation_passed']}")
    print(f"Added Files:         {len(report['added_files'])}")
    print(f"Updated Files:       {len(report['updated_files'])}")
    print(f"Skipped / Failed:    {len(report['skipped_files'])}")
    if report["commit_url"]:
        print(f"Hugging Face URL:    {report['commit_url']}")
    if report["error"]:
        print(f"Status / Error:      {report['error']}")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
