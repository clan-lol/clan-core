#!/usr/bin/env bash

# For vnc debugging
export VNC_USERNAME=$USER
export VNC_PASSWORD=""

CA_CRT=tests/data/vnc-security/ca.crt

vncviewer 127.0.0.1 -Shared -X509CA $CA_CRT

