import subprocess
import os
import re
import csv
import json
from defect_features.config import conf
#from defect_features.utils.extensions import in_our_extensions
import logging

SHOW_CMD = 'git show {!s}:{!s} > {!s}'
LOG_CMD = 'git log --pretty=format:\"commit: %H\" --name-status --diff-filter=MA --all --reverse -- \"*.java\"'
BASIC_PROJECT_PATH = '/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git'
BASIC_DEST_PATH = '/home/wenfeng/vlis/defect_prediction/data'

# logging
logger_name = 'get_file'

def escape_char(str):
    return str.replace('$','\$').replace('{','\{').replace('}','\}')


def git_show(commit_id,file,project_path,dest_path):
    try:
        out = subprocess.check_call(SHOW_CMD.format(commit_id, file, dest_path), shell=True, cwd=project_path)
    except subprocess.CalledProcessError as e:
        print('git_show error', commit_id, file, e.stderr, )


def get_all_files(project,project_path):
    try:
        raw_out = subprocess.check_output(LOG_CMD,shell=True,cwd=project_path).decode('utf-8',errors='ignore')
    except Exception as e:
        print('get_all_files error', e)
    chunks = raw_out.split('commit: ')
    all_files = dict()
    for chunk in chunks[1:]:
        lines = chunk.split('\n')
        commit = lines[0]
        files = list()
        for line in lines[1:]:
            if line:
                file = re.split('\w\t',line)[1]
                files.append(file)
        if files:
            all_files[commit] = files
    return all_files

def get_clean_files(all_files,buggy_files):
    all_clean_files = dict()
    for commit, files in all_files.items():
        if commit in buggy_files:
            clean_files = list(set(files) - set(buggy_files[commit]))
        else:
            clean_files = files
        if clean_files:
            all_clean_files[commit] = clean_files
    return all_clean_files

def main(project):
    csv_file = os.path.join(os.path.dirname(conf.data_path),os.pardir,'report',project + '.csv')
    project_path = os.path.join(BASIC_PROJECT_PATH,project)
    dest_project_dir = os.path.join(BASIC_DEST_PATH, project)
    # make project dir to store files modified by each commit
    os.mkdir(dest_project_dir)
    # make clean file dir
    clean_dir = os.path.join(dest_project_dir,'clean_files')
    os.mkdir(clean_dir)
    # make buggy file dir
    buggy_dir = os.path.join(dest_project_dir, 'buggy_files')
    os.mkdir(buggy_dir)
    buggy_files = dict()
    all_files = get_all_files(project,project_path)
    with open(csv_file,'r') as file:
        f_csv = csv.DictReader(file)
        for row in f_csv:
            if row['buggy_lines'] != '':
                buggy_files[row['commit_id']] = list(json.loads(row['buggy_lines']).keys())
    # get buggy files
    for commit_id, files in buggy_files.items():
        commit_dir = os.path.join(buggy_dir, commit_id)
        os.mkdir(commit_dir)
        for file in files:
            file_name = escape_char(file.replace('/', '[SEP]'))
            file_path = os.path.join(commit_dir, file_name)
            git_show(commit_id,file,project_path,file_path)

    clean_files = get_clean_files(all_files,buggy_files)
    for commit_id, files in clean_files.items():
        commit_dir = os.path.join(clean_dir,commit_id)
        os.mkdir(commit_dir)
        for file in files:
            file_name = escape_char(file.replace('/', '[SEP]'))
            file_path = os.path.join(commit_dir, file_name)
            git_show(commit_id,file_name,project_path,file_path)


if __name__ == '__main__':
    projects = ['AspectJ']
    for project in projects:
        main(project)
