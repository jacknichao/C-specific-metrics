cbs_plus_get_ordered_data <- function(test_data, prob){

	bugDensity <- prob / (test_data$real_la+test_data$real_ld+0.00001)
    test_data$density <- bugDensity
	if(length(which(prob >= 0.5)) > 0){
		buggy_data <- test_data[which(prob >= 0.5),]
		ordered_buggy_data <- buggy_data[order(buggy_data$density, decreasing=TRUE),]
		clean_data <- test_data[-which(prob>=0.5),]
		ordered_clean_data <- clean_data[order(clean_data$density , decreasing=TRUE),]
		ordered_data <- rbind(ordered_buggy_data, ordered_clean_data)
		return(ordered_data)
	}
	else{
		ordered_data <- test_data[order(test_data$density , decreasing=TRUE),]
		return(ordered_data)
	}
}