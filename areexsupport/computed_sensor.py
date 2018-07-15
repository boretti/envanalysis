
# encoding: utf-8
'''
Support of a sensor that has been calculated (like point de rosee).

This module exposes the computed_sensor class.

This module only exposes one single class : computed_sensor ; Just use `from areexsupport.computed_sensor import computed_sensor` to use it
'''

import logging
from areexsupport.sensor import sensor

logger = logging.getLogger(__name__)

__all__ = ["computed_sensor"]


class computed_sensor(sensor):
    '''
    Class defining a computed sensor.

    This class is an computed sensor, with a name, a unit and datas.
    '''

    def __init__(self, name, val, unit='V'):
        '''
            Initialize this sensor.

            Mandatory parameters :
            - name : This is the name of this sensor and it should be unique.
            - val : Initial values for this sensor

            Optional parameters :
            - unit : This is the unit of this sensor (by default V), others classical value are °C and RH%.
        '''
        sensor.__init__(self, name, unit, 'N/A', val, 'COMPUTED')

        logger.debug('A new computed sensor has been created - %s', self)
