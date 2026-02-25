# shellcheck shell=bash
set -euo pipefail

if [[ $# = 0 ]]; then
	set -- dev
fi
case $1 in
dev)
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
		pnpm install
	fi
	if [[ -n $browser ]]; then
		set -- --open
	fi
	pnpm run dev -- "$@"
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
		pnpm install
	fi
	pnpm run build
	if [[ -n $serve ]]; then
		if [[ -n $browser ]]; then
			set -- -o
		fi
		pnpm run preview -- "$@"
	fi
	;;
lint)
	if [[ ! -e node_modules ]]; then
		pnpm install
	fi
	pnpm run prelint
	pnpm run "/^lint:.+/"
	;;
esac
