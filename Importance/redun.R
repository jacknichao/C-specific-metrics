rm(list=ls())
require(caret)
require(e1071)
require(Hmisc)
library(rms)


# the variable is used to set which projects should be analyzed
projects_name <- "cprojects"

collinearity <- read.csv(paste("./collinearity-analysed.csv", sep=""))
 

root_path <- paste(c("preprocess/", projects_name, "/"), collapse="")

c_projects <- c("scrcpy","git","obs-studio","FFmpeg","curl","the_silver_searcher","mpv","radare2","goaccess","nnn")

studied_projects <- c_projects

for (project in studied_projects){
	print(project)
  	# the '-' will be escaped as '.'
    if (project == "obs-studio"){
	  cor_features <- collinearity[,'obs.studio']
	}else{
	  cor_features <- collinearity[,project]
    }
  
	data_path <- paste(c(root_path, project, ".csv"), collapse="")
	label <- "contains_bug"
	data <- read.csv(data_path)
	vars <- names(data)
	var_names1 <- vars[vars != label]
	var_names1 <- var_names1[!var_names1 %in% cor_features]

	var_str <- paste(var_names1, collapse="+")
	form_str <- paste("~", var_str, sep="")
	redun_form <- as.formula(form_str)
	#print(redun_form)
	out=redun(redun_form, data, nk=0)
	print(out)

}
print("redun analysis done!!")


