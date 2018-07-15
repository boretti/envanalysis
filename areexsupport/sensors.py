
# encoding: utf-8
'''
Support of a set of areex sensors.

This module exposes the sensors class.

This module only exposes one single class : sensors ; Just use `from areexsupport.sensors import sensors` to use it
'''

from areexsupport.sensor import sensor
from areexsupport.dewpoint_sensor import dewpoint_sensor
from areexsupport.aggregated_sensor import aggregated_sensor

from datetime import datetime, timezone
import numpy as np

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
    def sensors(self):
        return self.__sensors.items()

    @property
    def groups(self):
        '''
        Names of the groups of this set of sensors
        '''
        return self.__groups.keys()

    @property
    def starttime(self):
        '''
        The date and time of the start of the period of this object.
        '''
        return self.__starttime

    @property
    def endtime(self):
        '''
        The date and time of the end of the period of this object.
        '''
        return self.__endtime

    @property
    def source(self):
        '''
        The source file for this object.
        '''
        return self.__source

    @staticmethod
    def fastparsedate(instr):
        '''
        Convert a date formated 01.01.2017 00:00:00 - dd.mm.yyyy HH:MM:SS to a datetime.

        This implementation is not generic, but faster

        Parameter :
        - instr : the string to be converted.
        '''
        # '01.01.2017 00:00:00'
        day = int(instr[0:2])
        month = int(instr[3:5])
        year = int(instr[6:10])
        hour = int(instr[11:13])
        minute = int(instr[14:16])
        second = int(instr[17:19])
        return datetime(year, month, day, hour, minute, second, 0, timezone.utc)

    def __init__(self, filename, mergeFunction=sensor.dateTimeToMinute(), groupFunction=lambda n: 'default', metaFunction=lambda n: {'def': {k: v for k, v in n.items()}}, filterOutFunction=None, categoriesFunction=lambda n: None, dewpoint='Point de rosée'):
        '''
        Create an instance of sensors.

        Mandatory parameters :
        - filename : the path to the source file (pseudo-csv format from areex)

        Optional parameters :
        - mergeFunction : A function that receive a date time and compute a merged date time.
            By default, if omitted, a function that merge date by minute is used.
            In case a sensor has several value for the merged time, they are averaged.
        - groupFunction : A function to compute the group of a sensor. This function receive the sensor name and must return the group name.
            By default, if omitted, all sensor are added to the default group.
            * See below for informations about group
        - metaFunction : A function that compute meta sensor. This function receive array of tuple of the sensor [(name1, sensor1), ...] and return the structured meta sensor {m1:{n1:s1,...},...}.
            By default, if omitted, all sensors are added to the meta sensor def.
            * See below for informations about meta-sensors
        - filterOutFunction : A function to filter out (remove sensor when returning true) sensors. This function receive the sensor and must return a boolean.
            By default, no sensor are removed.
        - categoriesFunction : A function to compute optional categories of sensors. This function receive the sensor name and must return an array of string (or None).
            By default, no categories are added
            * See below for informations about categories
        - dewpoint : text to be used when creating devpoint sensor - By default, this is Point de rosée.

        Groups :
         Groups are used to define are sensors are part of a logical set of sensors. Virtual aggregated sensors will be computed for each group:
         - One for (each unit and physical sensor) - Assuming there are at least 2 sensors of this type
         - One for all dewpoint - Assuming there are at least 2 sensors of this type

        Meta-Sensors :
         Meta-sensors are used to define a set that are the same (for instance a sensor computing °C and %RH).
         If a meta-sensors contains one sensor that is °C and one sensore that is %RH (ignoring the others), the dewpoint will be computed

        Categories :
         Categories are marker on the sensors it self. They are also used to create additional groups.

        Processing order :
        - The file is readed. Each sensor is categorized by using categoriesFunction. Time are merged by using mergeFunction
        - If filterOutFunction is specified, remove sensors according this function
        - Create the groups by using the groupFunction
        - Create the meta-sensors by using metaFunction
        - Create groups based on the categories of the sensor (for each sensor, add it in also the groups corresponding to the categories)
        - Average the value of each time of the sensor
        - Compute dewpoint :
         - For each meta-sensors, if it is possible to compute the dewpoint :
           - compute it and create a new sensor
           - add this sensor to the current meta-sensor, and to all groups of the source °C and %RH sensor.
        - Compute distribution :
         - For each groups and each units
          - if there is at least 2 physical sensors
           - compute the aggregated sensors.
          - if there is at least 2 dewpoint sensors
           - compute the aggregated sensors.
         - Create meta sensors for this sensors and it to them the source sensors and the computed sensor
         - Add the computed sensors to the current groups
        '''
        self.__source = filename
        self.__sensors = {}
        self.__groups = {}
        self.__starttime = None
        self.__endtime = None
        sensorByPos = {}
        try:
            s = 0
            f = open(filename, 'r', buffering=1024 * 1024)
            for n, l in enumerate(f, 1):
                if n % 100000 == 0:
                    logger.info("Processing line:{}".format(n))
                if s == 5 and l != '\n':
                    ls = l.rstrip('\n').split('\t')
                    dt_obj = sensors.fastparsedate(ls[0])
                    if self.__starttime > dt_obj:
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
                    dt = l.split(':')[1].strip()
                    self.__starttime = datetime(
                        int(dt[6:10]), int(dt[3:5]), int(dt[0:2]), 0, 0, 0, 0, timezone.utc)
                    s = 3
                    continue
                if s == 3 and l.startswith('End date'):
                    dt = l.split(':')[1].strip()
                    self.__endtime = datetime(
                        int(dt[6:10]), int(dt[3:5]), int(dt[0:2]), 23, 59, 59, 0, timezone.utc)
                    s = 4
                    continue
                if s == 4 and l.startswith('Time'):
                    s = 5
                    continue
                if s == 2 and l != '\n':
                    ls = l.rstrip('\n').split('\t')
                    n = ls[1]
                    cs = sensor(n, ls[2], int(ls[0]),
                                categories=categoriesFunction(n))
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
        logger.info("Create groups from categories")
        categories = []
        for c in map(lambda v: v.categories, self.__sensors.values()):
            categories += c
        categories = set(categories)
        for c in filter(lambda this: this not in self.__groups, categories):
            self.__groups[c] = [f for f in filter(
                lambda this: c in this.categories, self.__sensors.values())]

        logger.info(
            "Post processing data : computing average for %s", mergeFunction)
        for s in self.__sensors.values():
            logger.info(
                "Post processing data : computing average for %s", s.name)
            s.setValues({dt: np.mean(v, dtype=np.float64)
                         for dt, v in sensorByPos[s.pos].items()})
        logger.info("Post processing data : computing dewpoint")
        self.__computePointRosee(dewpoint)
        logger.info("Post processing data : computing distribution")
        self.__computeDistribution(dewpoint)

    def __computePointRosee(self, dewpoint):
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
                "Post processing data : computing dewpoint for %s", msn)
            t = tl[0]
            rh = rhl[0]
            gs = [g for g, v in self.__groups.items() if t in v or rh in v]
            n = msn + ' - ' + dewpoint
            s = dewpoint_sensor(n, t, rh)
            self.__sensors[n] = s
            self.__metasensors[msn][n] = s
            for g in gs:
                self.__groups[g].append(s)

    def __computeDistribution(self, dewpoint):
        groups = self.__groups.keys()
        units = set(map(lambda v: v.unit, self.__sensors.values()))
        for g in groups:
            for u in units:
                def computeOne(tsensor, mn, categories):
                    if len(tsensor) > 1:
                        logger.info(
                            "Post processing data : compute distribution for  %s > %s : %s", g, u, [t.name for t in tsensor])
                        if g not in self.__metasensors:
                            self.__metasensors[g] = {}
                        ds = aggregated_sensor(mn, tsensor, categories)

                        self.__metasensors[mn] = {s.name: s for s in tsensor}
                        for s in tsensor:
                            self.__metasensors[g][s.name] = s

                        self.__groups[g].append(ds)
                        self.__sensors[mn] = ds
                        self.__metasensors[mn][mn] = ds
                        self.__metasensors[g][mn] = ds

                tsensor = self.sensorsByFunctionInGroup(
                    lambda this: this.unit == u and this.clazz == 'Sensor', g)
                computeOne(tsensor, '{} [{}]'.format(g, u), None)

                tsensor = self.sensorsByFunctionInGroup(
                    lambda this: this.unit == u and 'dewpoint' in this.categories, g)
                computeOne(
                    tsensor, '{} - {}'.format(g, dewpoint), ['computed', 'dewpoint'])

    def __repr__(self):
        metasensorid = {n: p for p, n in enumerate(
            sorted(self.__metasensors.keys()), 1)}

        maxmetaid = max(map(lambda this: len(
            str(this)), metasensorid.values()))

        def formatMetaSensorId(item):
            return '{} : {}'.format(str(item[1]).rjust(maxmetaid), item[0])

        maxmetaidname = max(map(lambda this: len(
            formatMetaSensorId(this)), metasensorid.items()))

        def grpsForSensor(s):
            return ', '.join(sorted([g[0] for g in self.__groups.items() if s in g[1]]))

        def metasForSensor(s):
            return ', '.join(map(str, sorted([metasensorid[g[0]] for g in self.__metasensors.items() if s.name in g[1].keys()])))

        def categoriesForSensor(s):
            return ', '.join(s.categories)

        lenmaxname = max(max(map(lambda this: len(
            this.name), self.__sensors.values())), 4)
        lenmaxunit = max(max(map(lambda this: len(
            this.unit), self.__sensors.values())), 4)
        lenmaxperiod = max(max(map(lambda this: len(
            this.period), self.__sensors.values())), 6)
        lenmaxrange = max(max(map(lambda this: len(
            this.range), self.__sensors.values())), 5)
        lenmaxval = max(max(map(lambda this: len(str(len(
            this))), self.__sensors.values())), 7)
        lenmaxclazz = max(max(map(lambda this: len(
            this.clazz), self.__sensors.values())), 5)
        lenmaxcategories = max(max(map(lambda this: len(
            categoriesForSensor(this)), self.__sensors.values())), 10)
        lenmaxgroups = max(max(map(lambda this: len(
            grpsForSensor(this)), self.__sensors.values())), 5)
        lenmetagroups = max(max(map(lambda this: len(
            metasForSensor(this)), self.__sensors.values())), 12)

        titlestring = '| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format('Name'.ljust(
            lenmaxname), 'Unit'.ljust(lenmaxunit), 'Period'.ljust(lenmaxperiod), 'Range'.ljust(lenmaxrange), '#Values'.rjust(lenmaxval), 'Clazz'.ljust(lenmaxclazz), 'Categories'.ljust(lenmaxcategories), 'Group'.ljust(lenmaxgroups), 'Meta-sensors'.ljust(lenmetagroups))
        fill = '|-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-|'.format('-' *
                                                                       lenmaxname, '-' * lenmaxunit, '-' * lenmaxperiod, '-' * lenmaxrange, '-' * lenmaxval,  '-' * lenmaxclazz, '-' * lenmaxcategories, '-' * lenmaxgroups, '-' * lenmetagroups)
        bfill = '+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+-{}-+'.format('-' *
                                                                        lenmaxname, '-' * lenmaxunit, '-' * lenmaxperiod, '-' * lenmaxrange, '-' * lenmaxval,  '-' * lenmaxclazz, '-' * lenmaxcategories, '-' * lenmaxgroups, '-' * lenmetagroups)

        def formatSensor(s):
            grps = grpsForSensor(s)
            metas = metasForSensor(s)
            cats = categoriesForSensor(s)
            return '| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(s.name.ljust(
                lenmaxname), s.unit.ljust(lenmaxunit), s.period.ljust(lenmaxperiod), s.range.ljust(lenmaxrange), str(len(s)).rjust(lenmaxval), s.clazz.ljust(lenmaxclazz), cats.ljust(lenmaxcategories), grps.ljust(lenmaxgroups), metas.ljust(lenmetagroups))

        sensors = '\n'.join(map(formatSensor, sorted(self.__sensors.values())))
        metaids = '\n'.join(
            map(formatMetaSensorId, sorted(metasensorid.items())))

        general = 'Source file : {}\nStart time  : {}\nEnd time    : {}'.format(self.__source,
                                                                                self.__starttime, self.__endtime)
        maxgeneral = max(map(len, general.split('\n')))

        return 'All Sensors:\n{}\n{}\n{}\n{}\n{}\n\nMeta-Sensors:\n{}\n{}\n\nGeneral informations:\n{}\n{}'.format(bfill, titlestring, fill, sensors, bfill, '-' * max(maxmetaidname, 13), metaids, '-' * maxgeneral, general)

    def sensorsByFunction(self, acceptFunction):
        return [value for value in self.__sensors.values() if acceptFunction(value)]

    def sensorsByFunctionInGroup(self, acceptFunction, group):
        return [value for value in self.__groups[group] if acceptFunction(value)]

    def toFigure(self, acceptFunctionOnSensor, ytitle, title=None, y2label=None, functionYAxis=lambda n: 'y', prune=False, baseline=False):
        return sensors.__tofigureObject([x.asScatter(yaxis=functionYAxis(x), prune=prune, baseline=baseline) for x in self.sensorsByFunction(acceptFunctionOnSensor)], ytitle, title, y2label)

    @staticmethod
    def sensorToFigure(sensor, title=None, prune=False, withBaseline=False, withPeak=False):
        s1 = [sensor.asScatter(prune=prune)]
        if withBaseline:
            s1.append(sensor.asScatter(prune=prune, baseline=True))
        if withPeak:
            s1.append(sensor.asScatter(prune=prune, peak=True))
        return sensors.__tofigureObject(s1, sensor.unit, title)

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
