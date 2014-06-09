###Summer Network from automated workflow

###############################################################################
#Hummingbird Flower Interactions at the Santa Lucia and Maquipucuna EcoReserves
###############################################################################
#Ben Weinstein - Stony Brook University - Department of Ecology and Evolution

require(chron)
require(bipartite)
require(ggplot2)
require(ape)
require(reshape)
require(sna)
require(stringr)
require(maptools)
require(taxize)

#Set droppath
droppath<-"C:/Users/Ben/Dropbox/"

#Set Gitpath
gitpath<-"C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/"


##Load in data if rerun
load(paste("gitpath","network.RData"))

###################
#Source Functions
###################

############################################
##############Read In Data##################
############################################

###Read in Flower Camera Dataset####
dat<-read.csv(paste(droppath,"Thesis/Automated_Monitering/FlowerVideoAuto.csv",sep=""))

#Fix date format
dat$Month<-as.numeric(format(as.Date(dat$Date,"%m/%d/%Y"),"%m"))

#bring in clade data
clades<-read.csv("C:/Users/Ben/Documents/Maquipicuna/InputData//CladeList.txt",header=FALSE)[,-1]
colnames(clades)<-c("Clade","Genus","Species","double","English")
clades<-clades[,1:5]

############################################
##############Data Import Complete##########
############################################

###########################
#Hummingbird Data Cleaning 
###########################
.simpleCap <- function(x) {
  s <- strsplit(x, " ")[[1]]
  paste(toupper(substring(s, 1, 1)), substring(s, 2),
        sep = "", collapse = " ")
}

#Caps Hummingbird
dat$Hummingbird<-factor(sapply(dat$Hummingbird,function(x) {.simpleCap(as.character(x))}))

#make a object, just to save typing
h<-levels(dat$Hummingbird)

#look up taxize english names?
missp<-h[!h %in% clades$English]

paste("misspelled levels",missp)
h[h %in% missp]

head(clades)

###Data Cleaning Plants###########

#Iplant<-tnrs(levels(dat$Flower)[-1],stripauthority=TRUE,resolve_once=TRUE)

#get family names?
#classification(Iplant)

#tax_name(query = Iplant, get = "family", db = "ncbi")

#################Data Cleaning Complete################


#########Descriptive Stats
#Final levels
print(paste("Final Flower Species:", levels(factor(dat$Flower))))

#How many Birds Species
#print(paste("Number of Hummingbird Species:",nlevels(dat$Hummingbird)))
print(paste("Final Hummingbird Species:",levels(dat$Hummingbird)))


#Take our any bad data
dat_e<-droplevels(dat[!dat$Hummingbird %in% c("","NANA","UKWN","Ukwn","Western Emerald"),])


print("data cleaned")

############################################
#Run Network Function for the entire dataset

#Drop any unused factors?
datf<-droplevels(dat_e)

h<-levels(datf$Hummingbird)

#turn to sceintific name
sc<-clades[clades$English %in% h,c("English","double")]

#replace levels
replace_name<-sapply (1:length(h),function(x){
  repl<-sc[sc$English %in% h[x],"double"]
})

levels(datf$Hummingbird)<-replace_name

#Interaction of flowers and birds
F_H<-as.data.frame.array(table(datf$Flower,datf$Hummingbird))
# abbreviate names?
# #species
# spec<-word(rownames(F_H),sep=" ",-1)
# 
# #genus
# gen<-substr(word(rownames(F_H),sep=" "),1,6)
# rownames(F_H)<-paste(gen,spec,sep=".")


plotweb(F_H)


visweb(F_H,type="nested")

rm(birds.prop)

#Metrics across entire
tryCatch(birds.prop<-data.frame(HummingbirdNetwork=networklevel(F_H,level="higher")),error=function(e)
  print(e))


#Network prop for plants
#Metrics across entire
tryCatch(plants.prop<-data.frame(HummingbirdNetwork=networklevel(F_H,level="lower")),error=function(e)
  print(e))

#Merge networks
NetworkProp<-data.frame(birds.prop,plants.prop)

#Metrics across species, write to file
tryCatch(H.species.prop<-specieslevel(F_H,level="higher"),error = function(e) {
  print(paste("Not enough Species:",e))})

if(!exists("H.species.prop")){
  return("Not Enough Hummingbird Species")
}

#Hummingbird Properties


#Plant Network Metrics  
#Metrics across species, write to file
tryCatch(P.species.prop<-specieslevel(F_H,level="lower"),error = function(e) {
  print(paste("Not enough plant Species:",e))})
}
###################################
#Specialization for each species
##################################################

birds.special<-dfun(t(F_H))
birds.spl<-data.frame(lapply(birds.special,data.frame))
colnames(birds.spl)<-names(birds.special)
birds.spl$Species<-rownames(birds.spl)

#size by sample size?

ggplot(birds.spl,aes(x=Species,y=dprime)) + geom_point() + theme_bw() + theme(axis.text.x=element_text(angle=90))
ggsave("Specialization.svg",height=8,width=9)

############################################


orderflowers<-names(sort(apply(F_H,1,sum),decreasing=FALSE))

orderbirds<-names(sort(apply(F_H,2,sum),decreasing=TRUE))

a<-melt(as.matrix(F_H))

colnames(a)<-c("Flowers","Birds","value")

a$Flowers<-factor(a$Flowers,levels=orderflowers)
a$Birds<-factor(a$Birds,levels=orderbirds)

ggplot(a[a$value>0,],aes(x=Birds,y=Flowers,fill=value)) + geom_tile()+ theme_bw() + scale_fill_continuous(low="blue",high="red") + theme(axis.text.x = element_text(angle = 90, hjust = 1)) + labs(fill="# of Visits")
ggsave(paste(droppath,"Thesis/Automated_Monitering/Figures/MatrixPlot.jpeg",sep=""),dpi=600,height=6.5,width=7)
ggsave(paste(droppath,"Thesis/Automated_Monitering/Figures/MatrixPlot.eps",sep=""),dpi=600,height=6.5,width=7)
