import sys,os

sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir,os.pardir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from defect_features.db.models import HistoryFeatures, ExperienceFeatures, SizeFeatures, DiffusionFeatures,\
    CommitMeta,PurposeFeatures
import pandas as pd
from defect_features.config import confDB,conf



def load_data_v(project):
    engine = create_engine('mysql+mysqlconnector://%s:%s@%s:3306/%s?charset=utf8' %
                             (confDB.__username, confDB.__password, confDB.__ip, confDB.__db_name),
                           pool_recycle=confDB.pool
                        )

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    history_features = session.query(HistoryFeatures).filter(HistoryFeatures.project == project).all()
    experience_features = session.query(ExperienceFeatures).filter(ExperienceFeatures.project == project).all()
    size_features = session.query(SizeFeatures).filter(SizeFeatures.project == project).all()
    diffusion_features = session.query(DiffusionFeatures).filter(DiffusionFeatures.project == project).all()
    commits_dict = dict()
    for elem in history_features:
        commits_dict[elem.commit_id] = {'commit_id':elem.commit_id,'project':elem.project,
                                     'ndev':elem.ndev,'age':elem.age,'nuc':elem.nuc}
    for elem in experience_features:
        if elem.commit_id not in commits_dict:
            continue
        else:
            commits_dict[elem.commit_id]['exp'] = elem.exp
            commits_dict[elem.commit_id]['rexp'] = elem.rexp
            commits_dict[elem.commit_id]['sexp'] = elem.sexp

    for elem in size_features:
        if elem.commit_id not in commits_dict:
            continue
        else:
            commits_dict[elem.commit_id]['la'] = elem.la
            commits_dict[elem.commit_id]['ld'] = elem.ld
            commits_dict[elem.commit_id]['lt'] = elem.lt

    for elem in diffusion_features:
        if elem.commit_id not in commits_dict:
            continue
        else:
            commits_dict[elem.commit_id]['ns'] = elem.ns
            commits_dict[elem.commit_id]['nd'] = elem.nd
            commits_dict[elem.commit_id]['nf'] = elem.nf
            commits_dict[elem.commit_id]['entropy'] = elem.entropy

    df = pd.DataFrame(commits_dict).T
    save_path = os.path.join('./data_tmp',project + '_v.csv')
    df.to_csv(save_path,index=False,columns=['commit_id','project','ndev','age','nuc',
                                             'exp','rexp','sexp','la','ld','lt','ns',
                                             'nd','nf','entropy'])

def load_data_a(project):
    engine = create_engine('mysql+mysqlconnector://%s:%s@%s:3306/%s?charset=utf8' %
                             (confDB.__username, confDB.__password, confDB.__ip, confDB.__db_name),
                           pool_recycle=confDB.pool
                        )
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    commits_meta = session.query(CommitMeta).filter(CommitMeta.project == project).all()
    purpose_features = session.query(PurposeFeatures).filter(PurposeFeatures.project == project).all()
    commits_dict = dict()
    for elem in commits_meta:
        commits_dict[elem.commit_id] = {'commit_id':elem.commit_id,'project':elem.project,
                                     'creation_time':elem.creation_time,'time_stamp':elem.time_stamp,
                                        'author_email':elem.author_email,'commit_message':elem.commit_message,
                                        'is_merge':elem.is_merge}
    for elem in purpose_features:
        if elem.commit_id not in commits_dict:
            continue
        else:
            commits_dict[elem.commit_id]['is_fix'] = elem.is_fix
            commits_dict[elem.commit_id]['classification'] = elem.classification
            commits_dict[elem.commit_id]['contains_bug'] = elem.contains_bug
            commits_dict[elem.commit_id]['fix_by'] = elem.fix_by
            commits_dict[elem.commit_id]['fixes'] = elem.fixes
            commits_dict[elem.commit_id]['find_interval'] = elem.find_interval
            commits_dict[elem.commit_id]['fix_file_num'] = elem.fix_file_num
            commits_dict[elem.commit_id]['buggy_lines'] = elem.buggy_lines

    df = pd.DataFrame(commits_dict).T
    save_path = os.path.join('./data_tmp',project + '_a.csv')
    df.to_csv(save_path,index=False,columns=['commit_id','project','creation_time','time_stamp','author_email',
                                             'commit_message','is_merge','is_fix','classification','contains_bug',
                                             'fix_by','find_interval','buggy_lines','fixes','fix_file_num'])

def combination(project):
    read_path_v = os.path.join('./data_tmp',project + '_v.csv')
    df_v = pd.read_csv(read_path_v).set_index('commit_id').T
    dict_v = df_v.to_dict()
    read_path_a = os.path.join('./data_tmp', project + '_a.csv')
    df_a = pd.read_csv(read_path_a).set_index('commit_id').T
    dict_a = df_a.to_dict()
    for commit_id,elem in dict_a.items():
        elem.update(dict_v[commit_id])
        elem.update({'commit_id':commit_id})
    df = pd.DataFrame(dict_a).T.sort_values(by=['time_stamp'],ascending=False)
    
    save_path = os.path.join(os.path.dirname(conf.data_path), os.pardir, 'report', project + ".csv")

    columns_write = ['commit_id', 'time_stamp', 'creation_time', 'author_email', 'commit_message', 'ns', 'nd', 'nf',
                     'entropy', 'exp', 'rexp','sexp', 'ndev', 'age', 'nuc', 'la', 'ld', 'lt','is_fix', 'classification',
                     'contains_bug', 'buggy_lines', 'fix_by', 'find_interval', 'fixes', 'fix_file_num', ]

    df.to_csv(save_path,index=False,columns=columns_write)

if __name__=='__main__':
    projects_v = ['Grant']
    for project in projects_v:
        load_data_v(project)
    # projects_a = ['Grant']
    # for project in projects_a:
    #     load_data_a(project)
    projects_combination = ['Grant']
    for project in projects_combination:
        combination(project)