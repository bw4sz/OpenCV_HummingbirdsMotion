#!/bin/sh
echo "HOSTNAME"
hostname

echo "ENV"
printenv

echo "command"
#echo "./dist/motionmeerkat $@"

python ./MotionMeerkat/main.py $@

