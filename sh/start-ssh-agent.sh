#!/bin/bash

if [ "$0" = "$BASH_SOURCE" ]; then
    echo Please source this script: source $0
    exit
fi

SSH_ENV="$HOME/.ssh/environment"

function start_ssh_agent {
	echo "initializing new ssh-agent..."
	(umask 066; ssh-agent > "$SSH_ENV")
	source "$SSH_ENV" > /dev/null
	ssh-add
}

function test_ssh_id {
	ssh-add -l | grep "The agent has no identities" > /dev/null
	if [ $? -eq 0 ]; then
		ssh-add
		[ $? -eq 2 ] && start_ssh_agent
	fi
}

if [ -n "$SSH_AGENT_PID" ]; then
	ps -ef | grep "$SSH_AGENT_PID" | grep ssh-agent > /dev/null
	[ $? -eq 0 ] && test_ssh_id
else
	[ -f "$SSH_ENV" ] && source "$SSH_ENV" > /dev/null

	ps -ef | grep "$SSH_AGENT_PID" | grep -v grep | grep ssh-agent > /dev/null

	if [ $? -eq 0 ]; then
		test_ssh_id
	else
		start_ssh_agent
	fi
fi
