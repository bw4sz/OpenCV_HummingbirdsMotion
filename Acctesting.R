###Motion Threshold Testing
require(reshape)
require(pROC)

###read in data
droppath<-"C:/Users/Jorge/Dropbox/"
dat<-read.csv(paste(droppath,"Thesis/Automated_Monitering/MotionTest.csv",sep=""))

##Find number of frames
###Video FL80 has 14385 frames

#set file directory. 

FLID<-"FL080/130727AA/"
##loop through accAVG
RAN<-seq(.2,.6,.05)
filelength<-lapply(RAN,function(a){
  fileD<-capture.output(cat("F:/AutomatedTests",a,"Flowers",FLID,sep="/"))
  length(list.files(fileD))
  })
names(filelength)<-RAN
filelength<-data.frame(rbind(strsplit(FLID,"/")[[1]]),melt(filelength))

colnames(filelength)<-c("ID","Video","Returned","AccAVG")

##merge with data
datm<-merge(dat,filelength,by=c("ID","Video","AccAVG"))
