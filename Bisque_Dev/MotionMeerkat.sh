#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/Motion $@"

exec ./dist/Motion $@

