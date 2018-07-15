
# encoding: utf-8
'''
Support of a sensor that is computed.

This module exposes the computed_sensor class.

This module only exposes one single class : computed_sensor ; Just use `from areexsupport.computed_sensor import computed_sensor` to use it
'''

import logging
from areexsupport.virtual_sensor import virtual_sensor

logger = logging.getLogger(__name__)

__all__ = ["computed_sensor"]


class computed_sensor(virtual_sensor):
    '''
    Class defining a computed sensor.

    This class is an computed sensor, with a name, a unit and datas.
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
        virtual_sensor.__init__(self, name, val, unit,
                                ['computed'] if categories == None else ['computed'] + categories)

        logger.debug('A new computed sensor has been created - %s', self)
