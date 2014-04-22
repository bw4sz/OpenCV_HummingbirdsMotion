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
require(rPlant)
require(maptools)
require(taxize)

#Set droppath
droppath<-"C:/Users/Ben/Dropbox/"

#Set Gitpath
gitpath<-"C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/"

###################
#Source Functions
###################

############################################
##############Read In Data##################
############################################

###Read in Flower Camera Dataset####
dat<-read.csv(paste(droppath,"Thesis/Maquipucuna_SantaLucia/Data2013/csv/FlowerVideoClean.csv",sep=""),row.names=1)

#Get desired columns
dat<-dat[,colnames(dat) %in% c("ID","Video","Date","Iplant_Double","Time","Hummingbird","Sex","Temp","Piercing","lon","lat","ele")]

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

missp<-h[!h %in% clades$English]

paste("misspelled levels",missp)
h[h %in% missp]

spellC<-c("Fawn-breasted Brilliant","Gorgeted Sunangel","Tyrian Metaltail","UKWN","Violet-tailed Sylph")

paste("Spelling Correction",spellC)

h[h %in% missp]<-spellC

head(clades)
#can taxize do english names? 

levels(dat$Hummingbird) <- h

#Take our any bad data
dat_e<-droplevels(dat[!dat$Hummingbird %in% c("","NANA","UKWN","Ukwn","Western Emerald"),])

#Remove out piercing events for now?
table(dat$Piercing)
datPierce<-dat_e[dat_e$Piercing %in% c("Yes","YES"),]
dat_e<-dat_e[!dat_e$Piercing %in% c("Yes","YES"),]


#################Data Cleaning Complete################

#Final levels
print(paste("Final Flower Species:", levels(factor(dat_e$Iplant_Double))))

#How many Birds Species
print(paste("Number of Hummingbird Species:",nlevels(dat_e$Hummingbird)))
print(paste("Final Hummingbird Species:",levels(dat_e$Hummingbird)))

print("data cleaned")

############################################
#Run Network Function for the entire dataset

#Drop any unused factors?
datf<-droplevels(dat_e)

#Drop any observations without plants
datf<-droplevels(datf[!datf$Iplant_Double %in% "",])

#Interaction of flowers and birds
F_H<-as.data.frame.array(table(datf$Iplant_Double,datf$Hummingbird))

#species
spec<-word(rownames(F_H),sep="_",-1)

#genus
gen<-substr(word(rownames(F_H),sep="_"),1,2)
rownames(F_H)<-paste(gen,spec,sep=".")

#Save Input Matrix
write.csv(F_H,"BirdXFlower.csv")

#View Web
svg(filename="WebPlot.svg",height=7,width=15)
plotweb(F_H)
dev.off()

#create a order for hummingbirds
toOrd<-merge(clades,data.frame(English=colnames(F_H)),sort=FALSE,all.y=TRUE)$English

#create a order for plants
Hlab<-names(which(!apply(F_H,2,sum)==0))

toOrd<-as.character(merge(clades,data.frame(English=Hlab),sort=FALSE,all.y=TRUE)$English)

Plab<-names(which(!apply(F_H,1,sum)==0))

sequ<-list(seq.high=toOrd,seq.low=Plab)

svg(filename="Results/WebPlotOrder.svg",height=7,width=15)
plotweb(F_H,sequence=sequ)
dev.off()

jpeg(filename="Results/MatrixPlotCompartments.jpeg",res=300)
visweb(F_H,type="nested")
dev.off()

rm(birds.prop)

#Metrics across entire
tryCatch(birds.prop<-data.frame(HummingbirdNetwork=networklevel(F_H,level="higher")),error=function(e)
  print(e))

#Add in a flag if the network is just too small. 
if(!exists("birds.prop")){
  return("Not Enough Hummingbird Species")
}

#Network prop for plants
#Metrics across entire
tryCatch(plants.prop<-data.frame(HummingbirdNetwork=networklevel(F_H,level="lower")),error=function(e)
  print(e))

#Add in a flag if the network is just too small. 
if(!exists("plants.prop")){
  return("Not Enough Plant Species")
}

#Merge networks
NetworkProp<-data.frame(birds.prop,plants.prop)

#Write to file
write.csv(NetworkProp,"Results/NetworkProperties.csv")

