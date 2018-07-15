'''
Created on 10 juil. 2018

@author: borettim
'''

from areexsupport.sensor import sensor
from areexsupport.virtual_sensor import virtual_sensor

from datetime import datetime
from pytz import timezone


def testSensorInitOnlyMandataParameter():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:00', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:02:00', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name', val={d1: 1, d2: 2, d3: 3})
    s2 = sensor('name', val={d1: 2, d2: 4, d3: 9})
    s3 = sensor('name', val={d1: 3, d2: 6, d3: 12})
    s = virtual_sensor('name', [s1, s2, s3])
    assert s.name == 'name'
    assert s.unit == 'V'
    assert s.pos == 'N/A'
    assert len(s.values) == 3
    assert s.values == {d1: 2, d2: 4, d3: 8}
    assert s.clazz == 'VIRTUAL'


def testAsScatterError():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:00', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:02:00', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name', val={d1: 1, d2: 2, d3: 3})
    s2 = sensor('name', val={d1: 2, d2: 4, d3: 9})
    s3 = sensor('name', val={d1: 3, d2: 6, d3: 12})
    s = virtual_sensor('name', [s1, s2, s3])
    sc2 = s.asScatter(withError=True)
    assert list(sc2.x) == [d1, d2, d3]
    assert list(sc2.y) == [2, 4, 8]
    assert list(sc2.error_y.array) == [
        1, 2, 4]
    assert list(sc2.error_y.arrayminus) == [
        1, 2, 5]
