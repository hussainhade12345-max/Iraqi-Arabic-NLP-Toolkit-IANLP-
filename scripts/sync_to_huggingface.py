#!/usr/bin/env python3
"""
Sync repository content (corpus/, lexicon/, README.md) to a Hugging Face dataset repo.

Requirements:
- NEVER hardcode a token. Read HF_TOKEN from the environment.
- REPO_ID is defined near the top for easy edits.
- Skip uploading iraqi_nlp/, .git/, __pycache__/, and patterns listed in .gitignore.
- Print a clear summary at the end.
"""

from pathlib import Path
import os
import sys
import fnmatch
from typing import List

from huggingface_hub import HfApi, upload_file

# Edit this to change target repo later
REPO_ID = "hussainhadi/ianlp"  # target on Hugging Face Hub
REPO_TYPE = "dataset"

ROOT = Path(__file__).resolve().parents[1]  # repo root (one level up from scripts/)
GITIGNORE_PATH = ROOT / ".gitignore"

# Directories to sync
UPLOAD_DIRS = ["corpus", "lexicon"]
README = "README.md"

# Always skip these top-level entries
ALWAYS_SKIP_PREFIXES = ("iraqi_nlp", ".git")
ALWAYS_SKIP_CONTAINS = ("__pycache__",)

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
    # Normalize path to forward slashes for pattern matching
    rel = rel_path.replace(os.sep, "/")
    for pat in patterns:
        # Convert gitignore directory pattern "dir/" -> "dir/*"
        p = pat
        if p.endswith("/"):
            p = p + "*"
        # Try fnmatch both the full rel path and the basename
        if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
            return True
    return False

def should_skip(rel_path: str, gitignore_patterns: List[str]) -> bool:
    # Skip always-specified prefixes
    for pfx in ALWAYS_SKIP_PREFIXES:
        if rel_path == pfx or rel_path.startswith(pfx + "/"):
            return True
    # Skip if contains any 'always skip' segments
    for seg in ALWAYS_SKIP_CONTAINS:
        if f"/{seg}/" in "/" + rel_path or rel_path.endswith(seg) or f"/{seg}" in rel_path:
            return True
    # Skip if matched by .gitignore patterns
    if matches_any_pattern(rel_path, gitignore_patterns):
        return True
    return False

def upload_directory(api: HfApi, token: str, dir_name: str, uploaded: List[str], gitignore_patterns: List[str]):
    base = ROOT / dir_name
    if not base.exists():
        print(f"Skipping {dir_name}: directory not found.")
        return
    for root, _, files in os.walk(base):
        for fname in files:
            full = Path(root) / fname
            rel = str(full.relative_to(ROOT)).replace(os.sep, "/")
            if should_skip(rel, gitignore_patterns):
                # debug: print(f"Skipping {rel} (ignored)")
                continue
            # path_in_repo should mirror repo structure starting from root
            path_in_repo = rel
            try:
                upload_file(
                    path_or_fileobj=str(full),
                    path_in_repo=path_in_repo,
                    repo_id=REPO_ID,
                    repo_type=REPO_TYPE,
                    token=token,
                )
                uploaded.append(path_in_repo)
                print(f"Uploaded: {path_in_repo}")
            except Exception as e:
                # Don't print token or sensitive headers. Provide guidance instead.
                print(f"Failed to upload {path_in_repo}: {type(e).__name__}. Check HF_TOKEN and network connectivity.")

def upload_readme(api: HfApi, token: str, uploaded: List[str], gitignore_patterns: List[str]):
    readme_path = ROOT / README
    if not readme_path.exists():
        print("No README.md at repo root to upload.")
        return
    rel = str(readme_path.relative_to(ROOT)).replace(os.sep, "/")
    if should_skip(rel, gitignore_patterns):
        print("README.md is ignored by .gitignore; skipping.")
        return
    try:
        upload_file(
            path_or_fileobj=str(readme_path),
            path_in_repo="README.md",
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            token=token,
        )
        uploaded.append("README.md")
        print("Uploaded: README.md")
    except Exception as e:
        print(f"Failed to upload README.md: {type(e).__name__}. Check HF_TOKEN and network connectivity.")


def main():
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("HF_TOKEN is not set. Export it first (export HF_TOKEN=your_token) and retry.")

    api = HfApi()
    gitignore_patterns = load_gitignore_patterns(GITIGNORE_PATH)

    # Verify repo exists; if not, create it
    try:
        api.repo_info(repo_id=REPO_ID, repo_type=REPO_TYPE, token=token)
        print(f"Found Hugging Face repo: {REPO_ID}")
    except Exception:
        print(f"Hugging Face repo {REPO_ID} not found. Attempting to create it as a dataset repo...")
        try:
            api.create_repo(repo_id=REPO_ID, repo_type=REPO_TYPE, token=token)
            print(f"Created dataset repo {REPO_ID} on Hugging Face Hub.")
        except Exception as e:
            sys.exit("Could not create or access the Hugging Face repo. Check HF_TOKEN and your permissions.")

    uploaded_files: List[str] = []
    try:
        for d in UPLOAD_DIRS:
            upload_directory(api, token, d, uploaded_files, gitignore_patterns)
        # Upload README
        upload_readme(api, token, uploaded_files, gitignore_patterns)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print("An unexpected error occurred during upload:", type(e).__name__)
        sys.exit(1)

    # Summary
    print("\nSync complete.")
    if uploaded_files:
        print(f"Uploaded {len(uploaded_files)} file(s):")
        for p in uploaded_files:
            print(f" - {p}")
    else:
        print("No files were uploaded (check .gitignore and the listed directories).")

    print(f"Hugging Face dataset URL: https://huggingface.co/datasets/{REPO_ID}")

if __name__ == "__main__":
    main()
