import subprocess
import os
import time
import re
import pandas as pd
import xml.etree.ElementTree as ET

LOG_CMD = "git log --name-status --pretty=format:'commit: %H timestamp: %at date: %cd' --reverse  "
BASIC_PATH = "/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git"
SHOW_CMD = 'git show {!s}:{!s} > {!s}'
PMD_CMD = 'java -cp p3c-pmd.jar net.sourceforge.pmd.PMD -d {!s} -f xml -r {!s} -R rule/ali-comment.xml,' \
          'rule/ali-concurrent.xml,rule/ali-constant.xml,rule/ali-exception.xml,rule/ali-flowcontrol.xml,rule/ali-naming.xml,' \
          'rule/ali-oop.xml,rule/ali-orm.xml,rule/ali-set.xml,rule/ali-other.xml'
RM_CMD = 'rm {!s}'
COLUMNS_WRITE = ['file','block','critical','major']


class File(object):
    def __init__(self,project, file_name):
        self.file_name = file_name
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
    java_tmp = os.path.join(project_dir,file_obj.file_name)
    xml_tmp = '/home/wenfeng/vlis/defect_prediction/p3c_pmd/tmp/tmp_' + file_obj.project + '.xml'
    try:
        # 部分文件或文件夹命名有可能使用环境变量，在这里对环境变量临时转义为普通变量.解决 /bin/bash： bad substitution 问题
        subprocess.call(PMD_CMD.format(java_tmp, xml_tmp), shell=True,executable='/bin/bash')
    except Exception as e:
        print ('get_pmd error:', e)
        return None
    block, critical, major = parse_xml(xml_tmp)
    subprocess.call(RM_CMD.format(xml_tmp),shell=True,executable='/bin/bash')
    return block, critical, major

def escape_char(str):
    return str.replace('$','\$').replace('{','\{').replace('}','\}')


def main(project):
    project_dir = os.path.join(BASIC_PATH,project)
    files = subprocess.check_output('git ls-files | grep .java$',cwd=project_dir,shell=True).\
        decode('utf-8',errors='ignore').split('\n')
    block_total = 0
    critical_total = 0
    major_total = 0
    files_dict = dict()
    for file in files:
        if not file.endswith('java'):
            continue
        file = escape_char(file)
        file_obj = File(project,file)
        block, critical, major = p3c(file_obj,project_dir)
        print(file,block,critical,major)
        files_dict[file] = {'file':file,'block':block,'critical':critical,'major':major}
        block_total += block
        critical_total += critical
        major_total += major
    df = pd.DataFrame(files_dict).T
    df.to_csv(project + '_master.csv',index=False,columns=COLUMNS_WRITE)

    with open('p3c_master.txt','a') as f_p3c_master:
        print(time.asctime(time.localtime()),project,block_total,critical_total,major_total,file=f_p3c_master)




if __name__ == '__main__':
    projects = ['Grant']
    for project in projects:
        main(project)


