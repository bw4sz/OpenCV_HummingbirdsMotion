###Motion Threshold Testing

#load packages
require(reshape)
require(pROC)
require(ggplot2)

###read in data
droppath<-"C:/Users/Jorge/Dropbox/"
dat<-read.csv(paste(droppath,"Thesis/Automated_Monitering/MotionTest.csv",sep=""))

#Bring in observer reviewed data
obsdat<-read.csv(paste(droppath,"Thesis/Maquipucuna_SantaLucia/Data2013/csv/FlowerVideo.csv",sep=""))

#Bring in .35 adapt data
Adat<-read.csv(paste(droppath,"Thesis/Automated_Monitering/FlowerVideoAuto.csv",sep=""))

##############
  
##Total Number of frames need to be entered by hand.

##Find number of frames
###Video FL80 has 14385 frames
Totalframes<-data.frame(ID=NA,Total=NA)

Totalframes[1,colnames(Totalframes)]<-c("FL080","14385")
Totalframes[2,colnames(Totalframes)]<-c("FL081","14386")
Totalframes[3,colnames(Totalframes)]<-c("FL098","14385")
Totalframes[4,colnames(Totalframes)]<-c("FL061","14384")
Totalframes[5,colnames(Totalframes)]<-c("FL060","14386")
Totalframes[6,colnames(Totalframes)]<-c("FL103","21586")

###Find number of returned "positive" frames for each video
#set file directory. 

#add directory to this list
FLID<-unique(paste(dat$ID,dat$Video,sep="/"))

##loop through outputs from testing video
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

frame_count<-melt(returned)
colnames(frame_count)<-c("ID","Video","AccAVG","variable","frames","L1")


#find number of returned frames in adapted data
returnedAdapt<-lapply(FLID,function(x){
  print(x)
  fileD<-capture.output(cat("F:/Summer2013flowers/AutoNetwork/",x,sep="/"))
  filelength<-length(list.files(fileD))
  filelength<-data.frame(rbind(strsplit(x,"/")[[1]]),melt(filelength))
  colnames(filelength)<-c("ID","Video","Adaptive AccAVG")
  return(filelength)
})

frame_countAdapt<-melt(returnedAdapt)
colnames(frame_countAdapt)<-c("ID","Video","Adapt","framesAdapt","L1")

##Find number of feeding events for automated and reviewed data
datEvents<-aggregate(dat$Flower,list(dat$ID,dat$Video,dat$AccAVG),length)
colnames(datEvents)<-c("ID","Video","AccAVG","Auto_Events")

obsEvents<-aggregate(obsdat$Flower,list(obsdat$ID,obsdat$Video),length)
colnames(obsEvents)<-c("ID","Video","Obs_Events")

adaptEvents<-aggregate(Adat$Flower,list(Adat$ID,Adat$Video),length)
colnames(adaptEvents)<-c("ID","Video","Adapt_Events")

#merge frames together
alld<-merge(obsEvents,datEvents,by=c("ID","Video"))

allE<-merge(alld,adaptEvents,by=c("ID","Video"))

#merge with positive frame call
frame_all<-merge(allE,frame_count,by=c("ID","Video","AccAVG"))

#merge with total number of frames in the video
fdat<-merge(frame_all,Totalframes,by="ID")

fdat_all<-merge(fdat,frame_countAdapt,by=c("ID","Video"))

require(scales)

#plot performance
p<-ggplot(fdat_all,aes(x=frames/as.numeric(Total),y=Auto_Events/Obs_Events,col=AccAVG)) + geom_point(size=3) + geom_line(aes(group=ID)) + ylim(0,1.5) + facet_wrap(~ID,scales="free_x") + xlab("Percentage of Total Images Returned") + ylab("Percetange of Events Captured") + labs(col="AccAVG Parameter") 
p<-p + scale_y_continuous(labels = percent_format()) + scale_x_continuous(labels = percent_format()) + scale_colour_gradient(low="blue",high="red",limits=c(.2,.6),breaks=seq(.2,.6,.05)) + theme_bw()

#add adapt events, make two color object
p<- p + geom_point(aes(x=framesAdapt/as.numeric(Total),y=Adapt_Events/Obs_Events,fill=Adapt),col="black",shape=22,size=3.5) + scale_fill_manual(values="yellow") + labs(fill="")
p
ggsave(paste(droppath,"Thesis/Automated_Monitering/Figures/Sensitivity.jpg",sep=""),dpi=300,height=6,width=10)
ggsave(paste(droppath,"Thesis/Automated_Monitering/Figures/Sensitivity.eps",sep=""),dpi=300,height=4.5,width=7.5)
