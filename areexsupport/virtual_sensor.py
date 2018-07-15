
# encoding: utf-8
'''
Support of a sensor that is virtual (not a physical sensor).

This module exposes the virtual_sensor class.

This module only exposes one single class : virtual_sensor ; Just use `from areexsupport.virtual_sensor import virtual_sensor` to use it
'''

import logging
from areexsupport.sensor import sensor

logger = logging.getLogger(__name__)

__all__ = ["virtual_sensor"]


class virtual_sensor(sensor):
    '''
    Class defining a virtual sensor.

    This class is an virtual sensor, with a name, a unit and datas.
    '''

    def __init__(self, name, val, unit='V', categories=None):
        '''
        Initialize this sensor.

        Mandatory parameters :
        - name : This is the name of this sensor and it should be unique.
        - val : Initial values for this sensor

        Optional parameters :
        - unit : This is the unit of this sensor (by default V), others classical value are °C and RH%.
        - categories : This may be an array of category to marks this sensor
        '''
        sensor.__init__(self, name, unit, 'N/A', val, 'VIRTUAL',
                        ['virtual'] if categories == None else ['virtual'] + categories)

        logger.debug('A new virtual sensor has been created - %s', self)
