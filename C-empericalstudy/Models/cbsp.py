#!usr/bin/env python
#-*- coding:utf-8 _*-
 
from sklearn.linear_model import LogisticRegression
from imblearn.under_sampling import RandomUnderSampler
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from Models.effort import Effort
import time,sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"commons"))
from commons.Configs import AllConfigs



class CBSP:
 
    def __init__(self):
        self.__features: list = AllConfigs.expsettings['featurename']
        self.__label: str = AllConfigs.expsettings['labelname']


    def fit(self,X:pd.DataFrame ,y:pd.Series):
        """
        build a prediction model
        :param X: training data
        :param y: training label
        :return:
        """

        # step 0:  
        # X.drop(self.coll_redun_features_delete, axis=1, inplace=True)
        # columns_names_left:list = X.columns.to_list()
        columns_names_left:list = X.columns.to_list()


        # step 1: undersample
        undersample= RandomUnderSampler(random_state=1)
        # resample will destroy the input data type, and convert them to numpy.narray
        X_resample, y_resample = undersample.fit_resample(X,y)
        # after resample, we need to re-constract X_resample,y _resample as dataframe
        X_resample:pd.DataFrame = pd.DataFrame(X_resample,columns=columns_names_left)
        y_resample:pd.Series = pd.Series(y_resample,name=self.__label)


        # step 2: apply standard logarithmic transformation to each metric
        # except for FIX;
        log_features: list =columns_names_left
        log_features.remove('is_fix')

        X_resample_log= X_resample.loc[:,log_features].applymap(lambda data: np.log2(data+1) if data>0 else data)
        X_resample_log['is_fix']= X_resample['is_fix']

        # step 4: build prediction model
        self.lr = LogisticRegression(solver='liblinear', max_iter=1000)
        self.lr.fit(X_resample_log,y_resample)

    def predict(self,X_test:pd.DataFrame, y_test:pd.Series):
        """
        predict on test data and return two types of performance measures

        :param X_test: testing data
        :param y_test: label of testing data
        :return: all effort performance values
        """
        # step 0: 
        # X_test.drop(self.coll_redun_features_delete, axis=1, inplace=True)
        # columns_names_left: list = X_test.columns.to_list()
        columns_names_left: list = X_test.columns.to_list()

        # pre-processing
        # step 1: apply standard logarithmic transformation to each metric
        # except for FIX;
        log_features: list =columns_names_left
        log_features.remove('is_fix')

        X_test_log = X_test.loc[:, log_features].applymap(lambda data: np.log2(data+1) if data>0 else data)
        X_test_log['is_fix'] = X_test['is_fix']

        y_pred = self.lr.predict(X_test_log)
        y_pred_prob = self.lr.predict_proba(X_test_log)[:, 1]

        # after prediction, we need to add y_pred and y_pred_prob into original dataframe
        X_test['y_pred']= y_pred
        X_test['y_pred_prob']= y_pred_prob
        X_test['locs'] = X_test['la'] + X_test['ld']
        X_test['ratio'] = y_pred_prob/ (X_test['la'] + X_test['ld']+0.000001)
        X_test['contains_bug'] = y_test

        # two sort order: descending order by y_pred, then ascending order by locs
        X_test_sorted = X_test.sort_values(by=['y_pred','ratio'],ascending=[False,False])

        # get performance results
        effort = Effort(testFullData=X_test_sorted[['la','ld','contains_bug']])
        effort_values = effort.getAllMeasures()

        return effort_values




if __name__ == "__main__":
    print('hello')

    __features: list = AllConfigs.expsettings['featurename']
    __label: str = AllConfigs.expsettings['labelname']

    filepath = "axios.csv"

    df: pd.DataFrame = pd.read_csv(filepath)
    df.sort_values(by='time_stamp',inplace=True)
    # sort by time_stamp if we consider commit time
    X = df[__features]
    y = df[__label].astype(np.int)
    tsSplit = TimeSeriesSplit(n_splits=3, max_train_size=None)
    # load time series data
    for trainIndex, testIndex in tsSplit.split(X,y):
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        cbsp = CBSP()
        cbsp.fit(X.loc[trainIndex,],y.loc[trainIndex,])
        perfornamces =cbsp.predict(X.loc[testIndex,],y_test=y.loc[testIndex,])
        print(perfornamces)
        time.sleep(5)








