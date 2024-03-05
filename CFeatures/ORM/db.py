import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"Commons"))

from Common.allConfigures import Allconfiguration
import sqlalchemy
from sqlalchemy.orm import session, sessionmaker,scoped_session
from dbmodules import ModuleBase
from sqlalchemy.pool import QueuePool
import pandas as pd



class DBOperator:
    def __init__(self):
        self.username = Allconfiguration.configures_json['username']
        self.password = Allconfiguration.configures_json['password']
        self.host = Allconfiguration.configures_json['host']
        self.database = Allconfiguration.configures_json['database']
        self.poolsize = Allconfiguration.configures_json['poolsize']
        engine = self.__create_engine()
        self.session_factory: sessionmaker = sessionmaker(bind=engine, autocommit=False)
        # thread safety(each thread only has a unique session)
        self.scoppedSession: scoped_session = scoped_session(self.session_factory)
        # test session
        self.mysession = self.session_factory()

    def __create_engine(self):
        # ref to {https://www.cnblogs.com/jackadam/p/8727409.html}
        dburl = "mysql+mysqlconnector://{username}:{password}@{host}/{database}".format(username=self.username,password=self.password,host=self.host,database=self.database)
        # pool_size = 10
        # pool_recycle = -1 
        # max_overflow = -1 
        # pool_timeout = 30
        # echo = False
        # pool_pre_ping = True

        engine = sqlalchemy.create_engine(dburl, pool_size=self.poolsize,
                                          max_overflow=10,
                                          pool_timeout=30,
                                          pool_pre_ping=True,poolclass=QueuePool)
        # create all related tables
        ModuleBase.metadata.create_all(engine)
        return engine

    def getNewSession(self):
        """
        return a new session when called
        :return:
        """
        return self.session_factory()

    def getScopedSession(self)->scoped_session:
        """
        return a thread-safety session, which means one thread has only one session
        :return:
        """
        return self.scoppedSession()



    def executor_rawsql(self,sql:str)->pd.DataFrame:
        """
        pull data from a table using specific sql string
        :param sql:
        :return:
        """
        try:
            df= pd.read_sql(str)
        except Exception as ex:
            print("execute sql error")

        return df

