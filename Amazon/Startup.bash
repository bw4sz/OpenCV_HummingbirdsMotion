#!/bin/bash 

# spawn instance and store id, need a larger default block size
instance_id=$(aws ec2 run-instances --image-id ami-5ec1673e --security-group-ids sg-923a98f6 --count 1 --instance-type t2.micro --key-name rstudio --instance-initiated-shutdown-behavior stop --query 'Instances[0].{d:InstanceId}' --output text --iam-instance-profile Name="Ben" --block-device-mappings '[{"DeviceName":"/dev/sdb","Ebs":{"VolumeSize":12,"DeleteOnTermination":false,"VolumeType":"standard"}}])

# wait until instance is up and running
aws ec2 wait instance-running --instance-ids $instance_id

#add name tag
aws ec2 create-tags --resources $instance_id --tags Key=Name,Value=MotionMeerkat

#cloudwatch monitor
aws cloudwatch put-metric-alarm --alarm-name cpu-mon --alarm-description "Alarm when CPU drops below 2 over 10 minutes%" --metric-name CPUUtilization --namespace AWS/EC2 --statistic Average --period 300 --threshold 2 --comparison-operator LessThanThreshold  --dimensions Name=InstanceId,Value=$instance_id --evaluation-periods 2 --alarm-actions arn:aws:sns:us-west-2:477056371121:Instance_is_idle --unit Percent
aws cloudwatch put-metric-alarm --alarm-name memory --alarm-description "Alarm when Memory rate exceeds 90%%" --metric-name MemoryUtilization --namespace System/Linux --statistic Average --period 300 --threshold 90 --comparison-operator GreaterThanThreshold  --dimensions Name=InstanceId,Value=$instance_id --evaluation-periods 2 --alarm-actions arn:aws:sns:us-west-2:477056371121:Instance_is_idle --unit Percent

# retrieve public dns
dns=$(aws ec2 describe-instances --instance-ids $instance_id --query 'Reservations[*].Instances[*].PublicDnsName' --output text | grep a)

#Wait for port to be ready, takes about a minute.
sleep 50

# copy over Job.bash to instance
scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i '/c/Users/Ben/.ssh/rstudio.pem' /c/Users/Ben/Documents/OpenCV_HummingbirdsMotion/Amazon/RunMotionMeerkat.bash ec2-user@$dns:~

# run job script on instance, don't wait for finish and disconnect terminal
#add nohup and & if you like
time ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i "/c/Users/Ben/.ssh/rstudio.pem" ubuntu@$dns "nohup ./RunMotionMeerkat.bash"