#Metrics across species, write to file
tryCatch(H.species.prop<-specieslevel(F_H,level="higher"),error = function(e) {
  print(paste("Not enough Species:",e))})

if(!exists("H.species.prop")){
  return("Not Enough Hummingbird Species")
}

#Hummingbird Properties

write.csv(H.species.prop,"Results/HummingbirdMetrics.csv")


#Plant Network Metrics  
#Metrics across species, write to file
tryCatch(P.species.prop<-specieslevel(F_H,level="lower"),error = function(e) {
  print(paste("Not enough plant Species:",e))})

if(!exists("P.species.prop")){
  return("Not Enough Plant Species")
}

write.csv(P.species.prop,"Results/PlantMetrics.csv")

##################################################
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

jpeg(filename="Results/MatrixPlot.jpeg",res=300)
visweb(F_H,type="nested",labsize=1.5)
dev.off()

orderflowers<-names(sort(apply(F_H,1,sum),decreasing=FALSE))

orderbirds<-names(sort(apply(F_H,2,sum),decreasing=TRUE))

a<-melt(as.matrix(F_H))

colnames(a)<-c("Flowers","Birds","value")

a$Flowers<-factor(a$Flowers,levels=orderflowers)
a$Birds<-factor(a$Birds,levels=orderbirds)

ggplot(a[a$value>0,],aes(x=Birds,y=Flowers,fill=value)) + geom_tile()+ theme_bw() + scale_fill_continuous(low="blue",high="red") + theme(axis.text.x = element_text(angle = 90, hjust = 1))
ggsave("Results/MatrixPlot.jpeg",dpi=300,height=6.5,width=7)
##################################
#Retrieve Classes, name them, melt 
#Start with networkwide properties
##################################

#Get the desired files from paths - within time?
fil.list<-list.files(paste(netPath,"Temporal",sep="/"),pattern="NetworkProperties.csv",recursive=TRUE,full.names=TRUE)

fil<-list()
#Read and name each file
for (x in 1:length(fil.list)){
  fil[[x]]<-read.csv(fil.list[[x]])
  names(fil)[x]<-strsplit(fil.list[[x]],"/")[[1]][11]
}

#melt the outputs to a single dataframe
m.Prop<-melt(fil)
colnames(m.Prop)<-c("Metric","Level","value","Time")

#Correct the naming of levels
levels(m.Prop$Level)<-c("Hummingbirds","Plants")

#If you want to remove overall metrics
month.Prop<-m.Prop[!m.Prop$Time=="Total",]
#Which metrics are desired?
droplevels(month.Prop)

metricskeep<-c("connectance","links per species","nestedness","Shannon diversity","H2","niche overlap","robustness.HL","number of compartments","robustness.LL","number.of.species.HL")
month.Prop<-droplevels(month.Prop[month.Prop$Metric %in% metricskeep,])

#Quick and dirty look at all metrics
month.Prop$Time<-factor(month.Prop$Time,c("6","7","8","9","10","11","12","1","2","3","4","5"))

p<-ggplot(na.omit(month.Prop),aes(x=factor(Time),y=value,col=Level)) + geom_point() + geom_line(linetype="dashed",aes(group=Level)) + facet_wrap(~Metric,scales="free_y") + scale_x_discrete(breaks=c(6:12,1))
p + theme_bw() 

##############################################
#Compute Metrics for each Humminbird species
##############################################

#Get the desired files from paths
fil.list<-list.files(paste(netPath,"Temporal",sep="/"),pattern="HummingbirdMetrics.csv",recursive=TRUE,full.names=TRUE)

fil<-list()
#Read and name each file
for (x in 1:length(fil.list)){
  fil[[x]]<-read.csv(fil.list[[x]])
  names(fil)[x]<-strsplit(fil.list[[x]],"/")[[1]][11]
}

Hum.Time<-melt(fil)
colnames(Hum.Time)<-c("Species","Metric","value","Time")

#Just get the Metrics which make sense for this analysis
head(Hum.Time)

metricskeep<-c("nestedrank","resource.range","betweenness","d","degree","species.strength")
Hum.Time<-droplevels(Hum.Time[Hum.Time$Metric %in% metricskeep ,])

