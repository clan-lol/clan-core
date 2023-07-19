# !/usr/bin/env python3
import sys
import subprocess


def showhelp():
    print('''
    usage:
    clan admin ...
    clan join ...
    clan delete ...
    ''')


try:
    cmd = f'clan-{sys.argv[1]}'
except:  # noqa
    showhelp()

try:
    subprocess.Popen([cmd] + sys.argv[2:])
except FileNotFoundError:
    print(f'command {cmd} not found')
    exit(2)
