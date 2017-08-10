#!/bin/bash

if [ "$OSTYPE" = "msys" ]; then
	CMD="py -3"
else
	CMD="python3"
fi

$CMD "$(dirname "$(readlink -f "$0")")/repos.py" "$@"
