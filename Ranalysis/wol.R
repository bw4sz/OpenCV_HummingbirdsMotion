a<-list.files("C:/Users/Jorge/Dropbox/Thesis/Automated_Monitering/webol/",full.names=TRUE)

b<-a[-c(90,91)]

d<-lapply(b,read.csv)

sum.d<-sapply(d,sum)

hist(sum.d)

data.frame(b,sum.d)
