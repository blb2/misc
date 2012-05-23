#!/bin/bash

shopt -s extglob

BASE=$(pwd)
TOOLS=

type -p hg  &> /dev/null && TOOLS="hg  $TOOLS"
type -p svn &> /dev/null && TOOLS="svn $TOOLS"
type -p git &> /dev/null && TOOLS="git $TOOLS"

function update
{
	local CWD=$(pwd)
	local DIR=${CWD/#$BASE*(\/)/}

	[ ! -z "$DIR" ] && DIR="${DIR}/"

	for PROJ in `ls`; do
		local FOUND=false

		for SCM in $TOOLS; do
			if [ -d "$PROJ" -a -d "${PROJ}/.${SCM}" ]; then
				pushd "$PROJ" > /dev/null

				case "$SCM" in
					'git')
						echo "git pull ${DIR}${PROJ} ..."
						git pull
						;;
					'svn')
						echo "svn update ${DIR}${PROJ} ..."
						svn update
						;;
					'hg')
						echo "hg update ${DIR}${PROJ} ..."
						hg update
						;;
				esac

				popd > /dev/null

				FOUND=true
				break
			fi
		done

		if ! $FOUND && [ -d "$PROJ" ]; then
			pushd "$PROJ" > /dev/null
			update
			popd > /dev/null
		fi
	done
}

[ ! -z "$TOOLS" ] && update
