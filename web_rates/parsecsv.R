library("lattice")
require(ggplot2)
require(reshape)
setwd("/home/chad/vrbo/web_rates")
rates=read.table("rates.csv",sep=",",header=TRUE,stringsAsFactors = FALSE, na.strings="*")
# format first column as a date
rates$date=as.Date(rates$date,"%b-%d-%Y")
# xyplot(rates$X460512+rates$X567974+rates$X242896+rates$X369723~rates$date)
q=melt(rates,id="date")
ggplot(q,aes(date,value))+geom_line(aes(colour=variable))

myrates=rates[,colSums(is.na(rates))<70]
myrates=na.omit(myrates)
qq=myrates[,2:9]
fit=kmeans(qq,6)
aggregate(qq,by=list(fit$cluster),FUN=mean)
qqq=data.frame(qq,fit$cluster)
qplot(myrates$date,rowMeans(qq),color=qqq$fit.cluster)
