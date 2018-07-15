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
    assert s.categories == []


def testSensorInitExplicit():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', 'RH%', 2, {d1: 1}, 'c', ['a'])
    assert s.name == 'name'
    assert s.unit == 'RH%'
    assert s.pos == 2
    assert s.values == {d1: 1}
    assert s.clazz == 'c'
    assert s.categories == ['a']


def testSensorDateTimeToMinute():
    m = sensor.dateTimeToMinute()
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    assert d1 != d2
    assert m(d1) == d1
    assert m(d2) == d1


def testSetValues():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name')
    assert len(s.values) == 0
    s.setValues({d1: 1.0})
    assert len(s.values) == 1
    assert d1 in s
    assert s.values[d1] == 1.0


def testStr():
    s = sensor('name', 'RH%', 2, {timezone('Europe/Zurich').localize(
        datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S')): 1}, 'c', ['x'])
    assert str(
        s) == "name:\tunit:RH%\tposition:2\tvalues count:1\tclazz:c\tcategories:['x']"


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


def testSub():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    s2 = sensor('name', val={d1: 0.5, d2: 1, d3: 5})
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
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    nt = []
    for x in sorted(s):
        nt.append(x)
    assert nt == [d1, d2, d3, d4]


def testItem():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    assert s[d1] == 1.0


def testLen():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    assert len(s) == 4


def testRange():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    assert s.range == '1.0 to 4.1'


def testPeriod():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})
    assert s.period == '2017-01-01 00:00:00 to 2017-01-01 00:01:01'


def testPeak():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    d5 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:02:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1, d5: -10})
    assert s.peaks == {d4: 4.1}


def testAsScatterPeak():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    d5 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:02:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1, d5: -10})
    sc1 = s.asScatter(peak=True)
    assert list(sc1.x) == [d4]
    assert list(sc1.y) == [4.1]
    assert sc1.name == "name - Peak"
    assert sc1.yaxis == "y"
    assert sc1.mode == 'markers'


def testAsScatterNoPrune():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    s1 = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1})
    sc1 = s1.asScatter()
    assert list(sc1.x) == [d1, d2, d3]
    assert list(sc1.y) == [1.0, 2.1, 3.1]
    assert sc1.name == "name"
    assert sc1.yaxis == "y"


def testAsScatterNoPruneBaseLine():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:01:01', '%d.%m.%Y %H:%M:%S'))
    s = sensor('name', val={d1: 1.0, d2: 2.1, d3: 3.1, d4: 4.1})

    sc1 = s.asScatter(baseline=True)
    assert sc1.name == "name - Baseline"
    assert list(sc1.x) == [d1, d2, d3, d4]
    assert list(sc1.y)[0] == approx(1)
    assert list(sc1.y)[1] == approx(2.1)
    assert list(sc1.y)[2] == approx(3.1)
    assert list(sc1.y)[3] == approx(4.1)


def testAsScatterPrune():
    d1 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:00', '%d.%m.%Y %H:%M:%S'))
    d2 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:01', '%d.%m.%Y %H:%M:%S'))
    d3 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:02', '%d.%m.%Y %H:%M:%S'))
    d4 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:03', '%d.%m.%Y %H:%M:%S'))
    d5 = timezone(
        'Europe/Zurich').localize(datetime.strptime('01.01.2017 00:00:04', '%d.%m.%Y %H:%M:%S'))

    s = sensor('name', val={d1: 1.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1]
    assert list(sc.y) == [1.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d5: 1.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d5]
    assert list(sc.y) == [1.0, 1.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d5]
    assert list(sc.y) == [1.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.5, d5: 1.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d5]
    assert list(sc.y) == [1.0, 1.5, 1.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.0, d5: 1.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d5]
    assert list(sc.y) == [1.0, 1.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 2.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d5]
    assert list(sc.y) == [1.0, 2.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d5]
    assert list(sc.y) == [1.0, 1.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.5, d3: 1.0, d5: 1.5})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d3, d5]
    assert list(sc.y) == [1.0, 1.5, 1.0, 1.5]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.0, d3: 1.0, d5: 1.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d5]
    assert list(sc.y) == [1.0, 1.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.0, d3: 1.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d3, d5]
    assert list(sc.y) == [1.0, 1.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 2.0, d3: 2.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d5]
    assert list(sc.y) == [1.0, 2.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.5, d3: 1.0, d4: 2.0, d5: 1.5})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d3, d4, d5]
    assert list(sc.y) == [1.0, 1.5, 1.0, 2.0, 1.5]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.5, d3: 1.0, d4: 2.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d3, d4, d5]
    assert list(sc.y) == [1.0, 1.5, 1.0, 2.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.0, d3: 1.5, d4: 2.0, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2, d3, d4, d5]
    assert list(sc.y) == [1.0, 1.0, 1.5, 2.0, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"

    s = sensor('name', val={d1: 1.0, d2: 1.5, d3: 1.5, d4: 1.5, d5: 2.0})
    sc = s.asScatter(prune=True)
    assert list(sc.x) == [d1, d2,  d4, d5]
    assert list(sc.y) == [1.0, 1.5, 1.5, 2.0]
    assert sc.name == "name"
    assert sc.yaxis == "y"


def testHash():
    s1 = sensor('name1')
    s2 = sensor('name2')
    s3 = sensor('name2', unit='RH%')
    assert hash(s1) == hash('name1')
    assert hash(s2) == hash('name2')
    assert hash(s3) == hash('name2')


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
