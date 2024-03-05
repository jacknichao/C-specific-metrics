file_in = '../nohup_1.out'
MAX_CHANGE = 300
with open(file_in,'r') as f_obj:
    regions_commit = f_obj.read().split('history_sep')
    next_commit = regions_commit[1].split('\n')[-2]
    mem = 0
    for region in regions_commit[1:]:
        lines = region.split('\n')[8:]
        for line in lines:
            segs = line.split(' ')
            if 'MiB' not in segs:
                continue
            # if '49' not in segs:
            #     continue
            #print(segs)MAX_CHANGE
            MiB_counter = 0
            for seg in segs:
                if seg == '':
                    continue
                else:
                    if seg == 'MiB':
                        MiB_counter += 1
                        continue
                    if MiB_counter == 1:
                        change = float(seg)
                        if change != 0:
                            print(change,line)
                        #
                        if change < MAX_CHANGE:
                            mem += change
                        next_flag = False
    print(mem)
#         #next_commit = lines[-2]
# with open(file_in,'r') as file:
#     regions = file.read().split('history_sep')[1:]
#     for region in regions:
#         if 'non_merge' in region:
#             continue
#         print('-'*100)
#         lines = region.split('\n')[5:]
#         print(lines)