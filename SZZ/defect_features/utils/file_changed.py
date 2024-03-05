import csv
import os
from defect_features.config import  conf



LOG_CMD = 'git log --pretty=format:\"commit: %H\" --name-status  --reverse '
#BASIC_PROJECT_PATH = '/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git'
basic_file_path= os.path.join(os.path.dirname(conf.data_path),os.pardir, 'report')


file_dict = dict()

def file_change(project_namestat,project):
    file_path = os.path.join(basic_file_path,project+".csv")
    save_path = os.path.join(basic_file_path,project+"_2.csv")
    with open(save_path,"w") as f_obj:
        columns_write = ['commit_id', 'time_stamp', 'creation_time', 'author_email',
                         'commit_message', 'ns', 'nd', 'nf', 'entropy', 'exp', 'rexp',
                         'sexp', 'ndev', 'age', 'nuc', 'la', 'ld', 'lt', 'block',
                         'critical', 'major', 'block_total', 'critical_total', 'major_total',
                         'is_fix', 'classification', 'contains_bug', 'file_changed','buggy_lines', 'fix_by',
                         'find_interval', 'fixes', 'fix_file_num', 'rules', ' bug_fix_files']
        writer = csv.DictWriter(f_obj,fieldnames=columns_write)
        writer.writeheader()
        with open(file_path, "r") as f_obj_2:
            f_csv = csv.DictReader(f_obj_2)
            for row in f_csv:
                commit_id = row["commit_id"]
                file_changed = list()
                if commit_id in project_namestat:
                    for key in project_namestat[commit_id].file_modify_type.keys():
                        file_changed.append(key)
                row["file_changed"] = ",CAS_DELIMITER,".join(file_changed[:50])

                writer.writerow(row)






if __name__=="__main__":
    projects = ["Grant"]
    for project in projects:
        file_change("",project)