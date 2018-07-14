'''
Created on 10 juil. 2018

@author: borettim
'''
from pytest import approx, raises

from areexsupport.sensor import sensor
from datetime import datetime
from pytz import timezone


def testSensorInitOnlyMandataParameter():
    s = sensor('name')
    assert s.name == 'name'
    assert s.unit == 'V'
    assert s.pos == 1
    assert len(s.values) == 0
    assert s.clazz == 'Sensor'


def testSensorInitExplicit():
    s = sensor('name', 'RH%', 2, {'x': 'y'}, 'c')
    assert s.name == 'name'
    assert s.unit == 'RH%'
    assert s.pos == 2
    assert s.values == {'x': 'y'}
    assert s.clazz == 'c'


def testSensorDateTimeToMinute():
    m = sensor.dateTimeToMinute()
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    assert d1 != d2
    assert m(d1) == d1
    assert m(d2) == d1


def testAdd():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name')
    assert len(s.values) == 0
    s.add(1.0, d1)
    assert len(s.values) == 1
    assert d1 in s
    assert s.values[d1] == 1.0


def testStr():
    s = sensor('name', 'RH%', 2, {'x': 'y'}, 'c')
    assert str(
        s) == "name:\tunit:RH%\tposition:2\tvalues count:1\tclazz:c"


def testSensorDateTimeTo5Minute():
    m = sensor.dateTimeTo5Minute()
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:05:00', '%d.%m.%Y %H:%M:%S'))
    d5 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:05:01', '%d.%m.%Y %H:%M:%S'))
    d6 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:06:01', '%d.%m.%Y %H:%M:%S'))
    assert m(d1) == d1
    assert m(d2) == d1
    assert m(d3) == d1
    assert m(d4) == d4
    assert m(d5) == d4
    assert m(d6) == d4


def testMergeValueBy():
    m = sensor.dateTimeToMinute()
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    d5 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:00', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name')
    s.add(1.2, d1)
    s.add(1.8, d2)
    s.add(2.4, d3)
    s.add(2.5, d4)
    s.mergeValueBy(m)
    assert s.values == {d1: 1.8, d5: 2.5}


def testToBaseLine():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name')
    s.add(1.0, d1)
    s.add(2.1, d2)
    s.add(3.1, d3)
    s.add(4.1, d4)
    s2 = s.toBaseLine()
    assert s2.values[d1] == approx(1)
    assert s2.values[d2] == approx(2.1)
    assert s2.values[d3] == approx(3.1)
    assert s2.values[d4] == approx(4.1)


def testSub():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name')
    s1.add(1.0, d1)
    s1.add(2.1, d2)
    s1.add(3.1, d3)
    s1.add(4.1, d4)
    s2 = sensor('name')
    s2.add(0.5, d1)
    s2.add(1, d2)
    s2.add(5, d3)
    s3 = s1 - s2
    assert s3.values[d1] == approx(0.5)
    assert s3.values[d2] == approx(1.1)
    assert s3.values[d3] == approx(-1.9)
    with raises(ValueError):
        s1 - 1


def testIter():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name')
    s.add(1.0, d1)
    s.add(2.1, d2)
    s.add(3.1, d3)
    s.add(4.1, d4)
    nt = []
    for x in sorted(s):
        nt.append(x)
    assert nt == [d1, d2, d3, d4]


def testAsScatter():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name')
    s1.add(1.0, d1)
    s1.add(2.1, d2)
    s1.add(3.1, d3)
    s2 = sensor('name')
    s2.add(0.5, d1)
    s2.add(1, d2)
    s2.add(3.1, d3)
    s3 = sensor('name')
    s3.add(6, d1)
    s3.add(8, d2)
    s3.add(5, d3)
    sc1 = s1.asScatter()
    assert list(sc1.x) == [d1, d2, d3]
    assert list(sc1.y) == [1.0, 2.1, 3.1]
    assert sc1.name == "name"
    assert sc1.yaxis == "y"
    sc2 = s1.asScatter('xname', s2, s3, 'y2')
    assert list(sc2.x) == [d1, d2, d3]
    assert list(sc2.y) == [1.0, 2.1, 3.1]
    assert sc2.name == "xname"
    assert sc2.yaxis == "y2"
    assert list(sc2.error_y.array) == [
        5.0, 5.9, 1.9]
    assert list(sc2.error_y.arrayminus) == [
        0.5, 1.1, 0]


def testEq():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert (s1 == s2) == False
    assert s2 == s3
    assert (s2 == s1) == False
    assert s3 == s2
    assert (s1 == 'x') == False


def testLt():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert s1 < s2
    assert(s2 < s3) == False
    assert(s2 < s1) == False
    assert(s3 < s2) == False
    assert(s1 < 'x') == False


def testLe():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert s1 <= s2
    assert s2 <= s3
    assert(s2 <= s1) == False
    assert s3 <= s2
    assert(s1 <= 'x') == False


def testGt():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert(s1 > s2) == False
    assert(s2 > s3) == False
    assert s2 > s1
    assert(s3 > s2) == False
    assert(s1 > 'x') == False


def testGe():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert(s1 >= s2) == False
    assert s2 >= s3
    assert s2 >= s1
    assert s3 >= s2
    assert(s1 >= 'x') == False
