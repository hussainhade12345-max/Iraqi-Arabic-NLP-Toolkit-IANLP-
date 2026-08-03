## Syncing to Hugging Face

We provide a helper script to sync the dataset resources (corpus/, lexicon/, and the project README) to a Hugging Face dataset repository.

1. Create a Hugging Face token at https://huggingface.co/settings/tokens
2. Set it locally (do NOT commit this token):
   ```bash
   export HF_TOKEN=your_token_here
   ```
   If you ever accidentally share the token, revoke it and create a new one.
3. Run the sync script:
   ```bash
   python scripts/sync_to_huggingface.py
   ```
4. CI Automation: add the token as a GitHub Actions repository secret named `HF_TOKEN` (Settings → Secrets and variables → Actions). The workflow .github/workflows/sync-huggingface.yml runs the script and references the secret; it does not contain any token values.

Notes:
- The script reads HF_TOKEN only from the environment. It will exit with an error if HF_TOKEN is not set.
- The script skips source code under `iraqi_nlp/`, `.git/`, `__pycache__/`, and any paths matched by .gitignore.
