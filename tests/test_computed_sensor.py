'''
Created on 10 juil. 2018

@author: borettim
'''

from areexsupport.computed_sensor import computed_sensor
from datetime import datetime
from pytz import timezone


def testSensorInitOnlyMandataParameter():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    s = computed_sensor('name', {d1: 3})
    assert s.name == 'name'
    assert s.unit == 'V'
    assert s.pos == 'N/A'
    assert len(s.values) == 1
    assert s.values == {d1: 3}
    assert s.clazz == 'COMPUTED'
    assert s.categories == ['computed']


def testSensorInitExplicit():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    s = computed_sensor('name', {d1: 1}, 'RH%', ['x'])
    assert s.name == 'name'
    assert s.unit == 'RH%'
    assert s.pos == 'N/A'
    assert s.values == {d1: 1}
    assert s.clazz == 'COMPUTED'
    assert s.categories == ['computed', 'x']
