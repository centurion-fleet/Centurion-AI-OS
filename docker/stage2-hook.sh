#!/bin/sh
# s6-overlay stage2 hook — runs as root after the supervision tree is
# up but before user services start. Handles UID/GID remap, volume
# chown, config seeding, and skills sync.
#
# Per-service privilege drop happens inside each service's `run` script
# (and in main-wrapper.sh) via s6-setuidgid, not here.
#
# Wired into the image as /etc/cont-init.d/01-centurion-setup by the
# Dockerfile. The shim at docker/entrypoint.sh forwards to this script
# so external references to docker/entrypoint.sh still work.
#
# NB: cont-init.d scripts run with no arguments — the user's CMD args
# are NOT visible here. That's fine: we use Architecture B (s6-overlay
# main-program model), so main-wrapper.sh runs the CMD with full
# stdin/stdout/stderr access and handles arg parsing there.

set -eu

CENTURION_HOME="${CENTURION_HOME:-/opt/data}"
INSTALL_DIR="/opt/centurion"

# --- UID/GID remap ---
if [ -n "${CENTURION_UID:-}" ] && [ "$CENTURION_UID" != "$(id -u centurion)" ]; then
    echo "[stage2] Changing centurion UID to $CENTURION_UID"
    usermod -u "$CENTURION_UID" centurion
fi
if [ -n "${CENTURION_GID:-}" ] && [ "$CENTURION_GID" != "$(id -g centurion)" ]; then
    echo "[stage2] Changing centurion GID to $CENTURION_GID"
    # -o allows non-unique GID (e.g. macOS GID 20 "staff" may already
    # exist as "dialout" in the Debian-based container image).
    groupmod -o -g "$CENTURION_GID" centurion 2>/dev/null || true
fi

# --- Fix ownership of data volume ---
actual_centurion_uid=$(id -u centurion)
needs_chown=false
if [ -n "${CENTURION_UID:-}" ] && [ "$CENTURION_UID" != "10000" ]; then
    needs_chown=true
elif [ "$(stat -c %u "$CENTURION_HOME" 2>/dev/null)" != "$actual_centurion_uid" ]; then
    needs_chown=true
fi
if [ "$needs_chown" = true ]; then
    echo "[stage2] Fixing ownership of $CENTURION_HOME to centurion ($actual_centurion_uid)"
    # In rootless Podman the container's "root" is mapped to an
    # unprivileged host UID — chown will fail. That's fine: the volume
    # is already owned by the mapped user on the host side.
    chown -R centurion:centurion "$CENTURION_HOME" 2>/dev/null || \
        echo "[stage2] Warning: chown failed (rootless container?) — continuing"
    # The .venv must also be re-chowned when UID is remapped, otherwise
    # lazy_deps.py cannot install platform packages (discord.py, etc.).
    chown -R centurion:centurion "$INSTALL_DIR/.venv" 2>/dev/null || \
        echo "[stage2] Warning: chown .venv failed (rootless container?) — continuing"
fi

# Always reset ownership of $CENTURION_HOME/profiles to centurion on every
# boot. Profile dirs and files can land owned by root when commands
# are invoked via `docker exec <container> centurion …` (which defaults
# to root unless `-u` is passed), and that breaks the cont-init
# reconciler (02-reconcile-profiles) which runs as centurion and walks
# the profiles dir. Idempotent; skipped on rootless containers where
# chown would fail.
if [ -d "$CENTURION_HOME/profiles" ]; then
    chown -R centurion:centurion "$CENTURION_HOME/profiles" 2>/dev/null || true
fi

# --- config.yaml permissions ---
# Ensure config.yaml is readable by the centurion runtime user even if it
# was edited on the host after initial ownership setup.
if [ -f "$CENTURION_HOME/config.yaml" ]; then
    chown centurion:centurion "$CENTURION_HOME/config.yaml" 2>/dev/null || true
    chmod 640 "$CENTURION_HOME/config.yaml" 2>/dev/null || true
fi

# --- Seed directory structure as centurion user ---
# Run as centurion via s6-setuidgid so dirs end up owned correctly (matters
# under rootless Podman where chown back to root would fail).
#
# Use direct `mkdir -p` invocation (no `sh -c "..."` wrapper) so the
# shell isn't a second interpreter — defends against $CENTURION_HOME values
# containing shell metacharacters. PR #30136 review item O2.
s6-setuidgid centurion mkdir -p \
    "$CENTURION_HOME/cron" \
    "$CENTURION_HOME/sessions" \
    "$CENTURION_HOME/logs" \
    "$CENTURION_HOME/hooks" \
    "$CENTURION_HOME/memories" \
    "$CENTURION_HOME/skills" \
    "$CENTURION_HOME/skins" \
    "$CENTURION_HOME/plans" \
    "$CENTURION_HOME/workspace" \
    "$CENTURION_HOME/home"

# --- Install-method stamp (read by detect_install_method() in centurion status) ---
# Preserved from the tini-era entrypoint (PR #27843). Must be written as
# the centurion user so ownership matches the file's documented owner.
# tee is invoked directly via s6-setuidgid (no `sh -c` wrapper) for the
# same shell-metacharacter safety described above.
printf 'docker\n' | s6-setuidgid centurion tee "$CENTURION_HOME/.install_method" >/dev/null \
    || true

# --- Seed config files (only on first boot) ---
seed_one() {
    dest=$1
    src=$2
    if [ ! -f "$CENTURION_HOME/$dest" ] && [ -f "$INSTALL_DIR/$src" ]; then
        s6-setuidgid centurion cp "$INSTALL_DIR/$src" "$CENTURION_HOME/$dest"
    fi
}
seed_one ".env" ".env.example"
seed_one "config.yaml" "cli-config.yaml.example"
seed_one "SOUL.md" "docker/SOUL.md"

# .env holds API keys and secrets — restrict to owner-only access. Applied
# unconditionally (not only on first-seed) so a host-mounted .env that was
# created with a permissive umask gets tightened on every container start.
if [ -f "$CENTURION_HOME/.env" ]; then
    chown centurion:centurion "$CENTURION_HOME/.env" 2>/dev/null || true
    chmod 600 "$CENTURION_HOME/.env" 2>/dev/null || true
fi

# auth.json: bootstrap from env on first boot only. Same semantics as the
# pre-s6 entrypoint — the [ ! -f ] guard is critical to avoid clobbering
# rotated refresh tokens on container restart.
if [ ! -f "$CENTURION_HOME/auth.json" ] && [ -n "${HERMES_AUTH_JSON_BOOTSTRAP:-}" ]; then
    printf '%s' "$HERMES_AUTH_JSON_BOOTSTRAP" > "$CENTURION_HOME/auth.json"
    chown centurion:centurion "$CENTURION_HOME/auth.json" 2>/dev/null || true
    chmod 600 "$CENTURION_HOME/auth.json"
fi

# --- Sync bundled skills ---
# Invoke the venv's python by absolute path so we don't need a `sh -c`
# wrapper to source the activate script. This is safe because
# skills_sync.py doesn't depend on any environment exports beyond what
# the python binary's own bin-stub already sets up (sys.path is rooted
# at the venv's site-packages by virtue of running .venv/bin/python).
if [ -d "$INSTALL_DIR/skills" ]; then
    s6-setuidgid centurion "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/tools/skills_sync.py" \
        || echo "[stage2] Warning: skills_sync.py failed; continuing"
fi

echo "[stage2] Setup complete; starting user services"
