#To run on ec2 startup

#install docker
sudo yum -y install  docker 

#start docker
sudo service docker start

#Pull MotionMeerkat
sudo docker pull bw4sz/bw4sz:MotionMeerkat

#Run MotionMeerkat Container
sudo docker run -it bw4sz/bw4sz:MotionMeerkat

#cd home
cd ~
#Run MotionMeerkat
python OpenCV_HummingbirdsMotion/MotionMeerkat/main.py --i ~/OpenCV_HummingbirdsMotion/PlotwatcherTest.tlv --fileD ~/MotionMeerkat

#grab the logs
cd MotionMeerkat

#exit docker 
exit

#kill run
sudo halt
