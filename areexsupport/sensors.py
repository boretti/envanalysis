
# encoding: utf-8
'''
Support of a set of areex sensors.

This module exposes the sensors class.

This module only exposes one single class : sensors ; Just use `from areexsupport.sensors import sensors` to use it
'''

from areexsupport.sensor import sensor
from datetime import datetime, timezone
import statistics

import logging

logger = logging.getLogger(__name__)

__all__ = ["sensors"]


class sensors:
    '''
    This is a list of data sensors.

    This object is build from the pseudo csv of an export of the areex sensor.
    '''

    def __iter__(self):
        '''
        Provides iterator support, based on the sensors name.
        '''
        return iter(self.__sensors.keys())

    def items(self):
        '''
        Provides the sensors.
        '''
        return self.__sensors.items()

    def keys(self):
        '''
        Provides the sensors name.
        '''
        return self.__sensors.keys()

    def values(self):
        '''
        Provides the sensors.
        '''
        return self.__sensors.values()

    def __getitem__(self, name):
        '''
        Return a sensor by his name.
        '''
        return self.__sensors[name]

    def __len__(self):
        '''
        Return the number of sensors.
        '''
        return len(self.__sensors.items())

    @property
    def metassensors(self):
        return self.__metasensors.items()

    @property
    def groupsensors(self):
        return self.__metasensors.items()

    @property
    def sensors(self):
        return self.__sensors.items()

    @property
    def groups(self):
        return self.__groups.keys()

    @staticmethod
    def fastparsedate(instr):
        # '01.01.2017 00:00:00'
        day = int(instr[0:2])
        month = int(instr[3:5])
        year = int(instr[6:10])
        hour = int(instr[11:13])
        minute = int(instr[14:16])
        second = int(instr[17:19])
        return datetime(year, month, day, hour, minute, second, 0, timezone.utc)

    def __init__(self, filename, mergeFunction=sensor.dateTimeToMinute(), groupFunction=lambda n: 'default', metaFunction=lambda n: {'def': {k: v for k, v in n.items()}}, filterOutFunction=None):
        self.__sensors = {}
        self.__groups = {}
        sensorByPos = {}
        dtlimit = sensors.fastparsedate('01.01.2017 00:00:00')
        try:
            s = 0
            f = open(filename, 'r', buffering=1024 * 1024)
            for n, l in enumerate(f, 1):
                if n % 100000 == 0:
                    logger.info("Processing line:{}".format(n))
                if s == 4 and l != '\n':
                    ls = l.rstrip('\n').split('\t')
                    dt_obj = sensors.fastparsedate(ls[0])
                    if dtlimit > dt_obj:
                        continue
                    dt_obj = mergeFunction(dt_obj)
                    for p, v in filter(
                            lambda pi: pi[1] != '', enumerate(ls[1:], start=1)):
                        if dt_obj not in sensorByPos[p]:
                            sensorByPos[p][dt_obj] = [float(v)]
                        else:
                            sensorByPos[p][dt_obj].append(float(v))
                    continue
                if s == 0 and l.startswith('Sensors:'):
                    s = 1
                    continue
                if s == 1 and l.startswith('Column'):
                    s = 2
                    continue
                if s == 2 and l.startswith('Start date'):
                    s = 3
                    continue
                if s == 3 and l.startswith('Time'):
                    s = 4
                    continue
                if s == 2 and l != '\n':
                    ls = l.rstrip('\n').split('\t')
                    n = ls[1]
                    cs = sensor(n, ls[2], int(ls[0]))
                    sensorByPos[int(ls[0])] = {}
                    self.__sensors[cs.name] = cs

        finally:
            f.close()
        if filterOutFunction != None:
            logger.info("Filter sensor by using %s", filterOutFunction)
            self.__sensors = {
                n: v for n, v in self.__sensors.items() if not filterOutFunction(v)}
        logger.info("Create group sensor by using %s", groupFunction)
        for s in self.__sensors.values():
            gname = groupFunction(s.name)
            if gname not in self.__groups:
                self.__groups[gname] = []
            self.__groups[gname].append(s)
        logger.info("Create meta sensor by using %s", metaFunction)
        self.__metasensors = metaFunction(self.__sensors)
        logger.info(
            "Post processing data : computing average for %s", mergeFunction)
        for s in self.__sensors.values():
            logger.info(
                "Post processing data : computing average for %s", s.name)
            s.setValues({dt: statistics.mean(v)
                         for dt, v in sensorByPos[s.pos].items()})
        logger.info("Post processing data : computing point de rosee")
        self.__computePointRosee()
        logger.info("Post processing data : computing distribution")
        self.__computeDistribution()
        logger.info("Post processing data : computing baseline")
        self.__computeBaseLine()

    def __computePointRosee(self):
        for msn, ms in list(self.__metasensors.items()):
            if len(ms) < 2:
                continue
            tl = [s for s in ms.values() if s.unit ==
                  '°C' and s.clazz == 'Sensor']
            if len(tl) != 1:
                continue
            rhl = [s for s in ms.values() if s.unit ==
                   'RH%' and s.clazz == 'Sensor']
            if len(rhl) != 1:
                continue
            logger.info(
                "Post processing data : computing point de rosee for %s", msn)
            t = tl[0]
            rh = rhl[0]
            gs = [g for g, v in self.__groups.items() if t in v or rh in v]
            pt = {d: t.values[d] - (100 - v) / 5 for d,
                  v in rh.values.items() if d in t.values}
            n = msn + ' - Point de rosée'
            s = sensor(n, "°C", -1, pt, 'Point de rosée')
            self.__sensors[n] = s
            self.__metasensors[msn][n] = s
            for g in gs:
                self.__groups[g].append(s)

    def __computeDistribution(self):
        groups = self.__groups.keys()
        units = set(map(lambda v: v.unit, self.__sensors.values()))
        clazzs = set(map(lambda v: v.clazz, self.__sensors.values()))
        for g in groups:
            for u in units:
                for c in clazzs:
                    tsensor = self.sensorsByFunctionInGroup(
                        lambda this: this.unit == u and this.clazz == c, g)
                    if len(tsensor) > 1:
                        logger.info(
                            "Post processing data : compute distribution for  %s > %s > %s", g, u, c)
                        if g not in self.__metasensors:
                            self.__metasensors[g] = {}
                        tvalues = {}
                        for sn in tsensor:
                            for dt, v in sn.values.items():
                                if(dt not in tvalues):
                                    tvalues[dt] = []
                                tvalues[dt].append(v)
                        target = {'p-Variance': statistics.pvariance, 'Mean': statistics.mean,
                                  'Median': statistics.median, 'Min': min, 'Max': max}
                        mn = '{} - {} [{}]'.format(g, c, u)
                        self.__metasensors[mn] = {s.name: s for s in tsensor}
                        for s in tsensor:
                            self.__metasensors[g][s.name] = s
                        for name, method in target.items():
                            logger.info(
                                "Post processing data : compute distribution for  %s > %s > %s > %s", g, u, c, name)
                            n = '{} - {} [{}] / {}'.format(g, c, u, name)
                            s = sensor(n, u, -1, {d: method(v) for d, v in tvalues.items(
                            )},  c + "->" + name)
                            self.__groups[g].append(s)
                            self.__sensors[n] = s
                            self.__metasensors[mn][n] = s
                            self.__metasensors[g][n] = s

    def __computeBaseLine(self):
        for g, v in list(self.__groups.items()):
            logger.info(
                "Post processing data : compute baseline for group %s", g)
            for sn in list(v):
                logger.info(
                    "Post processing data : compute baseline for sensor %s", sn.name)
                s = sn.toBaseLine()
                self.__sensors[s.name] = s
                self.__groups[g].append(s)
                mn = [mn for mn, v in self.__metasensors.items()
                      if sn in v.values()]
                for m in mn:
                    self.__metasensors[m][s.name] = s

    def __repr__(self):
        def allsensors():
            return '\n\t'.join(map(sensor.__repr__, sorted(self.__sensors.values())))

        def allgroups():
            return '\n\t'.join(map(lambda g: '{}\n\t\t{}'.format(g, '\n\t\t'.join(map(sensor.__repr__, self.__groups[g]))), sorted(self.__groups.keys())))

        def allmetas():
            return '\n\t'.join(map(lambda m: '{}\n\t\t{}'.format(m, '\n\t\t'.join(map(sensor.__repr__, self.__metasensors[m].values()))), sorted(self.__metasensors.keys())))

        return 'All Sensors :\n\t{}\nGroups:\n\t{}\nMeta Sensors:\n\t{}'.format(allsensors(), allgroups(), allmetas())

    def sensorsByFunction(self, acceptFunction):
        return [value for value in self.__sensors.values() if acceptFunction(value)]

    def sensorsByFunctionInGroup(self, acceptFunction, group):
        return [value for value in self.__groups[group] if acceptFunction(value)]

    def toFigure(self, acceptFunctionOnSensor, ytitle, title=None, y2label=None, functionYAxis=lambda n: 'y'):
        return sensors.__tofigureObject([x.asScatter(yaxis=functionYAxis(x)) for x in self.sensorsByFunction(acceptFunctionOnSensor)], ytitle, title, y2label)

    @staticmethod
    def sensorToFigure(sensor, title=None):
        return sensors.__tofigureObject([sensor.asScatter()], sensor.unit, title)

    @staticmethod
    def scattersToFigure(scatters, ytitle, title=None, y2label=None):
        return sensors.__tofigureObject(scatters, ytitle, title, y2label)

    @staticmethod
    def __tofigureObject(data, ylabel, title=None, y2label=None):
        y2axis = None if y2label == None else dict(
            title=y2label, overlaying='y', side='right')
        return dict(
            data=data,
            layout=dict(
                xaxis=dict(
                    title='Date',
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label='1h', step='hour',
                                     stepmode='backward'),
                            dict(count=12, label='12h',
                                 step='hour', stepmode='backward'),
                            dict(count=1, label='1d', step='day',
                                 stepmode='backward'),
                            dict(count=2, label='2d', step='day',
                                 stepmode='backward'),
                            dict(count=7, label='1w', step='day',
                                 stepmode='backward'),
                            dict(count=14, label='2w',
                                 step='day', stepmode='backward'),
                            dict(count=1, label='1m', step='month',
                                 stepmode='backward'),
                            dict(count=2, label='2m', step='month',
                                 stepmode='backward'),
                            dict(count=6, label='6m', step='month',
                                 stepmode='backward'),
                            dict(count=1, label='YTD',
                                 step='year', stepmode='todate'),
                            dict(count=1, label='1y', step='year',
                                 stepmode='backward'),
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
