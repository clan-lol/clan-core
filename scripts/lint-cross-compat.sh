#!/usr/bin/env bash
#
# Lint: packages with a statically configured system.
#
# To support cross compilation, always use pkgs.callPackage.
#
# Suppress: # allow-cross-compat: <reason>
set -euo pipefail

check_files() {
  awk '
  FNR == 1 { prev = "" }

  {
    matched = 0

    # Skip comments and documentation strings
    if ($0 ~ /^[ \t]*#/ || $0 ~ /^[ \t]*\*/) { prev = $0; next }
    if ($0 ~ /defaultText[ \t]*=/ || $0 ~ /literalExpression/) { prev = $0; next }

    if ($0 ~ /\.(legacy)?[Pp]ackages\.[$][{]/) matched = 1
    if (!matched && $0 ~ /\.(legacy)?[Pp]ackages\."?(x86_64|aarch64|i686|armv7l|riscv64)-(linux|darwin)/) matched = 1
    if (!matched && $0 ~ /builtins\.currentSystem/) matched = 1

    if (matched) {
      if ($0 ~ /allow-cross-compat:/) {
        if ($0 !~ /allow-cross-compat:[ \t]*[^ \t]/) {
          print FILENAME ":" FNR ": " $0
          invalid_ignore++
        }
        prev = $0; next
      }
      if (prev ~ /^[ \t]*#.*allow-cross-compat:/) {
        if (prev !~ /allow-cross-compat:[ \t]*[^ \t]/) {
          print FILENAME ":" (FNR-1) ": " prev
          invalid_ignore++
        }
        prev = $0; next
      }
      print FILENAME ":" FNR ": " $0
      found++
    }

    prev = $0
  }

  END {
    rc = 0
    if (found > 0) {
      print ""
      print "Found " found " statically configured system reference(s)."
      print ""
      print "To support cross compilation, always use callPackage:"
      print "  pkgs.callPackage (path/to/myPkg.nix) {}"
      print ""
      print "Not:"
      print "  *.packages.<system>.myPkg"
      print ""
      print "To suppress: # allow-cross-compat: <reason>"
      rc = 1
    }
    if (invalid_ignore > 0) {
      print ""
      print "Found " invalid_ignore " allow-cross-compat comment(s) without a reason."
      rc = 1
    }
    if (rc) exit 1
  }
  ' "$@"
}

if [ $# -gt 0 ]; then
  check_files "$@"
else
  mapfile -t files < <(
    git ls-files \
      'clanServices/**/*.nix' \
      'nixosModules/**/*.nix' \
    | grep -v '/tests/' \
    | sort
  )
  if [ ${#files[@]} -eq 0 ]; then
    exit 0
  fi
  check_files "${files[@]}"
fi
