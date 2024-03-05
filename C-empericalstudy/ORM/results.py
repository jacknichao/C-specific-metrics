#!usr/bin/env python
#-*- coding:utf-8 _*-
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from Configs import AllConfigs

Base = declarative_base()

class TimeSeriesEffrot(Base):
    """
    10 time series cross validation considering effort
    """
    __tablename__ = AllConfigs.expsettings['dbtablename']

    id = Column(Integer, primary_key=True, autoincrement=True)
    # project name
    pname = Column(String(64), nullable=False)
    # project type[oss-original,js]
    ptype = Column(String(64),nullable=False)

    # the classification model used
    model = Column(String(64), nullable=False)

    # model type; indicate supervised or unsupervised
    modeltype = Column(String(64), nullable=False)
    # the series index of cross-validation
    seriesindex = Column(Integer, nullable=False)

    # effort measures
    # the recall of defect-inducing changes when using 20% of the entire effort requies to inspect all changes to the top ranked change
    precision20p = Column(Float, nullable=False)
    recall20p = Column(Float, nullable=False)
    fmeasure20p = Column(Float, nullable=False)
    # proportion of changes inspected when 20% loc modified by all changes are inspected
    pci20p = Column(Float, nullable=False)
    # Popt
    popt = Column(Float, nullable=False)
    # number of initial false alarms encountered before we find the first defect
    ifa = Column(Float, nullable=False)