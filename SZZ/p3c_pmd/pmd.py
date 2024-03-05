#!/usr/bin/python3
import subprocess
import os
import re
import time
import json
import shutil
import xml.etree.ElementTree as ET
from defect_features.config import conf
from defect_features.utils.extensions import in_our_extensions
from defect_features.object import files
from defect_features.utils import linux_utils


class Pmd(object):
    """
    get pmd result

    """
    LOG_CMD = 'git log --pretty=format:\"commit: %H\" --name-status --all --reverse'
    SHOW_CMD = 'git show {!s}:{!s} > {!s}'
    PMD_CMD = 'java -cp p3c-pmd.jar net.sourceforge.pmd.PMD -d {!s} -f csv -R rule/ali-comment.xml,' \
              'rule/ali-concurrent.xml,rule/ali-constant.xml,rule/ali-exception.xml,rule/ali-flowcontrol.xml,rule/ali-naming.xml,' \
              'rule/ali-oop.xml,rule/ali-orm.xml,rule/ali-set.xml,rule/ali-other.xml'
    RM_CMD = 'rm {!s} '
    DIFF_CMD = "git diff {commit_id}^ {commit_id_2} --unified=0 | while read; do echo 'LINE_START:' \"$REPLY\";done"
    MAX_LINE = 10000

    def __init__(self, project,all_commits):
        self.project = project
        self.pmd_path = os.path.join(conf.df_basic_path,'p3c_pmd')
        self.java_tmp = self.pmd_path + '/tmp/tmp_' + project + '.java'
        self.project_dir = os.path.join(conf.data_path,project)
        self.all_commits = all_commits
        self.file_objs = dict()

    def update_file_p3c(self,file_name,p3c_results):
        # reset warning
        self.file_objs[file_name].block = 0
        self.file_objs[file_name].critical = 0
        self.file_objs[file_name].major = 0
        for p3c_result in p3c_results.values():
            if p3c_result['priority'] == 1:
                self.file_objs[file_name].block += 1
            elif p3c_result['priority'] == 2:
                self.file_objs[file_name].critical += 1
            elif p3c_result['priority'] == 3:
                self.file_objs[file_name].major += 1


    def process_total(self,commit_obj):
        for file_obj in self.file_objs.values():
            if file_obj.current_type == 'delete' or file_obj.current_type == 'rename':
                continue
            else:
                commit_obj.block_total += file_obj.block
                commit_obj.critical_total += file_obj.critical
                commit_obj.major_total += file_obj.major

    def _get_add_lines(self,diff_raw):

        # files(lines) to be analyzed. key: string, file name; values : list , the line number of deleted line
        add_lines = dict()

        # start to parse git diff information
        # one file one region
        regions = diff_raw.split('LINE_START: diff --git')[1:]
        for region in regions:
            # chinese character error
            try:
                file_name = re.search(r' b/(.+)',region).group(1)
            except Exception as e:
                print('_get_add_lines: parse file name error', e, region)
            if file_name not in add_lines:
                add_lines[file_name] = list()
            chunks = region.split('LINE_START: @@')[1:]
            for chunk in chunks:
                lines = chunk.split('\n')
                line_info = re.search(r'\+(\d*)',lines[0])
                # current line number of file a(usually previous file)
                current_b = int(line_info.group(1))
                # parse each line, except chunk header
                # some file may not delete any line, and we need process this condition later
                for line_raw in lines[1:]:
                    line = line_raw.strip('LINE_START: ')
                    # ignore line not del
                    if not line.startswith('+'):
                        continue
                    add_lines[file_name].append(current_b)
                    current_b += 1
            if not add_lines[file_name]:
                add_lines.pop(file_name)
        return add_lines

    def get_add_lines(self,commit):
        try:
            diff_raw = subprocess.check_output(self.DIFF_CMD.format(commit_id=commit, commit_id_2=commit), shell=True,
                                               cwd=self.project_dir, executable='/bin/bash').decode('utf-8',errors='ignore')
            add_lines = self._get_add_lines(diff_raw)
            return add_lines
        except subprocess.CalledProcessError as e:
            print('get_add_lines error:', commit, e)
            return -1

    def get_target_files(self,commit):
        target_files = list() # file modified
        for elem in commit.file_name_stat:
            file_name = elem['modified_path']
            file_type = elem['type']
            if file_name not in self.file_objs:
                file_obj = files.File(file_name,file_type)
                self.file_objs[file_name] = file_obj
            else:
                self.file_objs[file_name].current_type = file_type
            if in_our_extensions(file_name):
                target_files.append(file_name)
        return target_files

    # get the modified files after the commit
    def get_pmd(self,commit, file):
        """

        :param commit:
        :param file:
        :return:
        """
        pmd_result = dict()
        try:
            # 部分文件或文件夹命名有可能使用环境变量，在这里对环境变量临时转义为普通变量.解决 /bin/bash： bad substitution 问题
            subprocess.call(self.SHOW_CMD.format(commit,linux_utils.escape_char(file),
                                                 linux_utils.escape_char(self.java_tmp)), shell=True,cwd=self.project_dir,executable='/bin/bash')
            pmd_path = os.path.dirname(__file__)
            out_bytes = subprocess.check_output(self.PMD_CMD.format(linux_utils.escape_char(self.java_tmp)),shell=True,executable='/bin/bash',
                                                cwd=pmd_path)
        except subprocess.CalledProcessError as e:
            out_bytes = e.output
            code = e.returncode
            lines = out_bytes.decode('utf-8').split('\n')
            pmd_result = dict()
            for line in lines[1:]:
                if line == '':
                    continue
                try:
                    elem = line.split(',')
                    problem = int(elem[0].strip("\"").strip("\""))
                    file_name = elem[2].strip("\"").strip("\"")
                    priority = int(elem[3].strip("\"").strip("\""))
                    line_st = int(elem[4].strip("\"").strip("\""))
                    rule = elem[7].strip("\"").strip("\"")
                    pmd_result[problem] = {'line_st':line_st,'file_name':file_name,'priority':priority,'rule':rule}
                except Exception as e:
                    print(e)
                    return pmd_result
        return pmd_result

    def compare(self,commit,add_lines,p3c_results):
        for line_num in add_lines:
            for p3c_result in p3c_results.values():
                if p3c_result['line_st'] == line_num:
                    if p3c_result['priority'] == 1:
                        commit.block += 1
                    elif p3c_result['priority'] == 2:
                        commit.critical += 1
                    elif p3c_result['priority'] == 3:
                        commit.major += 1
                    if not commit.rules:
                        commit.rules = json.dumps({p3c_result['rule']:1})
                    else:
                        rules = json.loads(commit.rules)
                        if p3c_result['rule'] in rules:
                            rules[p3c_result['rule']] = int(rules[p3c_result['rule']]) + 1
                        else:
                            rules[p3c_result['rule']] = 1
                        commit.rules = json.dumps(rules)



    def pmd_main(self):
        print (self.project,': p3c_pmd start to analyze!')
        start = time.time()
        all_num = len(self.all_commits)
        current = 1
        # only analyze modified files
        for commit in self.all_commits:
            target_files = self.get_target_files(commit)
            for file_name in target_files:
                if self.file_objs[file_name].current_type == 'delete' or self.file_objs[file_name].current_type == 'rename':
                    print('escape pmd_main',file_name, self.file_objs[file_name].current_type)
                    continue
                else:
                    pmd_results = self.get_pmd(commit.commit_id, file_name)
                    # pmd analysis without result
                    if not pmd_results:
                        continue
                # update file p3c warning
                self.update_file_p3c(file_name,pmd_results)

                add_lines = self.get_add_lines(commit.commit_id)  # dict key:file value: list add line
                # init commit
                if add_lines == -1:
                    break
                # target file dose not add any target line
                if not add_lines or (file_name not in add_lines):
                    continue
                self.compare(commit,add_lines[file_name],pmd_results)
            print(self.project, 'pmd analyzing ({current}/{all_num})'.format(current=current, all_num=all_num),
                  commit.commit_id, commit.block, commit.critical, commit.major)
            self.process_total(commit)
            print(self.project, 'pmd analyzing ({current}/{all_num}) total:'.format(current=current, all_num=all_num),
                  commit.commit_id, commit.block_total, commit.critical_total, commit.major_total)
            current += 1
        end = time.time()
        print(self.project, 'pmd analysis using  cpu time {cpu_time}(min)'.format(cpu_time = (end-start)/60))


if __name__=='__main__':
    repos = 'Grant'
    pmd = Pmd(repos,[])
    pmd.pmd_main()


