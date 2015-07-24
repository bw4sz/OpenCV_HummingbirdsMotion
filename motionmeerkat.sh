#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/motionmeerkat $@"

exec ./dist/motionmeerkat $@

