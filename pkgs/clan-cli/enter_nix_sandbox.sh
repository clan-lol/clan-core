#!/usr/bin/env bash

set -xeuo pipefail

PID_NIX=$(pgrep --full "python -m pytest" | cut -d " " -f2 | head -n1)

sudo cntr attach "$PID_NIX"
