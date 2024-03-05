import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir,os.path))
# "/home/wenfeng/vlis/defect_prediction")
import subprocess
import shutil
import re
from defect_features.features.git_commit_features import GitCommitFeatures

basic_project_dir = "/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git"
data_dir = "tmp"


def toCommitIn(commits):
    commit_info = list()
    son_parent = dict()
    for commit in commits:
        commit_id = commit.commit_id
        son_parent[commit_id] = commit.parent
        parent_id = ",".join(commit.parent)
        son_id = ",".join(commit.sons)
        project = commit.project
        author_email = commit.author_email
        time_stamp = str(commit.time_stamp)
        message = " ".join(commit.commit_message.replace("\r", " ").split("\n"))
        commit_str = ";".join([commit_id,parent_id,son_id,project,author_email,time_stamp,message])
        commit_info.append(commit_str)
    commit_in_dir = os.path.join(data_dir,project,"commit_in")
    with open(commit_in_dir,"w") as file_obj:
        file_obj.write("\n".join(commit_info))
    return son_parent

# non merge commit
def toFileIn(git_commit_features,project_dir,project_data_dir,son_parent):
    diff_dir = os.path.join(project_data_dir, "diff")
    blame_dir = os.path.join(project_data_dir, "blame")
    os.mkdir(diff_dir)
    os.mkdir(blame_dir)
    file_info = list()
    commits = git_commit_features.project_logs
    name_status = git_commit_features.project_namestat
    numstat = git_commit_features.project_numstat
    for commit in commits:
        commit_id = commit.commit_id
        # merge commit
        if len(commit.parent) > 1:
            continue
        parent_id = ",".join(son_parent[commit_id])
        file_dict = dict()
        for elem in name_status[commit_id].file_name_stat:
            file_name = elem['modified_path']
            modified_path = elem['modified_path']
            rename = ""
            modified_type = elem['type']
            if modified_type == 'add':
                status = 'A'
            elif modified_type == 'delete':
                status = 'D'
            elif modified_type == 'rename':
                file_name = elem['current_path']
                rename = elem['modified_path']
                status = 'R'
            else:
                status = 'M'
            file_dict[modified_path] = {"filename":file_name,"status":status,"rename":rename,
                                        "commit_id":commit_id,"parent_id":parent_id,
                                        "diff":"","blame":""}
        for elem in numstat[commit_id].file_stat:
            modified_path = elem["modified_path"]
            num_added_lines = elem["added"]
            num_deleted_lines = elem["deleted"]
            file_dict[modified_path]["num_added_lines"] = num_added_lines
            file_dict[modified_path]["num_deleted_lines"] = num_deleted_lines
        if len(commit.parent) > 0:
            getDiff(commit.commit_id, project_dir, diff_dir)
            getBlame(commit.commit_id, file_dict, project_dir, blame_dir)
        # to file_in
        for values in file_dict.values():
            file_str = ";".join([values["filename"],values["commit_id"],
                                values["parent_id"],values["status"],
                                str(values["num_added_lines"]),str(values["num_deleted_lines"]),
                                values["rename"],values["diff"],values["blame"]])
            file_info.append(file_str)
    file_in_dir = os.path.join(project_data_dir,"file_in")
    with open(file_in_dir,"w") as file_obj:
        file_obj.write("\n".join(file_info) + "\n")

# merge commit
def toFileInMerge(git_commit_features,project_data_dir):
    file_info = list()
    merge_name_status = git_commit_features.project_merge_namestat
    merge_numstat = git_commit_features.project_merge_numstat
    for commit_base, elem in merge_name_status.items():
        commit_id = elem.commit_id
        parent_id = elem.base_commit
        file_dict = dict()
        for f_name_stat in elem.file_name_stat:
            file_name = f_name_stat['modified_path']
            modified_type = f_name_stat['type']
            modified_path = f_name_stat['modified_path']
            rename = ""
            if modified_type == 'add':
                status = 'A'
            elif modified_type == 'delete':
                status = 'D'
            elif modified_type == 'rename':
                file_name = f_name_stat['current_path']
                rename = f_name_stat['modified_path']
                status = 'R'
            else:
                status = 'M'
            file_dict[modified_path] = {"filename": file_name, "status": status, "rename": rename,
                                        "commit_id": commit_id, "parent_id": parent_id,
                                        "diff": "", "blame": ""}
        for f_num_stat in merge_numstat[commit_base].file_stat:
            num_added_lines = f_num_stat['added']
            num_deleted_lines = f_num_stat['deleted']
            modified_path = f_num_stat['modified_path']
            file_dict[modified_path]['num_added_lines'] = num_added_lines
            file_dict[modified_path]['num_deleted_lines'] = num_deleted_lines
        # to file_in
        for values in file_dict.values():
            file_str = ";".join([values["filename"], values["commit_id"],
                                 values["parent_id"], values["status"],
                                 str(values["num_added_lines"]), str(values["num_deleted_lines"]),
                                 values["rename"], values["diff"], values["blame"]])
            file_info.append(file_str)
    file_in_dir = os.path.join(project_data_dir, "file_in")
    with open(file_in_dir, "w") as file_obj:
        file_obj.write("\n".join(file_info))

def escape_char(str):
    return str.replace('$','\$').replace('{','\{').replace('}','\}')


def getDiff(commit,project_dir,diff_dir):
    out_raw = subprocess.check_output("git diff {commit_id}^ {commit_id_2}".
                                      format(commit_id=commit,commit_id_2 = commit),
                                      cwd=project_dir,shell=True).decode("utf-8",errors='ignore')
    regions = out_raw.split("diff --git")[1:]
    for region in regions:
        file_name = re.search(r'b/(\S+)',region).group(1)
        file_name = escape_char(file_name.replace('/', '[SEP]'))
        with open(os.path.join(diff_dir,commit+'_'+file_name),'w') as file_obj:
            file_obj.write(region)

def getBlame(commit,file_status,project_dir,blame_dir):
    for key,value in file_status.items():
        status = value['status']
        file_name = value['filename']
        # blame rename file
        # https://stackoverflow.com/questions/29468273/why-git-blame-does-not-follow-renames
        if status == "R":
            blame_name = value['rename']
        else:
            blame_name = file_name
        if status != "A":
            try:
                out_raw = subprocess.check_output("git blame -f -n {commit}^ -l -- {file}".
                                        format(commit=commit,file=blame_name),
                                        cwd=project_dir,shell=True).decode("utf-8",errors='ignore')

                file_dir = os.path.join(blame_dir,commit + "_"+escape_char(file_name.replace('/', '[SEP]')))
                with open(file_dir,'w') as file_obj:
                    file_obj.write(out_raw)
            except subprocess.CalledProcessError as e:
                print(e)


def main(project):
    project_dir = os.path.join(basic_project_dir, project)
    project_data_dir =  os.path.join(data_dir,project)
    if not os.path.isdir(project_data_dir):
        os.mkdir(project_data_dir)
    else:
        shutil.rmtree(project_data_dir)
        os.mkdir(project_data_dir)
    gcf = GitCommitFeatures
    gcf.initialize(project, merge_all_log=True)
    son_parent = toCommitIn(gcf.project_logs)
    toFileIn(gcf,project_dir,project_data_dir,son_parent)
    toFileInMerge(gcf,project_data_dir)
if __name__=="__main__":
    projects = ["pf4j"]
    for project in projects:
        print(project)
        main(project)