import csv
import os
from defect_features.config import conf


file_path= os.path.join(os.path.dirname(conf.data_path),os.pardir,'report')



def count_fix_file_num(project):
    count_1 = 0
    count_2 = 0
    count_3 = 0
    count_4 = 0
    count_5_plus = 0
    csv_file = os.path.join(file_path,project+'.csv')
    with open(csv_file,'r') as file:
        f_csv = csv.DictReader(file)
        for row in f_csv:
            fix_file_num = int(row['fix_file_num'])
            if fix_file_num == 1:
                count_1 += 1
            elif fix_file_num == 2:
                count_2 += 1
            elif fix_file_num == 3:
                count_3 += 1
            elif fix_file_num == 4:
                count_4 += 1
            elif fix_file_num >= 5:
                count_5_plus += 1
            else:
                continue
    print(count_1,count_2,count_3,count_4,count_5_plus)



if __name__=='__main__':
    count_fix_file_num('scmcenter')