
# encoding: utf-8
'''
Created on 10 juil. 2018

@author: borettim
'''

from areexsupport.Sensor import SensorClass
from datetime import datetime
from pytz import timezone

class SensorDataClass:
    '''
    This is a list of data sensor
    '''
    
    @staticmethod
    def __fastparsedate(instr):
        #'01.01.2017 00:00:00'
        day = int(instr[0:2])
        month = int(instr[3:5])
        year = int(instr[6:10])
        hour  = int(instr[11:13])
        minute  = int(instr[14:16])
        second = int(instr[17:19])
        return datetime(year, month, day, hour, minute, second)

    def __init__(self,filename):
        self.__sensors={}
        sensorByPos={}
        dtlimit = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        dtzone = timezone('Europe/Zurich')
        try:
            s = 0
            f = open(filename,'r')
            for n,l in enumerate(f,1):
                if n%100000==0 : print ("Processing line:{}".format(n))
                if s==0 and l.startswith('Sensors:'):
                    s = 1
                    continue
                if s==1 and l.startswith('Column'):
                    s = 2
                    continue
                if s==2 and l.startswith('Start date'):
                    s = 3
                    continue
                if s==3 and l.startswith('Time'):
                    s = 4
                    continue;
                if s==2 and l!='\n':
                    ls=l.rstrip('\n').split('\t')
                    n=ls[1]
                    cs=SensorClass(n, ls[2], ls[0])
                    sensorByPos[int(ls[0])]=cs
                    self.__sensors[cs.name]=cs
                if s==4 and l!='\n':
                    ls=l.rstrip('\n').split('\t')
                    dt_obj=dtzone.localize(SensorDataClass.__fastparsedate(ls[0]))
                    if dtlimit>dt_obj: continue
                    for p,v in enumerate(ls[1:]) :
                        if v!='':
                            self.__sensors[sensorByPos[p+1].name].add(float(v),dt_obj)
        finally:
            f.close()
            
    def __repr__(self):
        return 'Sensors :\n{}'.format('\n'.join(map(SensorClass.__repr__,self.__sensors.values())))
    
    def sensorsNameByType(self,sensorType):
        return [x for x in self.__sensors if self.__sensors[x].unit==sensorType];

    def toScatters(self,sensorType):
        return [self.__sensors[v].toScatter() for v in self.sensorsNameByType(sensorType)]
    
    def toFigure(self,sensorType):
        return SensorDataClass.__tofigure(self.toScatters(sensorType),sensorType)
        
    @staticmethod
    def __tofigure(data,ylabel,title=None):
        return dict(
                data=data,
                layout=dict(
                    xaxis=dict(
                        title='Date'),
                    yaxis=dict(
                        title=ylabel),
                    title=title
                    )
                )
    
    def toMultiFigures(self):
        ext = self.__sensors['Extérieur'].toScatter()
        result={
            '.temp':self.toFigure('°C'),
            '.rh':self.toFigure('RH%'),
            }
        for sn in self.sensorsNameByType('°C'):
            if sn!='Extérieur' and ' - Point de rosée' not in sn:
                result['.temp.'+self.__sensors[sn].pos]=SensorDataClass.__tofigure([ext,self.__sensors[sn].toScatter()],'°C')
            elif ' - Point de rosée' in sn:
                n=sn.replace(' - Point de rosée',' - T')
                result['.temp.'+self.__sensors[n].pos+".2"]=SensorDataClass.__tofigure([ext,self.__sensors[sn].toScatter(),self.__sensors[n].toScatter()],'°C')
        for sn in self.sensorsNameByType('RH%'):
            result['.rh.'+self.__sensors[sn].pos]=SensorDataClass.__tofigure([self.__sensors[sn].toScatter()],'RH%',title=sn)
        return result

    def filterOutSensor(self,filterFunctionToRemove):
        self.__sensors = {n:v for n,v in self.__sensors.items() if not filterFunctionToRemove(v)}
        
    def mergeValueBy(self,functionToMergeTime):
        for v in self.__sensors.values():
            v.mergeValueBy(functionToMergeTime)
            
    def valueForPointRosee(self,sn):
        snt = sn.replace(' - RH',' - T')
        return {d:self.__sensors[snt].values[d]-(100-v)/5 for d,v in self.__sensors[sn].values.items() if d in self.__sensors[snt].values}
            
    def computePointRosee(self):
        for sn in self.sensorsNameByType("RH%"):
            snt = sn.replace(' - RH',' - T')
            if snt in self.__sensors :
                pt=self.valueForPointRosee(sn)
                n=sn.replace(' - RH',' - Point de rosée')
                s=SensorClass(n, "°C", -1, pt,'markers')
                self.__sensors[n]=s