#Probably should exclude rare species?
H.c<-cast(Hum.Time,...~Metric)
Hum.Time<-melt(H.c)

Hum.Time$Time<-factor(Hum.Time$Time,c("6","7","8","9","10","11","12","1","2","3","4","5"))

#Quick and dirty look across species 
ggplot(Hum.Time,aes(Time,value,col=Species)) + facet_wrap(~Metric,scales="free") + geom_line(linetype="dashed",aes(group=Species)) + geom_point() + theme_bw()
ggsave(paste(netPath,"TimeFigures/HumSpecies_Time.svg",sep=""),height=8,width=11)

#Plot for each species, or for each metric?
for(x in levels(droplevels(Hum.Time$Species))){
  print(x)
  if(nrow(Hum.Time[Hum.Time$Species %in% x & !Hum.Time$Time %in% "Total",])==0) next
  
  #drop the total column and added a dashed total line
  p<-ggplot(Hum.Time[Hum.Time$Species %in% x & !Hum.Time$Time %in% "Total",],aes(as.numeric(Time),value)) + facet_wrap(~Metric,scales="free") + geom_line(linetype="dashed",aes(group=Species)) + geom_point() + theme_bw()
  ggsave(paste(netPath,paste(x,".svg",sep=""),sep="TimeFigures/"),height=8,width=11) 
  
}

#######################################################################
#Bring in Transect Data and Compare Specilization and available resources across all Elevations
#######################################################################
#At first just use the across entire network properies and all flowers from all elevations
#The next step is to set species ranges and get flower transects across that range

#The script FlowerTransects.R must be run
#source(paste(gitpath),"FlowerTransects.R")

####################
#Network Properties
head(month.Prop)
####################

########################################################
#For now there is a bit of a mismatch, since the network 
#is not split by elevation, but the flowers are aggregated into 200m bins
#########################################################

setwd(droppath)
load("Thesis/Maquipucuna_SantaLucia/Results/FlowerTransect.Rdata")

#THIS NEEDS TO BE FIXED
#setwd to dropbox
droppath<-"C:/Users/Ben/Dropbox/"
setwd(droppath)
#Set github path
gitpath<-"C:/Users/Ben/Documents/Maquipicuna/"

#The aggregate totals of the flower assemblage
head(fl.totals)

#aggregate by month for now, not elev split
month.totals<-aggregate(fl.totals$TotalFlowers,list(fl.totals$Month),sum)
colnames(month.totals)<-c("Month","Flowers")

#Start with just hummingbird levels
month.Hum<-month.Prop[month.Prop$Level == "Hummingbirds",]

#combine the flower totals and network metrics
network.fl<-merge(month.totals,month.Hum,by.x="Month",by.y="Time")

#Quick visualization
p<-ggplot(network.fl,aes(Flowers,value,col=as.factor(Month))) + facet_wrap(~Metric,scale="free") + geom_point(size=3) + geom_smooth(method="lm",aes(group=1))
ggsave(paste(netPath,"NetworkPropFlowers.svg",sep=""),height=8,width=11,dpi=300)

###############################################
#Hummingbird Properties and Available Resources
###############################################
head(Hum.Time)

#Take out the total time
Hum.Time<-Hum.Time[!Hum.Time$Time %in% "Total",]
hum.fl<-merge(month.totals,Hum.Time,by.x="Month",by.y="Time")

#Need to subset by number of interactions, get rid of the species just seen once?
with(hum.fl,table(Species,Month))
month_Pres<-aggregate(hum.fl$Month,list(hum.fl$Species),function(x) nlevels(factor(x)))

#Keep species seen more than 1 month
species_keep<-month_Pres[which(month_Pres$x > 1),]$Group.1

#remove an unknwon species
species_keep<-species_keep[!species_keep %in% "UKWN"]
ggplot(hum.fl[hum.fl$Species %in% species_keep,],aes(as.numeric(Flowers),value,col=as.factor(Month))) + facet_grid(Metric~Species,scale="free") + geom_point() + geom_smooth(method="lm",aes(group=1))
ggsave(paste(netPath,"SpeciesPropFlowers.svg",sep=""),height=8,width=11,dpi=300)

#Save image to file
setwd(droppath)
save.image("Thesis/Maquipucuna_SantaLucia/Results/Network/NetworkData.Rdata")