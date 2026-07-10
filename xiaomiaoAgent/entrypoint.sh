#!/bin/sh
script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
dir="${XIAOMIAO_AGENT_HOME:-$repo_root/.cache/agent/nanobot}"
if [ -d "$dir" ] && [ ! -w "$dir" ]; then
    owner_uid=$(stat -c %u "$dir" 2>/dev/null || stat -f %u "$dir" 2>/dev/null)
    cat >&2 <<EOF
Error: $dir is not writable (owned by UID $owner_uid, running as UID $(id -u)).

Fix (pick one):
  Host:   sudo chown -R 1000:1000 $dir
  Docker: docker run --user \$(id -u):\$(id -g) ...
  Podman: podman run --userns=keep-id ...
EOF
    exit 1
fi
exec nanobot "$@"
