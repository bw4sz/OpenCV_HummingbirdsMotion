##Call python from R

list.files("C:/Users/Jorge/Dropbox/VideosforBen/")
runtype<-"file"
inDEST<-"C:/Users/Jorge/Dropbox/VideosforBen/OBS_22.mp4"
fileD<-"C:/Users/Jorge/Dropbox/VideosforBen/"
accAVG<-0.5

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))

system(commandC,intern=TRUE,show.output.on.console=TRUE)

#If you need to kill
@system("TASKKILL /IM python*")


##loop through accAVG
for (a in seq(.2,.6,.05)){
  runtype<-"file"
  inDEST<-"F:/Summer2013flowers/SantaLucia/Flowers/FL098/130812AA.TLV"
  fileD<-paste("F:/AutomatedTests/",paste(a,"/",sep=""),sep="")
  accAVG<-a
  commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))
  system(commandC,intern=TRUE,show.output.on.console=TRUE)
}


runtype<-"file"
inDEST<-"C:/Users/Jorge/Dropbox/Plotwatcher_Photos_AZ_Hummingbirds/130802AA.TLV"
fileD<-"C:/Users/Jorge/Dropbox/Plotwatcher_Photos_AZ_Hummingbirds"
accAVG<-0.4

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))

system(commandC,intern=TRUE,show.output.on.console=TRUE)
