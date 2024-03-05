import pandas as pd

def count_author_num(project,file_path):
    df = pd.read_csv(file_path)
    author_set = set()
    for index,commit in df.iterrows():
        commit_author = commit.author_email
        author_set.add(commit_author)
    print("%s has %s developer(s)" % (project, len(author_set)))



if __name__=="__main__":
    project = ""
    file_path = "/home/wenfeng/vlis/defect_prediction/defect_features/report/pf4j.csv"
    count_author_num(project,file_path)
