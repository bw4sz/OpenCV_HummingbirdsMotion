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
#History

Threshold<-str_match(a,"Ben.Desktop.MotionMeerkatTest..(\\w+)")[2]

Detector<-str_match(a,"Ben.Desktop.MotionMeerkatTest..\\w+.(\\w+)")[2]

MOGN<-as.numeric(str_match(a,"Ben.Desktop.MotionMeerkatTest..\\w+.\\w+.(\\w+)")[2])

#File name
fnm<-str_match(a,"Ben.Desktop.MotionMeerkatTest..\\w+.\\w+.\\w+.\\w+.(\\w+)")[2]

#Number of frames returned
r<-length(unique(dat$Frame))

data.frame(File=fnm,value=MOGN,Returned=r,Detector,Threshold)
})

d<-rbind.fill(d)


ggplot(d,aes(col=Detector,x=value,y=Returned)) + facet_wrap(~File,scales="free",nrow=3) + geom_line(aes(group=Detector)) + geom_point(size=3) + theme_bw()

#How many frames in each file
File<-c("00011","garcon_test","Rees","MoyTest","Schiavicci")
Feature<-c("Low Frame Rate - Deep Water","High Frame - Pelagic Baited Camera","High Frame Rate - Shallow Baited Camera","High Frame Rate - Avian Nest Box","Low Frame Rate - Avian Nest Camera")
Total<-c(2987,6415,1609,1609,55417)
True<-c(1202,0,546,873,0)

m<-data.frame(File,Total,Feature,True)

#Rees
(1-95) + (803-163)
f<-merge(d,m)

head(f)

f$PReturned<-f$Returned/f$Total

#round
f$PR<-round(f$PReturned,2)

#True ratio
f$TR<-f$True/f$Total

#Create labels with the correct levels
f$DetectorLabel<-factor(paste(f$Detector,f$value),levels=c('Acc 15',"Acc 25", "Acc 35" ,"MOG 100","MOG 500","MOG 1000","MOG 1500","MOG 2000"))

p<-ggplot(f,aes(col=Detector,x=DetectorLabel,y=PR,shape=Threshold)) + facet_wrap(~Feature,nrow=3,scales="free_y") + geom_point(size=5) + theme_bw()
p<-p + labs(x="Background Subtractor",y="Total Frames Returned")
p + geom_hline(aes(yintercept=TR),linetype='dashed',size=.75,col="black") + scale_y_continuous(labels=percent)
ggsave("SensitivityThreshold.jpg",dpi=300,height=9,width=13)
ggsave("SensitivityThreshold.eps",dpi=300,height=5,width=8)

save.image("Sensitivity.Rdata")
