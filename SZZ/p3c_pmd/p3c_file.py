import subprocess
import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
from defect_features.utils.linux_utils import escape_char

LOG_CMD = "git log --name-status --pretty=format:'commit: %H timestamp: %at date: %cd' --reverse  "
BASIC_PATH = "/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git"
SHOW_CMD = 'git show {!s}:{!s} > {!s}'
PMD_CMD = 'java -cp p3c-pmd.jar net.sourceforge.pmd.PMD -d {!s} -f xml -r {!s} -R rule/ali-comment.xml,' \
          'rule/ali-concurrent.xml,rule/ali-constant.xml,rule/ali-exception.xml,rule/ali-flowcontrol.xml,rule/ali-naming.xml,' \
          'rule/ali-oop.xml,rule/ali-orm.xml,rule/ali-set.xml,rule/ali-other.xml'
RM_CMD = 'rm {!s} {!s}'
COLUMS_WRITE = ['commit_id','date','timestamp','file_num','block','critical','major']


class File(object):
    def __init__(self,project, file_name, status,commit):
        self.file_name = file_name
        self.status = status
        self.current_commit = commit
        self.all_commits = list()
        self.all_commits.append(commit)
        self.project = project

    def set_p3c(self,block,critical,major):
        self.block = block
        self.critical = critical
        self.major = major

    def set_commit(self,commit):
        self.current_commit = commit
        self.all_commits.append(commit)

class Commit(object):
    def __init__(self,commit_id,timestamp,date):
        self.commit_id = commit_id
        self.block = 0
        self.critical = 0
        self.major = 0
        self.file_num = 0
        self.timestamp = timestamp
        self.date =date


def parse_xml(xml_file):
    block_file = 0
    critical_file = 0
    major_file = 0
    try:
        tree = ET.ElementTree(file=xml_file)
        for elem in tree.iter(tag='violation'):
            priority = int(elem.get('priority'))
            if priority == 1:
                block_file += 1
            elif priority == 2:
                critical_file += 1
            else:
                major_file += 1
    except Exception as e:
        print('parse_xml error:', e)
    finally:
        return block_file,critical_file,major_file

# get the modified files after the commit
def p3c(file_obj,project_dir):
    java_tmp = '/home/wenfeng/vlis/defect_prediction/p3c_pmd/tmp/tmp_' + file_obj.project + '.java'
    xml_tmp = '/home/wenfeng/vlis/defect_prediction/p3c_pmd/tmp/tmp_' + file_obj.project + '.xml'
    try:
        # 部分文件或文件夹命名有可能使用环境变量，在这里对环境变量临时转义为普通变量.解决 /bin/bash： bad substitution 问题
        subprocess.call(SHOW_CMD.format(file_obj.current_commit,file_obj.file_name,java_tmp), shell=True,cwd=project_dir,executable='/bin/bash')
        subprocess.call(PMD_CMD.format(java_tmp, xml_tmp), shell=True,executable='/bin/bash')
    except Exception as e:
        print ('get_pmd error:', e)
        return None
    block, critical, major = parse_xml(xml_tmp)
    subprocess.call(RM_CMD.format(java_tmp,xml_tmp),shell=True,executable='/bin/bash')
    return block, critical, major


def main(project):
    project_dir = os.path.join(BASIC_PATH,project)
    p3c_dict = dict()
    files_dict = dict()
    file_store = "./total_" + project + ".csv"
    out_raw = subprocess.check_output(LOG_CMD,shell=True,cwd=project_dir).decode('utf-8',errors='ignore')
    regions_commit = out_raw.split('commit: ')[1:]
    commits_num = len(regions_commit)
    current = 1
    for region in regions_commit:
        lines = region.split('\n')
        pat = r"(\w+) timestamp: (\d+) date: (.+)"
        try:
            re_out = re.search(pat,lines[0])
            commit_id = re_out.group(1)
            timestamp = re_out.group(2)
            date = re_out.group(3)
        except Exception as e:
            print('regular expressio error',e)
            continue
        print("{!s} {!s}/{!s}: {!s}".format(project,current, commits_num, commit_id))
        commit_obj = Commit(commit_id,timestamp,date)
        for line in lines[1:]:
            if line == '':
                continue
            status = line.split('\t')[0]
            file_name = line.split('\t')[1]
            ext = os.path.splitext(file_name)[1]
            if ext != '.java':
                continue
            else:

                file_name = escape_char(file_name)
            if file_name in files_dict:
                files_dict[file_name].status = status
                files_dict[file_name].set_commit(commit_id)
            else:
                file_obj = File(project,file_name,status,commit_id)
                files_dict[file_name] = file_obj
            if file_obj.status != 'D':
                block, critical,major = p3c(file_obj,project_dir)
                file_obj.set_p3c(block,critical,major)
        for file_obj in files_dict.values():
            if file_obj.status != 'D':
                commit_obj.file_num += 1
                commit_obj.block += file_obj.block
                commit_obj.critical += file_obj.critical
                commit_obj.major += file_obj.major
        if commit_obj.commit_id not in p3c_dict:
            p3c_dict[commit_obj.commit_id] = dict()
            p3c_dict[commit_obj.commit_id]['commit_id'] = commit_obj.commit_id
            p3c_dict[commit_obj.commit_id]['timestamp'] = commit_obj.timestamp
            p3c_dict[commit_obj.commit_id]['date'] = commit_obj.date
            p3c_dict[commit_obj.commit_id]['file_num'] = commit_obj.file_num
            p3c_dict[commit_obj.commit_id]['block'] = commit_obj.block
            p3c_dict[commit_obj.commit_id]['critical'] = commit_obj.critical
            p3c_dict[commit_obj.commit_id]['major'] = commit_obj.major
            print(commit_obj.file_num, commit_obj.block,commit_obj.critical,commit_obj.major)
            current += 1
    df = pd.DataFrame(p3c_dict).T.sort_values(by=['timestamp'],ascending=False)
    df.to_csv(file_store, index=False, columns=COLUMS_WRITE)




if __name__ == '__main__':
    projects = ['force','scmcenter']
    for project in projects:
        main(project)

