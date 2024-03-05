#-*- coding: utf-8 -*-
from .git_commit_features import GitCommitFeatures
from copy import deepcopy
import sys
from defect_features.utils.extensions import in_our_extensions
from defect_features.git_analysis.analyze_git_logs import retrieve_git_logs
from defect_features.object.features import SizeFeatures as SizeFeaturesObj



class SizeFeatures(GitCommitFeatures):
    mem = 0
    def __init__(self, rgcm):
        super(SizeFeatures, self).__init__(rgcm)

    def evolve_from_prior_commit(self):
        la = 0
        ld = 0
        lt = 0
        nf = 0
        gcf = GitCommitFeatures
        # 这里的stats实际上就是project_numstat，即GitNumStat实例
        stats = self.stats
        namestats = self.namestat

        # 判断当前的commit有几个父commit
        if len(self.parents) == 0:
            p = None
        elif len(self.parents) == 1:
            p = self.parents[0]
        else:
            # 多个父commit，说明是merge过来的，大修中被列举出来的实例中并没有这种情况
            if gcf.project_merge_numstat[self.commit_id].base_commit is not None:
                p = gcf.project_merge_numstat[self.commit_id].base_commit
                stats = gcf.project_merge_numstat[self.commit_id]
                namestats = gcf.project_merge_namestat[self.commit_id]
            else:
                p = self.parents[0]
                stats = None

        if stats is not None:
            # 其中files表示所有修改的文件，是一个元祖构成的set，即set (（'modified_path','added','deleted'）)
            # rename_files 表示修改的文件中是重命名操作的文件，是一个字典即 '修改之前的文件路径'->'修改之后的文件路径'
            files, rename_files = stats.modified_files
        else:
            # merge后和两个分支对比都没有变化
            files = []
            rename_files = []

        # 不是初始化的commit，查找其父commit的相关情况，以便于获得父辈commit中获取所有文件相关的commit，这是是一个递归的关系，
        # 这些文件的信息都是从最原始的initialize中得到的，同时也会伴随着modification和delete等操作会更新项目中文件的信息，主要是文件的行数
        if p is not None:
            file_stats = gcf.parent_file_stats[p]['files']
            if gcf.parent_file_stats[p]['son_num'] == 1:
                gcf.parent_file_stats[self.commit_id]['files'] = file_stats
            else:
                # 新建分支，file_stats deepcopy一份
                gcf.parent_file_stats[self.commit_id]['files'] = deepcopy(file_stats)

        # 遍历所有修改的文件
        for f, added, deleted in files:
            try:
                # 类GitNameStat, 确定文件的修改类型
                namestats.file_modify_type[f]
            except Exception as e:
                print("Warning: special file path: %s; ignored!" % f)
                continue

            # 分别判断每个修改的文件的修改类型
            if namestats.file_modify_type[f] == 'add':
                assert (deleted == 0)
                #
                gcf.parent_file_stats[self.commit_id]['files'][f] = added
                if in_our_extensions(f):
                    nf += 1
                    la += added
            elif namestats.file_modify_type[f] == 'delete':
                assert (added == 0)
                #assert(deleted == file_stats[f])

                if in_our_extensions(f):
                    lt += file_stats[f]
                    nf += 1
                    ld += deleted
                #
                del gcf.parent_file_stats[self.commit_id]['files'][f]
            elif namestats.file_modify_type[f] == 'rename':
                cur_file = rename_files[f]
                tmp = file_stats[f]
                assert (tmp + added - deleted >= 0)
                #
                gcf.parent_file_stats[self.commit_id]['files'][cur_file] = tmp + added - deleted
                if in_our_extensions(f) or in_our_extensions(cur_file):
                    lt += tmp
                    nf += 1
                    la += added
                    ld += deleted
                #
                del gcf.parent_file_stats[self.commit_id]['files'][f]
            else:
                assert (namestats.file_modify_type[f] == 'modify')
                tmp = file_stats[f]
                assert (tmp + added - deleted >= 0)
                #
                gcf.parent_file_stats[self.commit_id]['files'][f] = tmp + added - deleted
                if in_our_extensions(f):
                    lt += tmp
                    nf += 1
                    la += added
                    ld += deleted
        if len(self.parents) > 1:
            # merger 的commit 这些都是为零的
            lt = 0
            la = 0
            ld = 0
        else:
            inner_nf = 0
            for inner_f, inner_added, inner_deleted in files:
                if self.in_required_extensions(inner_f):
                    inner_nf += 1
            assert inner_nf == nf
            # 这一块代码有问题，应该是只检查我们关心的文件
            # nf = len(files)

            if nf > 0:
                lt = 1.0 * lt / nf
        return lt, la, ld

    def extract(self):
        # # ignore commit with the same timestamp
        # if self.check_identical_commit():
        #     return None
        gcf = GitCommitFeatures
        gcf.parent_file_stats[self.commit_id] = dict()
        gcf.parent_file_stats[self.commit_id]['files'] = dict()
        gcf.parent_file_stats[self.commit_id]['son_num'] = len(self.sons)
        lt, la, ld = self.evolve_from_prior_commit()
        lt = round(lt, 2)
        return {'project': self.project,
                'commit_id': self.commit_id,
                'la': la, 'ld': ld, 'lt': lt}


def extract_to_db_obj(project):
    # size的基类
    gcf = GitCommitFeatures
    # 类的静态方法，通过该方法，commit的基础元数据信息都有了
    gcf.initialize(project)

    rgcms = retrieve_git_logs(project)
    db_objs = list()
    root = set() # 没有父commit的提交，即第一次初始化的
    rgcm_dict = dict()
    for rgcm in rgcms:
        rgcm_dict[rgcm.commit_id] = rgcm
        if len(rgcm.parent) == 0:
            root.add(rgcm.commit_id)
    del rgcms
    gcf.current_root = root
    gcf.calculated_commit = set()
    gcf.candidate_commit = set()
    gcf.rgcm_dict = rgcm_dict
    while len(SizeFeatures.current_root) > 0:
        extract_results = gcf.calculate_features_for_root(SizeFeatures)
        assert(isinstance(extract_results, list))
        for er in extract_results:
            sf_obj = SizeFeaturesObj(er)
            #sf_obj.print_attributes()
            db_objs.append(sf_obj.to_db_obj())
    return db_objs


if __name__ == '__main__':
    project = 'ant'
    extract_to_db_obj(project)


