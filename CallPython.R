##Call python from R

runtype<-"file"
inDEST<-"F:/Summer2013flowers/SantaLucia/Flowers/FL080/130727AA.TLV"
fileD<-"F:/AutomatedTests/"
accAVG<-.35

commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))

system(commandC,intern=TRUE,show.output.on.console=TRUE)

#If you need to kill
system("TASKKILL /IM python*")


##loop through accAVG
for (a in seq(.2,.4,.05)){
  runtype<-"file"
  inDEST<-"F:/Summer2013flowers/SantaLucia/Flowers/FL080/130727AA.TLV"
  fileD<-paste("F:/AutomatedTests/",paste(a,"/",sep=""),sep="/")
  accAVG<-a
  commandC<-capture.output(cat("python motion.py",runtype,inDEST,fileD,accAVG))
  system(commandC,intern=TRUE,show.output.on.console=TRUE)
}