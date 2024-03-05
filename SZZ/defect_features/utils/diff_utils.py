import re


def is_nosise(line):
    #
    line = line.strip('\t').strip('\r').strip()
    # ignore blank line
    if line == '':
        return True
    # ignore comment
    # here, we should consider different comment indicator in different programing language
    # TO DO java javascript python
    if line.startswith('//') or line.startswith('/**') or line.startswith('*') or \
            line.startswith('/*') or line.endswith('*/'):
        return True
    # ignore import line
    # here, we should take different programing language into consideration...e.g., python javascript
    if line.startswith('import '):
        return True
    return False

def get_add_lines(diff_raw):
    # files(lines) to be analyzed. key: string, file name; values : list , the line number of deleted line
    add_lines = dict()

    # start to parse git diff information
    # one file one region
    regions = diff_raw.split('LINE_START: diff --git')[1:]
    for region in regions:
        file_name = re.search(r' b/(.+)', region).group(1)
        if file_name not in add_lines:
            add_lines[file_name] = list()
        chunks = region.split('LINE_START: @@')[1:]
        for chunk in chunks:
            lines = chunk.split('\n')
            line_info = re.search(r'\+(\d*)', lines[0])
            # current line number of file a(usually previous file)
            current_b = int(line_info.group(1))
            # parse each line, except chunk header
            # some file may not delete any line, and we need process this condition later
            for line_raw in lines[1:]:
                line = line_raw.strip('LINE_START: ')
                # ignore line not del
                if not line.startswith('+'):
                    continue
                # process noise
                if is_nosise(line.strip('+')):
                    # update line num of file a
                    current_b += 1
                    continue
                add_lines[file_name].append(current_b)
                current_b += 1
    return add_lines
