
undersampling <- function(data, class){
	positive_label <- "buggy"
	buggy_data <- data[which(data[class][,1] == positive_label),]
	clean_data <- data[-(which(data[class][,1] == positive_label)),]
	sampled_index <- sample(nrow(clean_data), nrow(buggy_data))
	sampled_data <- clean_data[sampled_index,]
	ret_data <- rbind(buggy_data, sampled_data)
	return(ret_data)
}

