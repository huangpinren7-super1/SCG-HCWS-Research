# Branch protection policy

The repository should treat the following GitHub Actions checks as required before a PR can merge:

- `BootLoops-Lab Infrastructure Smoke / BootLoops-Lab Infrastructure Smoke`
- `BootLoops Acceptance Battery / BootLoops 49-package acceptance battery`

Both workflows now run on every pull request, so newly added SCG/HCWS research files cannot bypass the required checks. Main-branch pushes remain path-filtered to the laboratory/research surfaces. Their concurrency groups are keyed by PR number when the event is a pull request, so a push to `main` cannot cancel a PR run.

The repository Actions workflows have read-only `GITHUB_TOKEN` permissions. Enabling branch protection itself is a repository-administration setting and is intentionally not encoded as executable code here. The required-check names above are the stable names to configure in GitHub branch protection/rulesets.

Do not enable “require status checks to be up to date” by substituting a mutable or historical check name. After any workflow renaming, update this document and the branch protection rule together.
