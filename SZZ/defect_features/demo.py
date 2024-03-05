import subprocess
import numpy as np
from defect_features.utils.diff_utils import is_noise

SHOW_CMD = "git show {commit_id}:{file_name}"
project_dir = "/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git/apache/derby"

def process_splited_line(commit_id,file_name,line_num):
    content = subprocess.check_output(SHOW_CMD.format(commit_id=commit_id,
                                        file_name=file_name),shell=True,cwd=project_dir).\
                                       decode("utf-8").split("\n")
    whole_line = ""
    index = 0
    current_line_num = 0
    for line in content:
        index += 1
        if is_noise(line):
            current_line_num = index + 1
            continue
        whole_line += line
        if line.endswith(";") or line.endswith("}")or line.endswith("{"):
            print(current_line_num,whole_line)
            whole_line = ""
            current_line_num = index + 1

LOG_CMD = 'git log  --pretty=format:\"[COMMIT]%H[SEP]%an[SEP]%ad[SEP]%B\"'
def test():
    l = [[1,2,3],[4,6]]
    a = np.array(l)
    print(a)



if __name__=="__main__":
    target_content = "dbname, getHostName(), String.valueOf(getPortNumber()));"
    commit_id="f2ec1d8c88b705a154801a104ad4e0f65e1b69d1"
    file_name = "java/engine/org/apache/derby/impl/store/replication/slave/SlaveController.java"
    line_num = 362
    #process_splited_line(commit_id,file_name,line_num)
    test()