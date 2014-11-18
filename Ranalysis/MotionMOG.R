###Motion Detection R Analysis###
require(chron)
require(scales)
require(ggplot2)
require(stringr)
require(plyr)
require(reshape2)
##get data

setwd("C:/Users/Ben/Dropbox/Thesis/Automated_Monitering/Figures/")
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
Feature<-c("Low Light - Deep Water","Slow Moving Animal - Pelagic Baited Camera","Low Visibility - Shallow Baited Camera","Variable Background - Avian Nest Box","Low Frame Rate - Avian Nest Camera")
Total<-c(2987,6415,1609,1609,44963)
True<-c(1202,3468,546,873,1794)

m<-data.frame(File,Total,Feature,True)

#Rees
f<-merge(d,m)

head(f)

f$PReturned<-f$Returned/f$Total

#round
f$PR<-round(f$PReturned,2)

#True ratio
f$TR<-f$True/f$Total

#relevel the decimals for acc

#Create labels with the correct levels
f$DetectorLabel<-paste(f$Detector,f$value)

f$DetectorLabel[f$DetectorLabel %in% "Acc 15"]<-"Acc .15"
f$DetectorLabel[f$DetectorLabel %in% "Acc 25"]<-"Acc .25"
f$DetectorLabel[f$DetectorLabel %in% "Acc 35"]<-"Acc .35"

#reorder
f$DetectorLabel<-factor(f$DetectorLabel,levels=c('Acc .15',"Acc .25", "Acc .35" ,"MOG 100","MOG 500","MOG 1000","MOG 1500","MOG 2000"))




p<-ggplot(f,aes(col=Detector,x=DetectorLabel,y=PR,shape=Threshold)) + facet_wrap(~Feature,nrow=3,scales="free") + geom_point(size=5) + theme_bw()
p<-p + labs(x="Background Subtractor",y="Total Frames Returned")
p + geom_hline(aes(yintercept=TR),linetype='dashed',size=.75,col="black") + scale_y_continuous(labels=percent)
ggsave("Figure3.jpg",dpi=400,height=9.5,width=13.5)
ggsave("Figure3.tiff",dpi=400,height=9.5,width=13.5)

ggsave("Figure3.eps",dpi=300,height=5,width=8)

save.image("Sensitivity.Rdata")
