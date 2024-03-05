import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),os.path.pardir,"commons"))
import pandas as pd
import pymysql
from Configs import AllConfigs

class GetResult:
    """
    get average measures from the database and output the data to csv files
    """

    connectStr: dict = {
        "host":"localhost",
        "user":"user",
        "password":"password",
        "database":"cexperiment"
    }

    def _getdbconn(self)->dict:
        #  get database connection
        con = pymysql.connect(host=self.connectStr['host'], user=self.connectStr['user'], password=self.connectStr['password'],
                                        database=self.connectStr['database'])
        return con

    def fetch_each_project_csv(self, table_name, result_file_name, project_names, root_path_to_result, models):
            sql_str = "select model, pname, AVG(precision20p), AVG(recall20p), AVG(fmeasure20p), AVG(pci20p), AVG(popt), AVG(ifa) from %s where pname='%s' and model='%s'"
            con: dict = self._getdbconn()
            results = pd.DataFrame(columns=('model', 'pname', 'AVG(precision20p)', 'AVG(recall20p)', 'AVG(fmeasure20p)', 'AVG(pci20p)', 'AVG(popt)', 'AVG(ifa)'))
            for m in models:
                for p in project_names:
                    pn = p + ".csv"
                    results = results.append(pd.read_sql(sql_str%(table_name, pn, m), con))                    
                    print("Fetching project %s method %s."%(p,m))
            results.to_csv(os.path.join(root_path_to_result, result_file_name), index=False)
            print("Fetching results done.")

if __name__ == '__main__':
    
    # the studied projects
    project_names = ["scrcpy","git","obs-studio","FFmpeg","curl", "the_silver_searcher","mpv","radare2","goaccess", "nnn"]

    # the studied model
    models = ["cbsp"]

    # the root path to save the csv results
    root_path_to_result = "/data/result"
    
    table_name = AllConfigs.expsettings['dbtablename']
    result_file_name = table_name + ".csv"

    instance = GetResult()
    instance.fetch_each_project_csv(table_name, result_file_name, project_names, root_path_to_result, models)