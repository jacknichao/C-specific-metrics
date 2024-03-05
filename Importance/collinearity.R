rm(list=ls())
source("packages/base.R")

variables1 <- c("meminc", "memdec", "memchg", "singlepointer", "multiplepointer", "maxpointerdepth", "gotostm", "indexused", "autoincredecre", "ns", "nd", "nf", "entropy", "exp", "rexp", "sexp", "ndev", "age", "nuc", "la", "ld", "lt", "is_fix", "contains_bug", "real_la", "real_ld")
variables <- c("meminc", "memdec", "memchg", "singlepointer", "multiplepointer", "maxpointerdepth", "gotostm", "indexused", "autoincredecre", "ns", "nd", "nf", "entropy", "exp", "rexp", "sexp", "ndev", "age", "nuc", "la", "ld", "lt", "is_fix", "contains_bug")
log_features <- c("meminc", "memdec", "memchg", "singlepointer", "multiplepointer", "maxpointerdepth", "gotostm", "indexused", "autoincredecre", "ns", "nd", "nf", "entropy", "exp", "rexp", "sexp", "ndev", "age", "nuc", "la", "ld", "lt")

c_projects <- c("scrcpy","git","obs-studio","FFmpeg","curl","the_silver_searcher","mpv","radare2","goaccess","nnn")

# the variable is used to set which projects should be analysised.
projects_name <- "cprojects"
root_path <- paste(c("datainput/", projects_name, "/"), collapse="")

label <- "contains_bug"

result_fn <- paste(c("./collinearity_", projects_name, ".txt"), collapse="")
cat("", file=result_fn, append=FALSE)

preprocess_c <- function(data){
	temp_label <- data[label][,1]
	temp_label <- as.vector(temp_label)
	# temp_label[which(temp_label=="False")] <- "clean"
	# temp_label[which(temp_label=="True")] <- "buggy"
	temp_label[which(temp_label=="FALSE")] <- "clean"
	temp_label[which(temp_label=="TRUE")] <- "buggy"
	data[,label] <- temp_label	
	
	real_la <- data$la
	real_ld <- data$ld
	
	indexes <- which(data$lt != 0)
	normalized_la <- rep(0, nrow(data))
	normalized_ld <- rep(0, nrow(data))
	normalized_la[indexes] <- data$la[indexes] / data$lt[indexes] / data$nf[indexes]
	normalized_ld[indexes] <- data$ld[indexes] / data$lt[indexes] / data$nf[indexes]
	data$la <- normalized_la
	data$ld <- normalized_ld
	print("preprocess c")
	data_log <- get_log_data(data, log_features)
	
	data_log$real_la <- real_la
	data_log$real_ld <- real_ld
	
	return(data_log)
}

studied_projects = c_projects

for (project in studied_projects){
  print(paste("Analysing Project Type:",projects_name,"File Name:", project,sep = "  "))
  
  data_path <- paste(c(root_path, project, ".csv"), collapse="")
  print(data_path)
  
  cat(data_path, file=result_fn, append=TRUE)
  cat("\n", file=result_fn, append=TRUE)
  data <- read.csv(data_path)
	
	# filter useless features 
	data <-data[variables]
	
	data <- preprocess_c(data)

	# set all features to be used
	data <- data[variables1]
	
	preprocess_path <- paste(c("preprocess", "/",projects_name, "/", project, ".csv"), collapse="")
	write.csv(data, preprocess_path, row.names=FALSE)
	data <- data[variables]

	vars <- names(data)

	var_names1 <- vars[vars != label]

	correlations <- cor(data[var_names1], data[var_names1], method="spearman")
 
	for (i in 1:(length(var_names1)-1)){
		for (j in (i+1):length(var_names1)){
			corr_val <- correlations[var_names1[i], var_names1[j]]
			if (corr_val > 0.8 | corr_val < -0.8){
			  #ifea <- cor(data[var_names1[i]], as.numeric(data[label]))
			  #print(ifea)
				cat(paste(c(var_names1[i], var_names1[j], ":", as.character(corr_val), "\n"), collapse=" "), file=result_fn, append=TRUE)
			}
		}
	}
}
