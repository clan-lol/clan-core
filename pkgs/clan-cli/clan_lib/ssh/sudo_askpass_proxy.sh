# shellcheck shell=bash
set -euo pipefail

# Create temporary directory
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

# Create FIFOs
prompt_fifo="$tmpdir/prompt_fifo"
password_fifo="$tmpdir/password_fifo"

mkfifo -m600 "$prompt_fifo"
mkfifo -m600 "$password_fifo"

# Create askpass script
askpass_script="$tmpdir/askpass.sh"

cat >"$askpass_script" <<EOF
#!/bin/sh
set -eu
prompt="\${1:-[sudo] password:}"
echo "\$prompt" > "$prompt_fifo"
password=\$(head -n 1 "$password_fifo")
if [ "\$password" = "CANCELED" ]; then
  exit 1
fi
echo "\$password"
EOF
chmod +x "$askpass_script"
echo "ASKPASS_SCRIPT: $askpass_script"

while read -r PROMPT  < "$prompt_fifo"; do
  echo "PASSWORD_REQUESTED: $PROMPT"
  read -r password
  echo ####################################### >&2
  echo "$password" >"$password_fifo"
done
