#!/usr/bin/env bash

set -e -o pipefail

check_git_tag() {
    local repo_path="$1"
    local target_tag="$2"

    # Change directory to the specified Git repository
    pushd "$repo_path" > /dev/null 2>&1
    # shellcheck disable=SC2181
    if [ $? -ne 0 ]; then
        echo "Error: Failed to change directory to $repo_path"
        return 1
    fi

    # Get the current Git tag
    local current_tag
    current_tag=$(git describe --tags --exact-match 2>/dev/null)

    # Restore the original directory
    popd > /dev/null 2>&1

    # Check if the current tag is 2.0
    if [ "$current_tag" = "$target_tag" ]; then
        echo "Current Git tag in $repo_path is $target_tag"
    else
        echo "Error: Current Git tag in $repo_path is not $target_tag"
        exit 1
    fi
}



if [ -z "$1" ]; then
  echo "Usage: $0 <democlan>"
  exit 1
fi

democlan="$1"

check_git_tag "$democlan" "v2.2"

check_git_tag "." "demo-v2.3"

rm -rf ~/.config/clan

clan history add "clan://$democlan#localsend-wayland1"

clear
cat << EOF
Open up this link in a browser:
"clan://$democlan#localsend-wayland2"
EOF
