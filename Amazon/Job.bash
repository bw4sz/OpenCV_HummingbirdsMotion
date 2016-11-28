#!/bin/bash 

#clean temp file for memory utility
rm -rf /var/tmp/aws-mon.bak
mv /var/tmp/aws-mon /var/tmp/aws-mon.bak

#clone
git clone git@github.com:bw4sz/WhaleShape.git --depth 1

cd WhaleShape||sudo halt

#make new branch
#name it the instance ID
iid=$(ec2metadata --instance-id)

git checkout -b $iid

#render script
Rscript -e "rmarkdown::render('DynamicForaging.Rmd')" &> run.txt

#push results
git add --all
git commit -m "ec2 run complete"
git push -u origin $iid

#kill instance
sudo halt
