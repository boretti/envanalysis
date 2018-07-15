'''
Created on 10 juil. 2018

@author: borettim
'''

from pytest import fixture

from areexsupport.sensors import sensors
from datetime import datetime
from pytz import timezone
import textwrap


@fixture(scope="session")
def simpleinput(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("input.txt")
    ffn = open(fn, 'w')
    try:
        ffn.write(textwrap.dedent('''
        Measurement log

        Sensors:
        
        Column    Sensor    Unit
        1    Maquette Partie Haute - V    V
        2    Maquette Partie Haute - RH    RH%
        3    Maquette Partie Haute - T    °C
        4    Extérieur    °C
        
        Start date: 14.07.2018
        End date: 15.07.2018
        
        Time    1    2    3    4
        14.07.2018 00:00:39     3.2        23.4    
        14.07.2018 00:00:40                25.2
        14.07.2018 00:01:07        48.2        
        14.07.2018 00:01:29            23.4    
        14.07.2018 00:01:31                25.2
        14.07.2018 00:01:47        48.2        
        14.07.2018 00:02:09                25.2
        14.07.2018 00:02:33            23.4    
        14.07.2018 00:03:00                25.2
        14.07.2018 00:03:04        48.2        
        14.07.2018 00:03:44            23.4    
        14.07.2018 00:03:46                25.2
        14.07.2018 00:04:40        48.2        
        14.07.2018 00:04:52                25.1
        14.07.2018 00:05:27            23.4    
        14.07.2018 00:05:58        48.2        
        14.07.2018 00:06:04                25.2
        14.07.2018 00:06:21            23.4    
        14.07.2018 00:06:40        48.2        
        14.07.2018 00:19:27     3.2            ''').replace('    ', '\t'))
    finally:
        ffn.close()
    return fn


def testSensorsInitOnlyMandataParameter(simpleinput):
    d = sensors(simpleinput)
    d1 = sensors.fastparsedate('14.07.2018 00:00:00')
    d2 = sensors.fastparsedate('14.07.2018 00:01:00')
    d3 = sensors.fastparsedate('14.07.2018 00:02:00')
    d4 = sensors.fastparsedate('14.07.2018 00:03:00')
    d5 = sensors.fastparsedate('14.07.2018 00:04:00')
    d6 = sensors.fastparsedate('14.07.2018 00:05:00')
    d7 = sensors.fastparsedate('14.07.2018 00:06:00')

    dn = sensors.fastparsedate('15.07.2018 23:59:59')

    assert d.starttime == d1
    assert d.endtime == dn

    assert 'Extérieur' in d.keys()
    assert 'Maquette Partie Haute - RH' in d.keys()
    assert 'Maquette Partie Haute - T' in d.keys()
    assert 'Maquette Partie Haute - V' in d.keys()
    assert len(d.groups) == 1
    assert 'default' in d.groups
    assert len(d) == 5
    assert len(d['Extérieur'].values) == 6
    assert d['Extérieur'][d1] == 25.2
    assert d['Extérieur'][d2] == 25.2
    assert d['Extérieur'][d3] == 25.2
    assert d['Extérieur'][d4] == 25.2
    assert d['Extérieur'][d5] == 25.1
    assert d['Extérieur'][d7] == 25.2

def testSensorsInitWithFilterOutFunction(simpleinput):
    d = sensors(simpleinput,filterOutFunction=lambda this:this.name=='Extérieur')

    assert 'Extérieur' not in d.keys()
    assert 'Maquette Partie Haute - RH' in d.keys()
    assert 'Maquette Partie Haute - T' in d.keys()
    assert 'Maquette Partie Haute - V' in d.keys()
    assert len(d.groups) == 1
    assert 'default' in d.groups
    assert len(d) == 4

