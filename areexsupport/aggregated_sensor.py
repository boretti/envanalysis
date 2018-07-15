
# encoding: utf-8
'''
Support of a sensor which is aggregated, meaning it aggregate value from several sensors.

This module exposes the aggregated_sensor class.

This module only exposes one single class : virtual_sensor ; Just use `from areexsupport.aggregated_sensor import aggregated_sensor` to use it
'''

import logging
from areexsupport.virtual_sensor import virtual_sensor
import statistics
import plotly.graph_objs as go
import numpy as np

logger = logging.getLogger(__name__)

__all__ = ["aggregated_sensor"]


class aggregated_sensor(virtual_sensor):
    '''
    Class defining a aggregated sensor, meaning it aggregate value from several sensors.

    This class is an aggregated sensor, with a name, a unit and datas.

    The default values of this sensor are the mean of the received one.

    Also contains a min, max, median and p-variance for each time point
    '''

    def __init__(self, name, sources, categories=None):
        '''
        Initialize this sensor.

        Mandatory parameters :
        - name : This is the name of this sensor and it should be unique.
        - source : the sources sensors

        Optional parameters :
        - categories : This may be an array of category to marks this sensor
        '''
        tvalues = {}
        for sn in sources:
            for dt, v in sn.values.items():
                if(dt not in tvalues):
                    tvalues[dt] = []
                tvalues[dt].append(v)

        mean = {d: np.mean(v, dtype=np.float64) for d, v in tvalues.items(
        )}
        virtual_sensor.__init__(self, name, mean, sources[0].unit, [
            'aggregated'] if categories == None else ['aggregated'] + categories)

        self.__minValues = {d: min(v) for d, v in tvalues.items(
        )}

        self.__maxValues = {d: max(v) for d, v in tvalues.items(
        )}

        self.__medianValues = {d: np.median(v) for d, v in tvalues.items(
        )}

        self.__pvarianceValues = {d: statistics.pvariance(v, mean[d]) for d, v in tvalues.items(
        )}

        logger.debug('A new aggregated sensor has been created - %s', self)

    @staticmethod
    def __asScatterError(values, name, minv, maxv, yaxis='y'):
        xt = []
        yt = []
        minyt = []
        maxyt = []
        for d, v in sorted(values.items()):
            xt.append(d)
            yt.append(v)
            minyt.append(v - minv[d])
            maxyt.append(maxv[d] - v)
        return go.Scattergl(x=xt, y=np.asarray(yt), name=name, error_y=dict(type='data', symmetric=False, array=np.asarray(maxyt), arrayminus=np.asarray(minyt)), yaxis=yaxis)

    def asScatterWithError(self, name=None, yaxis='y'):
        '''
        Generate a scatter (from plotly) for this sensor, with eror (means vs min and max).

        This return a Scattergl instance for this sensor. X are the datetime entries and Y are the measures.

        Optional parameters :
        - name : to override the name of the scatter (by default this is the name of the sensor)
        - yaxis : to override the default y axis
        - prune : if set to True, this will prune the generated scatter (not applicable for min/max variante), by removing successive identical y values

        '''
        return aggregated_sensor.__asScatterError(self.values, self.name if name == None else name, self.__minValues, self.__maxValues, yaxis)
