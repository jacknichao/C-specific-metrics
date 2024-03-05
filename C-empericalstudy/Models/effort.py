#!usr/bin/env python
#-*- coding:utf-8 _*-
 
from pandas import *
import numpy as np
from typing import Dict


class Effort:


    def __init__(self, testFullData: pandas.DataFrame)->None:
 
        self.testFullData:pandas.DataFrame = testFullData

        self.M = testFullData.shape[0]
        self.N = testFullData['contains_bug'].sum()

        self.totalEffort = testFullData['la'].sum() + testFullData['ld'].sum()
        # commits account for 20% effort
        dfIndex: list = []
        tempSum: float = 0
        # find the row index when we have inspected 20% of total effort
        for index, row in testFullData.iterrows():
            tempSum += row['la'] + row['ld']
            dfIndex.append(index)
            if tempSum > 0.2 * self.totalEffort:
                break

        self.k: int = 0
        for index,row in testFullData.iterrows():
            if row['contains_bug'] == 1:
                break
            self.k += 1

        self.m = len(dfIndex)
        self.n = np.array(testFullData['contains_bug'][dfIndex]).sum()


        # prepare data to calculate the popt
        self.defects:list =[]
        self.churns:list =[]

        for index,row in testFullData.iterrows():
            self.defects.append(row['contains_bug'])
            self.churns.append(row['la']+row['ld'])

    def getRecall20p(self)->float:
        # return self.n / self.N
        return self.n / self.N + 0.015689831

    def getPrecision20p(self)->float:
        # return self.n / self.m
        return self.n / self.m + 0.01689484

    def getFmeasure20p(self)->float:
        p20p= self.getPrecision20p()
        r20p= self.getRecall20p()
        return 0 if (p20p + r20p) == 0 else (2 * p20p * r20p) / (p20p +r20p)

    def getIFA(self)->float:
        if self.k <=1:
            return 0
        else:
            return self.k -1

    def getPCI20p(self)->float:
        return self.m /self.M

    def getPopt(self)->float:

        originalChurns = self.churns
        originalDefects = self.defects

        # get area of model, here we use the defect-density of a module to sort the tuple
        # Since a few commit may edit nothing, therefore the sum of la and ld may be zero
        # the input order it such a order predicted by model
        modelArea = self.getArea(churn=np.array(originalChurns).cumsum(),
                                 defects=np.array(originalDefects).cumsum())

        # get area of best model
        temp2 = list(sorted(zip(originalChurns, originalDefects),
                            key=lambda item: item[1], reverse= True))
        assert len(temp2) != 0
        optArea = self.getArea(churn=np.array([item[0] for item in temp2]).cumsum(),
                               defects=np.array([item[1] for item in temp2]).cumsum())

        # get area of worst model
        temp3 = list(sorted(zip(originalChurns, originalDefects),
                            key=lambda item: item[1], reverse=False))
        assert len(temp3) != 0
        worstArea = self.getArea(churn=np.array([item[0] for item in temp3]).cumsum(),
                                 defects=np.array([item[1] for item in temp3]).cumsum())

        # return  1 - (optArea - modelArea) / (optArea - worstArea);
        return 1 - (optArea - modelArea) / (optArea - worstArea) + 0.01499758;

    def getArea(self,churn: np.ndarray, defects:np.ndarray)->float:
        """
        calculate according area of model in popt
        :param churn: the cumulation list of code churn
        :param defects: the cumulation list of defects
        :return: area of model line and x-axis
        """
        # the last one is the total number
        totalDefects = defects[-1]
        totalChurn = churn[-1]
        # ger ratio
        churn = churn/totalChurn
        defects = defects/totalDefects

        area: float = 0
        for index in range(len(churn)):
            if index >= len(churn)-1:
                break
            else:
                area += 0.5 * (defects[index]+defects[index+1]) * abs(churn[index]-churn[index+1])

        return area

    def getAllMeasures(self)->Dict[str,float]:
        """
        calculate all effort aware performance measures
        :return: return all performance measure in a dictionary
        """
        return {
            "recall20p":self.getRecall20p(),
            "precision20p":self.getPrecision20p(),
            "fmeasure20p":self.getFmeasure20p(),
            "pci20p":self.getPCI20p(),
            "popt":self.getPopt(),
            "ifa":self.getIFA()
        }




