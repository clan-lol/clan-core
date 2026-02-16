# shellcheck shell=bash
set -euo pipefail

case ${1-} in
"" | dev)
	shift
	arg=$(getopt -n clan-site -o 'b' -- "$@")
	eval set -- "$arg"
	unset arg
	browser=''
	while true; do
		case $1 in
		-b)
			browser=1
			shift
			;;
		--)
			shift
			break
			;;
		*)
			echo >&2 "Unknown flag $1"
			exit 1
			;;
		esac
	done

	if [[ ! -e node_modules ]]; then
		npm install
	fi
	if [[ -n $browser ]]; then
		set -- --open
	fi
	npm run dev -- "$@"
	;;
build)
	shift
	arg=$(getopt -n clan-site -o 'bs' -- "$@")
	eval set -- "$arg"
	unset arg
	browser=''
	serve=''
	while true; do
		case $1 in
		-b)
			browser=1
			serve=1
			shift
			;;
		-s)
			serve=1
			shift
			;;
		--)
			shift
			break
			;;
		*)
			echo >&2 "Unknown flag $1"
			exit 1
			;;
		esac
	done

	if [[ ! -e node_modules ]]; then
		npm install
	fi
	npm run build
	if [[ -n $serve ]]; then
		if [[ -n $browser ]]; then
			set -- -o
		fi
		npm run preview -- "$@"
	fi
	;;
esac
