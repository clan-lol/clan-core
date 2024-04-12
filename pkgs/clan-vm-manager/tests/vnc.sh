#!/usr/bin/env bash

set -euo pipefail


# For vnc debugging
export VNC_USERNAME="$USER"
export VNC_PASSWORD=""

CA_CRT=$GIT_ROOT/pkgs/clan-vm-manager/tests/data/vnc-security/ca.crt

vncviewer 127.0.0.1 -Shared -X509CA "$CA_CRT"

