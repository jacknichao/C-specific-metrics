rm(list=ls())
library("e1071")
library("ScottKnottESD")
library("caret")
library(ggplot2)

source("packages/order_data.R")
source("packages/imbalance.R")
source("packages/base.R")
source("packages/VarImportance.R")


projects_name <- "cprojects"

collinearity <- read.csv(paste("collinearity-analysed.csv", sep=""))

c_projects <- c("scrcpy","git","obs-studio","FFmpeg","curl","the_silver_searcher","mpv","radare2","goaccess","nnn")

studied_projects = c_projects

root_path <- paste(c("preprocess/", projects_name, "/"), collapse="")

positive_label = "buggy"


output<- paste(c("foundImportantFeatures/", projects_name,".csv"), collapse="")

for (project in studied_projects){
  
  print(project)
  # the '-' will be escaped as '.'
	if (project == "obs-studio"){
	  cor_features <- collinearity[,'obs.studio']
	}else{
	  cor_features <- collinearity[,project]
    }

	data_path <- paste(c(root_path, project, ".csv"), collapse="")
	data <- read.csv(data_path)
	label <- "contains_bug"

	data[,label] <- factor(data[,label], order=TRUE, levels=c("clean", "buggy"))

	vars <- names(data)
	var_names <-  vars[vars != label]
	var_names1 <- var_names[!var_names %in% as.character(cor_features)]
	var_names1 <- var_names1[!var_names1 %in% c("real_la", "real_ld")]
	varnames_str <- paste(var_names1, collapse="+")

	importance_matrix <- NULL
	form <- as.formula(paste(label, varnames_str, sep=" ~ "))

	for (i in 1:10){
		set.seed(i); 
		folds <- createFolds(data[,label], 10)
		for (j in 1:10){
			# print(j)
			test_indexes <- folds[[j]]
			test_set <- data[test_indexes,]
			train_set <- data[-test_indexes,]
			
			lenBuggy = nrow(train_set[train_set$contains_bug=='buggy',])
			lenClean = nrow(train_set[train_set$contains_bug=='clean',])
			
			if (lenClean > lenBuggy){
			  train_set <- undersampling(train_set, "contains_bug")
			}
			
			fit <- glm(form, train_set, family=binomial(link = "logit"))
			importance_scores <- VarImportanceCE(fit, "logistic_regression", var_names1, test_set, label)
			if (is.null(importance_matrix)){
				importance_matrix <- matrix(importance_scores, nrow=1)
			}
			else {
				importance_matrix <- rbind(importance_matrix, matrix(importance_scores, nrow=1))
			}
		}
	}
	

	importance_frame <- data.frame(importance_matrix)
	names(importance_frame) <- var_names1
	row.names(importance_frame) <- as.character(1:100)
	sk <- sk_esd(importance_frame)
	tmp_features <- names(sk$groups)
	groups <- as.vector(sk$groups)
	
	#save_path <- paste(c("foundImportantFeatures/", projects_name, "/", project, ".csv"), collapse="")
	#result_frame <- data.frame(tmp_features, groups)
	#names(result_frame) <- c("feature", "rank")
	#write.csv(result_frame, save_path, row.names=FALSE)
	
	tmp_features <- names(sk$groups)
	groups <- as.vector(sk$groups)
	print(sk$groups)
	lst <-list()
	for(gl in unique(groups)){
	  outtext = paste(tmp_features[which(groups==gl)],collapse = "&")
	  lst<-c(lst,outtext)
	}
	
	cat(paste(c(project,unique(groups),"\n"),collapse = ","),file=output,append = T)
	cat(paste(c(project,lst,"\n"),collapse = ","),file = output,append = T)
}

