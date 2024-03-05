import os,time,sys


curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from CORE.c_metric_calculator import *

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir, "ORM"))
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir, "CORE"))
from ORM import dbmodules, db
from sqlalchemy.orm import query, scoped_session
from Common.mylogger import logger
import pandas as pd
import subprocess
import re
from git.repo import Repo

print(sys.path)



class ExtractClanguageCharacteristic:

    def __init__(self, project_root_path):
        """
        :param project_root_path: root path of the project
        """
        self.project_root_path = project_root_path
        # Get a connection to the database
        self.sess = db.DBOperator().getScopedSession()
        # self.git_log_str = r"""git log  --unified=0 -1  {commit_index}"""
        # self.git_log_add_line_prefix = r''' awk '{print "LINE_START: "$0}' '''

    def wrapper_change_path(func):
        """
        This function is used to switch the working directory 
        :return:
        """
        cwd = os.getcwd()

        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        os.chdir(cwd)
        return inner

    @wrapper_change_path
    def extract_c_features(self,project_name):
        # Read all the commits of the current project
        repo = Repo(os.path.join(self.project_root_path, project_name))
        # Get commits objects on the main branch
        # commit_list = list(repo.iter_commits(max_count=-1))
        # Get commits objects on all branches
        commit_list = list(repo.iter_commits("--all", max_count=-1))
        all_commits = [chex.hexsha for chex in commit_list]

        # Change the working directory to the corresponding project to run the git command
        target_dir = os.path.join(self.project_root_path, pname)
        os.chdir(target_dir)
        logger.info("project: %s, commit numbers: %s"%(project_name, len(all_commits)))

        templist = []
        interval: int = 0
        # Calculate the git log content for each commit
        for each_commit in all_commits:

            try:
                cmd= """ git log  --unified=0 -1  %s | awk '{print "LINE_START:"$0}'"""%(each_commit.strip())
                commit_msg = subprocess.check_output( cmd,  shell=True, cwd=target_dir, executable='/bin/bash').decode('utf-8', errors='ignore')

                # extract metrics from commit_msg
                object: dbmodules.CFeature = CLanguageCommitMetricCalculator(pname, each_commit.strip(), commit_msg).getCFeatures()
                templist.append(object)
                interval = interval + 1

                if interval % 200 == 0:  # Submit for every 200 commit
                    self.sess.add_all(templist)
                    templist = []  # Clear data
                    self.sess.commit()  # submit
                    self.sess.flush()
                    time.sleep(1)
                    logger.info("sumbit: %d times" % ((interval - 1) // 200 + 1))

            except Exception as e:
                logger.error("error arise. current project: %s, current commit_id: %s, err_msg: %s"%(pname, each_commit, e))

        if templist:
            self.sess.add_all(templist)
            self.sess.commit()
            self.sess.flush()
            logger.info("sumbit: %d times" % ((interval - 1) // 100 + 1))




if __name__ == '__main__':
    
    # the root path of all c repos
    project_root_path = r"/data/projects/"

    project_names = ["scrcpy","git","obs-studio","FFmpeg","curl", "the_silver_searcher","mpv","radare2", "goaccess", "nnn"]

    for pname in project_names:
        print("current project: %s"%pname)
        extJSC = ExtractClanguageCharacteristic(project_root_path)
        extJSC.extract_c_features(pname)
        # print(pname)
    
    print("ok")