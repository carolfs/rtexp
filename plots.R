#Copyright 2014, 2015 Carolina Feher da Silva
#
#This file is part of rtexp.
#
#rtexp is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#rtexp is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with rtexp.  If not, see <http://www.gnu.org/licenses/>.

library("grid")

fonte <- "Arial"

w <- 18
h <- 12

library('ggplot2')
a1 = read.csv('ana1exp1278.csv')
a1$noise <- factor(a1$noise)
levels(a1$noise)[levels(a1$noise)==0]  <- expression(paste(plain(Noise) ~~ sigma == 0, ", Cue 8:5:2"))
levels(a1$noise)[levels(a1$noise)==2]  <- expression(paste(plain(Noise) ~~ sigma == 2, ", Cue 8:8:2"))
a1$type <- factor(a1$type,
         levels = c("SRT", "CRT"))
dataM <- subset(a1, variable == "Valid" | variable == "Invalid" | variable == "Neutral")
#png("rtevo.png", width=w, height=h, units='cm', res=1000)
tiff("rtevo.tiff", width=w, height=h, units='cm', res=900, compression="lzw")
ggplot(dataM, aes(x=g, y=value, colour=variable)) + geom_line() + geom_point() + labs(colour="Cue") + xlab("Generation") + ylab("RT") + scale_colour_brewer(palette="Set1", limits=c("Valid", "Neutral", "Invalid")) + facet_grid(noise ~ type, scales="free_y", labeller=label_parsed) + theme_bw() + theme(axis.title=element_text(size=12, family=fonte), strip.text=element_text(size=12, family=fonte), legend.title=element_text(size=12, family=fonte), legend.text=element_text(size=8, family=fonte), axis.text=element_text(size=8, family=fonte), plot.margin = unit(c(0, 0, 0, 0), "cm"))

w <- 8.5
h <- 17

rtss = read.csv('anartss.csv')
rtss$exptype <- factor(rtss$exptype,
         levels = c("SRT", "CRT"))
rtss$cuetype <- factor(rtss$cuetype,
         levels = c("Valid", "Neutral", "Invalid"))
rtss$cond <- factor(rtss$cond)
levels(rtss$cond)[levels(rtss$cond)=="cond2"]  <- expression(paste(plain(Noise) ~~ sigma == 0, ", Cue 8:5:2"))
levels(rtss$cond)[levels(rtss$cond)=="cond3"]  <- expression(paste(plain(Noise) ~~ sigma == 0, ", Cue 8:8:2"))
levels(rtss$cond)[levels(rtss$cond)=="cond4"]  <- expression(paste(plain(Noise) ~~ sigma == 2, ", Cue 8:8:2"))
#png("rtss.png", width=w, height=h, units='cm', res=1000)
tiff("rtss.tiff", width=w, height=h, units='cm', res=900, compression="lzw")

ggplot(rtss, aes(x=cuetype, y=mean, fill=cuetype)) + geom_bar(stat="identity") + geom_errorbar(aes(ymin=ciinf, ymax=cisup), width=.2) + xlab("Cue Type") + ylab("RT") + facet_grid(cond ~ exptype, scales="free_y", labeller=label_parsed) + theme_bw() + theme(axis.title=element_text(size=12, family=fonte), strip.text=element_text(size=12, family=fonte), legend.title=element_text(size=12, family=fonte), legend.text=element_text(size=8, family=fonte), axis.text=element_text(size=8, family=fonte), legend.position="none", plot.margin = unit(c(0, 0, 0, 0), "cm"))

w <- 8.5
h <- 10

bayes = read.csv('anabayes.csv')
bayes$exptype <- factor(bayes$exptype,
         levels = c("SRT", "CRT"))
bayes$cuetype <- factor(bayes$cuetype,
         levels = c("Valid", "Neutral", "Invalid"))
bayes$gamma <- factor(bayes$gamma)
levels(bayes$gamma)[levels(bayes$gamma)==0.8]  <- expression(gamma == 0.8)
levels(bayes$gamma)[levels(bayes$gamma)==0.95]  <- expression(gamma == 0.95)
#png("rtbayes1.png", width=w, height=h, units='cm', res=1000)
tiff("rtbayes1.tiff", width=w, height=h, units='cm', res=900, compression="lzw")
dataM <- subset(bayes, signal == 5)

ggplot(dataM, aes(x=cuetype, y=rt, fill=cuetype)) + geom_bar(stat="identity") + geom_errorbar(aes(ymin=ciinf, ymax=cisup), width=.2) + xlab("Cue Type") + ylab("RT") + facet_grid(gamma ~ exptype, labeller=label_parsed) + theme_bw() + theme(axis.title=element_text(size=12, family=fonte), strip.text=element_text(size=12, family=fonte), legend.title=element_text(size=12, family=fonte), legend.text=element_text(size=8, family=fonte), axis.text=element_text(size=8, family=fonte), legend.position="none", plot.margin = unit(c(0, 0, 0, 0), "cm"))

#png("rtbayes2.png", width=w, height=h, units='cm', res=1000)
tiff("rtbayes2.tiff", width=w, height=h, units='cm', res=900, compression="lzw")
dataM <- subset(bayes, signal == 0.5)

ggplot(dataM, aes(x=cuetype, y=rt, fill=cuetype)) + geom_bar(stat="identity") + geom_errorbar(aes(ymin=ciinf, ymax=cisup), width=.2) + xlab("Cue Type") + ylab("RT") + facet_grid(gamma ~ exptype, labeller=label_parsed) + theme_bw() + theme(axis.title=element_text(size=12, family=fonte), strip.text=element_text(size=12, family=fonte), legend.title=element_text(size=12, family=fonte), legend.text=element_text(size=8, family=fonte), axis.text=element_text(size=8, family=fonte), legend.position="none", plot.margin = unit(c(0, 0, 0, 0), "cm"))