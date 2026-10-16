# One-push GitHub -> Zenodo workflow

1. Replace the current GitHub repository contents with the contents of this package.
2. Confirm `scripts/`, `docs/`, `config/`, `src/`, `tests/`, and `reference_outputs/` are visible on the public `main` branch.
3. Confirm no file from `data/restricted/` is staged except `README.md`.
4. Commit and push once.
5. Create tag/release `v1.1.1`.
6. In the Zenodo GitHub integration, archive that release as a **new version**.
7. Copy the new version DOI and provide it for final manuscript/response/checklist synchronization.

Suggested commands:

```bash
git add -A
git status
git commit -m "Publish full reproducibility release"
git push origin main
git tag -a v1.1.1 -m "v1.1.1 Full Reproducibility Release"
git push origin v1.1.1
```

Do not add restricted MIMIC-IV/eICU patient-level data or patient-level predictions.
