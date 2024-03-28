#!/usr/bin/env bash

# use https://github.com/ctypesgen/ctypesgen to generate python bindings for libvncclient

~/Projects/ctypesgen/run.py -R "$LIBVNC_LIB" -I "$LIBVNC_INCLUDE" -l libvncclient.so "$LIBVNC_INCLUDE/rfb/rfbclient.h" -o libvncclient.py