#-*- coding: utf-8 -*-
from defect_features.db import models
from defect_features.config import confDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker




class DbAPI:
    def __init__(self):
        self.__db_name = confDB.dbname
        self.__db_vendor = confDB.vendor
        self.__username = confDB.username
        self.__password = confDB.password
        self.__ip = confDB.ip
        self.engine = self.create_eng()
        # create tables
        models.Base.metadata.create_all(self.engine)
        self.__session = sessionmaker(bind=self.engine)()


    def create_eng(self):
        if self.__db_vendor == 'mysql':
            return create_engine('mysql+mysqlconnector://%s:%s@%s:3306/%s?charset=utf8mb4&collation=utf8mb4_general_ci' %
                                 (self.__username, self.__password,self.__ip, self.__db_name),pool_recycle=5)
        else:
            raise NotImplementedError
    def commit_session(self):
        self.__session.commit()

    def close_session(self):
        self.__session.close()

    @staticmethod
    def iter_to_list(iter_obj):
        assert(isinstance(iter_obj, iter))
        ret = list()
        for t in iter_obj:
            ret.append(t)
        return ret

#######################################################################
#
# General DB APIs
#
#######################################################################

    def insert_objs(self, db_objs):
        for db_obj in db_objs:
            self.__session.add(db_obj)
        self.__session.commit()

    def retrieve_query(self, table, project):
        """

        :param table:<class 'defect_features.db.models.SizeFeatures'>, not <class 'defect_features.object.features.SizeFeatures'>
        :param project:
        :return:
        """

        try:
            query = self.__session.query(table).filter(table.project==project).all()
            return query
        except KeyError:
            return None

    def raw_sql(self, sql):
        results = self.__session.execute(sql)
        return results