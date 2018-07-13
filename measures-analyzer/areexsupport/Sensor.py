'''
Created on 10 juil. 2018

@author: borettim
'''

import plotly.graph_objs as go
import statistics
import peakutils
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SensorClass:
    '''
    This is a class to support a sensor and the associated value
    '''
    
    @staticmethod
    def sensorIsGroup(groupe):
        return lambda v : v.groupe==groupe
    
    @staticmethod
    def sensorIsUnit(unit):
        return lambda v : v.unit==unit
    
    @staticmethod
    def sensorIsClazz(clazz):
        return lambda v : v.clazz==clazz
    
    @staticmethod
    def sensorIsUnitAndClazz(unit,clazz):
        return lambda v : v.clazz==clazz and v.unit==unit
    
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
    
    @property
    def clazz(self):
        return self.__clazz
    
    @property
    def parent(self):
        return self.__parent
    
    @property
    def children(self):
        return self.__children
    
    @property
    def groupe(self):
        return self.__groupe

    def __init__(self,name,unit='V',pos=1,val=None,mode='lines',clazz='Sensor',parent=None,groupe=None):
        self.__unit=unit
        self.__name=name
        self.__pos=pos
        self.__values={} if val==None else val
        self.__mode=mode
        self.__clazz=clazz
        self.__parent=[] if parent==None else parent
        self.__children=[]
        self.__groupe=groupe
        logger.debug('A new sensor has been created - %s',self)
        
    def __eq__(self,other):
        if isinstance(other, SensorClass):
            return self.name == other.name
        return False
        
    def add(self,v,d):
        self.__values[d]=v
        
    def addChildren(self,c):
        self.__children.append(c)
    
    def __repr__(self):
        return '{}:\tunit:{}\tposition:{}\tvalues count:{}\tmode:{}\tclazz:{}\tparent:{}\tchildren:{}\tgroup:{}'.format(self.__name,self.__unit,self.__pos,len(self.__values),self.__mode,self.__clazz,[x.name for x in self.__parent],[x.name for x in self.__children],self.__groupe)
    
    def asScatter(self,name=None,minSensor=None,maxSensor=None,yaxis='y'):
        xt = []
        yt = []
        minyt = []
        maxyt = []
        for d,v in sorted(self.__values.items()):
            xt.append(d)
            yt.append(v)
            if minSensor!=None:
                minyt.append(v-minSensor.__values[d])
            if maxSensor!=None:
                maxyt.append(maxSensor.__values[d]-v)
        if (len(xt)==len(minyt) and len(xt)==len(maxyt)) :
            return go.Scattergl(x=xt, y=yt,name=self.__name if name == None else name,error_y=dict(type='data',symmetric=False,array=maxyt,arrayminus=minyt),yaxis=yaxis)
        else :
            return go.Scattergl(x=xt, y=yt,name=self.__name if name == None else name,yaxis=yaxis)
    
    def toBaseLine(self):
        logger.debug('Generate a new sensor for baseline from %s',self)
        xt = []
        yt = []
        for d,v in sorted(self.__values.items()):
            xt.append(d)
            yt.append(v)
        baseline_values = peakutils.baseline(np.asarray(yt))
        values = {xt[dt]:v for dt,v in enumerate(baseline_values)}
        s = SensorClass(self.__name+' - baseline',unit=self.__unit,pos='_'+str(self.__pos),val=values,mode='lines',clazz=self.__clazz+'->Baseline',parent=[self],groupe=self.__groupe)
        self.__children.append(s)
        return s
    
    def __sub__(self,other):
        if not isinstance(other, SensorClass):
            raise ValueError('other must be a SensorClass')
         
        logger.debug('Generate a new sensor for %s (minus) %s',self,other)
        values={}
        for d,v in self.__values.items():
            if d in other.__values :
                values[d]=v-other.__values[d]
        s = SensorClass(self.__name+' (minus) '+other.__name,unit=self.__unit,pos='_'+str(self.__pos),val=values,mode=self.__mode,clazz=self.__clazz+'->Minus',parent=[self,other],groupe=self.__groupe)
        self.__children.append(s)
        other.__children.append(s)
        return s
    
    def mergeValueBy(self,functionToMergeTime):
        logger.debug('Merge value for %s',self)
        tvalues = {}
        for d,v in self.__values.items():
            dt = functionToMergeTime(d);
            if(dt not in tvalues) : tvalues[dt]=[]
            tvalues[functionToMergeTime(dt)].append(v)
        self.__values = {d:statistics.mean(v) for d,v in tvalues.items()}
    