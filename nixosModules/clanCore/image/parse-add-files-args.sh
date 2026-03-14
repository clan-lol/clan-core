#!/usr/bin/env bash
# Source this script to parse the standardized addFilesScript CLI arguments.
#
# After sourcing, the following variables are available:
#   source_image  - Path to the original built image (read-only)
#   output_image  - Path for the modified output image
#   extra_paths   - Array of (local-source, target-path) pairs
#
# Usage in a writeShellApplication:
#   source @parseAddFilesArgs@
#   # Now use $source_image, $output_image, ${extra_paths[@]}

source_image=""
output_image=""
extra_paths=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      source_image="$2"
      shift 2
      ;;
    --output)
      output_image="$2"
      shift 2
      ;;
    --extra-path)
      extra_paths+=("$2" "$3")
      shift 3
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      echo "Unexpected argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$source_image" ]]; then
  echo "Error: --source is required" >&2
  exit 1
fi

if [[ -z "$output_image" ]]; then
  echo "Error: --output is required" >&2
  exit 1
fi
