import csv
import numpy as np
def main(project):
    csv_file = '/home/wenfeng/vlis/defect_prediction/defect_features/' + project + '.csv'
    bug_w1 = 0
    bug_w2 = 0
    bug_w3 = 0
    non_w1 = 0
    non_w2 = 0
    non_w3 = 0
    num_bug = 0
    num_non = 0
    with open(csv_file,'r') as file:
        f_csv = csv.DictReader(file)
        for row in f_csv:
            if row['contains_bug'] == 'True':
                print('buggy', row['commit_id'])
                num_bug += 1
                bug_w1 += int(row['warn1'])
                bug_w2 += int(row['warn2'])
                bug_w3 += int(row['warn3'])
            else:
                print('clean', row['commit_id'])
                num_non += 1
                non_w1 += int(row['warn1'])
                non_w2 += int(row['warn2'])
                non_w3 += int(row['warn3'])
        bug_w1_avg = bug_w1 / num_bug
        bug_w2_avg = bug_w2 / num_bug
        bug_w3_avg = bug_w3 / num_bug
        non_w1_avg = non_w1 / num_non
        non_w2_avg = non_w2 / num_non
        non_w3_avg = non_w3 / num_non
    print('buggy commits: warn1: %s ; warn2: %s ; warn3: %s'%(bug_w1_avg,bug_w2_avg,bug_w3_avg))
    print('clearn commits: warn1: %s ; warn2: %s ; warn3: %s'% (non_w1_avg, non_w2_avg, non_w3_avg))

if __name__ == '__main__':
    main('force')