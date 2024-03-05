#!usr/bin/env python

from typing import Counter
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.types import VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

ModuleBase = declarative_base()


class CFeature(ModuleBase):
    """
    C features in commit
    """
    __tablename__ = "c_features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # project name
    project = Column(String(63), nullable=False)

    # commit id
    commit_id = Column(String(63), nullable=False)

    # number of memory requirement operations
    meminc = Column(Integer, nullable=False,default=0)

    # number of memory release operations
    memdec = Column(Integer, nullable=False, default=0)

    # number of memory change operations, i.e., realloc
    memchg = Column(Integer, nullable=False,default=0)

    # number of single pointer definitions or usage
    singlepointer = Column(Integer, nullable=False,default=0)

    # number of multiple pointer definitions or usage
    multiplepointer = Column(Integer, nullable=False, default=0)

    # max depth of the pointer definition or usage
    maxpointerdepth = Column(Integer, nullable=False,default=0)

    # number of goto statements
    gotostm = Column(Integer, nullable=False,default=0)

    # number of array indexing operations
    indexused = Column(Integer, nullable=False,default=0)

    # number of auto increasing or decreasing operations
    autoincredecre = Column(Integer, nullable=False,default=0)

     
    def __repr__(self) -> str:
        return '%s:(ID: %s, project:%s, commit_id:%s, meminc:%s, memdec:%s, memchg:%s, singlepointer:%s, multiplepointere:%s, maxpointerdepth:%s, gotstm:%s, indexused:%s, autoincredecre:%s. )' \
               % (self.id,self.project,self.commit_id,self.meminc,self.memdec,self.memchg,self.singlepointer,self.multiplepointer,self.maxpointerdepth,self.gotostm,self.indexused,self.autoincredecre)
