#!/bin/bash

shopt -s extglob

BASE_DIR=$(pwd)
SCM=

type -p bzr &> /dev/null && SCM="bzr $SCM"
type -p hg  &> /dev/null && SCM="hg  $SCM"
type -p svn &> /dev/null && SCM="svn $SCM"
type -p git &> /dev/null && SCM="git $SCM"

function get_absolute_path
{
	pushd "$1" > /dev/null
	pwd
	popd > /dev/null
}

function has_repos
{
	[ -d "$1" -a "$1" != "${1/%repos-*([^\/])/}" ]
}

function printable_dir
{
	echo ${1/#$BASE_DIR*(\/)/}
}

function update_repo
{
	local DIR="$1"
	local DIRP=$(printable_dir "$DIR")
	pushd "$DIR" > /dev/null

	for TYPE in $SCM; do
		if [ -d ".${TYPE}" ]; then
			case "$TYPE" in
				'git')
					echo "git pull ${DIRP} ..."
					git pull
					;;
				'svn')
					echo "svn update ${DIRP} ..."
					svn update
					;;
				'hg')
					echo "hg pull -u ${DIRP} ..."
					hg pull -u
					;;
				'bzr')
					echo "bzr update ${DIRP} ..."
					bzr update
					;;
			esac

			break
		fi
	done

	popd > /dev/null
}

function get_repo_url
{
	local DIR="$1"
	local DIRP=$(printable_dir "$DIR")
	pushd "$DIR" > /dev/null

	for TYPE in $SCM; do
		if [ -d ".${TYPE}" ]; then
			local URL=

			case "$TYPE" in
				'git')
					URL=$(git config remote.origin.url)
					;;
				'svn')
					URL=$(svn info | awk '/^URL: / { print $2 }')
					;;
				'hg')
					URL=$(hg showconfig paths.default)
					;;
				'bzr')
					URL=$(bzr config bound_location)
					;;
			esac

			[ ! -z "$URL" ] && printf "%-3s %s\n%4s%s\n" "$TYPE" "$DIRP" "" "$URL"

			break
		fi
	done

	popd > /dev/null
}

function repo_action
{
	local ACTION=$1
	local DIR="$2"
	pushd "$DIR" > /dev/null

	for FILE in `ls`; do
		[ ! -d "$FILE" ] && continue

		local PROJ_DIR="${DIR}/${FILE}"

		if has_repos "$PROJ_DIR"; then
			repo_action $ACTION "$PROJ_DIR"
		else
			$ACTION "$PROJ_DIR"
		fi
	done

	popd > /dev/null
}

ACTION=
case "$1" in
	'update')
		ACTION=update_repo
		;;
	'urls')
		ACTION=get_repo_url
		;;
	*)
		echo "Invalid action: $1"
		exit 1
		;;
esac

DIR="$2"
if [ ! -z "$DIR" -a ! -d "$DIR" ]; then
	echo "Invalid directory: $DIR"
	exit 1
elif [ -z "$DIR" ]; then
	DIR=$(pwd)
fi

repo_action $ACTION $(get_absolute_path "$DIR")