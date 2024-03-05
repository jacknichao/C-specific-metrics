import pandas as pd
from pandas.core.reshape import merge
import pymysql
import os


"""
merge the 14 features and 9 C-specific features to one csv file
"""
class MergeData:

    connectStr: dict = {
        "host":"localhost",
        "user":"user",
        "password":"password",
        "database":"db"
    }

    jit_features = ["commit_id", "time_stamp", "ns", "nd", "nf", "entropy", "la", "ld", "lt", "is_fix", "ndev", "age", "nuc", "exp", "rexp", "sexp","contains_bug"]
    c_features = ["commit_id", "meminc", "memdec", "memchg", "singlepointer", "multiplepointer",
                "maxpointerdepth","gotostm","indexused","autoincredecre"]


    def _getdbconn(self)->dict:
        #  get database connection
        con = pymysql.connect(host=self.connectStr['host'], user=self.connectStr['user'], password=self.connectStr['password'],
                                      database=self.connectStr['database'])
        return con

    def do_dataset_merge(self, 
    root_path_to_common_features, 
    root_path_to_c_features,
    root_path_to_merged,
    project_names):
        """
        merge the 14 features and 9 C-specific features
        """
        for pn in project_names:
            common_data = pd.read_csv(os.path.join(root_path_to_common_features, pn+".csv"))[self.jit_features]
            c_data = pd.read_csv(os.path.join(root_path_to_c_features, pn + "-only-c.csv"))[self.c_features]

            # print("current project: %s" % pn)
            # print("old size:", old_data.shape, "--->new size:", new_data.shape)

            mergered = pd.merge(common_data, c_data, how="left", left_on="commit_id", right_on="commit_id")
            # fill nan with 0

            # mergered.fillna(0).to_csv(os.path.join("/home/chaoni/js-major-revision-2020/JSFeatures/CORE/mergeddata", pn+"-add-js-feats.csv"), index=False)
            mergered.fillna(0).to_csv(os.path.join(root_path_to_merged,pn+".csv"),index=False)
            print("writng ", pn+"-merged.csv finished!!!")

            print("------------------------------------------------")


    def fetch_each_project_csv(self, project_names, root_path_to_c_features):

        sql_str = "select * from c_features where project='%s'"
        con: dict = self._getdbconn()
       
        for p in project_names:
            project_c_features: pd.DataFrame = pd.read_sql(sql_str %p,con)
            project_c_features.to_csv(os.path.join(root_path_to_c_features,"%s-only-c.csv"%p), index=False)
            print("Fetching %s successfully."%p)



if __name__ == '__main__':
    root_path_to_common_features="/data/common"
    root_path_to_c_features="/data/c"
    root_path_to_merged="/data/merged"

    instance =MergerData()

    project_names = ["FFmpeg", "curl", "git", "goaccess", "obs-studio", "radare2", "scrcpy", "the_silver_searcher", "mpv", "nnn"]

    # extract c features from the databse to csv files
    instance.fetch_each_project_csv(project_names,root_path_to_c_features)

    # merge data
    instance.do_dataset_merge(root_path_to_common_features,root_path_to_c_features,root_path_to_merged,project_names)

    for file in project_names:
        datas = pd.read_csv(os.path.join(root_path_to_merged,"%s.csv"%file))
        print("%s--%s"%(file,datas.shape))
    print("OK!")






