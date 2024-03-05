#-*- coding: utf-8 -*-
import pandas as pd
import os
from defect_features.config import conf

from defect_features.query.query import *

columns_write = ['commit_id','time_stamp','ns', 'nd', 'nf', 'entropy', 'exp',
                'rexp', 'sexp', 'ndev', 'age', 'nuc', 'la', 'ld', 'lt', 'is_fix','contains_bug']

# columns_write = ['commit_id','time_stamp','ndev', 'age', 'nuc']


def create_csv(project):

    print(project, 'Begin to load csv file')
    file_store = os.path.join(conf.df_basic_path, 'inputoutput', 'report',project + ".csv")
    meta = CommitMetaQuery(project).do_query()
    diffusion = DiffusionFeaturesQuery(project).do_query()
    size = SizeFeaturesQuery(project).do_query()
    purpose = PurposeFeaturesQuery(project).do_query()
    history = HistoryFeaturesQuery(project).do_query()
    experience = ExperienceFeaturesQuery(project).do_query()
    features_dict = features_to_dict(meta,diffusion,size,purpose,history,experience)
    # features_dict = features_to_dict(meta,[],[],[],history,[])
    df = pd.DataFrame(features_dict).T.sort_values(by=['time_stamp'],ascending=False)
    df.to_csv(file_store,index=False,columns=columns_write)



