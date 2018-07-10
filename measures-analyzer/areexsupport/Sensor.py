'''
Created on 10 juil. 2018

@author: borettim
'''

import plotly.graph_objs as go
from builtins import staticmethod
import statistics

class SensorClass:
    '''
    This is a class to support a sensor and the associated value
    '''
    
    @staticmethod
    def sensorIsUnit(unit):
        return lambda v : v.unit==unit
    
    @staticmethod
    def dateTimeToMinute():
        return lambda d : d.replace(second=0,microsecond=0)
    
    @staticmethod
    def __dateTimeTo5Minute(d):
        d = SensorClass.dateTimeToMinute()(d)
        return d.replace(minute=(d.minute//5)*5)
    
    @staticmethod
    def dateTimeTo5Minute():
        return SensorClass.__dateTimeTo5Minute
    
    @property
    def values(self):
        return self.__values
    
    @property
    def name(self):
        return self.__name
    
    @property
    def unit(self):
        return self.__unit
    
    @property
    def pos(self):
        return self.__pos
    
    @property
    def mode(self):
        return self.__mode

    def __init__(self,name,unit='V',pos=1,val=None,mode='lines'):
        self.__unit=unit
        self.__name=name
        self.__pos=pos
        self.__values={} if val==None else val
        self.__mode=mode
        
    def add(self,v,d):
        self.__values[d]=v
    
    def __repr__(self):
        return '{}:\tunit:{}\tposition:{}\tvalues count:{}\tmode:{}'.format(self.__name,self.__unit,self.__pos,len(self.__values),self.__mode)
    
    def toScatter(self):
        xt = []
        yt = []
        for d,v in sorted(self.__values.items()):
            xt.append(d)
            yt.append(v)
        return go.Scattergl(x=xt, y=yt,name=self.__name)#,mode=self.__mode
    
    def mergeValueBy(self,functionToMergeTime):
        tvalues = {}
        for d,v in self.__values.items():
            dt = functionToMergeTime(d);
            if(dt not in tvalues) : tvalues[dt]=[]
            tvalues[functionToMergeTime(dt)].append(v)
        self.__values = {d:statistics.mean(v) for d,v in tvalues.items()}
    