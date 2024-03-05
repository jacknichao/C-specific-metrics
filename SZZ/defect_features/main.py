#-*- coding: utf-8 -*-
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append("/home/vincent.zwf/Defect_Prediction/defect_prediction")
import time
from defect_features.object import commit_meta
from defect_features.git_analysis.analyze_git_logs import retrieve_git_logs
from defect_features.features import diffusion
from defect_features.features import experience
from defect_features.features import history
from defect_features.features import purpose
from defect_features.features import size
from defect_features.utils.load_csv import *
from defect_features.db.api import *


def store_meta(project):
    # a list of RawGitCommitMeta in the project
    gls:list() = retrieve_git_logs(project)

    db_objs = list()
    print('number of commits:',len(gls))
    print(project, 'Begin to store meta data')
    for gl in gls:
        cm = commit_meta.CommitMeta()
        cm.from_git_log(gl)
        db_objs.append(cm.to_db_obj())
    db_api = DbAPI()
    db_api.insert_objs(db_objs)
    db_api.close_session()


def store_features(project, feature_type):
    # get db object
    if feature_type == 'diffusion':
        print(project,'Begin to store diffusion features')
        db_objs = diffusion.extract_to_db_obj(project)
    elif feature_type == 'experience':
        print(project,'Begin to store experience features')
        db_objs = experience.extract_to_db_obj(project)
    elif feature_type == 'history':
        print(project,'Begin to store history features')
        db_objs = history.extract_to_db_obj(project)
    elif feature_type == 'purpose':
        print(project, 'Begin to store purpose features')
        db_objs = purpose.extract_to_db_obj(project)
    else:
        assert(feature_type == 'size')
        print(project,'Begin to store size features')
        db_objs = size.extract_to_db_obj(project)
    # store to db
    db_api = DbAPI()
    db_api.insert_objs(db_objs)
    db_api.close_session()


if __name__ == '__main__':
    for p in conf.projects:
        start = time.time()
        print(p)
        # store_meta(p)
        # store_features(p, 'diffusion')
        # store_features(p, 'experience')
        # store_features(p, 'purpose')
        # store_features(p, 'history')
        # store_features(p, 'size')
        create_csv(p)
        end = time.time()
        print('Project %s using time(min): %s' % (p, (end-start)/60))
