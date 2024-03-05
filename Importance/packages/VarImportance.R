library("pROC")
library("randomForest")
library("reshape")
library("e1071")
library("ScottKnottESD")
library("caret")

source("packages/measures.R")


predict_type <- c("prob", "response", "prob")
names(predict_type) <- c("random_forest", "logistic_regression", "naive_bayes")

probability <- function(prediction, model_type){
	if (model_type %in% c("random_forest", "naive_bayes")){
		v <- prediction[,2]
	}
	else{
		v <- prediction
	}
	return(v)
}

VarImportance <- function(model, model_type, varnames, test_set, label_attr){
	n_instances <- nrow(test_set)
	prediction <- predict(model, test_set, type=predict_type[model_type])
	prob <- probability(prediction, model_type)
	clean_acc <- accuracy(test_set, prob, label=label_attr)
	acc_diff_vec <- c()
	for (var in varnames){
		temp_set <- test_set
		temp_set[var][,1] <- sample(temp_set[var][,1], n_instances)

		temp_prediction <- predict(model, temp_set, type=predict_type[model_type])
		temp_prob <- probability(temp_prediction, model_type)
		temp_acc <- accuracy(test_set, temp_prob, label=label_attr)
		acc_diff_vec <- append(acc_diff_vec, clean_acc - temp_acc) 
	}
	return(acc_diff_vec)
}

VarImportanceCE <- function(model, model_type, varnames, test_set, label_attr){
	n_instances <- nrow(test_set)
	n_positive_instances <- length(which(test_set[,label_attr]==positive_label))
	prediction <- predict(model, test_set, type=predict_type[model_type])
	prob <- probability(prediction, model_type)
	ordered_data <- cbs_plus_get_ordered_data(test_set, prob)
	ce_results <- calculate_cost_effectiveness2(ordered_data, 0.2, "real_la", "real_ld", label_attr)
	precision20 <- ce_results[1] / ce_results[2]
	recall20 <- ce_results[1] / n_positive_instances
	clean_f20 <- 2 * precision20 * recall20 / (precision20 + recall20)
	#clean_acc <- accuracy(test_set, prob, label=label_attr)
	#acc_diff_vec <- c()
	f20_diff_vec <- c()
	
	for (var in varnames){
		temp_set <- test_set
		temp_set[var][,1] <- sample(temp_set[var][,1], n_instances)

		temp_prediction <- predict(model, temp_set, type=predict_type[model_type])
		temp_prob <- probability(temp_prediction, model_type)
		
		temp_ordered_data <- cbs_plus_get_ordered_data(temp_set, temp_prob)
		temp_ce_results <- calculate_cost_effectiveness2(temp_ordered_data, 0.2, "real_la", "real_ld", label_attr)
		temp_precision20 <- temp_ce_results[1] / temp_ce_results[2]
		temp_recall20 <- temp_ce_results[1] /n_positive_instances
		temp_f20 <- 2 * temp_precision20 * temp_recall20 / (temp_precision20 + temp_recall20)
		
		f20_diff_vec <- append(f20_diff_vec, clean_f20 - temp_f20)
		#temp_acc <- accuracy(test_set, temp_prob, label=label_attr)
		#acc_diff_vec <- append(acc_diff_vec, clean_acc - temp_acc) 
		
	}
	print(f20_diff_vec)
	return(f20_diff_vec)
}


