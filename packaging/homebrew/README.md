Homebrew packaging notes for Centurion AI OS.

Use `packaging/homebrew/centurion-ai-os.rb` as a tap or `homebrew-core` starting point.

Key choices:
- Stable builds should target the semver-named sdist asset attached to each GitHub release, not the CalVer tag tarball.
- `faster-whisper` now lives in the `voice` extra, which keeps wheel-only transitive dependencies out of the base Homebrew formula.
- The wrapper exports bundled-skills path environment variables (`CENTURION_BUNDLED_SKILLS`, `CENTURION_OPTIONAL_SKILLS`, and `CENTURION_MANAGED=homebrew`) so packaged installs keep runtime assets and defer upgrades to Homebrew. (Env var names are legacy identifiers in the runtime.)

Typical update flow:
1. Bump the formula `url`, `version`, and `sha256`.
2. Refresh Python resources with `brew update-python-resources --print-only centurion-agent`.
3. Keep `ignore_packages: %w[certifi cryptography pydantic]`.
4. Verify `brew audit --new --strict centurion-agent` and `brew test centurion-agent`.
