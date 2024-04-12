#!/usr/bin/env bash


PYTHON_DIR=$(dirname "$(which python3)")/..
gdb --quiet -ex "source $PYTHON_DIR/share/gdb/libpython.py" -ex "run" --args python "$1"