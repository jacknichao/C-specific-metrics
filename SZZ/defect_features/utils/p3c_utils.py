import xml.etree.ElementTree as ET

def parse_xml(xml_file):
    """

    :return: pmd_result: dict key: line num ,value: priority
    """
    try:
        tree = ET.ElementTree(file=xml_file)
    except Exception as e:
        print('parse_xml error:', e)
        return None
    pmd_result = dict()
    for elem in tree.iter(tag='violation'):
        beginline = int(elem.get('beginline'))
        endline = int(elem.get('endline'))
        priority = int(elem.get('priority'))
        for line in range(beginline, beginline + 1):
            if line in pmd_result:
                if pmd_result[line] > priority:
                    pmd_result[line] = priority
            else:
                pmd_result[line] = priority
    return pmd_result