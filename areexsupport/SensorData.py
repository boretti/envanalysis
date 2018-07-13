
# encoding: utf-8
'''
Created on 10 juil. 2018

@author: borettim
'''

from areexsupport.Sensor import SensorClass
from datetime import datetime
from pytz import timezone
import statistics

import logging

logger = logging.getLogger(__name__)

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

    def __init__(self,filename,mergeFunction=SensorClass.dateTimeToMinute()):
        self.__sensors={}
        sensorByPos={}
        dtlimit = timezone('Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00','%d.%m.%Y %H:%M:%S'))
        dtzone = timezone('Europe/Zurich')
        try:
            s = 0
            f = open(filename,'r')
            for n,l in enumerate(f,1):
                if n%100000==0 : logger.info("Processing line:{}".format(n))
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
                    cs=SensorClass(n, ls[2], ls[0],groupe='Extérieur' if n=='Extérieur' else 'Intérieur')
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
        logger.info("Post processing data : merging by %s",mergeFunction)
        self.__mergeValueBy(mergeFunction)
        logger.info("Post processing data : computing point de rosee")
        self.__computePointRosee()
        logger.info("Post processing data : computing distribution")
        self.__computeDistribution()
        logger.info("Post processing data : computing baseline")
        self.__computeBaseLine()
        
    def __mergeValueBy(self,functionToMergeTime):
        logger.debug("Merging by using %s",functionToMergeTime)
        for v in self.__sensors.values():
            logger.info("Post processing data : merging by %s for %s",functionToMergeTime,v.name)
            v.mergeValueBy(functionToMergeTime)
            
    def __valueForPointRosee(self,rh,t):
        return {d:t.values[d]-(100-v)/5 for d,v in rh.values.items() if d in t.values}

    def __computePointRosee(self):
        for rh in self.sensorsByUnitAndClazzAndGroup("RH%",'Sensor','Intérieur'):
            snt = rh.name.replace(' - RH',' - T')
            if snt in self.__sensors :
                t = self.__sensors[snt]
                pt=self.__valueForPointRosee(rh,t)
                n=rh.name.replace(' - RH',' - Point de rosée')
                s=SensorClass(n, "°C", -1, pt,'markers','Point de rosée',parent=[rh,t],groupe='Intérieur')
                rh.addChildren(s)
                t.addChildren(s)
                self.__sensors[n]=s
                
    def __computeDistribution(self):
        groups = set(map(lambda v : v.groupe,self.__sensors.values()))
        units = set(map(lambda v : v.unit,self.__sensors.values()))
        clazzs = set(map(lambda v : v.clazz,self.__sensors.values()))
        for g in groups :
            for u in units :
                for c in clazzs :
                    tsensor = self.sensorsByFunction(lambda this:this.groupe==g and this.unit==u and this.clazz==c)
                    if len(tsensor)>1 :
                        logger.info("Post processing data : compute distribution for  %s > %s > %s",g,u,c)
                        tvalues = {}
                        for sn in tsensor:
                            for dt,v in sn.values.items() :
                                if(dt not in tvalues) : tvalues[dt]=[]
                                tvalues[dt].append(v)
                        target={'p-Variance':statistics.pvariance,'Mean':statistics.mean,'Median':statistics.median,'Min':min,'Max':max}
                        for name,method in target.items():
                            logger.info("Post processing data : compute distribution for  %s > %s > %s > %s",g,u,c,name)
                            n='{} - {} [{}] / {}'.format(g,c,u,name)
                            s=SensorClass(n, u, -1, {d:method(v) for d,v in tvalues.items()},'markers',c+"->"+name,parent=tsensor,groupe=g)
                            for t in tsensor : t.addChildren(s)
                            self.__sensors[n]=s
        
    def __computeBaseLine(self):
        for sn in list(self.__sensors.values()):
            logger.info("Post processing data : compute baseline for %s",sn.name)
            s = sn.toBaseLine()
            self.__sensors[s.name]=s
            
    def __repr__(self):
        groups = set(map(lambda v : v.groupe,self.__sensors.values()))
        def gtostr(g):
            sensors = self.sensorsByFunction(SensorClass.sensorIsGroup(g))
            clazzs = set(map(lambda v : v.clazz,sensors))
            def ctostr(c):
                return '{}:\n\t\t{}'.format(c,'\n\t\t'.join(map(SensorClass.__repr__,[s for s in sensors if s.clazz==c])))
            return '{}:\n\t{}'.format(g,'\n\t'.join(map(ctostr,sorted(clazzs))))
        return 'Sensors :\n{}'.format('\n'.join(map(gtostr,sorted(groups))))
    
    def sensorsByFunction(self,acceptFunction):
        return [value for value in self.__sensors.values() if acceptFunction(value)]
    
    def sensorsByUnitAndClazz(self,unit,clazz):
        def finder(s):
            return s.unit==unit and s.clazz==clazz
        return self.sensorsByFunction(finder)
    
    def sensorsByUnitAndClazzAndGroup(self,unit,clazz,groupe):
        def finder(s):
            return s.unit==unit and s.clazz==clazz and s.groupe==groupe
        return self.sensorsByFunction(finder)

    def toFigure(self,acceptFunctionOnSensor,ytitle,title=None,y2label=None):
        return SensorDataClass.__tofigure([x.asScatter() for x in self.sensorsByFunction(acceptFunctionOnSensor)],ytitle,title,y2label)
    
    def oneToFigure(self,sensor,title=None):
        return SensorDataClass.__tofigure([sensor.asScatter()],sensor.unit,title)
    
    def toFigureFromScatters(self,scatters,ytitle,title=None,y2label=None):
        return SensorDataClass.__tofigure(scatters,ytitle,title,y2label)
        
    @staticmethod
    def __tofigure(data,ylabel,title=None,y2label=None):
        y2axis = None if y2label==None else dict(title=y2label,overlaying='y',side='right')
        return dict(
                data=data,
                layout=dict(
                    xaxis=dict(
                        title='Date',
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,label='1h',step='hour',stepmode='backward'),
                                dict(count=12,label='12h',step='hour',stepmode='backward'),
                                dict(count=1,label='1d',step='day',stepmode='backward'),
                                dict(count=2,label='2d',step='day',stepmode='backward'),
                                dict(count=7,label='1w',step='day',stepmode='backward'),
                                dict(count=14,label='2w',step='day',stepmode='backward'),
                                dict(count=1,label='1m',step='month',stepmode='backward'),
                                dict(count=2,label='2m',step='month',stepmode='backward'),
                                dict(count=6,label='6m',step='month',stepmode='backward'),
                                dict(count=1,label='YTD',step='year',stepmode='todate'),
                                dict(count=1,label='1y',step='year',stepmode='backward'),
                                dict(step='all')
                            ])
                        ),
                        rangeslider=dict(),
                        type='date'),
                    yaxis=dict(title=ylabel),
                    yaxis2=y2axis,
                    title=title
                    )
                )
    
    def toMultiFigures(self):
        def isExterieur(s):
            return s.groupe=='Extérieur'
        def isSensor(s):
            return SensorClass.sensorIsClazz('Sensor')(s)
        def isSensorBaseline(s):
            return SensorClass.sensorIsClazz('Sensor->Baseline')(s)
        
        # Generate one file per sensor
        result = {'details':{name:self.oneToFigure(value,value.name) for name,value in self.__sensors.items()},'/':{},'compare':{},'analyse':{}}
        
        # Generate a file with all input temp
        result['/']['Toutes les températures']=self.toFigure(SensorClass.sensorIsUnitAndClazz('°C','Sensor'), '°C', 'Toutes les températures')
        # Generate a file with all input rh
        result['/']['Toutes les humidités']=self.toFigure(SensorClass.sensorIsUnitAndClazz('RH%','Sensor'), 'RH%', 'Toutes les humidités')
        # Generate a file with all baseline temp
        result['/']['Toutes les températures - Baseline']=self.toFigure(SensorClass.sensorIsUnitAndClazz('°C','Sensor->Baseline'), '°C', 'Toutes les températures - Baseline')
        # Generate a file with all baseline rh
        result['/']['Toutes les humidités - Baseline']=self.toFigure(SensorClass.sensorIsUnitAndClazz('RH%','Sensor->Baseline'), 'RH%', 'Toutes les humidités - Baseline')
        
        # Generate on file per input sensor and baseline
        for cs in self.sensorsByFunction(isSensor):
            result['compare'][cs.name+" et Baseline"]=self.toFigure(lambda this:this==cs or (cs in this.parent and isSensorBaseline(this)), cs.unit, cs.name+" et Baseline")
        # Generate on file per temp sensor vs exterieur
        for cs in self.sensorsByFunction(lambda this:SensorClass.sensorIsUnitAndClazz('°C','Sensor')(this) and SensorClass.sensorIsGroup('Intérieur')(this)):
            result['compare'][cs.name+" vs Extérieur"]=self.toFigure(lambda this:this==cs or (isExterieur(this) and isSensor(this)), cs.unit, cs.name+" vs Extérieur")
        # Generate on file per temp sensor vs exterieur (baseline)
        for cs in self.sensorsByFunction(lambda this:SensorClass.sensorIsUnitAndClazz('°C','Sensor->Baseline')(this) and SensorClass.sensorIsGroup('Intérieur')(this)):
            result['compare'][cs.name+" vs Extérieur - Baseline"]=self.toFigure(lambda this:this==cs or (isExterieur(this) and isSensorBaseline(this)), cs.unit, cs.name+" vs Extérieur - Baseline")
        
        # Interieur vs Exterieur
        external = self.__sensors['Extérieur'].asScatter()
        internal = self.__sensors['Intérieur - Sensor [°C] / Mean'].asScatter(name='Intérieur',minSensor=self.__sensors['Intérieur - Sensor [°C] / Min'],maxSensor=self.__sensors['Intérieur - Sensor [°C] / Max'])
        result['/']['Comparaison intérieur vs extérieur']=self.toFigureFromScatters([external,internal], '°C', 'Intérieur vs Extérieur')
        
        external_b = self.__sensors['Extérieur - baseline'].asScatter()
        internal_b = self.__sensors['Intérieur - Sensor [°C] / Mean - baseline'].asScatter(name='Intérieur / Baseline')
        result['/']['Comparaison intérieur vs extérieur - avec baseline']=self.toFigureFromScatters([external,internal,external_b,internal_b], '°C', 'Intérieur vs Extérieur')
        
        internalcm = self.__sensors['Intérieur - Sensor [°C] / Mean'].asScatter(name='Intérieur - Température')
        internalcmb = self.__sensors['Intérieur - Sensor [°C] / Mean - baseline'].asScatter(name='Intérieur - Température / Baseline')
        internalrhm = self.__sensors['Intérieur - Sensor [RH%] / Mean'].asScatter(name='Intérieur - Humidité',yaxis='y2')
        internalrhb = self.__sensors['Intérieur - Sensor [RH%] / Mean - baseline'].asScatter(name='Intérieur - Humidité / Baseline',yaxis='y2')
        result['/']['Comparaison intérieur vs extérieur - avec baseline et humidité']=self.toFigureFromScatters([internalcm,internalcmb,internalrhm,internalrhb,external,external_b], '°C', 'Intérieur vs Extérieur','RH%')
        
        # Analyse de détail atelier sous fenêtre
        
        sous = self.__sensors['Atelier Sous-fenêtre - T'].asScatter(name='Atelier Sous-fenêtre')
        sousb = self.__sensors['Atelier Sous-fenêtre - T - baseline'].asScatter(name='Atelier Sous-fenêtre - baseline')
        diff_ext = (self.__sensors['Atelier Sous-fenêtre - T']-self.__sensors['Extérieur']).asScatter(name='Différence extérieur-atelier sous fenêtre')
        diff_extb = (self.__sensors['Atelier Sous-fenêtre - T - baseline']-self.__sensors['Extérieur - baseline']).asScatter(name='Différence extérieur-atelier sous fenêtre - baseline')
        result['analyse']['Comparaison Atelier sous-fenêtre vs extérieur']=self.toFigureFromScatters([external,external_b,sous,sousb,diff_ext,diff_extb], '°C', 'Atelier sous fenêtre vs Extérieur')
        
        #TODO
        
        return result

    def filterOutSensor(self,filterFunctionToRemove):
        self.__sensors = {n:v for n,v in self.__sensors.items() if not filterFunctionToRemove(v)}
    