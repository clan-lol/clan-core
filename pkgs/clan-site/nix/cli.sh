# shellcheck shell=bash
set -euo pipefail

if [[ -n "${CLAN_SITE_DIR:-}" ]]; then
	cd "$CLAN_SITE_DIR"
fi

# Remove generated files
# So we don't need to clean by hand when a markdown file is renamed or deleted
clean_routes() {
	if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		git clean -fdx -- src/routes/
	fi
}

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
	clean_routes
	if [[ -n $browser ]]; then
		set -- --open
	fi
	pnpm run dev -- "$@"
	;;
build)
	shift

	if [[ ! -e node_modules ]]; then
		pnpm install
	fi
	clean_routes
	pnpm run build
	;;
lint)
	shift
	arg=$(getopt -n clan-site -o '' -l 'fix' -- "$@")
	eval set -- "$arg"
	unset arg
	fix=''
	while true; do
		case $1 in
		--fix)
			fix=1
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
	clean_routes
	pnpm run prelint
	if [[ -z $fix ]]; then
		pnpm run "/^lint:.+/"
	else
		pnpm run lint-fix
	fi
	;;
esac
