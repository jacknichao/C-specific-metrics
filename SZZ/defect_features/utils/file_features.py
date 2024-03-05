import pandas as pd
import numpy as np
import os
import json
from defect_features.config import conf


def process_file_feature(project):

    file_in = os.path.join(os.path.dirname(conf.data_path), os.pardir,'report',project + ".csv")

    df = pd.read_csv(file_in)
    commit_list = list()
    for index,row in df.iterrows():
        f_exp = row.exp
        f_rexp = row.exp
        buggy_files = dict()
        if not pd.isnull(row.buggy_lines):
            buggy_files = json.loads(row.buggy_lines)
        file_size = os.path.join("../file_features/", project, row.commit_id + "_size")
        # 检查是否存在
        if os.path.isfile(file_size):
            with open(file_size, 'r') as f_size:
                tmp = f_size.read()
                size_dict = json.loads(tmp)
                for file_name, v in size_dict.items():
                    print(file_name)
                    if file_name in buggy_files:
                        contains_bug = True
                    else:
                        contains_bug = False
                    f_la = v['la']
                    f_ld = v['ld']
                    f_lt = v['lt']
                    file_history =os.path.join("../file_features/",project,row.commit_id + "_history" )
                    # 检查是否存在
                    if os.path.isfile(file_history):
                        with open(file_history,'r') as f_history:
                            tmp = f_history.read()
                            history_dict=json.loads(tmp)
                            if file_name in history_dict:
                                f_ndev = history_dict[file_name]['f_ndev']
                                f_age = history_dict[file_name]['f_age']
                            else:
                                continue
                                f_ndev = 0
                                f_age = 0
                    else:
                        break
                        f_ndev = 0
                        f_age = 0
                    commit_list.append({'commit_id':row.commit_id,'file_name':file_name,'la':f_la,'ld':f_ld,'lt':f_lt,
                                        'exp':f_exp,'rexp':f_rexp,'ndev':f_ndev,'age':f_age,'contains_bug':contains_bug})
    df_out = pd.DataFrame(commit_list).sort_values(by=['commit_id'],ascending=False)
    df_out.to_csv(project+'_file_features.csv',index=False,columns=['commit_id','file_name','la','ld','lt','exp','rexp',
                                                          'ndev','age','contains_bug'])


        #new_dict[row.commit_id] = {}


if __name__=='__main__':
    process_file_feature('scmcenter')