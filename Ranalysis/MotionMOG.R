###Motion Detection R Analysis###
require(chron)
require(scales)
require(ggplot2)
require(stringr)
require(plyr)
require(reshape2)
##get data

fil<-list.files("C:/Users/Ben/Desktop/MotionMeerkatTest/",full.names=TRUE,pattern="Frames.csv",recursive = T)

d<-lapply(fil,function(a){
dat<-read.csv(a)
nrow(dat)
#History
Detector<-str_match(a,"Ben.Desktop.MotionMeerkatTest..(\\w+)")[2]

MOGN<-as.numeric(str_match(a,"Ben.Desktop.MotionMeerkatTest..\\w+.(\\w+)")[2])

#File name
fnm<-str_match(a,"Ben.Desktop.MotionMeerkatTest..\\w+.\\w+.\\w+.(\\w+)")[2]

#Subtractor type
data.frame(File=fnm,value=MOGN,Returned=nrow(dat),Detector)
})

d<-rbind.fill(d)


ggplot(d,aes(col=Detector,x=value,y=Returned)) + facet_wrap(~File,scales="free",nrow=3) + geom_line(aes(group=Detector)) + geom_point(size=3) + theme_bw()

#How many frames in each file
File<-c("00011","garcon_test","Rees","MoyTest","Schiavicci")
Feature<-c("Low Frame Rate - Deep Water","High Frame - Pelagic Baited Camera","High Frame Rate - Shallow Baited Camera","High Frame Rate - Avian Nest Box","Low Frame Rate - Avian Nest Camera")
Total<-c(2987,9401,10454,1608,55417)

m<-data.frame(File,Total,Feature)

f<-merge(d,m)

head(f)

f$PReturned<-f$Returned/f$Total

#Create labels with the correct levels
f$DetectorLabel<-factor(paste(f$Detector,f$value),levels=c('Acc 15',"Acc 25", "Acc 35" ,"MOG 100","MOG 500","MOG 1000","MOG 1500","MOG 2000"))

p<-ggplot(f,aes(col=Detector,x=DetectorLabel,y=PReturned)) + facet_wrap(~Feature,nrow=2) + geom_point(size=4) + geom_line(aes(group=Detector)) + theme_bw()
p+scale_y_continuous(labels=percent,limits=c(0,1)) + labs(x="Background Subtractor",y="Total Frames Returned")

save.image("Sensitivity.Rdata")