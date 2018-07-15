
# encoding: utf-8
'''
Support of a sensor that is a dew point.

This module exposes the dewpoint_sensor class.

This module only exposes one single class : dewpoint_sensor ; Just use `from areexsupport.dewpoint_sensor import dewpoint_sensor` to use it
'''

import logging
from areexsupport.computed_sensor import computed_sensor

logger = logging.getLogger(__name__)

__all__ = ["dewpoint_sensor"]


class dewpoint_sensor(computed_sensor):
    '''
    Class defining a dewpoint sensor.

    This class is an dewpoint sensor, with a name, a unit and datas.
    '''

    def __init__(self, name, t, rh, categories=None):
        '''
        Initialize this sensor.

        Mandatory parameters :
        - name : This is the name of this sensor and it should be unique.
        - t : Sensor with T value
        - rh Sensor with RH value

        Optional parameters :
        - categories : This may be an array of category to marks this sensor
        '''
        computed_sensor.__init__(self, name, {d: t.values[d] - (100 - v) / 5 for d,
                                              v in rh.values.items() if d in t.values}, '°C',
                                 ['dewpoint'] if categories == None else ['dewpoint'] + categories)

        logger.debug('A new dewpoint sensor has been created - %s', self)
