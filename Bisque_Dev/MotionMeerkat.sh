#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
echo "./dist/MotionMeerkat $@"

exec ./dist/MotionMeerkat $@

