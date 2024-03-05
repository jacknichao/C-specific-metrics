#-*- coding: utf-8 -*-
from defect_features.config import load_config
# read all configured settings
conf = load_config.Config()

# read all configured db settings
confDB = load_config.SQLConfig()
