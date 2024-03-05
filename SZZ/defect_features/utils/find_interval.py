import csv
import numpy as np

SEC2DAY = (60*60*24)
DAY_1 = SEC2DAY * 1
DAY_3 = SEC2DAY * 3
DAY_7 = SEC2DAY * 7


def main(project):
    csv_file = '/home/wenfeng/vlis/defect_prediction/defect_features/' + project + '.csv'
    interval_list = list()
    with open(csv_file, 'r') as file:
        f_csv = csv.DictReader(file)
        for row in f_csv:
            if row['find_interval']:
                interval_list.append(int(row['find_interval'])/SEC2DAY)
    np_array = np.array(interval_list)
    mean = np.mean(np_array)
    quantile_1 = np.percentile(np_array,25)
    quantile_2 = np.percentile(np_array, 50)
    quantile_3 = np.percentile(np_array, 75)
    print("%s\nQ1:%s\nQ2:%s\nQ3:%s\nMean:%s" % (project, quantile_1,quantile_2,quantile_3,mean))




if __name__ == '__main__':
    main('force')