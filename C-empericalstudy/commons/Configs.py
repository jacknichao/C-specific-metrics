#!usr/bin/env python
#-*- coding:utf-8 _*-

import simplejson
import os



upper_dir = os.path.abspath(os.path.dirname((os.path.dirname(__file__))))

class AllConfigs:
    """
    read all configs
    """
    sql:dict = None
    expsettings:dict =None # settings about experiment


    with open(os.path.join(upper_dir, "config.json"), "r") as conf:
        contents: str = conf.read()
        contents_json = simplejson.loads(contents)
        sql = contents_json['sql']
        expsettings = contents_json['expsettings']


if __name__ == "__main__":
    print("ok!!!")
    print(AllConfigs.data_path)
    print(os.path.abspath(AllConfigs.data_path))
    print(AllConfigs.projects)
    print(AllConfigs.sql)









