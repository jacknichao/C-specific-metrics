#!usr/bin/env python
#-*- coding:utf-8 _*-

import logging as root_logging

# Set up the logger
logger = root_logging.getLogger()
logger.setLevel(root_logging.INFO)
logger_format = root_logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')


#logging_file_handler = root_logging.FileHandler(config['logging_system']['filename'])
#logging_file_handler.setLevel(root_logging.INFO)
#logging_file_handler.setFormatter(logger_format)
#logger.addHandler(logging_file_handler)

logging_stream_handler = root_logging.StreamHandler()
logging_stream_handler.setLevel(root_logging.INFO)
logging_stream_handler.setFormatter(logger_format)
logger.addHandler(logging_stream_handler)

logging = root_logging