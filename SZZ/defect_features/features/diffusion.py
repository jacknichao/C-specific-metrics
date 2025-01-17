#-*- coding: utf-8 -*-
from defect_features.features.git_commit_features import GitCommitFeatures
from defect_features.git_analysis.analyze_git_logs import retrieve_git_logs
from defect_features.object.features import DiffusionFeatures as DiffusionFeaturesObj


class DiffusionFeatures(GitCommitFeatures):
    def __init__(self, rgcm):
        super(DiffusionFeatures, self).__init__(rgcm)

    def extract(self):
        # # ignore commit with the same timestamp
        # if self.check_identical_commit():
        #     return None
        ns = len(self.stats.modified_subsystems)
        nd = len(self.stats.modified_dirs)
        files, rename_files = self.stats.modified_files
        nf = 0
        for f, added, deleted in files:
            if self.in_required_extensions(f):
                nf += 1
        entropy = self.stats.entropy
        return {'project': self.project,
                'commit_id': self.commit_id,
                'ns': ns, 'nd': nd, 'nf': nf, 'entropy': entropy}


def extract_to_db_obj(project):
    GitCommitFeatures.initialize(project)
    # a list of RawGitCommitMeta in project
    rgcms = retrieve_git_logs(project)
    db_objs = list()
    sorted_rgcms = sorted(rgcms, key=lambda x: x.time_stamp)
    for rgcm in sorted_rgcms:
        df = DiffusionFeatures(rgcm)
        attr_dict = df.extract()
        if attr_dict is None:
            continue
        # df_obj type: <class 'defect_features.object.features.DiffusionFeatures'>
        df_obj = DiffusionFeaturesObj(attr_dict)
        # get diffusion attribute and construct df_obj ok
        # df_obj.print_attributes()
        db_objs.append(df_obj.to_db_obj())
    return db_objs


if __name__ == '__main__':
    project = 'ant'
    extract_to_db_obj(project)

