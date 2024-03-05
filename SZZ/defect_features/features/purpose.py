#-*- coding: utf-8 -*-
from defect_features.features.git_commit_features import GitCommitFeatures
from defect_features.git_analysis.analyze_git_logs import retrieve_git_logs
from defect_features.object.features import PurposeFeatures as PurposeFeaturesObj
from classifier.classifier import *
from analyzer.git_commit_linker import *



class PurposeFeatures(GitCommitFeatures):
    def __init__(self, rgcm):
        super(PurposeFeatures, self).__init__(rgcm)


    def extract(self):
        """
        reconstruct extract()
        """
        # # ignore commit with the same timestamp
        # if self.check_identical_commit():
        #     return None
        is_fix = False
        if self.is_merge == True:
            classification = 'Merge'
        else:
            classifier = Classifier()
            classification = classifier.categorize(self.commit_msg)
            if classification == "Corrective":
                is_fix = True
        linked = False
        contains_bug = False
        fix_by = None
        fixes = None
        block = 0
        critical = 0
        major = 0
        block_total = 0
        critical_total = 0
        major_total = 0
        file_name_stat = self.namestat.file_name_stat
        la = self.stats.added_number
        ld = self.stats.deleted_number
        find_interval = None

        return {
            'project': self.project,
            'commit_id': self.commit_id,
            'time_stamp': self.time_stamp,
            'is_fix': is_fix,
            'classification':classification,
            'linked':linked,
            'contains_bug':contains_bug,
            'fix_by': fix_by,
            'fixes': fixes,
            'bug_fix_files':None,
            'fix_file_num':0,
            'buggy_lines':None,
            'clean_lines':None,
            'block': block,
            'critical': critical,
            'major': major,
            'block_total': block_total,
            'critical_total': critical_total,
            'major_total': major_total,
            'la': la,
            'ld': ld,
            'file_name_stat': file_name_stat,
            'find_interval': find_interval,
            'rules': None
        }

def extract_to_db_obj(project):
    # start get features
    GitCommitFeatures.initialize(project)
    rgcms = retrieve_git_logs(project)

    db_objs = list()
    pf_objs = list()
    corrective_commits = dict() # key: commit_id; value: pf_obj
    all_commits = dict() # key:commit_id; value: pf_obj
    sorted_rgcms = sorted(rgcms, key=lambda x: x.time_stamp)
    # get features done
    for rgcm in sorted_rgcms:
        pf = PurposeFeatures(rgcm)
        attr_dict = pf.extract()
        if attr_dict is None:
            continue
        pf_obj = PurposeFeaturesObj(attr_dict)
        pf_objs.append(pf_obj)
        all_commits[pf_obj.commit_id] = pf_obj
        if pf_obj.classification == 'Corrective':
            corrective_commits[pf_obj.commit_id] = pf_obj
    # # link corrective commit to buggy commit. szz algorithm
    try:
        git_commit_linker = GitCommitLinker(project, corrective_commits, all_commits)
        git_commit_linker.link_corrective_commits()
    except Exception as e:
        print(e)
        raise
    #p3c pmd

    # pmd = Pmd(project, pf_objs)
    # pmd.pmd_main()
    for pf_obj in pf_objs:
        # to json
        if pf_obj.fix_by != None:
            pf_obj.fix_by = json.dumps(pf_obj.fix_by)
        if pf_obj.fixes != None:
            pf_obj.fixes = json.dumps(pf_obj.fixes)
        if pf_obj.buggy_lines != None:
            pf_obj.buggy_lines = json.dumps(pf_obj.buggy_lines)
        if pf_obj.clean_lines != None:
            pf_obj.clean_lines = json.dumps(pf_obj.clean_lines)
        if pf_obj.bug_fix_files != None:
            pf_obj.bug_fix_files = json.dumps(pf_obj.bug_fix_files)
        # change object/features.py PurposeFeatures object to db object
        db_objs.append(pf_obj.to_db_obj())
    return db_objs


if __name__ == '__main__':
    project = 'ant'
    extract_to_db_obj(project)

