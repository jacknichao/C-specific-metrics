import subprocess
import os
import time


PMD_CMD = 'java -cp p3c-pmd.jar net.sourceforge.pmd.PMD -d {!s} -f csv -R rule/ali-comment.xml,' \
              'rule/ali-concurrent.xml,rule/ali-constant.xml,rule/ali-exception.xml,rule/ali-flowcontrol.xml,rule/ali-naming.xml,' \
              'rule/ali-oop.xml,rule/ali-orm.xml,rule/ali-set.xml,rule/ali-other.xml '
#file = '/home/wenfeng/vlis/defect_prediction/p3c_pmd/tmp/DiffsImpl.java'
def ls_files(project):
    project_dir = os.path.join('/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git',project)
    out = subprocess.check_output('git ls-files | grep .java$',cwd=project_dir,shell=True,executable='/bin/bash').decode('utf-8')
    files = out.split('\n')
    return files

def main(project):
    project_dir = os.path.join('/home/wenfeng/vlis/cas_vlis/ingester/CASRepos/git', project)
    files = ls_files(project)
    files = ['/home/wenfeng/vlis/defect_prediction/p3c_pmd/PluginDescriptor.java']
    for file in files:
        try:
            file_name = os.path.join(project_dir,file)
            out_bytes = subprocess.call(PMD_CMD.format(file_name),shell=True,executable='/bin/bash')
        except Exception as e:
            pass
            #print(e)
        #print(type(out_bytes))
        lines = out_bytes.decode('utf-8').split('\n')
        # for line in lines[1:-2]:
        #     if line == '':
        #         continue
        #     elem = line.split(',')
        #     file_name = elem[2]
        #     priority = elem[3]
        #     line_st = elem[4]
        #     rule = elem[7]
        #     print(file_name,line_st,rule,priority)



if __name__=='__main__':
    start = time.time()
    main('force')
    end = time.time()
    print((end-start)/60)