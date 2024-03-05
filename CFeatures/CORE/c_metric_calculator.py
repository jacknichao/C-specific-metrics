# -*- coding: utf-8 -*-
# function: main function for extracting c programming language feature
import sys, os
import re
from collections import Counter

from sqlalchemy.sql.schema import FetchedValue

sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir, "ORM"))
from ORM import db, dbmodules
#from ORM.db import DBOperator
#from ORM.dbmodules import CFeature
from Common.mylogger import logger


class CLanguageCommitMetricCalculator:
    def __init__(self, project_name, commit_index, commit_msg):
        # project name
        self.project_name = project_name
        # commit index
        self.commit_index = commit_index
        # log message of commit
        self.commit_msg = commit_msg

        # goto statement pattern
        self.re_gotstm = re.compile("goto\s+\w+\s*;")

        # meminc pattern
        self.re_meminc_1 = re.compile("malloc")
        self.re_meminc_2 = re.compile("calloc")
        self.re_meminc_3 = re.compile("realloc")

        # memdec pattern
        self.re_memdec = re.compile("free")

        # memchg pattern
        self.re_memchg = re.compile("realloc")

        # indexused pattern
        self.re_indexused = re.compile("\[\w+\]")

        # autoincredecre pattern
        self.re_autoincredecre_1 = re.compile("(\+{2})")
        self.re_autoincredecre_2 = re.compile("\-{2}")

        # pointer pattern 
        self.re_pointerusages = re.compile("\*{1,}\s*\w*[,;=]?")
    
    def getCFeatures(self):
        return self._ayalysis_inner_git_regions()

    def _ayalysis_inner_git_regions(self) -> dbmodules.CFeature:

        # number of memory requirement operations
        meminc = 0
        
        # number of memory release operations
        memdec = 0
        
        # number of memory change operations, i.e., realloc
        memchg = 0
        
        # number of single pointer definitions or usage
        singlepointer = 0
        
        # number of multiple pointer definitions or usage
        multiplepointer = 0
        
        # max depth of the pointer definition or usage
        maxpointerdepth = 0
        
        # number of goto statements
        gotostm = 0
        
        # number of array indexing operations
        indexused = 0
        
        # number of auto increasing or decreasing operations
        autoincredecre = 0

        # Start analyzing each git region. Note that a line prefix 'LINE_START:' is added to the output of git log
        regions = self.commit_msg.split('LINE_START:diff --git')[1:]

        for region in regions:
            file_name = re.search(r'a/(\S+)', region).group(1)
            # filter out files that do not end with [cChH]
            if not( file_name.endswith("c") or file_name.endswith("C") or file_name.endswith("h") or file_name.endswith("H")):
                logger.warning(
                    "Project name: %s, Commit index: %s, Current file: %s, has been filtered out!" % (self.project_name, self.commit_index, file_name))
                continue

            chunks = region.split('LINE_START:@@')[1:]
            for chunk in chunks:
                # remove the line prefix
                chunk = chunk.replace("LINE_START:", "")
                # print(chunk)
                # print("------------------------------------------")

                # Eliminate comment lines before calculating the metrics
                # Exclude the use of * in code comments
                chunk = re.sub('//.*?\n|/\*.*?\*/', '', chunk, flags=re.S|re.M)

                gotostm += self._calculate_gotostm(chunk)
                meminc += self._calculate_meminc(chunk)
                memdec += self._calculate_memdec(chunk)
                memchg += self._calculate_memchg(chunk)
                indexused += self._calcuate_indexused(chunk)
                autoincredecre += self._calculate_autoincredec(chunk)

                pointer_dict = self._calculate_pointers(chunk)
                singlepointer += pointer_dict['singlepointer']
                multiplepointer += pointer_dict['multiplepointer']

                maxpointerdepth = pointer_dict['maxpointerdepth'] if pointer_dict['maxpointerdepth'] >maxpointerdepth else maxpointerdepth

        # Create a database to record the calculated metrics
        return dbmodules.CFeature(project=self.project_name,
                                   commit_id=self.commit_index,
                                   meminc=meminc,
                                   memdec=memdec,
                                   memchg=memchg,
                                   singlepointer=singlepointer,
                                   multiplepointer=multiplepointer,
                                   maxpointerdepth=maxpointerdepth,
                                   gotostm= gotostm,
                                   indexused=indexused,
                                   autoincredecre=autoincredecre
                                   )

    def _calculate_gotostm(self, chunk: str)-> int:

        gotostm_match = self.re_gotstm.findall(chunk)

        return len(gotostm_match)

    def _calculate_meminc(self, chunk: str)-> int:
        meminc_match_1 =self.re_meminc_1.findall(chunk)
        meminc_match_2 =self.re_meminc_2.findall(chunk)
        meminc_match_3 =self.re_meminc_3.findall(chunk)

        return len(meminc_match_1) + len(meminc_match_2) + len(meminc_match_3)

    def _calculate_memdec(self, chunk: str)-> int:
        memdec_match = self.re_memdec.findall(chunk)
        
        return len(memdec_match) 

    def _calculate_memchg(self, chunk: str)-> int:
            memchg_match = self.re_memchg.findall(chunk)
            
            return len(memchg_match) 

    def _calcuate_indexused(self,chunk: str)-> int:
        indexused_match = self.re_indexused.findall(chunk)

        return len(indexused_match)

    def _calculate_autoincredec(self, chunk: str)-> int:
        autoincredecre_match_1 = self.re_autoincredecre_1.findall(chunk)
        autoincredecre_match_2 = self.re_autoincredecre_2.findall(chunk)

        return len(autoincredecre_match_1) + len(autoincredecre_match_2)

    def _calculate_pointers(self, chunk: str)->dict:
        

        pointer_match_list = self.re_pointerusages.findall(chunk)

        if len(pointer_match_list) == 0:
            # No pointer operation found
            singlepointer = 0
            multiplepointer = 0
            maxpointerdepth = 0
        else:
            star_count_list = [star.count("*") for star in pointer_match_list]

            singlepointer = Counter(star_count_list)[1]
            multiplepointer = len(star_count_list) - singlepointer
            maxpointerdepth = max(star_count_list)

        return {
            'singlepointer':singlepointer,
            'multiplepointer':multiplepointer,
            'maxpointerdepth': maxpointerdepth
        }




if __name__ == '__main__':

    lines = open("./target.diff").read()
    print(CLanguageCommitMetricCalculator("anamel","index",lines).getCFeatures())

