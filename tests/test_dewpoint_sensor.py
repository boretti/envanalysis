'''
Created on 10 juil. 2018

@author: borettim
'''

from areexsupport.sensor import sensor
from areexsupport.dewpoint_sensor import dewpoint_sensor

from datetime import datetime
from pytz import timezone


def testSensorInitOnlyMandataParameter():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:00', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:02:00', '%d.%m.%Y %H:%M:%S'))
    t = sensor('name', val={d1: 10, d2: 20, d3: 30})
    rh = sensor('name', val={d1: 35, d2: 40, d3: 50})
    s = dewpoint_sensor('name', t, rh)
    assert s.name == 'name'
    assert s.unit == '°C'
    assert s.pos == 'N/A'
    assert len(s.values) == 3
    assert s.values == {d1: -3.0, d2: 8.0, d3: 20.0}
    assert s.clazz == 'VIRTUAL'
    assert s.categories == ['virtual', 'computed', 'dewpoint']
