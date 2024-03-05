# **JIT defect prediction with C-specific features**
## **Basic introduction**
- `oss-cproject`: the csv data of 10 OSS projects mainly developed by C/C++ programming language
- `CFeatures`: scripts for calculating C-specific features
- `Importance`: scripts for filtering correlated and redundant features, and for calculating importance of features
- `C-empericalstudy`: scripts for the ten-fold time-aware validation experiment

## **Instructions for replication**
### **Data Preparation**
- The `OSSprojects` directory includes the csv data of 10 OSS peojects that can be directly used for evaluation.
- Alternatively, you could clone new projects and build your own dataset with the following steps:
  - (1) Clone a git repository;
  - (2) Calculate the 14 features proposed by Kamei et al. and label the changes with scripts in directory `SZZ`. This process could take hours if the git project is huge. Please refer to `SZZ/defect_features/README` for instructions;
  - (3) Calculate the 9 C-specific features with scripts in directory `CFeatures/CORE`;
  - (4) To output final data with 14 + 9 features to csv files, please refer to `CFeatures/CORE/mergedata.py`.

### **Dealing with correlated and redundant features**
- Scripts written in R language are included in the directory `Importance`. First run `collinearity.R` to analyze correlated features, then run `redun.R` to filter redundant features.
- Please refer to `Importance/README` for detailed instructions.

### **RQ1: Ten-fold time-aware validation**
- Scripts are in the directory `C-empericalstudy/ExperimentSettings`. To conduct the validation experiment, modify the configurations and run
    ```Python
    python rq1.py
    ```
- The results will be stored in the database. To output the average performance measures into csv files, please refer to `getResult.py`.

### **RQ2: Feature importance**
- Run `Importance/importance.R` to calculate the importance of features. The results will be saved in the `foundImportantFeatures` directory.