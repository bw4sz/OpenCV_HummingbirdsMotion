##Call python from R

list.files("C:/Users/Office653-1/Dropbox/VideosforBen/")
runtype<-"batch"
inDEST<-"C:/Users/Office653-1/Dropbox/VideosforBen/"
fileD<-"C:/Users/Office653-1/Dropbox/VideosforBen/"
accAVG<-0.4

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG,'False'))

system.time(outC<-system(commandC,intern=TRUE,show.output.on.console=TRUE))
outC

#If you need to kill
@system("TASKKILL /IM python*")

##loop through accAVG
for (a in seq(.2,.6,.05)){
  runtype<-"file"
  inDEST<-"F:/Summer2013flowers/Maqui/Flowers/FL103/130815AA.TLV"
  fileD<-paste("F:/AutomatedTests/",paste(a,"/",sep=""),sep="")
  accAVG<-a
  commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG,'False'))
  system(commandC,intern=TRUE,show.output.on.console=TRUE)
}


runtype<-"file"
inDEST<-"C:/Users/Jorge/Dropbox/Plotwatcher_Photos_AZ_Hummingbirds/130802AA.TLV"
fileD<-"C:/Users/Jorge/Dropbox/Plotwatcher_Photos_AZ_Hummingbirds"
accAVG<-0.4

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))

system(commandC,intern=TRUE,show.output.on.console=TRUE)
