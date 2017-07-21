#!/bin/bash

if [ "$OSTYPE" = "msys" ]; then
	CMD="py -3"
else
	CMD="python3"
fi

$CMD "$(dirname "$0")/repos.py" "$@"
