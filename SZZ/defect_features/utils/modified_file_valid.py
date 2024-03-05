# coding=utf-8
import subprocess
import json
import sys
import re


FILE_CMD = "git log --pretty=format:\"commit:%H\"  --name-status --all  --diff-filter=MA -- *.java"
DIFF_CMD = "git diff {commit_id}^ {commit_id_2} --unified=0 -- {file}"
DIFF_PATTERN = re.compile(r"@@\s+-\d+(?:,?\d+)?\s+\+\d+(?:,?\d+)?\s+@@.*")


def is_noise(line):
    #
    line = line.strip('\t').strip('\r').strip()
    # ignore blank line
    if line == '':
        return True
    # ignore comment
    # consider more programming language
    # TO DO
    if line.startswith('//') or line.startswith('/**') or line.startswith('*') or \
            line.startswith('/*') or line.endswith('*/'):
        return True
    # ignore import line
    # consider more programming language
    # TO DO
    if line.startswith('import '):
        return True
    return False

def get_file(project_dir):
    files_dict = dict()
    out_raw = subprocess.check_output(FILE_CMD,cwd=project_dir,shell=True)\
        .decode("utf-8",errors="ignore")
    commits_regions = out_raw.split("commit:")[1:]
    for commit_region in commits_regions:
        lines = commit_region.split("\n")
        commit_id = lines[0]
        files_dict[commit_id] = list()
        for line in lines[1:]:
            if line == "":
                continue
            else:
                file_name = line.split("\t")[1]
            files_dict[commit_id].append(file_name)
    return files_dict

def filte_file(diff_list):
    for diff in diff_list:
        lines = diff.split("\n")
        for line in lines:
            strip_line = line.strip("-").strip("+")
            flag = is_noise(strip_line)
            if flag == False:
                return False
    return True

def main(project_dir,save_path):
    files_dict = get_file(project_dir)
    files_filted_dict = dict()
    for commit_id, files in files_dict.items():
        files_filted_dict[commit_id] = list()
        for file in files:
            try:
                diff_raw = subprocess.check_output(DIFF_CMD.format(commit_id=commit_id,
                                                                   commit_id_2=commit_id, file=file),
                                                   shell=True, cwd=project_dir, executable='/bin/bash') \
                    .decode('utf-8', errors='ignore')
                diff_list = DIFF_PATTERN.split(diff_raw)[1:]
                flag = filte_file(diff_list)
                if flag == False:
                    files_filted_dict[commit_id].append(file)
            except Exception as e:
                files_filted_dict[commit_id].append(file)
    with open(save_path,"w") as f:
        json.dump(files_filted_dict,f)


if __name__=="__main__":
    if len(sys.argv) != 3:
        print("no")
    project_dir = sys.argv[1]
    save_path = sys.argv[2]
    main(project_dir,save_path)
    print("yes")

