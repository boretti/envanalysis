
# encoding: utf-8
'''
Support of a areex sensor.

This module exposes the sensor class.

This module only exposes one single class : sensor ; Just use `from areexsupport.sensor import sensor` to use it
'''

import plotly.graph_objs as go
import peakutils
import numpy as np
import logging


logger = logging.getLogger(__name__)

__all__ = ["sensor"]


class sensor:
    '''
    Class defining an areex sensor.

    This class is an areex sensor, with a name, a unit and datas.
    '''

    @staticmethod
    def dateTimeToMinute():
        '''
        Method to return a function to normalize datetime to the minute.

        This method returns a function that strip the second and microsecond of a datetime.
        '''
        return lambda d: d.replace(second=0, microsecond=0)

    @staticmethod
    def __dateTimeTo5Minute(d):
        return d.replace(minute=(d.minute // 5) * 5, second=0, microsecond=0)

    @staticmethod
    def dateTimeTo5Minute():
        '''
        Method to return a function to normalize datetime by five minute.

        This method returns a function that strip the second and microsecond of a datetime and then round to every 5minute.
        '''
        return sensor.__dateTimeTo5Minute

    @property
    def values(self):
        '''
        Values of this sensor (association between date time and value).

        This is all the values of the sensors.

        The keys are the datetime object and the values are the measures (or computed) numerical value at this time.
        '''
        return self.__values

    @property
    def name(self):
        '''
        Name of this sensor.

        By convention, the name should by unique. This is required by the others class sensors.
        '''
        return self.__name

    @property
    def unit(self):
        '''
        Unit of this sensor (°C, RH%, ...).
        '''
        return self.__unit

    @property
    def pos(self):
        '''
        Position of the sensor in the source csv.

        Maybe anything when this sensor is computed.
        '''
        return self.__pos

    @property
    def categories(self):
        '''
        Categories of this sensor.
        '''
        return self.__categories

    @property
    def clazz(self):
        '''
        Class of this sensor. This is Sensor by default.

        Computed sensor use this property to set the way this was computed.
        '''
        return self.__clazz

    @property
    def range(self):
        '''
        range of value for this sensor.

        '''
        return '{:.1f} to {:.1f}'.format(min(self.__values.values()), max(self.__values.values()))

    @property
    def period(self):
        '''
        period of time for this sensor.

        '''
        return '{} to {}'.format(min(self.__values.keys()).strftime('%Y-%m-%d %H:%M:%S'), max(self.__values.keys()).strftime('%Y-%m-%d %H:%M:%S'))

    @property
    def peaks(self):
        '''
        peaks of the measures ; computed on the fly
        '''
        xt = []
        yt = []
        yt2 = []
        for d, v in sorted(self.__values.items()):
            xt.append(d)
            yt.append(v)
            yt2.append(-v)
        indexm1 = peakutils.indexes(
            np.asarray(yt), thres=0.5, min_dist=30)
        indexm2 = peakutils.indexes(np.asarray(yt2), thres=0.5, min_dist=30)
        result = {}
        for i in indexm1:
            result[xt[i]] = yt[i]
        for i in indexm2:
            result[xt[i]] = yt[i]
        return result

    def __iter__(self):
        '''
        Provides iterator support, based on the date of the measures.
        '''
        return iter(self.__values.keys())

    def __getitem__(self, date):
        '''
        Provides access by date to the dates
        '''
        return self.__values[date]

    def __len__(self):
        '''
        Return the number of entry of this sensor
        '''
        return len(self.__values)

    def __init__(self, name, unit='V', pos=1, val=None, clazz='Sensor', categories=None):
        '''
        Initialize this sensor.

        Mandatory parameters :
        - name : This is the name of this sensor and it should be unique.

        Optional parameters :
        - unit : This is the unit of this sensor (by default V), others classical value are °C and RH%.
        - pos : This is the position of this sensor in the pseudo csv from areex.
        - val : Initial values for this sensor. By default none
        - clazz : This is the clazz of this sensor. By default a real sensor is Sensor.
        - categories : This may be an array of category to marks this sensor
        '''
        self.__unit = unit
        self.__name = name
        self.__pos = pos
        self.__values = {} if val == None else val
        self.__blvalues = {} if val == None else sensor.__toBaseLine(val)
        self.__clazz = clazz
        self.__categories = [] if categories == None else categories

        logger.debug('A new sensor has been created - %s', self)

    def __hash__(self):
        '''
        Compute hash, based on the name
        '''
        return hash(self.__name)

    def __eq__(self, other):
        '''
        Compare two sensor, by comparing there name, for equality
        '''
        if isinstance(other, sensor):
            return self.name == other.name
        return False

    def __lt__(self, other):
        '''
        Compare two sensor, by comparing there name, for less
        '''
        if isinstance(other, sensor):
            return self.name < other.name
        return False

    def __le__(self, other):
        '''
        Compare two sensor, by comparing there name, for less or equal
        '''
        if isinstance(other, sensor):
            return self.name <= other.name
        return False

    def __ge__(self, other):
        '''
        Compare two sensor, by comparing there name, for greather or equal
        '''
        if isinstance(other, sensor):
            return self.name >= other.name
        return False

    def __gt__(self, other):
        '''
        Compare two sensor, by comparing there name, for greather
        '''
        if isinstance(other, sensor):
            return self.name > other.name
        return False

    def setValues(self, values):
        '''
        Set the values of this sensor.

        This method is used by the framework itself.
        '''
        self.__values = values
        self.__blvalues = sensor.__toBaseLine(values)

    def __repr__(self):
        return '{}:\tunit:{}\tposition:{}\tvalues count:{}\tclazz:{}\tcategories:{}'.format(self.__name, self.__unit, self.__pos, len(self.__values), self.__clazz, self.__categories)

    @staticmethod
    def __asScatterFull(values, name, yaxis='y'):
        xt = []
        yt = []
        for d, v in sorted(values.items()):
            xt.append(d)
            yt.append(v)
        return go.Scattergl(x=xt, y=np.asarray(yt), name=name, yaxis=yaxis)

    @staticmethod
    def __asScatterPrune(values, name, yaxis='y'):
        xt = []
        yt = []
        prevx = None
        prevy = None
        preva = None
        entries = sorted(values.items())
        for d, v in entries:
            if d == entries[0][0]:
                xt.append(d)
                yt.append(v)
                prevx = d
                prevy = v
                preva = True
                continue
            if preva and (v != prevy or d == entries[-1][0]):
                xt.append(d)
                yt.append(v)
                prevx = d
                prevy = v
                preva = True
                continue
            if preva and v == prevy:
                prevx = d
                prevy = v
                preva = False
                continue
            if not preva and (v == prevy and d != entries[-1][0]):
                prevx = d
                prevy = v
                preva = False
                continue
            if not preva and (v == prevy and d == entries[-1][0]):
                xt.append(d)
                yt.append(v)
                prevx = d
                prevy = v
                preva = True
                continue
            if not preva and v != prevy:
                xt.append(prevx)
                yt.append(prevy)
                xt.append(d)
                yt.append(v)
                prevx = d
                prevy = v
                preva = True
                continue
        return go.Scattergl(x=xt, y=np.asarray(yt), name=name, yaxis=yaxis)

    def asScatter(self, name=None, yaxis='y', prune=False, baseline=False):
        '''
        Generate a scatter (from plotly) for this sensor.

        This return a Scattergl instance for this sensor. X are the datetime entries and Y are the measures.

        Optional parameters :
        - name : to override the name of the scatter (by default this is the name of the sensor)
        - yaxis : to override the default y axis
        - prune : if set to True, this will prune the generated scatter (not applicable for min/max variante), by removing successive identical y values
        - baseline : if set to True, this will use the baseline

        '''
        logger.debug('Convert this sensor %s to a scatter', self)
        val = self.__blvalues if baseline else self.__values
        nname = (
            self.__name + " - Baseline" if baseline else self.__name) if name == None else name
        return self.__asScatterPrune(val, nname, yaxis) if prune else self.__asScatterFull(val, nname, yaxis)

    @staticmethod
    def __toBaseLine(values):
        xt = []
        yt = []
        for d, v in sorted(values.items()):
            xt.append(d)
            yt.append(v)
        baseline_values = peakutils.baseline(np.asarray(yt))
        return {xt[dt]: v for dt, v in enumerate(baseline_values)}

    def __sub__(self, other):
        '''
        Substract two sensors.

        Only date time existing in both sensor are substract.
        '''
        logger.debug('Generate a new sensor for %s (minus) %s', self, other)
        if not isinstance(other, sensor):
            raise ValueError('other must be a SensorClass')

        values = {}
        for d, v in self.__values.items():
            if d in other.__values:
                values[d] = v - other.__values[d]
        s = sensor(self.__name + ' (minus) ' + other.__name, unit=self.__unit, pos='_' + str(self.__pos),
                   val=values, clazz=self.__clazz + '->Minus')
        return s
