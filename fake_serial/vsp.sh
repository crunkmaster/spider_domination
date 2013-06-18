#!/bin/bash
echo "creating COM ports at $1 and $2"
socat PTY,link=$1 PTY,link=$2
