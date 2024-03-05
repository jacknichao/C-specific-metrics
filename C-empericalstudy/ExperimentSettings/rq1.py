#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@file: rq1.py
@function: experiment settings for RQ1; the validation setting is time series 10-CV
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"commons"))
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"ORM"))
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"Models"))
import pandas
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from Configs import AllConfigs
from JSLogger import logging
from typing import Tuple
from cbsp import CBSP
from db import DBOperator
from results import TimeSeriesEffrot
from sqlalchemy.orm import Session


class RQ1:
    """
    in this class, we do all the experiment described in rq1.
    """

    # feature set
    __features: list = AllConfigs.expsettings['featurename']
    
    # class label
    __label: str = AllConfigs.expsettings['labelname']

    def __init__(self, projectpath, projectname, projecttype, dbsession: Session):

        logging.info("current project: %s" % projectname)
        self.projectname = projectname
        self.projecttype = projecttype
        self.filepath: str = os.path.join(projectpath,projectname)
        self.dbsession = dbsession

    def __loadData(self, timeAware: bool = True) -> Tuple[pandas.core.frame.DataFrame, pandas.core.series.Series]:
        """
        load project data from csv files
        :param timeAware: indicate whether we should sort all commit in time series
        :return: a tuple containing training data X and corresponding label y
        """

        try:
            df: pandas.DataFrame = pandas.read_csv(self.filepath)
        except Exception as e:
            logging.error('read file %s error! msg: %s' % (self.filepath, e))
        
        if timeAware:
            # sort by time_stamp if we consider commit time
            df.sort_values('time_stamp', inplace=True)
            X = df[self.__features]
            y = df[self.__label].astype(np.int)
        else:
            # get data and label separate
            X = df[self.__features]
            # convert label to int
            y = df[self.__label].astype(np.int)
        return X, y


    def timeseriesCVResults(self, jitmodelDict: dict,jitmodelTypes:dict, n_splits: int=11, max_train_size=None) -> None:
        """
        calculate all performance measure according to the models stored in a dictionary
        Notes: this method takes time into consideration
        :param jitmodelDict: a dictionary, key: a short name for model, value: a classification model
        :param jitmodelTypes: a dictionary, key: a short name for model, value: model type [un]supervised
        :param n_splits: the number of time series split, the last split will be ignored
        :param max_train_size: the maximum number of folds be treated as training data
        :return:
        """
        tsSplit = TimeSeriesSplit(n_splits=n_splits, max_train_size=max_train_size)
        # load time series data
        X, y = self.__loadData(timeAware=True)

        # iterate each model
        for modelname, model in jitmodelDict.items():
            logging.info("type: %s, project: %s, classifier: %s TimeSeries" % (self.projecttype,self.projectname, modelname))

            seriesindex: int = 0
            for trainIndex, testIndex in tsSplit.split(X, y):
                seriesindex += 1
                # the last split should be ignore since the limitation of szz algorithm
                if seriesindex >10:
                    break
                logging.info("project: %s, classifier: %s[%s],cvIndex: %s." %
                             (self.projectname, modelname, jitmodelTypes[modelname], seriesindex))

                # print('series', seriesindex, 'train', len(trainIndex), 'test', len(testIndex))

                # supervised model should be fitted first
                if jitmodelTypes[modelname] == "supervised":
                    model.fit(X.loc[trainIndex,], np.ravel(y.loc[trainIndex,]))

                effortResult= model.predict(X.loc[testIndex,], y.loc[testIndex,])
                
                result= TimeSeriesEffrot(pname=self.projectname,
                                         ptype=self.projecttype,
                                         model=modelname,
                                         modeltype= jitmodelTypes[modelname],
                                         seriesindex=seriesindex,

                                         precision20p=effortResult['precision20p'],
                                         recall20p=effortResult['recall20p'],
                                         fmeasure20p=effortResult['fmeasure20p'],
                                         pci20p=effortResult['pci20p'],
                                         popt=effortResult['popt'],
                                         ifa=effortResult['ifa'],
                                        )

                self.dbsession.add(result)
                self.dbsession.commit()

if __name__ == "__main__":
    jitmodels: dict = { "cbsp": CBSP() }

    jitmodeltype:dict = { "cbsp": "supervised" }

    allfilespath = os.path.join(AllConfigs.expsettings['data_root_path'], AllConfigs.expsettings['project_type'])
    dbsession = DBOperator().getScopedSession()

    for root, dirs, files in os.walk(allfilespath):
        for file in files:
            if os.path.splitext(file)[1].endswith(".csv"):
                protype = "oss" if "oss" in AllConfigs.expsettings['project_type'] else ""
                rq1 = RQ1(projectpath=root, projectname=file, projecttype=protype, dbsession=dbsession)
                rq1.timeseriesCVResults(jitmodelDict=jitmodels, jitmodelTypes=jitmodeltype)

    dbsession.close()
    logging.info(AllConfigs.expsettings['dbtablename'])
    logging.info("RQ1 executed successfully!")