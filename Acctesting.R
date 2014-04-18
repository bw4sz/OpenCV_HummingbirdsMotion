###Motion Threshold Testing
require(reshape)
require(pROC)
require(ggplot2)

###read in data
droppath<-"C:/Users/Jorge/Dropbox/"
dat<-read.csv(paste(droppath,"Thesis/Automated_Monitering/MotionTest.csv",sep=""))

#Bring in observer reviewed data
obsdat<-read.csv(paste(droppath,"Thesis/Maquipucuna_SantaLucia/Data2013/csv/FlowerVideo.csv",sep=""))

##Total Number of frames need to be entered by hand.
##Find number of frames
###Video FL80 has 14385 frames
Totalframes<-matrix(nrow=10,ncol=2)
colnames(Totalframes)<-c("Video","Frames")
Totalframes[1,]<-c("FL080","14385")

###Find number of returned "positive" frames for each video
#set file directory. 

#add directory to this list
FLID<-c("FL080/130727AA/","FL081/130727AA")

##loop through outputs from video
returned<-lapply(FLID,function(x){
  RAN<-seq(.2,.6,.05)
  filelength<-lapply(RAN,function(a){
    fileD<-capture.output(cat("F:/AutomatedTests",a,"Flowers",x,sep="/"))
    length(list.files(fileD))
  })
  names(filelength)<-RAN
  filelength<-data.frame(rbind(strsplit(x,"/")[[1]]),melt(filelength))
  colnames(filelength)<-c("ID","Video","Returned","AccAVG")
  return(filelength)
})

head(dat)

##Find number of feeding events for automated and reviewed data
datEvents<-aggregate(dat$Flower,list(dat$ID,dat$Video,dat$AccAVG),length)
colnames(datEvents)<-c("ID","Video","AccAVG","Auto_Events")

obsEvents<-aggregate(obsdat$Flower,list(obsdat$ID,obsdat$Video),length)
colnames(obsEvents)<-c("ID","Video","Obs_Events")

#merge frames together
alld<-merge(obsEvents,datEvents,by=c("ID","Video"))

ggplot(alld,aes(x=AccAVG,y=Auto_Events/Obs_Events,col=ID)) + geom_line(aes(group=ID)) + ylim(0,1.5)
