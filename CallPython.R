##Call python from R

list.files("C:/Users/Office653-1/Dropbox/VideosforBen/NRPLOTS/OBS18")
runtype<-"file"
inDEST<-"C:/Users/Office653-1/Dropbox/VideosforBen/NRPLOTS/OBS18/18B.MPG"
fileD<-"C:/Users/Jorge/Dropbox/VideosforBen/"
accAVG<-0.5

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG,'False'))

system(commandC,intern=TRUE,show.output.on.console=TRUE)

#If you need to kill
@system("TASKKILL /IM python*")


##loop through accAVG
for (a in seq(.3,.6,.1)){
  runtype<-"file"
  inDEST<-"C:/Users/Office653-1/Dropbox/VideosforBen/NRPLOTS/OBS18/18B.MPG"
  fileD<-paste("C:/Users/Jorge/Dropbox/VideosforBen/",paste(a,"/",sep=""),sep="")
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
