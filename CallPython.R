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
for (a in seq(.01,.03,.005)){
  runtype<-"file"
  inDEST<-"C:/Users/Office653-1/Dropbox/VideosforBen/NRPLOTS/OBS18/18C.MPG"
  fileD<-paste("C:/Users/Office653-1/Dropbox/VideosforBen/",paste(a,"/",sep=""),sep="")
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
