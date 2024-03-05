#-*- coding: utf-8 -*-
import os
from defect_features.config import conf


def in_our_extensions(path:str):
    """
    check whether a file should be considered in our projects.
    :param path: the string of full path
    :return:
    """
    if len(conf.consider_extensions) == 0:
        return True
    ext = os.path.splitext(path)[1]
    return ext.lower() in conf.consider_extensions
