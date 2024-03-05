#-*- coding: utf-8 -*-
import simplejson
import os

upper_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    def __init__(self):
        #conf = file("../config.json", "r") # when run each dimension
        #conf = file("config.json", "r")  # when run main
        with open(os.path.join(upper_dir, "config.json"),"r") as conf:
            conf_str = conf.read()
            conf_json = simplejson.loads(conf_str)
            self.data_path = conf_json['data_root_path']
            self.git_log_path = conf_json['git_log_path']
            self.projects = conf_json['projects']

            self.consider_extensions = conf_json['extensions']
            self.df_basic_path = conf_json['df_basic_path']

    def project_log_path(self, project_name, log_filename=None):
        assert(project_name in self.projects)
        path = os.path.join(self.git_log_path, project_name)
        if not os.path.exists(path):
            os.makedirs(path)
        if log_filename is None:
            return path
        else:
            return os.path.join(path, log_filename + '.log')

    def project_path(self, project_name):
        assert(project_name in self.projects)
        return os.path.join(self.data_path, project_name)


class SQLConfig:
    """
    read all configured db settings
    """
    def __init__(self):

        with open(os.path.join(upper_dir, "config.json"), "r") as conf:
            conf_str = conf.read()
            conf_json = simplejson.loads(conf_str)
            self.vendor = conf_json['sql']['vendor']
            self.dbname = conf_json['sql']['dbname']
            self.username = conf_json['sql']['username']
            self.password = conf_json['sql']['password']
            self.ip = conf_json['sql']['ip']
            self.pool = conf_json['sql']['pool']


